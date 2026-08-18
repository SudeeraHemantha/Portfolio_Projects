from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from src.database import Base

class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    employee_code = Column(String(50), unique=True, nullable=False, index=True)
    full_name = Column(String(255), nullable=False)
    department = Column(String(100), default="Engineering", index=True)
    status = Column(String(50), default="Active")
    created_at = Column(DateTime, default=datetime.utcnow)

    attendance_logs = relationship("AttendanceLog", back_populates="employee", cascade="all, delete-orphan")


class AttendanceLog(Base):
    __tablename__ = "attendance_logs"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id", ondelete="CASCADE"), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    verification_status = Column(String(50), default="Verified") # Verified, Flagged
    confidence_score = Column(Float, default=0.95)
    camera_id = Column(String(50), default="cam_entrance_01")

    employee = relationship("Employee", back_populates="attendance_logs")
