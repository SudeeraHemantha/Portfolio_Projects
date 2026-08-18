import os
import sys
import webbrowser
import psutil
from datetime import datetime
import logging

logger = logging.getLogger("jarvis-commands")

def get_system_metrics() -> dict:
    """Queries real-time host hardware performance metrics."""
    cpu_usage = psutil.cpu_percent(interval=0.5)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')

    return {
        "cpu_usage_pct": cpu_usage,
        "ram_used_gb": round(memory.used / (1024**3), 2),
        "ram_total_gb": round(memory.total / (1024**3), 2),
        "ram_usage_pct": memory.percent,
        "disk_free_gb": round(disk.free / (1024**3), 2),
        "active_processes": len(psutil.pids())
    }


def execute_web_search(query: str) -> str:
    """Executes web search query."""
    clean_query = query.replace("search", "").replace("google", "").strip()
    url = f"https://www.google.com/search?q={clean_query}"
    try:
        webbrowser.open(url)
        return f"Opening browser search results for '{clean_query}'."
    except Exception as e:
        logger.error(f"Browser launch error: {e}")
        return f"Search prepared for '{clean_query}'."


def get_current_time_date() -> str:
    """Returns formatted current time and date."""
    now = datetime.now()
    return f"Current time is {now.strftime('%I:%M %p')} on {now.strftime('%B %d, %Y')}."


def route_voice_command(command_text: str) -> dict:
    """
    Evaluates transcript text and routes execution to corresponding automation handler.
    """
    cmd = command_text.lower().strip()
    logger.info(f"Processing command intent: '{cmd}'")

    if not cmd:
        return {"action": "empty", "spoken_response": "I didn't capture any command."}

    if "system" in cmd or "status" in cmd or "performance" in cmd or "cpu" in cmd:
        metrics = get_system_metrics()
        response_text = f"CPU utilization is at {metrics['cpu_usage_pct']} percent. RAM usage is at {metrics['ram_usage_pct']} percent, with {metrics['ram_used_gb']} gigabytes used."
        return {
            "action": "system_status",
            "spoken_response": response_text,
            "data": metrics
        }

    if "time" in cmd or "date" in cmd or "day" in cmd:
        time_text = get_current_time_date()
        return {
            "action": "time_date",
            "spoken_response": time_text
        }

    if "search" in cmd or "google" in cmd:
        search_res = execute_web_search(cmd)
        return {
            "action": "web_search",
            "spoken_response": search_res
        }

    if "hello" in cmd or "hi" in cmd or "jarvis" in cmd:
        return {
            "action": "greeting",
            "spoken_response": "Online and operational. How may I assist your systems today?"
        }

    return {
        "action": "unknown",
        "spoken_response": f"Command received: '{command_text}'. No custom automation rule matched."
    }
