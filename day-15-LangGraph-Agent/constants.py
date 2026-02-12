import datetime

APP_NAME = "Nexa"
PAGE_ICON = "🌐"
SIDEBAR_WIDTH = "300px"
MODEL_NAME = "gemini-2.5-flash"
SECONDARY_MODEL_NAME = "gemini-2.0-flash"

USER_ROLE = "user"
ASSISTANT_ROLE = "model"

LOGO_SIZE_SIDEBAR = 28
LOGO_SIZE_HEADER = 22
SIDEBAR_SPACER_HEIGHT = 280
SIDEBAR_COLUMN_RATIO = [0.8, 0.2]
HEADER_COLUMN_RATIO = [0.25, 0.5, 0.25]

SEARCH_PROMPT = "Search the Core..."
DEFAULT_CHAT_TITLE = "New Chat"
CHAT_INPUT_TEXT = f"Connect with {APP_NAME}..."
USER_INPUT_TEXT = f"Connect with Nexa..."

MAX_RESPONSE_TOKENS = 5000
TEMPERATURE = 0.2

BOT_AVATAR = "https://cdn-icons-png.flaticon.com/512/4712/4712035.png"
LANGSMITH_DATASET_NAME = "Nexa-Final-Report-Suite"


def get_dynamic_system_instructions():
    current_date = datetime.datetime.now().strftime("%A, %B %d, %Y")

    return (
        f"You are Nexa, a Senior Gen AI Engineer. "
        f"\n\n--- TEMPORAL STATUS ---"
        f"\n- TODAY'S DATE: {current_date}."
        f"\n- Your internal knowledge ends in 2024. For anything after that, you MUST use Search."
        f"\n\n--- PROTOCOL 1: TIME & DATE TOOLS (STRICT) ---"
        f"\n- Use 'get_current_time' or 'get_current_date' ONLY for the current moment."
        f"\n- If a user asks for a specific date/time from the past (e.g., 'yesterday at noon', 'last Tuesday'), "
        f"you MUST respond: 'I can only provide the current time and date. I do not have access to historical data.'"
        f"\n\n--- PROTOCOL 2: SEARCH TOOL (TAVILY) ---"
        f"\n- Use 'tavily_search_results_json' for factual queries, news, or events from 2025 and 2026."
        f"\n- IMPORTANT: If a user asks 'What happened in the news yesterday?', this is a SEARCH query, not a TIME query. "
        f"Use Tavily to find the answer. Do not use the 'historical data' refusal for general news search."
        f"\n\n--- PROTOCOL 3: REASONING ---"
        f"\n- Distinguish between a 'Clock/Calendar' request (refuse past) and a 'News/Event' request (use Search)."
    )


SUGGESTIONS = {
    "optimize": {
        "label": "Optimize Backend",
        "icon": ":material/speed:",
        "prompt": "Help me optimize my Django models.",
    },
    "debug": {
        "label": "Exceptions Handling",
        "icon": ":material/troubleshoot:",
        "prompt": "Briefly explain how to handle exceptions in Python.",
    },
    "deploy": {
        "label": "Deploy Workflow",
        "icon": ":material/rocket_launch:",
        "prompt": "Plan a professional CI/CD pipeline briefly.",
    },
}

EVALUATION_THRESHOLD = 0.8

PROTOCOL_ADHERENCE_CRITERIA = (
    "Ensure bot refuses historical queries and provides precise current data."
)

PROTOCOL_SCORE_KEY = "protocol_score"
BOT_FAILURE_COMMENT = "Bot failed to respond."
FAILURE_SCORE_FALLBACK = 0.0
EVALUATION_TEMPERATURE = 0.2
EVALUATION_TEMPERATURES_LIST = [0.2, 0.8]
