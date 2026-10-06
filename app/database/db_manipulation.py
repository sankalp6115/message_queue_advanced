from app.database.database import SessionLocal
from app.models.model import Job
from datetime import datetime, timezone

db = SessionLocal()
job = db.query(Job).filter(Job.id == "a08d4a34-6e9e-47fe-9767-821c59d07f90").first()
if job and job.updated_at:
    current = datetime.now(timezone.utc).replace(tzinfo=None)
    time_diff = current - job.updated_at
    print(time_diff.total_seconds())
db.commit()
db.close()