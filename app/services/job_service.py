import json
import uuid
from sqlalchemy.orm import Session
from app.models.model import Job
from app.schemas.schema import JobRequest, JobResponse

import os
import shutil
from pathlib import Path
from dotenv import load_dotenv
from fastapi import UploadFile, HTTPException, status

BASE_DIR = Path(__file__).resolve().parents[2]
load_dotenv(BASE_DIR / "app" / ".env")
ROOT_DIR = Path(os.getenv("ROOT_DIR", BASE_DIR))
ASSETS_DIR = Path(os.getenv("ASSETS_DIR", ROOT_DIR / "assets"))
IMG_DIR = Path(os.getenv("IMG_DIR", ASSETS_DIR / "image"))


def create_job(db: Session, request: JobRequest) -> Job:
    job = Job(
        id=str(uuid.uuid4()),
        type=request.type,
        payload=json.dumps(request.payload.model_dump()),
        status="pending",
    )

    try:
        db.add(job)
        db.commit()
        db.refresh(job)
        return job
    except Exception:
        db.rollback()
        raise


def create_image_job_from_upload(db: Session, file: UploadFile) -> Job:
    task_id = str(uuid.uuid4())
    ext = Path(file.filename or "").suffix.lower()
    if not ext:
        ext = ".jpg"

    saved_filename = f"{task_id}{ext}"
    IMG_DIR.mkdir(parents=True, exist_ok=True)
    destination = IMG_DIR / saved_filename

    try:
        with open(destination, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save uploaded image: {e}",
        )

    job = Job(
        id=task_id,
        type="image",
        payload=json.dumps({
            "image_path": saved_filename,
            "operation": "compress",
        }),
        status="pending",
    )

    try:
        db.add(job)
        db.commit()
        db.refresh(job)
        return job
    except Exception:
        db.rollback()
        if destination.exists():
            destination.unlink(missing_ok=True)
        raise


def get_job_by_id(db: Session, job_id: str) -> Job | None:
    return db.query(Job).filter(Job.id == job_id).first()


def list_jobs(db: Session) -> list[Job]:
    return db.query(Job).order_by(Job.created_at.desc()).all()

def to_job_response(job: Job) -> JobResponse:
    return JobResponse(
        id=job.id,
        type=job.type,
        payload=json.loads(job.payload),
        status=job.status,
        result=json.loads(job.result) if job.result else None,
        error=job.error,
        created_at=job.created_at,
        updated_at=job.updated_at,
    )
