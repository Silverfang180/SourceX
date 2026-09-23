import os
import fitz
from sourcex.config import config
from sourcex.langchain_pipeline.pipeline import run_pipeline

def create_tiny_pdf(path: str):
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50, 50), "The secret code to bypass the mainframe is 998877.")
    doc.save(path)
    doc.close()

def run_t010_smoke_test():
    print("Running T010 Live Smoke Test...")
    
    if not config.GEMINI_API_KEY:
        print("Error: GEMINI_API_KEY not set.")
        return
        
    pdf_path = "smoke_test_t010_dummy.pdf"
    create_tiny_pdf(pdf_path)
    
    try:
        question = "What is the secret code to bypass the mainframe?"
        print(f"Sending question: {question}")
        
        result = run_pipeline(pdf_path, question)
        
        answer = result["answer"]
        source_documents = result["source_documents"]
        
        print("\n--- Answer ---")
        print(answer)
        print("--------------")
        
        assert answer, "Answer should not be empty"
        assert "998877" in answer, "Answer did not contain expected explicit information"
        assert len(source_documents) > 0, "Should have returned source documents"
        
        print("T010 Smoke Test PASSED.\n")
    finally:
        if os.path.exists(pdf_path):
            os.remove(pdf_path)

if __name__ == "__main__":
    run_t010_smoke_test()
