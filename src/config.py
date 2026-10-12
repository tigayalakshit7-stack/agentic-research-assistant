import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MAX_SUB_QUESTIONS = 4
SEARCH_RESULTS_PER_QUERY = 4