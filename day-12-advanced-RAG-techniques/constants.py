EMBEDDING_MODEL_NAME = "models/gemini-embedding-001"
GENERATIVE_MODEL_NAME = "models/gemini-2.5-flash"
TEMPERATURE = 0.0

RETRIEVAL_TOP_K_RESULTS = 2
DEFAULT_KNOWLEDGE_SOURCE = "my_story.txt"

CHILD_CHUNK_SIZE = 300
CHILD_CHUNK_OVERLAP = 30
PARENT_CHUNK_SIZE = 1200
PARENT_CHUNK_OVERLAP = 120

CHATBOT_PAGE_TITLE = "Advanced-RAG-Techniques"
TARGET_DATASET = "Lahore_Haveli_Golden_Set"
EVALUATION_THRESHOLD = 0.7
EVALUATION_DECAY_RATE = 0.01

SYSTEM_INSTRUCTIONS = """
You are the Lahore Architect.
Use the following pieces of retrieved context to answer the question accurately.
If the question asks for a specific detail, provide that detail exactly as it appears in the text.
If you don't know the answer based on the context, just say I don't know as it's not provided in the context.

Context: {context}
"""

USER_QUESTION_TEMPLATE = "{question}"
