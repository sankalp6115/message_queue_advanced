from fastapi import FastAPI 
import uvicorn
from app.api.router import router
from app.database.database import engine
from app.models.model import Base

Base.metadata.create_all(bind=engine)

app = FastAPI()
app.include_router(router)

@app.get("/")
def root():
    return {
        "status": "healthy"
    }

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)