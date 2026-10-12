from langchain_core.prompts import ChatPromptTemplate
from src.config import MAX_SUB_QUESTIONS
from src.state import SubQuestion
from src.llm_factory import get_llm_with_fallbacks
import json


PLANNER_PROMPT = """You are a research planner. Given a topic, break it down into {max_q} focused sub-questions that together would produce a comprehensive understanding of the topic.

Topic: {topic}

Return ONLY a valid JSON array of objects with keys "question" and "rationale". No markdown, no explanation.

Example format:
[
  {{"question": "What is X?", "rationale": "Understanding X is foundational"}},
  {{"question": "How does X affect Y?", "rationale": "Explains the impact"}}
]
"""


def plan_research(topic: str) -> list[SubQuestion]:
    llm = get_llm_with_fallbacks(temperature=0.2)
    prompt = ChatPromptTemplate.from_template(PLANNER_PROMPT)
    chain = prompt | llm

    response = chain.invoke({"topic": topic, "max_q": MAX_SUB_QUESTIONS})
    content = response.content.strip()

    if content.startswith("```"):
        content = content.split("```")[1]
        if content.startswith("json"):
            content = content[4:]
        content = content.strip()

    try:
        data = json.loads(content)
        return [SubQuestion(**item) for item in data]
    except Exception as e:
        print(f"Planner parsing error: {e}\nRaw: {content}")
        return [SubQuestion(question=topic, rationale="Fallback to main topic")]