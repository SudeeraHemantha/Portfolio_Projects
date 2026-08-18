import os
import pickle
import logging
from datetime import datetime, timedelta
import numpy as np

from src.database import SessionLocal
from src.models import Employee, AttendanceLog

logger = logging.getLogger("recognize-attendance")
logging.basicConfig(level=logging.INFO)

ENCODINGS_FILE = os.path.join("dataset", "encodings.pickle")
MATCH_TOLERANCE = 0.6 # Standard Euclidean distance tolerance for 128D encodings

def load_known_encodings() -> dict:
    """Loads serialized 128D facial encodings pickle file."""
    if not os.path.exists(ENCODINGS_FILE):
        from src.encode_faces import build_face_encodings
        return build_face_encodings()

    with open(ENCODINGS_FILE, "rb") as f:
        return pickle.load(f)


def calculate_euclidean_distance(vector_a: np.ndarray, vector_b: np.ndarray) -> float:
    """Computes Euclidean distance between two 128-dimensional facial encodings."""
    return float(np.linalg.norm(vector_a - vector_b))


def log_employee_attendance(employee_code: str, confidence_score: float = 0.95) -> dict:
    """
    Logs attendance timestamp into PostgreSQL database, enforcing an anti-duplication
    cooldown window of 1 hour per employee.
    """
    db = SessionLocal()
    try:
        employee = db.query(Employee).filter(Employee.employee_code == employee_code).first()
        if not employee:
            # Create employee record if not existing yet
            employee = Employee(
                employee_code=employee_code,
                full_name=employee_code.replace("_", " "),
                department="Engineering"
            )
            db.add(employee)
            db.commit()
            db.refresh(employee)

        # Check last log timestamp within 1 hour window
        one_hour_ago = datetime.utcnow() - timedelta(hours=1)
        recent_log = db.query(AttendanceLog).filter(
            AttendanceLog.employee_id == employee.id,
            AttendanceLog.timestamp >= one_hour_ago
        ).first()

        if recent_log:
            logger.info(f"Attendance log skipped for {employee.full_name} (Cooldown active).")
            return {
                "status": "cooldown_skipped",
                "employee_code": employee.employee_code,
                "last_log": recent_log.timestamp.isoformat()
            }

        new_log = AttendanceLog(
            employee_id=employee.id,
            timestamp=datetime.utcnow(),
            verification_status="Verified",
            confidence_score=confidence_score
        )
        db.add(new_log)
        db.commit()
        db.refresh(new_log)

        logger.info(f"VERIFIED ATTENDANCE LOGGED: {employee.full_name} at {new_log.timestamp}")
        return {
            "status": "success",
            "log_id": new_log.id,
            "employee": employee.full_name,
            "timestamp": new_log.timestamp.isoformat()
        }
    except Exception as e:
        db.rollback()
        logger.error(f"Error logging attendance for {employee_code}: {e}")
        raise e
    finally:
        db.close()


def process_face_vector_matching(candidate_vector: np.ndarray) -> dict:
    """
    Evaluates candidate 128D facial vector against known encodings using Euclidean distance.
    """
    data = load_known_encodings()
    known_encodings = data["encodings"]
    known_names = data["names"]

    if not known_encodings:
        return {"status": "no_known_encodings"}

    distances = [calculate_euclidean_distance(candidate_vector, k_vec) for k_vec in known_encodings]
    min_dist_idx = int(np.argmin(distances))
    min_distance = distances[min_dist_idx]

    if min_distance <= MATCH_TOLERANCE:
        matched_name = known_names[min_dist_idx]
        confidence = max(0.5, round(1.0 - min_distance, 4))
        log_result = log_employee_attendance(matched_name, confidence_score=confidence)
        return {
            "matched": True,
            "employee_code": matched_name,
            "distance": round(min_distance, 4),
            "confidence": confidence,
            "log_details": log_result
        }
    
    return {
        "matched": False,
        "reason": "distance_exceeds_threshold",
        "closest_distance": round(min_distance, 4)
    }
