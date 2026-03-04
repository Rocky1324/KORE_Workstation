import os
import fitz  # PyMuPDF
import re

class SRSIntelligence:
    """Engine to automatically extract study cards (Q&A) from documents."""
    
    def __init__(self):
        # Common academic patterns in French/English
        # Support variations: Definition/Définition, Theorem/Théorème/Theoreme, etc.
        self.patterns = [
            # Pattern for Theorems: (Le)? (théorème|theoreme) (de)? [Nom] (stipule que|est)? [Enoncé]
            (r"(?i)(?:le\s+)?(th[eé]or[eè]me)\s+(?:de\s+)?(.*?)\s+(?:stipule\s+que|est|:)\s+([^.\n]+(?:[. \n][^.\n]+)?)", "Théorème"),
            
            # Pattern for Definitions: (La)? (définition|definition) (de)? [Terme] (est|:)? [Explication]
            (r"(?i)(?:la\s+)?(d[eé]finition)\s+(?:de\s+)?(.*?)\s+(?:est|:)\s+([^.\n]+(?:[. \n][^.\n]+)?)", "Définition"),
            
            # Pattern for Properties
            (r"(?i)(?:la\s+)?(propri[eé]t[eé])\s+(?:de\s+)?([^.\n:]+)\s+(?:est|:)\s+([^.\n]+(?:[. \n][^.\n]+)?)", "Propriété"),
            
            # Formula/Equation in LaTeX
            (r"(\$\$.*?\$\$)", "Formule")
        ]

    def scan_file(self, file_path):
        """Scans a file and returns a list of potential cards: [{'q': ..., 'a': ..., 'cat': ...}]"""
        ext = os.path.splitext(file_path)[1].lower()
        text = ""
        
        if ext == ".pdf":
            text = self._extract_text_pdf(file_path)
        elif ext in [".md", ".txt"]:
            text = self._extract_text_txt(file_path)
        else:
            return []
            
        return self._parse_text(text)

    def _extract_text_pdf(self, path):
        try:
            doc = fitz.open(path)
            full_text = ""
            for page in doc:
                full_text += page.get_text() + "\n"
            doc.close()
            return full_text
        except Exception as e:
            print(f"Error reading PDF {path}: {e}")
            return ""

    def _extract_text_txt(self, path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            print(f"Error reading text file {path}: {e}")
            return ""

    def _parse_text(self, text):
        cards = []
        # Clean text: normalize whitespace
        lines = text.split('\n')
        clean_text = "\n".join([line.strip() for line in lines if line.strip()])
        
        for pattern_str, category in self.patterns:
            matches = re.finditer(pattern_str, clean_text)
            for m in matches:
                if category == "Formule":
                    # For formulas, we might just grab the context before
                    start_idx = m.start()
                    context = clean_text[max(0, start_idx-50):start_idx].strip().split('\n')[-1]
                    q = f"Quelle est la formule pour : {context} ?" if context else "Identifiez cette formule :"
                    a = m.group(1)
                else:
                    # m.group(2) is the title/term, m.group(3) is the explanation/statement
                    keyword = m.group(1).capitalize()
                    q = f"{keyword} de : {m.group(2).strip()}"
                    a = m.group(3).strip()
                
                # Basic filtering
                if len(q) > 5 and len(a) > 5:
                    cards.append({
                        "q": q,
                        "a": a,
                        "category": category
                    })
        
        return cards
