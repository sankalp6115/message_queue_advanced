import json
import uuid
from sqlalchemy.orm import Session
from app.models.model import Job
from app.schemas.schema import JobRequest, JobResponse

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
