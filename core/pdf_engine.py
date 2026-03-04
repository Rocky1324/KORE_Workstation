import os
import fitz  # PyMuPDF
import re

class PDFEngine:
    def __init__(self, docs_folder="docs"):
        # Resolve path relative to this script's directory (.../core/pdf_engine.py)
        self.docs_folder = os.path.join(os.path.dirname(os.path.dirname(__file__)), docs_folder)
        
        # Ensure the directory exists
        if not os.path.exists(self.docs_folder):
            os.makedirs(self.docs_folder)
            
    def get_pdfs(self) -> list[str]:
        """Returns a list of PDF file paths in the docs folder."""
        pdfs = []
        if os.path.exists(self.docs_folder):
            for filename in os.listdir(self.docs_folder):
                if filename.lower().endswith('.pdf'):
                    pdfs.append(os.path.join(self.docs_folder, filename))
        return pdfs

    def search_query(self, query: str, context_words: int = 50) -> list[dict]:
        """
        Searches for a query across all PDFs and returns a list of results.
        Returns format: [{"file": "math.pdf", "page": 12, "context": "... definition of matrix ..."}, ...]
        """
        results = []
        pdfs = self.get_pdfs()
        
        if not pdfs:
            return [{"error": "Aucun fichier PDF trouvé dans le dossier 'docs/'"}]
            
        if len(query) < 3:
            return [{"error": "Requête trop courte (minimum 3 caractères)."}]
            
        query_lower = query.lower()
        
        for pdf_path in pdfs:
            try:
                doc = fitz.open(pdf_path)
                filename = os.path.basename(pdf_path)
                
                for page_num, page in enumerate(doc, start=1):
                    # We extract the text in blocks or entire page
                    text = page.get_text()
                    
                    if not text:
                        continue
                        
                    # Find occurrences
                    # We use regex to find the query and grab surrounding context
                    # e.g.: (?i)(.{0,100}matrice.{0,100})
                    escaped_query = re.escape(query_lower)
                    
                    # Pattern that captures up to X characters before and after
                    # It's better to clean up whitespace from the text first
                    clean_text = " ".join(text.split())
                    
                    # Search ignoring case
                    matches = [m.span() for m in re.finditer(escaped_query, clean_text.lower())]
                    
                    for start, end in matches:
                        # Extract the context
                        c_start = max(0, start - context_words)
                        c_end = min(len(clean_text), end + context_words)
                        
                        context_str = clean_text[c_start:c_end]
                        if c_start > 0:
                            context_str = "..." + context_str
                        if c_end < len(clean_text):
                            context_str = context_str + "..."
                            
                        # Highlight the matched term in simple ascii (could be markdown later)
                        # We just keep it simple for now
                        
                        results.append({
                            "file": filename,
                            "page": page_num,
                            "context": context_str
                        })
                        
                        # In a simple MVP, to avoid flooding, we break after 3 matches per page
                        if len(results[-1].get("context", "")) > 10 and len(matches) > 3:
                            break
                            
                doc.close()
            except Exception as e:
                print(f"Error reading {pdf_path}: {e}")
                
        # Limit to 10 best results globally to avoid overwhelming the UI
        return results[:10]
