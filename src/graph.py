from src.state import ResearchState, ResearchStage
from src.agents.planner import plan_research
from src.agents.researcher import research_sub_question
from src.agents.analyst import analyze_findings
from src.agents.writer import write_report


def run_research_pipeline(topic: str, progress_callback=None) -> ResearchState:
    """
    Orchestrates the full multi-agent research pipeline.
    Each stage feeds the next: Plan -> Research -> Analyze -> Write.
    """
    state = ResearchState(topic=topic)

    # Stage 1: Planning
    if progress_callback:
        progress_callback("🧠 Planner Agent: Breaking down the topic...")
    state.stage = ResearchStage.PLANNING
    state.sub_questions = plan_research(topic)

    # Stage 2: Researching
    state.stage = ResearchStage.RESEARCHING
    for i, sq in enumerate(state.sub_questions):
        if progress_callback:
            progress_callback(f"🔍 Researcher Agent: Investigating sub-question {i+1}/{len(state.sub_questions)}...")
        try:
            finding = research_sub_question(sq)
            state.findings.append(finding)
        except Exception as e:
            state.errors.append(f"Failed on '{sq.question}': {e}")

    # Stage 3: Analyzing
    state.stage = ResearchStage.ANALYZING
    if progress_callback:
        progress_callback("📊 Analyst Agent: Synthesizing findings...")
    state.analysis = analyze_findings(topic, state.findings)

    # Stage 4: Writing
    state.stage = ResearchStage.WRITING
    if progress_callback:
        progress_callback("✍️ Writer Agent: Compiling the report...")
    state.final_report = write_report(topic, state.analysis, state.findings)

    state.stage = ResearchStage.COMPLETE
    return state