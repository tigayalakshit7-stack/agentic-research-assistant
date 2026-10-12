from langchain_groq import ChatGroq
from src.config import GROQ_API_KEY


def get_llm_with_fallbacks(temperature: float = 0.3):
    """
    Returns an LLM with a 3-model fallback chain.
    Order: gpt-oss-120b -> qwen3.8-27b -> llama-3.3-70b
    If the primary hits a rate limit or fails, the next model takes over.
    """
    primary = ChatGroq(
        api_key=GROQ_API_KEY,
        model="openai/gpt-oss-120b",
        temperature=temperature,
    )
    secondary = ChatGroq(
        api_key=GROQ_API_KEY,
        model="qwen/qwen3.8-27b",
        temperature=temperature,
    )
    tertiary = ChatGroq(
        api_key=GROQ_API_KEY,
        model="llama-3.3-70b-versatile",
        temperature=temperature,
    )
    return primary.with_fallbacks([secondary, tertiary])