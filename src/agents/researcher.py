from langchain_core.prompts import ChatPromptTemplate
from src.state import SubQuestion, ResearchFinding
from src.tools.search import web_search
from src.llm_factory import get_llm_with_fallbacks

RESEARCHER_PROMPT = """You are a research analyst. Given a sub-question and web search results, write a concise 2-3 sentence summary grounded ONLY in these sources. Cite sources inline like [1], [2].

Rules:
- If the sources are irrelevant (e.g., dictionary definitions, product pages, homepages), state clearly that no substantive sources were found.
- Do NOT invent facts not present in the sources.
- Do NOT pad with general knowledge.

Sub-question: {question}

Search results:
{results}

Summary:"""

def research_sub_question(sub_question: SubQuestion) -> ResearchFinding:
    results = web_search(sub_question.question)

    if not results:
        return ResearchFinding(
            sub_question=sub_question.question,
            results=[],
            summary="No results found for this sub-question."
        )

    results_text = "\n".join([
        f"[{i+1}] {r.title}\n{r.snippet}\nURL: {r.url}"
        for i, r in enumerate(results)
    ])

    llm = get_llm_with_fallbacks(temperature=0.1)
    prompt = ChatPromptTemplate.from_template(RESEARCHER_PROMPT)
    chain = prompt | llm

    response = chain.invoke({
        "question": sub_question.question,
        "results": results_text
    })

    return ResearchFinding(
        sub_question=sub_question.question,
        results=results,
        summary=response.content.strip()
    )