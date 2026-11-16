from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.schema import JobRequest, JobResponse
from app.services.job_service import (
    create_job,
    create_image_job_from_upload,
    get_job_by_id,
    list_jobs,
    to_job_response,
)

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.post("", status_code=status.HTTP_201_CREATED, response_model=JobResponse)
def enqueue_job(
    request: JobRequest,
    db: Session = Depends(get_db),
):
    job = create_job(db, request)
    return to_job_response(job)


@router.post("/upload", status_code=status.HTTP_201_CREATED, response_model=JobResponse)
def upload_image(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    ext = Path(file.filename or "").suffix.lower()
    allowed_extensions = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".gif", ".tiff"}
    if ext not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file format '{ext}'. Allowed formats: {', '.join(sorted(allowed_extensions))}",
        )

    job = create_image_job_from_upload(db, file)
    return to_job_response(job)


@router.get("", response_model=list[JobResponse])
def get_all_jobs(db: Session = Depends(get_db)):
    return [to_job_response(job) for job in list_jobs(db)]


@router.get("/{job_id}",response_model=JobResponse)
def get_job(job_id: str, db: Session = Depends(get_db)):
    job = get_job_by_id(db, job_id)

    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")

    return to_job_response(job)

