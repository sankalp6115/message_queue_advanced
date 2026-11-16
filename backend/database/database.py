from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from pathlib import Path

import os
from dotenv import load_dotenv
load_dotenv()

BASE_DIR = Path(__file__).resolve().parents[2]
DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread":False})

SessionLocal = sessionmaker(
    bind = engine,
    autoflush=False,
    autocommit=False
)
