import pytest
from io import BytesIO
from app.services.pdf_parser import PDFParserService, PDFParsingError


def test_pdf_parser_service_initialization():
    """Test that PDFParserService initializes correctly"""
    service = PDFParserService()
    assert service._markitdown is not None


def test_pdf_parser_with_empty_bytes():
    """Test that parser handles empty bytes gracefully"""
    service = PDFParserService()
    
    with pytest.raises(PDFParsingError):
        service.parse_pdf_content(b"")


def test_pdf_parser_with_invalid_data():
    """Test that parser handles invalid PDF data gracefully"""
    service = PDFParserService()
    
    with pytest.raises(PDFParsingError):
        service.parse_pdf_content(b"not a pdf file")


def test_pdf_parser_with_bytesio():
    """Test that parser accepts BytesIO objects"""
    service = PDFParserService()
    invalid_pdf = BytesIO(b"not a pdf")
    
    with pytest.raises(PDFParsingError):
        service.parse_pdf_content(invalid_pdf) 