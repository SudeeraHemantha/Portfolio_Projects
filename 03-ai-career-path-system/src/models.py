from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, JSON
from pgvector.sqlalchemy import Vector
from src.database import Base

EMBEDDING_DIM = 384

class JobBenchmark(Base):
    __tablename__ = "job_benchmarks"

    id = Column(Integer, primary_key=True, index=True)
    role_title = Column(String(255), nullable=False, index=True)
    category = Column(String(100), default="Engineering", index=True)
    experience_level = Column(String(50), default="Junior") # Junior, Mid, Senior
    required_skills = Column(JSON, nullable=False, default=[]) # List of skill strings
    description = Column(Text, nullable=True)

    # 384-dimensional dense vector embedding representing skill taxonomy
    embedding = Column(Vector(EMBEDDING_DIM), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)


class StudentProfile(Base):
    __tablename__ = "student_profiles"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    target_role = Column(String(255), nullable=False)
    current_skills = Column(JSON, nullable=False, default=[]) # Candidate skill list

    # Candidate 384-dimensional dense vector embedding derived from skills + experience
    embedding = Column(Vector(EMBEDDING_DIM), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
