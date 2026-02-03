import datetime
import pytz
import streamlit as st

from langchain_core.tools import tool
from pydantic import BaseModel, Field


class TimeResponse(BaseModel):
    """Structured format for dynamic world-wide time queries."""
    time: str = Field(description="The current time in HH:MM:SS format")
    timezone: str = Field(description="The local timezone code, e.g., PKT, EST, PST")


class DateResponse(BaseModel):
    date: str = Field(description="The current date in YYYY-MM-DD format")
    day: str = Field(description="The full name of the day, e.g., Tuesday")


@tool
def get_current_time() -> str:
    """
    Returns the current local time based on the user's browser location.
    Works automatically in Pakistan, USA, or anywhere else.
    """
    try:
        user_tz = st.context.timezone or "Asia/Karachi"
    except Exception:
        user_tz = "Asia/Karachi"

    target_timezone = pytz.timezone(user_tz)
    local_timezone_now = datetime.datetime.now(target_timezone)
    timezone_name = local_timezone_now.strftime("%Z")

    return f"{local_timezone_now.strftime('%H:%M:%S')}|{timezone_name}"


@tool
def get_current_date() -> str:
    """
    Returns today's date and day name based on the system's local location.
    Works automatically in Pakistan, USA, or on any global server.
    """
    local_timezone_now = datetime.datetime.now().astimezone()

    return f"{local_timezone_now.strftime("%Y-%m-%d")}|{local_timezone_now.strftime("%A")}"
