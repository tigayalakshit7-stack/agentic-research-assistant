from langchain_core.prompts import ChatPromptTemplate
from src.state import ResearchFinding
from src.llm_factory import get_llm_with_fallbacks

WRITER_PROMPT = """You are a technical writer. Produce a professional research report in Markdown.

Topic: {topic}

Analysis:
{analysis}

Findings with numbered sources:
{findings}

CRITICAL RULES — follow exactly:
1. You may ONLY cite sources using the exact numbers [1] through [{max_ref}] that appear in the reference list below.
2. Do NOT invent citation numbers. Do NOT cite a number that is not in the list.
3. Do NOT include specific statistics (percentages, scores, sample sizes) unless they appear verbatim in the provided summaries.
4. If a claim cannot be supported by the provided sources, write "evidence is limited" instead of inventing details.
5. Do NOT write a References section. It will be appended automatically. End your report after the Conclusions section.

Report structure:
# [Title]
## Executive Summary
## Key Findings
## Detailed Analysis
## Conclusions

Stop after Conclusions. Do not add References, Footnotes, or a source list."""


def write_report(topic: str, analysis: str, findings: list[ResearchFinding]) -> str:
    findings_text = "\n\n".join([
        f"Sub-question: {f.sub_question}\nSummary: {f.summary}\nSources:\n"
        + "\n".join([f"  [{i+1}] {r.title} — {r.url}" for i, r in enumerate(f.results)])
        for f in findings
    ])

    all_refs = []
    for f in findings:
        for r in f.results:
            all_refs.append(f"[{len(all_refs)+1}] {r.title} — {r.url}")
    refs_text = "\n".join(all_refs)

    llm = get_llm_with_fallbacks(temperature=0.3)   # lowered from 0.5
    prompt = ChatPromptTemplate.from_template(WRITER_PROMPT)
    chain = prompt | llm

    response = chain.invoke({
        "topic": topic,
        "analysis": analysis,
        "findings": findings_text,
        "max_ref": len(all_refs),
    })

    report_body = response.content.strip()

      # Append the canonical reference list, or a clear note if no sources were found
    if all_refs:
        report_body += "\n\n---\n\n## References\n\n" + refs_text
    else:
        report_body += (
            "\n\n---\n\n## Note on Sources\n\n"
            "No substantive sources were retrieved for this topic. "
            "The conclusions above reflect this absence of evidence, not a synthesis of sources.\n"
        )
    return report_body