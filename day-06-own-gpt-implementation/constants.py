APP_NAME = "Nexa"
PAGE_ICON = "🌐"
SIDEBAR_WIDTH = "300px"
MODEL_NAME = "gemini-2.0-flash"

USER_ROLE = "user"
ASSISTANT_ROLE = "assistant"

LOGO_SIZE_SIDEBAR = 28
LOGO_SIZE_HEADER = 22
SIDEBAR_SPACER_HEIGHT = 280
SIDEBAR_COLUMN_RATIO = [0.8, 0.2]
HEADER_COLUMN_RATIO = [0.25, 0.5, 0.25]

SEARCH_PROMPT = "Search the Core..."
DEFAULT_CHAT_TITLE = "New Chat"
CHAT_INPUT_TEXT = f"Connect with {APP_NAME}..."

SUGGESTIONS = {
    "optimize": {
        "label": "Optimize Backend",
        "icon": ":material/speed:",
        "prompt": "Help me optimize my Django models",
    },
    "debug": {
        "label": "Bug Analysis",
        "icon": ":material/troubleshoot:",
        "prompt": "Analyze this Python error traceback",
    },
    "deploy": {
        "label": "Deploy Workflow",
        "icon": ":material/rocket_launch:",
        "prompt": "Plan a professional CI/CD pipeline",
    },
}
