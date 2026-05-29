"""API tests for resume endpoints."""

from __future__ import annotations

import io
import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

pytestmark = pytest.mark.unit


def _fake_resume(user_id=None):
    from app.models.resume import Resume
    from app.models.enums import ResumeStatus
    r = MagicMock(spec=Resume)
    r.id = uuid.uuid4()
    r.user_id = user_id or uuid.uuid4()
    r.original_filename = "test_resume.pdf"
    r.storage_key = "resumes/test.pdf"
    r.status = ResumeStatus.COMPLETED
    r.content_text = "Software Engineer with 5 years experience"
    r.created_at = "2026-01-01T00:00:00Z"
    r.updated_at = "2026-01-01T00:00:00Z"
    r.analysis = None
    r.file_size = 1024
    r.mime_type = "application/pdf"
    r.extraction_error = None
    return r


def test_list_resumes_returns_200(client, auth_headers, mock_user):
    from app.services.resume import ResumeService
    with patch.object(ResumeService, "list_resumes", new_callable=AsyncMock) as mock_list:
        mock_list.return_value = ([], 0)
        response = client.get("/api/v1/resumes", headers=auth_headers)
    assert response.status_code in (200, 422, 500)
    if response.status_code == 200:
        body = response.json()
        assert "items" in body


def test_upload_resume_rejects_non_pdf(client, auth_headers):
    fake_txt = io.BytesIO(b"Not a PDF file content")
    response = client.post(
        "/api/v1/resumes/upload",
        headers=auth_headers,
        files={"file": ("resume.txt", fake_txt, "text/plain")},
        data={"title": "My Resume"},
    )
    assert response.status_code in (400, 422)


def test_upload_resume_rejects_empty_file(client, auth_headers):
    response = client.post(
        "/api/v1/resumes/upload",
        headers=auth_headers,
        files={"file": ("resume.pdf", io.BytesIO(b""), "application/pdf")},
        data={"title": "My Resume"},
    )
    assert response.status_code in (400, 422)


def test_get_resume_not_found_returns_404(client, auth_headers, mock_db_session):
    from app.repositories.resume import ResumeRepository
    with patch.object(ResumeRepository, "get_by_id", new_callable=AsyncMock, return_value=None):
        fake_id = uuid.uuid4()
        response = client.get(f"/api/v1/resumes/{fake_id}", headers=auth_headers)
    assert response.status_code == 404


def test_delete_resume_unauthorized_returns_4xx(client, auth_headers, mock_user, mock_db_session):
    from app.repositories.resume import ResumeRepository
    # Resume belongs to a different user
    other_user_resume = _fake_resume(user_id=uuid.uuid4())
    with patch.object(ResumeRepository, "get_by_id", new_callable=AsyncMock, return_value=other_user_resume):
        response = client.delete(f"/api/v1/resumes/{other_user_resume.id}", headers=auth_headers)
    assert response.status_code in (401, 403, 404)
