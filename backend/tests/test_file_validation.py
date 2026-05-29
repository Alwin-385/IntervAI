"""Tests for file upload validation utilities."""

import pytest

pytestmark = pytest.mark.unit


class TestSanitizeFilename:
    def test_normal_filename_unchanged(self):
        from app.utils.file_validation import sanitize_filename
        assert sanitize_filename("my_resume.pdf") == "my_resume.pdf"

    def test_strips_path_traversal(self):
        from app.utils.file_validation import sanitize_filename
        result = sanitize_filename("../../etc/passwd.pdf")
        assert ".." not in result
        assert "/" not in result

    def test_replaces_special_chars(self):
        from app.utils.file_validation import sanitize_filename
        result = sanitize_filename("résumé & cv!.pdf")
        # Should produce a sanitized name ending in .pdf
        assert result.endswith(".pdf")

    def test_empty_name_raises(self):
        from app.utils.file_validation import sanitize_filename
        from app.core.exceptions import ValidationAppError
        with pytest.raises(ValidationAppError):
            sanitize_filename("")

    def test_long_name_truncated(self):
        from app.utils.file_validation import sanitize_filename
        long_name = "a" * 600 + ".pdf"
        result = sanitize_filename(long_name)
        assert len(result) <= 512


class TestValidatePdfUpload:
    def _settings(self):
        from app.core.config import Settings
        return Settings(resume_max_size_bytes=5 * 1024 * 1024)

    def test_valid_pdf_passes(self):
        from app.utils.file_validation import validate_pdf_upload
        validate_pdf_upload(
            filename="resume.pdf",
            content_type="application/pdf",
            data=b"%PDF-1.4 fake",
            settings=self._settings(),
        )

    def test_empty_file_raises(self):
        from app.utils.file_validation import validate_pdf_upload
        from app.core.exceptions import ValidationAppError
        with pytest.raises(ValidationAppError, match="empty"):
            validate_pdf_upload(
                filename="resume.pdf",
                content_type="application/pdf",
                data=b"",
                settings=self._settings(),
            )

    def test_oversized_file_raises(self):
        from app.utils.file_validation import validate_pdf_upload
        from app.core.exceptions import ValidationAppError
        big = b"%PDF-" + b"x" * (6 * 1024 * 1024)
        with pytest.raises(ValidationAppError, match="size"):
            validate_pdf_upload(
                filename="big.pdf",
                content_type="application/pdf",
                data=big,
                settings=self._settings(),
            )

    def test_non_pdf_extension_raises(self):
        from app.utils.file_validation import validate_pdf_upload
        from app.core.exceptions import ValidationAppError
        with pytest.raises(ValidationAppError):
            validate_pdf_upload(
                filename="resume.exe",
                content_type="application/pdf",
                data=b"%PDF-1.4",
                settings=self._settings(),
            )

    def test_fake_pdf_content_raises(self):
        from app.utils.file_validation import validate_pdf_upload
        from app.core.exceptions import ValidationAppError
        with pytest.raises(ValidationAppError, match="valid PDF"):
            validate_pdf_upload(
                filename="resume.pdf",
                content_type="application/pdf",
                data=b"This is not a PDF",
                settings=self._settings(),
            )

    def test_wrong_mime_raises(self):
        from app.utils.file_validation import validate_pdf_upload
        from app.core.exceptions import ValidationAppError
        with pytest.raises(ValidationAppError, match="content type"):
            validate_pdf_upload(
                filename="resume.pdf",
                content_type="text/html",
                data=b"%PDF-1.4",
                settings=self._settings(),
            )
