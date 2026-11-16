from fastapi import FastAPI 
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from backend.api.router import router
from backend.database.database import engine
from backend.models.model import Base

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
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000)