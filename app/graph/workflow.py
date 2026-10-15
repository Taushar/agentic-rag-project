from langgraph.graph import StateGraph, START, END
 
from app.graph.state import AgentState
from app.graph.nodes import (
    prepare_query,
    retrieve_documents,
    grade_documents,
    route_after_grading,
    rewrite_query,
    search_web,
    generate_answer
)
 
 
builder = StateGraph(AgentState)
 
builder.add_node("prepare_query", prepare_query)
builder.add_node("retrieve_documents", retrieve_documents)
builder.add_node("grade_documents", grade_documents)
builder.add_node("rewrite_query", rewrite_query)
builder.add_node("search_web", search_web)
builder.add_node("generate_answer", generate_answer)
 
builder.add_edge(START, "prepare_query")
builder.add_edge("prepare_query", "retrieve_documents")
builder.add_edge("retrieve_documents", "grade_documents")
 
builder.add_conditional_edges(
    "grade_documents",
    route_after_grading,
    {
        "answer": "generate_answer",
        "rewrite_query": "rewrite_query",
        "web_search": "search_web"
    }
)
 
builder.add_edge("rewrite_query", "retrieve_documents")
builder.add_edge("search_web", "generate_answer")
builder.add_edge("generate_answer", END)
 
graph = builder.compile()
 
 
def run_agent(question):
    initial_state = {
        "question": question,
        "search_query": question,
        "documents": [],
        "evidence_grade": "unknown",
        "retrieval_attempts": 0,
        "web_results": [],
        "answer": "",
        "sources": [],
        "route": ""
    }
 
    return graph.invoke(initial_state)