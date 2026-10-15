from typing import TypedDict
 
 
class AgentState(TypedDict):
    question: str
    search_query: str
    documents: list[dict]
    evidence_grade: str
    retrieval_attempts: int
    web_results: list[dict]
    answer: str
    sources: list[dict]
    route: str