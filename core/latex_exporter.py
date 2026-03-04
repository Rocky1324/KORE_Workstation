import os
from datetime import datetime

class LaTeXExporter:
    """Utility to export database content (Journal, Tracker) to LaTeX format."""
    
    def __init__(self, db_manager):
        self.db = db_manager

    def generate_journal_latex(self):
        """Generates a LaTeX string for all journal entries."""
        entries = self.db.get_journal_entries(limit=1000)
        
        latex = r"""\documentclass{article}
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage[french]{babel}
\usepackage{amsmath, amssymb}
\usepackage{geometry}
\geometry{a4paper, margin=2cm}

\title{Journal d'Ingénieur - KORE-Workstation}
\author{Étudiant EPFL}
\date{\today}

\begin{document}
\maketitle
\tableofcontents
\newpage
"""

        for entry in entries:
            # entry: (id, date, title, content, keywords)
            date_str = entry[1]
            title = self._clean_latex(entry[2])
            content = self._clean_latex(entry[3])
            keywords = self._clean_latex(entry[4])
            
            latex += f"\\section{{{title}}}\n"
            latex += f"\\textbf{{Date :}} {date_str} \\\\\n"
            if keywords:
                latex += f"\\textbf{{Tags :}} {keywords} \\\\\n"
            latex += "\n"
            latex += f"{content}\n"
            latex += "\\vspace{1em}\n"

        latex += r"\end{document}"
        return latex

    def generate_tracker_latex(self):
        """Generates a LaTeX string for the Math-Physics Tracker subjects."""
        topics = self.db.get_topics()
        
        latex = r"""\documentclass{article}
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage[french]{babel}
\usepackage{amsmath, amssymb, booktabs}
\usepackage{geometry}
\geometry{a4paper, margin=2.5cm}

\title{Récapitulatif - Math-Physics Tracker}
\date{\today}

\begin{document}
\maketitle

\section{Concepts en cours de révision}
\begin{center}
\begin{tabular}{lllc}
\toprule
\textbf{ID} & \textbf{Concept} & \textbf{Catégorie} & \textbf{Complexité} \\
\midrule
"""
        for t in topics:
            # t: (id, name, category)
            # We can also fetch the ease_factor if needed by joining with reviews
            name = self._clean_latex(t[1])
            cat = self._clean_latex(t[2])
            latex += f"{t[0]} & {name} & {cat} & --- \\\\\n"

        latex += r"""\bottomrule
\end{tabular}
\end{center}
\end{document}
"""
        return latex

    def _clean_latex(self, text):
        """Basic escaping for LaTeX special characters."""
        if not text: return ""
        chars = {
            '&': r'\&',
            '%': r'\%',
            '$': r'\$',
            '#': r'\#',
            '_': r'\_',
            '{': r'\{',
            '}': r'\}',
            '~': r'\textasciitilde{}',
            '^': r'\textasciicircum{}',
            '\\': r'\textbackslash{}'
        }
        for char, replacement in chars.items():
            text = text.replace(char, replacement)
        return text

    def save_to_file(self, content, filename):
        """Saves content to an .tex file in the exports/ directory."""
        # Get project root (parent of core/)
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        export_dir = os.path.join(project_root, "exports")
        
        if not os.path.exists(export_dir):
            os.makedirs(export_dir)
            
        path = os.path.join(export_dir, filename)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return os.path.abspath(path)
