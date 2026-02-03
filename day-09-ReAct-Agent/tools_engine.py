import datetime

import pytz
from langchain_core.tools import tool
from pydantic import BaseModel, Field


class TimeResponse(BaseModel):
    time: str = Field(description="The current time in HH:MM:SS format")
    timezone: str = Field(description="The timezone code, e.g., PKT")


class DateResponse(BaseModel):
    date: str = Field(description="The current date in YYYY-MM-DD format")
    day: str = Field(description="The full name of the day, e.g., Tuesday")


@tool
def get_current_time() -> str:
    """
    Returns the current local time for Pakistan (PKT).
    Use this whenever the user asks for the time.
    """
    timezone = pytz.timezone("Asia/Karachi")
    return f"{datetime.datetime.now(timezone).strftime('%H:%M:%S')}|PKT"


@tool
def get_current_date() -> str:
    """
    Returns today's date and day name for Pakistan(2026).
    Use this whenever the user asks for the date, day, or year.
    """
    timezone = pytz.timezone("Asia/Karachi")
    timezone_now = datetime.datetime.now(timezone)

    return f"{timezone_now.strftime('%Y-%m-%d')}|{timezone_now.strftime('%A')}"
