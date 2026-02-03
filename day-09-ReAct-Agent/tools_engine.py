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
    timezone = pytz.timezone("Asia/Karachi")
    return f"{datetime.datetime.now(timezone).strftime('%H:%M:%S')}|PKT"


@tool
def get_current_date() -> str:
    timezone = pytz.timezone("Asia/Karachi")
    datetime_now = datetime.datetime.now(timezone)
    return f"{datetime_now.strftime('%Y-%m-%d')}|{datetime_now.strftime('%A')}"
