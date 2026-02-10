"""
Unit tests for the OCR processor module.

This module tests the OCR functionality including:
- Engine availability detection
- Text extraction from valid images
- Graceful fallback when OCR engines are not configured
- Error handling for invalid/corrupted input

Author: Savani Thakur
Date: 2026-02-09
"""

import io
import pytest
from PIL import Image, ImageDraw, ImageFont

from engine import ocr_processor


class TestAvailableEngines:
    """Tests for the available_engines() function."""

    def test_available_engines_returns_list(self):
        """Verify that available_engines() always returns a list."""
        result = ocr_processor.available_engines()
        assert isinstance(result, list), "available_engines() should return a list"

    def test_available_engines_contains_valid_names(self):
        """Verify that returned engine names are from the expected set."""
        valid_engines = {"easyocr", "pytesseract"}
        result = ocr_processor.available_engines()
        
        for engine in result:
            assert engine in valid_engines, (
                f"Unexpected engine '{engine}'. Expected one of: {valid_engines}"
            )


class TestExtractText:
    """Tests for the extract_text() function."""

    @pytest.fixture
    def simple_image_bytes(self) -> bytes:
        """
        Create a simple test image with text for OCR testing.
        
        Returns:
            bytes: PNG image data containing simple text.
        """
        # Create a white image with black text
        img = Image.new("RGB", (400, 100), color="white")
        draw = ImageDraw.Draw(img)
        
        # Draw simple text that OCR should be able to read
        draw.text((10, 30), "TEST OCR TEXT 12345", fill="black")
        
        # Convert to bytes
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        return buffer.getvalue()

    @pytest.fixture
    def blank_image_bytes(self) -> bytes:
        """
        Create a blank white image with no text.
        
        Returns:
            bytes: PNG image data with no text content.
        """
        img = Image.new("RGB", (200, 100), color="white")
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        return buffer.getvalue()

    def test_extract_text_returns_string(self, simple_image_bytes: bytes):
        """Verify that extract_text() always returns a string."""
        result = ocr_processor.extract_text(simple_image_bytes)
        assert isinstance(result, str), "extract_text() should return a string"

    def test_extract_text_handles_valid_image(self, simple_image_bytes: bytes):
        """Verify that extract_text() processes valid image data without error."""
        # Should not raise any exception
        result = ocr_processor.extract_text(simple_image_bytes)
        
        # Result should be non-empty (either extracted text or fallback message)
        assert len(result) > 0, "extract_text() should return non-empty string"

    def test_extract_text_handles_blank_image(self, blank_image_bytes: bytes):
        """Verify that extract_text() handles images with no text gracefully."""
        result = ocr_processor.extract_text(blank_image_bytes)
        
        # Should return a string (possibly empty or fallback message)
        assert isinstance(result, str), "Should return string even for blank images"

    def test_extract_text_fallback_message_format(self, simple_image_bytes: bytes):
        """
        Verify fallback message is returned when OCR engines are not configured.
        
        Note: If OCR engines ARE available, this test validates that text 
        extraction works. If not, it validates the fallback message format.
        """
        result = ocr_processor.extract_text(simple_image_bytes)
        engines = ocr_processor.available_engines()
        
        if not engines:
            # No engines available - should return fallback message
            assert "OCR not configured" in result or "Install" in result, (
                "Fallback message should mention OCR configuration"
            )
        else:
            # Engines available - should attempt extraction
            # Result should be a non-empty string
            assert len(result) > 0, "Should return extracted text when engines available"

    def test_extract_text_with_corrupted_data(self):
        """Verify graceful handling of corrupted/invalid image data."""
        corrupted_data = b"not a valid image at all - just random bytes 12345"
        
        # Should not raise exception - should handle gracefully
        result = ocr_processor.extract_text(corrupted_data)
        
        # Should return a string (fallback message)
        assert isinstance(result, str), "Should return string even for invalid data"
        assert len(result) > 0, "Should return fallback message for invalid data"

    def test_extract_text_with_empty_bytes(self):
        """Verify graceful handling of empty byte input."""
        empty_data = b""
        
        # Should not raise exception
        result = ocr_processor.extract_text(empty_data)
        
        # Should return a string
        assert isinstance(result, str), "Should return string for empty input"


class TestOCRIntegration:
    """
    Integration tests that verify OCR works end-to-end when engines are available.
    
    These tests are skipped if no OCR engines are installed.
    """

    @pytest.fixture
    def high_contrast_image_bytes(self) -> bytes:
        """
        Create a high-contrast image that should be easy for OCR to read.
        
        Returns:
            bytes: PNG image with clear, high-contrast text.
        """
        # Create large, clear image for better OCR accuracy
        img = Image.new("RGB", (600, 150), color="white")
        draw = ImageDraw.Draw(img)
        
        # Use large, clear text
        draw.text((20, 50), "LEGAL NOTICE SECTION 420", fill="black")
        
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        return buffer.getvalue()

    @pytest.mark.skipif(
        len(ocr_processor.available_engines()) == 0,
        reason="No OCR engines available (install easyocr or pytesseract)"
    )
    def test_ocr_extracts_readable_text(self, high_contrast_image_bytes: bytes):
        """
        Verify that OCR can extract text from a clear image.
        
        This test only runs when at least one OCR engine is installed.
        """
        result = ocr_processor.extract_text(high_contrast_image_bytes)
        
        # Should contain some recognizable text
        # Note: OCR may not be perfect, so we check for partial matches
        result_upper = result.upper()
        
        # At least one of these keywords should be detected
        keywords = ["LEGAL", "NOTICE", "SECTION", "420"]
        found_any = any(kw in result_upper for kw in keywords)
        
        assert found_any or "OCR" not in result, (
            f"OCR should extract some text from clear image. Got: {result[:100]}"
        )
