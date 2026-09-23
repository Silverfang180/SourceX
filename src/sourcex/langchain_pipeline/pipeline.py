from typing import List, Dict, Any
import fitz

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

from sourcex.config import config
from sourcex.cleaning import clean_text

def extract_documents(pdf_path: str) -> List[Document]:
    """
    T002 equivalent: extraction.
    We manually wrap PyMuPDF to replicate the custom metadata generation and extraction accurately.
    """
    doc = fitz.open(pdf_path)
    documents = []
    
    # We use a simplified filename as document_id for parity with the manual script logic
    import os
    filename = os.path.basename(pdf_path)
    document_id = filename
    
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        text = page.get_text()
        
        # T003 equivalent: cleaning
        cleaned = clean_text(text)
        
        if cleaned.strip():
            metadata = {
                "source_file": filename,
                "page_number": page_num + 1,
                "document_id": document_id
            }
            documents.append(Document(page_content=cleaned, metadata=metadata))
            
    doc.close()
    return documents

def build_langchain_vectorstore(documents: List[Document]) -> FAISS:
    """
    T004, T005, T006, T007 equivalent.
    """
    # T004: chunking
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separators=["\n\n", "\n", " ", ""]
    )
    splits = text_splitter.split_documents(documents)
    
    # Add chunk_index to replicate T005 metadata
    for i, split in enumerate(splits):
        split.metadata["chunk_index"] = i
        # T006 formatting constraint for gemini-embedding-2: "title: none | text: {text}"
        split.page_content = f"title: none | text: {split.page_content}"
        
    # T006: embeddings + T007: FAISS indexing
    embeddings = GoogleGenerativeAIEmbeddings(
        model=config.EMBEDDING_MODEL,
        google_api_key=config.GEMINI_API_KEY
    )
    
    vectorstore = FAISS.from_documents(splits, embeddings)
    return vectorstore

def create_rag_chain(vectorstore: FAISS):
    """
    T008, T009 equivalent.
    """
    # T008: retrieval
    retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
    
    # T009: generation
    llm = ChatGoogleGenerativeAI(
        model=config.GENERATION_MODEL,
        google_api_key=config.GEMINI_API_KEY
    )
    
    prompt = PromptTemplate.from_template(
        "Answer the user's question based on the following context. "
        "If you don't know the answer or the context doesn't provide enough information, "
        "just say you don't know. Do not invent information.\n\n"
        "Context:\n{context}\n\n"
        "Question: {question}"
    )
    
    def format_docs(docs):
        # Format the document content exactly like the manual pipeline
        # (Stripping the "title: none | text: " prefix added for embedding matching)
        parts = []
        for i, doc in enumerate(docs):
            content = doc.page_content
            if content.startswith("title: none | text: "):
                content = content[len("title: none | text: "):]
            parts.append(f"[Document {i+1}]\n{content}")
        return "\n\n".join(parts)
        
    # We create a custom chain that also returns source documents
    rag_chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    
    return rag_chain, retriever

def run_pipeline(pdf_path: str, query: str) -> Dict[str, Any]:
    """
    Runs the full end-to-end LangChain pipeline.
    """
    # Format query identically to T008 for gemini-embedding-2
    formatted_query = f"task: question answering | query: {query}"
    
    documents = extract_documents(pdf_path)
    vectorstore = build_langchain_vectorstore(documents)
    rag_chain, retriever = create_rag_chain(vectorstore)
    
    answer = rag_chain.invoke(formatted_query)
    source_docs = retriever.invoke(formatted_query)
    
    return {
        "answer": answer,
        "source_documents": source_docs
    }
