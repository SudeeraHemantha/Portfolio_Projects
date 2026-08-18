from typing import List, Optional, Dict, Any
from datetime import datetime
from fastapi import FastAPI, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session

from src.database import engine, Base, get_db
from src.models import User, Habit, HabitLog
from src.tasks import recalculate_habit_streak

# Create database tables automatically on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Sentinel Habit Tracker & Analytics API",
    version="1.0.0",
    description="Enterprise Habit Tracking Engine with Hybrid JSONB Modeling and Celery Async Pipelines"
)

# --- Pydantic Schemas ---
class UserCreate(BaseModel):
    email: EmailStr
    full_name: str

class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str
    created_at: datetime
    class Config:
        from_attributes = True

class HabitCreate(BaseModel):
    user_id: int
    title: str
    description: Optional[str] = None
    category: str = "General"
    frequency: str = "daily"
    metadata_json: Optional[Dict[str, Any]] = Field(default_factory=dict)

class HabitResponse(BaseModel):
    id: int
    user_id: int
    title: str
    description: Optional[str]
    category: str
    frequency: str
    current_streak: int
    longest_streak: int
    total_completions: int
    is_active: bool
    metadata_json: Dict[str, Any]
    created_at: datetime
    class Config:
        from_attributes = True

class LogCreate(BaseModel):
    status: str = "completed"
    notes: Optional[str] = None

class LogResponse(BaseModel):
    id: int
    habit_id: int
    completed_at: datetime
    status: str
    notes: Optional[str]
    class Config:
        from_attributes = True


# --- API Routes ---

@app.get("/health", status_code=status.HTTP_200_OK)
def health():
    return {"status": "alive", "service": "Sentinel Habit Tracker API"}


@app.post("/api/v1/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user_in: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == user_in.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    user = User(email=user_in.email, full_name=user_in.full_name)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@app.get("/api/v1/users", response_model=List[UserResponse])
def list_users(db: Session = Depends(get_db)):
    return db.query(User).all()


@app.post("/api/v1/habits", response_model=HabitResponse, status_code=status.HTTP_201_CREATED)
def create_habit(habit_in: HabitCreate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == habit_in.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    habit = Habit(
        user_id=habit_in.user_id,
        title=habit_in.title,
        description=habit_in.description,
        category=habit_in.category,
        frequency=habit_in.frequency,
        metadata_json=habit_in.metadata_json or {}
    )
    db.add(habit)
    db.commit()
    db.refresh(habit)
    return habit


@app.get("/api/v1/habits", response_model=List[HabitResponse])
def list_habits(user_id: Optional[int] = None, db: Session = Depends(get_db)):
    query = db.query(Habit)
    if user_id:
        query = query.filter(Habit.user_id == user_id)
    return query.all()


@app.post("/api/v1/habits/{habit_id}/logs", response_model=LogResponse, status_code=status.HTTP_201_CREATED)
def log_habit_completion(habit_id: int, log_in: LogCreate, db: Session = Depends(get_db)):
    habit = db.query(Habit).filter(Habit.id == habit_id).first()
    if not habit:
        raise HTTPException(status_code=404, detail="Habit not found")

    log_entry = HabitLog(
        habit_id=habit_id,
        status=log_in.status,
        notes=log_in.notes
    )
    db.add(log_entry)
    habit.total_completions += 1
    db.commit()
    db.refresh(log_entry)

    # Trigger async Celery task for streak recalculation
    recalculate_habit_streak.delay(habit_id)

    return log_entry


@app.get("/api/v1/analytics/streaks", status_code=status.HTTP_200_OK)
def get_streak_analytics(user_id: int, db: Session = Depends(get_db)):
    habits = db.query(Habit).filter(Habit.user_id == user_id).all()
    if not habits:
        return {"user_id": user_id, "total_habits": 0, "active_streaks": []}

    analytics = []
    for h in habits:
        analytics.append({
            "habit_id": h.id,
            "title": h.title,
            "category": h.category,
            "current_streak": h.current_streak,
            "longest_streak": h.longest_streak,
            "total_completions": h.total_completions,
            "custom_metadata": h.metadata_json
        })

    return {
        "user_id": user_id,
        "total_habits": len(habits),
        "analytics": analytics
    }
