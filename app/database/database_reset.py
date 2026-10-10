from app.database.database import SessionLocal
from app.models.model import Job

db = SessionLocal()
jobs = db.query(Job).all()
for job in jobs:
    job.status = "pending"
    job.result = None
    job.error = None

db.commit()