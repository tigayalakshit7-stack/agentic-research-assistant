from pydantic import BaseModel, Field
from typing import List
from enum import Enum


class ResearchStage(str, Enum):
    PLANNING = "planning"
    RESEARCHING = "researching"
    ANALYZING = "analyzing"
    WRITING = "writing"
    COMPLETE = "complete"


class SubQuestion(BaseModel):
    question: str
    rationale: str


class SearchResult(BaseModel):
    title: str
    url: str
    snippet: str


class ResearchFinding(BaseModel):
    sub_question: str
    results: List[SearchResult]
    summary: str


class ResearchState(BaseModel):
    topic: str
    stage: ResearchStage = ResearchStage.PLANNING
    sub_questions: List[SubQuestion] = Field(default_factory=list)
    findings: List[ResearchFinding] = Field(default_factory=list)
    analysis: str = ""
    final_report: str = ""
    errors: List[str] = Field(default_factory=list)