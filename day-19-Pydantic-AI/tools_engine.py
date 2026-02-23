import math

from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.tools import tool


def get_search_tool():
    """Returns the search tool optimized for the latest news and technical data."""
    return TavilySearchResults(
        max_results=5,
        search_depth="advanced",
        topic="news",
        include_raw_content=True,
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
