from typing import Union, BinaryIO
from markitdown import MarkItDown
from pathlib import Path
import io
import logging

logger = logging.getLogger(__name__)


class PDFParsingError(Exception):
    """Custom exception for PDF parsing errors"""
    pass


class PDFParserService:
    """Clean service class for PDF parsing using MarkItDown"""
    
    def __init__(self):
        self._markitdown = MarkItDown()
    
    def parse_pdf_content(self, file_data: Union[bytes, BinaryIO]) -> str:
        """
        Parse PDF content to markdown
        
        Args:
            file_data: PDF file as bytes or binary file-like object
            
        Returns:
            Parsed markdown content as string
            
        Raises:
            PDFParsingError: If parsing fails
        """
        try:
            # Convert bytes to BytesIO if needed
            if isinstance(file_data, bytes):
                file_stream = io.BytesIO(file_data)
            else:
                file_stream = file_data
            
            # Ensure we're at the beginning of the stream
            file_stream.seek(0)
            
            # Parse using MarkItDown
            result = self._markitdown.convert_stream(file_stream)
            
            if not result or not result.text_content:
                raise PDFParsingError("No content extracted from PDF")
                
            return result.text_content
            
        except Exception as e:
            logger.error(f"PDF parsing failed: {str(e)}")
            raise PDFParsingError(f"Failed to parse PDF: {str(e)}") from e
    
    def parse_pdf_file(self, file_path: Union[str, Path]) -> str:
        """
        Parse PDF file from filesystem
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            Parsed markdown content as string
        """
        try:
            with open(file_path, 'rb') as f:
                return self.parse_pdf_content(f)
        except FileNotFoundError:
            raise PDFParsingError(f"PDF file not found: {file_path}")
        except PermissionError:
            raise PDFParsingError(f"Permission denied accessing: {file_path}") 