from datetime import datetime,timezone,timedelta
from app.database.database import SessionLocal
from app.models.model import Job

def recover_stale_jobs():
    db = SessionLocal()
    
    # Sleep jobs are limited to five minutes. A ten-minute timeout keeps this
    # recovery mechanism safe for the supported local job types.
    cutoff_time = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(seconds=60)
    
    try:
        stale_jobs = db.query(Job).filter(
            Job.status == 'running', 
            Job.updated_at < cutoff_time
        ).all()

        for job in stale_jobs:
            print(f"Recovering jobID{job.id}")
            job.status = 'pending'

        if stale_jobs:
            db.commit()

        return stale_jobs

    finally:
        db.close()