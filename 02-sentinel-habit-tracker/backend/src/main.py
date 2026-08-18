"""Sentinel Habit Tracker API Entrypoint"""
from fastapi import FastAPI

app = FastAPI(title="Sentinel Habit Tracker API")

@app.get("/")
def root():
    return {"message": "Sentinel Habit Tracker API Operational"}
