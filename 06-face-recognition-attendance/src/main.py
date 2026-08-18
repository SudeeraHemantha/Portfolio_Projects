from typing import List, Optional
from datetime import datetime
from fastapi import FastAPI, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.database import engine, Base, get_db
from src.models import Employee, AttendanceLog
from src.encode_faces import build_face_encodings, generate_mock_face_encoding
from src.recognize_attendance import process_face_vector_matching

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Face Recognition Smart Attendance System API",
    version="1.0.0",
    description="Biometric Computer Vision Attendance Logging Platform with PostgreSQL Persistence"
)

# --- Pydantic Schemas ---
class EmployeeCreate(BaseModel):
    employee_code: str
    full_name: str
    department: str = "Engineering"

class EmployeeResponse(BaseModel):
    id: int
    employee_code: str
    full_name: str
    department: str
    status: str
    created_at: datetime
    class Config:
        from_attributes = True

class AttendanceLogResponse(BaseModel):
    id: int
    employee_id: int
    timestamp: datetime
    verification_status: str
    confidence_score: float
    camera_id: str
    class Config:
        from_attributes = True

class VerificationRequest(BaseModel):
    employee_code: str


# --- REST Routes ---

@app.get("/health", status_code=status.HTTP_200_OK)
def health():
    return {"status": "alive", "service": "Face Recognition Attendance API"}


@app.post("/api/v1/employees", response_model=EmployeeResponse, status_code=status.HTTP_201_CREATED)
def register_employee(emp_in: EmployeeCreate, db: Session = Depends(get_db)):
    existing = db.query(Employee).filter(Employee.employee_code == emp_in.employee_code).first()
    if existing:
        raise HTTPException(status_code=400, detail="Employee code already registered")
    
    emp = Employee(
        employee_code=emp_in.employee_code,
        full_name=emp_in.full_name,
        department=emp_in.department
    )
    db.add(emp)
    db.commit()
    db.refresh(emp)
    return emp


@app.get("/api/v1/employees", response_model=List[EmployeeResponse])
def list_employees(db: Session = Depends(get_db)):
    return db.query(Employee).all()


@app.get("/api/v1/attendance", response_model=List[AttendanceLogResponse])
def get_attendance_logs(limit: int = 50, db: Session = Depends(get_db)):
    return db.query(AttendanceLog).order_by(AttendanceLog.timestamp.desc()).limit(limit).all()


@app.post("/api/v1/verify", status_code=status.HTTP_200_OK)
def verify_attendance(req: VerificationRequest):
    """Simulates biometric facial vector recognition for an employee code."""
    candidate_vector = generate_mock_face_encoding(req.employee_code)
    result = process_face_vector_matching(candidate_vector)
    return result


@app.post("/api/v1/encode", status_code=status.HTTP_200_OK)
def trigger_face_encoding_job():
    """Triggers dataset re-encoding pipeline."""
    result = build_face_encodings()
    return {"status": "success", "total_encoded": len(result["encodings"])}
