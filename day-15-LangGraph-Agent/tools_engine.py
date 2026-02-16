import datetime
import math

import pytz
from langchain_core.tools import tool
from pydantic import BaseModel, Field
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_classic.chains import LLMMathChain


class TimeResponse(BaseModel):
    time: str = Field(description="The current time in HH:MM:SS format")
    timezone: str = Field(description="The local timezone code, e.g., PKT, EST, PST")


class DateResponse(BaseModel):
    date: str = Field(description="The current date in YYYY-MM-DD format")
    day: str = Field(description="The full name of the day, e.g., Tuesday")


@tool
def get_current_time(region: str = "Asia/Karachi") -> str:
    """
    Returns the current time for a specific region/timezone.
    Args:
        region (str): The timezone string (e.g., 'UTC', 'America/New_York', 'Europe/London').
    """
    formatted_time_response = ""

    try:
        target_timezone = pytz.timezone(region.strip())
        timezone_now = datetime.datetime.now(target_timezone)

        formatted_time_response = (
            f"{timezone_now.strftime('%H:%M:%S')}|{timezone_now.strftime("%Z")}"
        )
    except Exception:
        formatted_time_response = "Error: Invalid Timezone|UTC"

    return formatted_time_response


@tool
def get_current_date() -> str:
    """
    Returns today's date and day name based on the system's local location.
    Works automatically in Pakistan, USA, or on any global server.
    """
    local_timezone_now = datetime.datetime.now().astimezone()

    return f"{local_timezone_now.strftime("%Y-%m-%d")}|{local_timezone_now.strftime("%A")}"


def get_search_tool():
    """
    Returns the search tool optimized for LATEST news, sports scores and events.
    It automatically looks for TAVILY_API_KEY in your environment variables.
    """
    return TavilySearchResults(
        max_results=3,
        search_depth="advanced",
        topic="news",
        time_range="day"
    )


@tool
def Calculator(expression: str) -> str:
    """
    Evaluate a mathematical expression.
    Input must be a valid Python math expression.
    """
    try:
        execution_output = str(eval(expression, {"__builtins__": None}, vars(math)))
    except Exception:
        execution_output = "Invalid mathematical expression."

    return execution_output
