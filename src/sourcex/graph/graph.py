from langchain_core.retrievers import BaseRetriever
from langgraph.graph import StateGraph, START, END
from sourcex.graph.state import GraphState
from sourcex.graph.nodes import analyze_query, RetrieveContextNode

def create_graph(retriever: BaseRetriever):
    """
    Creates and compiles the LangGraph workflow for SourceX.
    Takes the LangChain retriever as a dependency.
    """
    workflow = StateGraph(GraphState)
    
    retrieve_node = RetrieveContextNode(retriever)
    
    workflow.add_node("analyze_query", analyze_query)
    workflow.add_node("retrieve_context", retrieve_node)
    
    workflow.add_edge(START, "analyze_query")
    workflow.add_edge("analyze_query", "retrieve_context")
    workflow.add_edge("retrieve_context", END)
    
    return workflow.compile()
