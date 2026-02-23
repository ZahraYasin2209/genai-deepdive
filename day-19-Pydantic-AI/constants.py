import datetime

APP_NAME = "Vanguard Research"
PAGE_ICON = "🛡️"
MODEL_NAME = "gemini-2.5-flash"
USER_ROLE = "user"
ASSISTANT_ROLE = "model"
BOT_AVATAR = "https://cdn-icons-png.flaticon.com/512/4712/4712035.png"

LOGO_SIZE_SIDEBAR = 28
SIDEBAR_COLUMN_RATIO = [0.8, 0.2]
HEADER_COLUMN_RATIO = [0.25, 0.5, 0.25]
USER_INPUT_TEXT = "Request Research Intelligence..."
SEARCH_PROMPT = "Search the Core..."
MAX_RESPONSE_TOKENS = 4000
TEMPERATURE = 0.1


def get_dynamic_system_instructions():
    current_date = datetime.datetime.now().strftime("%A, %B %d, %Y")
    return (
        f"You are {APP_NAME}, a Senior Multi-Architecture Research Assistant. Today is {current_date}. "
        "\n\n--- OPERATIONAL DIRECTIVES ---"
        "\n1. TEMPORAL AWARENESS: If a user asks about an event on a date that has already passed (e.g., yesterday), "
        "you MUST search for the results and report them as historical facts. DO NOT claim the match is in the future."
        "Must give response to every event that happened even on today's date."
        "\n2. GREETING: Identify as a Multi-Architecture Research Specialist."
        "\n3. RESEARCH: For 2026 events, use Search immediately. Do not speculate."
        "\n4. FORMATTING: Deliver reports in technical Markdown with bold headers and tables."
    )


SUGGESTIONS = {
    "optimize": {
        "label": "Technical Report",
        "icon": ":material/analytics:",
        "prompt": "Detailed report on AI advancements in software development.",
    },
    "debug": {
        "label": "Medical Insight",
        "icon": ":material/medical_services:",
        "prompt": "Briefly explain 2026 healthcare innovations.",
    },
    "news": {
        "label": "Latest Events",
        "icon": ":material/news:",
        "prompt": "Latest news of 2026.",
    },
}

BOT_FAILURE_COMMENT = "Agent failed to provide a valid synthesized report."
EVALUATION_TEMPERATURE = 0.0
EVALUATION_THRESHOLD = 0.7
FAILURE_SCORE_FALLBACK = 0.0
LANGSMITH_DATASET_NAME = "Vanguard_Research_Benchmark_Chatbot"
PROTOCOL_SCORE_KEY = "protocol_adherence"


HARVESTER_INSTRUCTIONS = (
    "You are the Intelligence Harvester. "
    "Use Search tool for:"
    " -Any real-world event"
    " -Any data requiring verification"
    " -Any claim needing factual backing "
    "DO NOT answer using internal knowledge for current events. Summarize search results raw."
)

SYNTHESIZER_INSTRUCTIONS = (
    "WRITER ROLE: You are the Lead Synthesis Engineer. "
    "1. REVIEW harvested data. 2. FORMAT: Use concise Markdown tables and bold headers. "
    "3. TONAL GUARDRAILS: Do not use conversational filler like 'I found this' or 'I hope this helps'."
)

PROTOCOL_ADHERENCE_CRITERIA = """
1. Accuracy (2026): Did the output contain verified 2026 dates, venues, or technical details?
2. Structural Integrity: Is the report technical (using Markdown headers and tables) rather than conversational?
3. Collaborative Flow: Does the output suggest data was harvested via search before being synthesized?
"""
