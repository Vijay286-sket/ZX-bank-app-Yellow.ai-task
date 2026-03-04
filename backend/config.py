import os
from dotenv import load_dotenv

load_dotenv()

# API Keys
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyCHV3H00vxRtQX0wHDTUuxe6TxaXMH8sQ0")

# Model Configuration
LLM_MODEL = "gemini-2.5-flash"

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DOCS_DIR = os.path.join(BASE_DIR, "docs")
DATA_DIR = os.path.join(BASE_DIR, "data")
FAISS_INDEX_PATH = os.path.join(DATA_DIR, "faiss.index")
CHUNKS_JSON_PATH = os.path.join(DATA_DIR, "chunks.json")
ESCALATIONS_JSON_PATH = os.path.join(DATA_DIR, "escalations.json")
ESCALATIONS_CSV_PATH = os.path.join(DATA_DIR, "escalations.csv")
SESSIONS_JSON_PATH = os.path.join(DATA_DIR, "sessions.json")

# Retrieval Configuration
RETRIEVAL_THRESHOLD = 0.25
TOP_K_RETRIEVAL = 5
TOP_K_FINAL = 3

# Session Configuration
SESSION_EXPIRY_MINUTES = 30
MAX_HISTORY_TURNS = 10
