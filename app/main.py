from fastapi import FastAPI 
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from app.api.router import router
from app.database.database import engine
from app.models.model import Base

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"])
app.include_router(router)

@app.get("/")
def root():
    return {
        "status": "healthy"
    }

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000)