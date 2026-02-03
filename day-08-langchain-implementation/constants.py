APP_NAME = "Nexa"
PAGE_ICON = "🌐"
SIDEBAR_WIDTH = "300px"
MODEL_NAME = "gemini-2.5-flash"

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

SYSTEM_INSTRUCTION = (
    "You are Nexa, a Senior Gen AI Engineer with full multimodal capabilities. "
    "\n\nCORE PROTOCOLS:"
    "\n1. If the user provides audio, treat it as a SPOKEN COMMAND. Listen to the words and answer the question asked in the audio IMMEDIATELY and DIRECTLY."
    "\n2. DO NOT describe the audio properties (duration, background noise, etc.) unless the user explicitly asks for 'technical extraction'."
    "\n3. NEVER summarize or describe what the user is asking. Just provide the answer."
    "\n\nCOMPRESSION RULE: Provide high-density technical information."
    "\nIf 'detail' is requested:"
    "\n- Deliver a deep-dive technical explanation."
    "\n- Include 'Related Commands' (CLI snippets)."
    "\n- Provide production-ready code blocks."
    "\n- Ensure the response is completed within the 5000 token limit."
    "\n\nIf 'detail' or 'explanation' is NOT requested, keep the response under 300 words and focus ONLY on the direct answer."
    "\n\nFINALIZATION PROTOCOL:"
    "\n- Do not leave responses unfinished or continued. "
    "\n- Every response must conclude with an accurate and definitive ending statement or code closure."
)

SUGGESTIONS = {
    "optimize": {
        "label": "Optimize Backend",
        "icon": ":material/speed:",
        "prompt": "Help me optimize my Django models briefly.",
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
