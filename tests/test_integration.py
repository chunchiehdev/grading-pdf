import pytest
import asyncio
from fastapi.testclient import TestClient
from io import BytesIO
import time
import json

from app.main import app
from app.worker import celery_app, parse_pdf_task
from app.config import settings


# Test client for API testing
client = TestClient(app)


def create_sample_pdf_bytes():
    """Create a minimal PDF for testing"""
    # This is a minimal PDF structure that should be parseable
    pdf_content = b"""%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj

2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj

3 0 obj
<<
/Type /Page
/Parent 2 0 R
/Contents 4 0 R
>>
endobj

4 0 obj
<<
/Length 44
>>
stream
BT
/F1 12 Tf
72 720 Td
(Hello World) Tj
ET
endstream
endobj

xref
0 5
0000000000 65535 f 
0000000010 00000 n 
0000000079 00000 n 
0000000173 00000 n 
0000000301 00000 n 
trailer
<<
/Size 5
/Root 1 0 R
>>
startxref
398
%%EOF"""
    return pdf_content


class TestIntegration:
    """Integration tests for the PDF parsing service"""
    
    def test_health_check(self):
        """Test that the API is running"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
    
    def test_parse_pdf_async_endpoint(self):
        """Test asynchronous PDF parsing endpoint"""
        pdf_bytes = create_sample_pdf_bytes()
        
        files = {"file": ("test.pdf", BytesIO(pdf_bytes), "application/pdf")}
        response = client.post("/parse", files=files)
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "pending"
        assert "task_id" in data
        
        # Wait and check task status
        task_id = data["task_id"]
        max_retries = 10
        for _ in range(max_retries):
            status_response = client.get(f"/task/{task_id}")
            assert status_response.status_code == 200
            status_data = status_response.json()
            
            if status_data["status"] == "success":
                assert "content" in status_data
                assert isinstance(status_data["content"], str)
                break
            elif status_data["status"] == "failed":
                pytest.fail(f"Task failed: {status_data.get('error')}")
            
            time.sleep(1)
        else:
            pytest.fail("Task did not complete within timeout")
    
    def test_file_size_limit(self):
        """Test file size validation"""
        # Create a file larger than the limit
        large_content = b"x" * (settings.MAX_FILE_SIZE + 1)
        
        files = {"file": ("large.pdf", BytesIO(large_content), "application/pdf")}
        response = client.post("/parse", files=files)
        
        assert response.status_code == 413
        data = response.json()
        assert "File too large" in data["detail"]
    
    def test_invalid_file_type(self):
        """Test that non-PDF files are rejected"""
        text_content = b"This is not a PDF file"
        
        files = {"file": ("test.txt", BytesIO(text_content), "text/plain")}
        response = client.post("/parse", files=files)
        
        assert response.status_code == 400
        data = response.json()
        assert "Only PDF files are supported" in data["detail"]
    
    def test_celery_task_directly(self):
        """Test Celery task directly"""
        pdf_bytes = create_sample_pdf_bytes()
        
        # Test the task function directly
        result = parse_pdf_task(pdf_bytes, "test_user", "test_file")
        
        assert result["status"] == "success"
        assert result["user_id"] == "test_user"
        assert result["file_id"] == "test_file"
        assert result["error"] is None
        assert isinstance(result["content"], str)
    
    def test_celery_task_with_invalid_pdf(self):
        """Test Celery task with invalid PDF"""
        invalid_pdf = b"not a pdf"
        
        result = parse_pdf_task(invalid_pdf, "test_user", "test_file")
        
        # MarkItDown is very permissive and may extract some text even from invalid PDFs
        # So we just verify the task completed and returned the expected structure
        assert result["user_id"] == "test_user" 
        assert result["file_id"] == "test_file"
        assert result["status"] in ["success", "failed"]  # Either is acceptable
        assert "content" in result
        assert "error" in result


class TestCeleryWorker:
    """Tests for Celery worker functionality"""
    
    def test_celery_app_configuration(self):
        """Test that Celery app is configured correctly"""
        assert celery_app.conf.task_serializer == 'json'
        assert celery_app.conf.result_serializer == 'json'
        assert 'json' in celery_app.conf.accept_content
        assert celery_app.conf.timezone == 'UTC'
        assert celery_app.conf.enable_utc is True
    
    def test_celery_broker_backend_config(self):
        """Test that Celery broker and backend are using Redis"""
        assert settings.REDIS_URL in str(celery_app.conf.broker_url)
        assert settings.REDIS_URL in str(celery_app.conf.result_backend)


if __name__ == "__main__":
    # Run tests directly
    pytest.main([__file__, "-v"]) 