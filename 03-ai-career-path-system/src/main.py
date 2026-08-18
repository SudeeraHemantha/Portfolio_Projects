from typing import List, Optional, Dict, Any
from datetime import datetime
from fastapi import FastAPI, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session
from sqlalchemy import text

from src.database import engine, Base, get_db, init_vector_extension
from src.models import JobBenchmark, StudentProfile
from src.matcher import generate_mock_embedding, calculate_cosine_similarity, analyze_skill_gaps

# Initialize pgvector extension and create tables
try:
    init_vector_extension()
    Base.metadata.create_all(bind=engine)
except Exception as e:
    print(f"Warning: Database initialization exception: {e}")

app = FastAPI(
    title="AI Career Path & Skill Navigation API",
    version="1.0.0",
    description="Vector Search Powered Career Matching Engine with pgvector and Skill Gap Analytics"
)

# --- Pydantic Schemas ---
class JobBenchmarkCreate(BaseModel):
    role_title: str
    category: str = "Engineering"
    experience_level: str = "Junior"
    required_skills: List[str]
    description: Optional[str] = None

class JobBenchmarkResponse(BaseModel):
    id: int
    role_title: str
    category: str
    experience_level: str
    required_skills: List[str]
    description: Optional[str]
    created_at: datetime
    class Config:
        from_attributes = True

class StudentProfileCreate(BaseModel):
    full_name: str
    email: EmailStr
    target_role: str
    current_skills: List[str]

class StudentProfileResponse(BaseModel):
    id: int
    full_name: str
    email: str
    target_role: str
    current_skills: List[str]
    created_at: datetime
    class Config:
        from_attributes = True

class MatchRequest(BaseModel):
    student_id: int
    top_k: int = Field(default=3, ge=1, le=10)

class MatchResult(BaseModel):
    job_id: int
    role_title: str
    category: str
    experience_level: str
    similarity_score: float
    skill_coverage_pct: float
    missing_skills: List[str]


# --- REST Routes ---

@app.get("/health", status_code=status.HTTP_200_OK)
def health(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1;"))
        return {
            "status": "alive",
            "service": "AI Career Path System API",
            "database": "connected",
            "vector_extension": "active"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database connection error: {e}")


@app.post("/api/v1/jobs", response_model=JobBenchmarkResponse, status_code=status.HTTP_201_CREATED)
def create_job_benchmark(job_in: JobBenchmarkCreate, db: Session = Depends(get_db)):
    skills_str = ", ".join(job_in.required_skills)
    text_content = f"{job_in.role_title} {job_in.category} {skills_str} {job_in.description or ''}"
    embedding_vec = generate_mock_embedding(text_content)

    job = JobBenchmark(
        role_title=job_in.role_title,
        category=job_in.category,
        experience_level=job_in.experience_level,
        required_skills=job_in.required_skills,
        description=job_in.description,
        embedding=embedding_vec
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


@app.get("/api/v1/jobs", response_model=List[JobBenchmarkResponse])
def list_job_benchmarks(db: Session = Depends(get_db)):
    return db.query(JobBenchmark).all()


@app.post("/api/v1/students", response_model=StudentProfileResponse, status_code=status.HTTP_201_CREATED)
def create_student_profile(student_in: StudentProfileCreate, db: Session = Depends(get_db)):
    existing = db.query(StudentProfile).filter(StudentProfile.email == student_in.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    skills_str = ", ".join(student_in.current_skills)
    text_content = f"{student_in.target_role} {skills_str}"
    embedding_vec = generate_mock_embedding(text_content)

    student = StudentProfile(
        full_name=student_in.full_name,
        email=student_in.email,
        target_role=student_in.target_role,
        current_skills=student_in.current_skills,
        embedding=embedding_vec
    )
    db.add(student)
    db.commit()
    db.refresh(student)
    return student


@app.post("/api/v1/match", response_model=List[MatchResult], status_code=status.HTTP_200_OK)
def match_student_to_jobs(req: MatchRequest, db: Session = Depends(get_db)):
    student = db.query(StudentProfile).filter(StudentProfile.id == req.student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found")

    jobs = db.query(JobBenchmark).all()
    if not jobs:
        return []

    results = []
    student_vec = list(student.embedding) if student.embedding is not None else generate_mock_embedding(", ".join(student.current_skills))

    for j in jobs:
        job_vec = list(j.embedding) if j.embedding is not None else generate_mock_embedding(", ".join(j.required_skills))
        sim = calculate_cosine_similarity(student_vec, job_vec)
        gap_analysis = analyze_skill_gaps(student.current_skills, j.required_skills)

        results.append(MatchResult(
            job_id=j.id,
            role_title=j.role_title,
            category=j.category,
            experience_level=j.experience_level,
            similarity_score=round(sim, 4),
            skill_coverage_pct=gap_analysis["skill_coverage_pct"],
            missing_skills=gap_analysis["missing_skills"]
        ))

    # Sort descending by vector similarity score
    results.sort(key=lambda x: x.similarity_score, reverse=True)
    return results[:req.top_k]


@app.get("/api/v1/roadmap/{student_id}", status_code=status.HTTP_200_OK)
def generate_career_roadmap(student_id: int, db: Session = Depends(get_db)):
    student = db.query(StudentProfile).filter(StudentProfile.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found")

    # Match best fitting benchmark
    jobs = db.query(JobBenchmark).filter(JobBenchmark.role_title.ilike(f"%{student.target_role}%")).all()
    if not jobs:
        jobs = db.query(JobBenchmark).all()

    if not jobs:
        return {"student_id": student_id, "message": "No job benchmarks available yet"}

    target_job = jobs[0]
    gap = analyze_skill_gaps(student.current_skills, target_job.required_skills)

    roadmap_steps = []
    for idx, skill in enumerate(gap["missing_skills"], 1):
        roadmap_steps.append({
            "phase": f"Phase {idx}: Skill Mastery",
            "skill": skill,
            "recommended_action": f"Complete hands-on project and coursework focusing on {skill}.",
            "estimated_weeks": 3
        })

    return {
        "student_id": student_id,
        "candidate_name": student.full_name,
        "target_role": target_job.role_title,
        "current_coverage_pct": gap["skill_coverage_pct"],
        "acquired_skills": gap["acquired_skills"],
        "missing_skills": gap["missing_skills"],
        "personalized_roadmap": roadmap_steps
    }
