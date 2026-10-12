from langchain_core.prompts import ChatPromptTemplate
from src.state import ResearchFinding
from src.llm_factory import get_llm_with_fallbacks


ANALYST_PROMPT = """You are a senior analyst. Given research findings on a topic, synthesize them into a coherent analysis. Identify:
1. Key themes that emerge across findings
2. Areas of consensus and disagreement
3. Gaps or open questions

Topic: {topic}

Findings:
{findings}

Write a structured analysis (3-5 paragraphs) in plain prose. Do not use markdown headers."""


def analyze_findings(topic: str, findings: list[ResearchFinding]) -> str:
    findings_text = "\n\n".join([
        f"Sub-question: {f.sub_question}\nSummary: {f.summary}"
        for f in findings
    ])

    llm = get_llm_with_fallbacks(temperature=0.3)
    prompt = ChatPromptTemplate.from_template(ANALYST_PROMPT)
    chain = prompt | llm

    response = chain.invoke({"topic": topic, "findings": findings_text})
    return response.content.strip()