from langchain_community.tools.tavily_search import TavilySearchResults


def get_search_tool():
    """Returns the search tool optimized for the latest news and technical data."""
    return TavilySearchResults(
        max_results=5,
        search_depth="advanced",
        topic="news",
        time_range="day"
    )
