from datetime import datetime, timezone, timedelta
from app.workers.recovery import recover_stale_jobs
import time
import json

from app.database.database import SessionLocal
from app.models.model import Job
from app.workers.handlers import task_executor

def claim_next_job(db:SessionLocal):
    candidate = db.query(Job).filter(Job.status == 'pending').first()
    if not candidate:
        return None

    rows_updated = db.query(Job).filter(
        Job.id == candidate.id,
        Job.status == 'pending'
    ).update({
        "status": "running"
    })

    db.commit()

    if rows_updated == 1:
        return candidate
    else:
        return None

def process_job(db:SessionLocal,job:Job):
    print(f"Executing {job.id}")

    try:
        job_payload = json.loads(job.payload)
        result = task_executor(job,job_payload)
        job.status = "completed"
        return result
    
    except Exception as e:
        job.status = "failed"
        job.error = str(e)
        print(f"JobID {job.id} failed: {e}")

    finally:    
        db.commit()

def executor():
    while(True):
        print("Trying")
        db = SessionLocal()
        try:
            job = claim_next_job(db)
            if job:
                process_job(db,job)

            recover_stale_jobs()
        except Exception as e:
            print(f"Error processing jobs: {e}")
        finally:
            db.close()
                
        # Throttling
        time.sleep(1)


if __name__ == "__main__":
    executor()
