import logging
from datetime import datetime, timedelta
from src.celery_app import celery_app
from src.database import SessionLocal
from src.models import Habit, HabitLog

logger = logging.getLogger("sentinel-tasks")

@celery_app.task(name="tasks.recalculate_habit_streak")
def recalculate_habit_streak(habit_id: int):
    """Asynchronous background task to evaluate streak continuity for a given habit."""
    db = SessionLocal()
    try:
        habit = db.query(Habit).filter(Habit.id == habit_id).first()
        if not habit:
            logger.warning(f"Habit ID {habit_id} not found for streak recalculation.")
            return {"status": "skipped", "reason": "not_found"}

        logs = db.query(HabitLog).filter(
            HabitLog.habit_id == habit_id,
            HabitLog.status == "completed"
        ).order_by(HabitLog.completed_at.desc()).all()

        if not logs:
            habit.current_streak = 0
            db.commit()
            return {"habit_id": habit_id, "current_streak": 0}

        # Evaluate daily streak continuity
        streak = 0
        current_day = datetime.utcnow().date()
        logged_dates = {log.completed_at.date() for log in logs}

        # Check today or yesterday as streak anchor
        check_date = current_day
        if check_date not in logged_dates:
            check_date = current_day - timedelta(days=1)

        while check_date in logged_dates:
            streak += 1
            check_date -= timedelta(days=1)

        habit.current_streak = streak
        if streak > habit.longest_streak:
            habit.longest_streak = streak
        habit.total_completions = len(logs)

        db.commit()
        logger.info(f"Habit {habit_id} streak updated: {streak} days.")
        return {
            "habit_id": habit_id,
            "current_streak": habit.current_streak,
            "longest_streak": habit.longest_streak
        }
    except Exception as e:
        db.rollback()
        logger.error(f"Error recalculating streak for habit {habit_id}: {e}")
        raise e
    finally:
        db.close()


@celery_app.task(name="tasks.evaluate_all_active_streaks")
def evaluate_all_active_streaks():
    """Periodic task scanning all active habits across users."""
    db = SessionLocal()
    try:
        active_habits = db.query(Habit).filter(Habit.is_active == True).all()
        processed_count = 0
        for habit in active_habits:
            recalculate_habit_streak.delay(habit.id)
            processed_count += 1
        return {"status": "success", "habits_enqueued": processed_count}
    finally:
        db.close()
