import customtkinter as ctk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import re

class LatexPreviewView(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Autocomplete Dictionary
        self.snippets = {
            r"\frac": r"\frac{num}{den}",
            r"\int": r"\int_{a}^{b} f(x) dx",
            r"\sum": r"\sum_{i=0}^{n} a_i",
            r"\lim": r"\lim_{x \to \infty}",
            r"\sqrt": r"\sqrt{x}",
            r"\pdv": r"\frac{\partial f}{\partial x}",
            r"\textbf": r"\textbf{text}",
            r"\vec": r"\vec{v}",
            r"\matrix": r"\begin{bmatrix} a & b \\ c & d \end{bmatrix}"
        }
        
        self.templates = {
            "Vide": "",
            "Rapport de Labo": r"\title{Rapport de Laboratoire}\n\author{KORE}\n\date{\today}\n\n\section{Introduction}\n\n\section{Méthodes}\n\n\section{Résultats}\n\n\section{Conclusion}",
            "Fiche de Révision": r"\textbf{Thème: }\n\n\noindent\rule{\textwidth}{0.4pt}\n\n\textbf{Définitions:}\n\begin{itemize}\n\item \n\end{itemize}\n\n\textbf{Formules:}\n\begin{equation}\n\n\end{equation}",
            "Équations Multiples": r"\begin{align*}\n E &= mc^2 \\\n F &= ma\n\end{align*}"
        }

        # Header with Template Selector
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, columnspan=2, sticky="ew")
        
        self.header = ctk.CTkLabel(header_frame, text="LaTeX Live Preview", font=ctk.CTkFont(size=24, weight="bold"))
        self.header.pack(side="left", pady=10)
        
        self.menu_template = ctk.CTkOptionMenu(header_frame, values=list(self.templates.keys()), command=self._load_template)
        self.menu_template.pack(side="right", padx=10, pady=10)

        # Left Side: Editor
        self.editor_frame = ctk.CTkFrame(self)
        self.editor_frame.grid(row=1, column=0, sticky="nsew", padx=(0, 10), pady=10)
        self.editor_frame.grid_columnconfigure(0, weight=1)
        self.editor_frame.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(self.editor_frame, text="Code LaTeX", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, pady=5)
        
        self.textbox = ctk.CTkTextbox(self.editor_frame, font=ctk.CTkFont(family="Consolas", size=14))
        self.textbox.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        self.textbox.insert("1.0", r"\int_{a}^{b} f(x) dx = F(b) - F(a)")
        
        # Bindings for Autocomplete
        self.textbox.bind("<KeyRelease>", self._on_key_release)
        self.textbox.bind("<Tab>", self._on_tab)
        self.textbox.bind("<Return>", self._on_return)
        
        # Autocomplete popup
        self.popup = None
        self.current_word = ""
        self.suggestions = []
        self.selected_suggestion_idx = 0

        # Right Side: Preview
        self.preview_frame = ctk.CTkFrame(self)
        self.preview_frame.grid(row=1, column=1, sticky="nsew", pady=10)
        self.preview_frame.grid_columnconfigure(0, weight=1)
        self.preview_frame.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(self.preview_frame, text="Aperçu", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, pady=5)
        
        self.canvas_frame = ctk.CTkFrame(self.preview_frame, fg_color="#2B2B2B")
        self.canvas_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        
        from matplotlib.figure import Figure
        self.fig = Figure(figsize=(5, 4), dpi=100)
        self.fig.patch.set_facecolor('#2B2B2B')
        self.ax = self.fig.add_subplot(111)
        self.ax.axis('off')
        self.ax.set_facecolor('#2B2B2B')
        
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.canvas_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        self.after(200, self.update_preview)

    def _load_template(self, template_name):
        if template_name in self.templates:
            self.textbox.delete("1.0", "end")
            self.textbox.insert("1.0", self.templates[template_name])
            self.update_preview()

    def _on_key_release(self, event):
        # Update preview
        self.update_preview()
        
        # Don't trigger for navigation keys
        if event.keysym in ("Up", "Down", "Left", "Right", "Tab", "Return", "Escape"):
            return
            
        # Get word under cursor
        try:
            cur_pos = self.textbox.index("insert")
            line, col = map(int, cur_pos.split("."))
            content = self.textbox.get(f"{line}.0", cur_pos)
            
            # Find the last word starting with backslash
            match = re.search(r"(\\[\w]*)$", content)
            if match:
                self.current_word = match.group(1)
                self._show_autocomplete_popup()
            else:
                self._hide_popup()
        except Exception:
            self._hide_popup()

    def _show_autocomplete_popup(self):
        self.suggestions = [k for k in self.snippets.keys() if k.startswith(self.current_word)]
        
        if not self.suggestions:
            self._hide_popup()
            return
            
        if not self.popup:
            # Create a Toplevel window for the popup - this is the most reliable way to be on top
            self.popup = tk.Toplevel(self)
            self.popup.overrideredirect(True) # Borderless
            self.popup.attributes("-topmost", True)
            self.popup.configure(bg="#333333")
            
            self.listbox = tk.Listbox(self.popup, bg="#333333", fg="white", 
                                     selectbackground="#0a84ff", borderwidth=1, 
                                     relief="flat", font=("Consolas", 12),
                                     highlightthickness=0)
            self.listbox.pack(fill="both", expand=True)
            self.listbox.bind("<Double-Button-1>", lambda e: self._on_return())
            
            # Hide on focus loss
            self.textbox.bind("<FocusOut>", lambda e: self.after(100, self._hide_popup), add="+")

        self.listbox.delete(0, "end")
        for s in self.suggestions:
            self.listbox.insert("end", s)
            
        self.listbox.selection_clear(0, "end")
        self.listbox.selection_set(0)
        self.selected_suggestion_idx = 0
            
        # Calculate screen coordinates
        try:
            # get cursor bbox in text widget
            x, y, w, h = self.textbox._textbox.bbox("insert")
            
            # Get root window coordinates
            root_x = self.textbox._textbox.winfo_rootx()
            root_y = self.textbox._textbox.winfo_rooty()
            
            # Final screen position
            abs_x = root_x + x
            abs_y = root_y + y + h + 5
            
            self.popup.geometry(f"180x{min(200, len(self.suggestions)*25)}+{abs_x}+{abs_y}")
            self.popup.deiconify()
        except Exception:
            self._hide_popup()

    def _hide_popup(self, event=None):
        if self.popup:
            self.popup.withdraw()  # Withdraw instead of destroy for reuse
            self.suggestions = []

    def _on_tab(self, event):
        if self.suggestions:
            self._on_return()
            return "break" # Prevent default tab behavior

    def _on_return(self, event=None):
        if self.suggestions:
            idx = self.listbox.curselection()
            if not idx: idx = (0,)
            selected = self.suggestions[idx[0]]
            self._insert_snippet(selected)
            self._hide_popup()
            return "break"

    def _insert_snippet(self, command):
        snippet = self.snippets.get(command, command)
        
        cur_pos = self.textbox.index("insert")
        line, col = map(int, cur_pos.split("."))
        
        # Replace the partial word with the snippet
        start_col = col - len(self.current_word)
        self.textbox.delete(f"{line}.{start_col}", cur_pos)
        self.textbox.insert(f"{line}.{start_col}", snippet)
        
        self.update_preview()

    def update_preview(self, event=None):
        latex_text = self.textbox.get("1.0", "end-1c").strip()
        if not latex_text:
            return

        self.ax.clear()
        self.ax.axis('off')
        
        try:
            # Wrap in $ for math mode if not present
            if not latex_text.startswith("$") and not r"\begin" in latex_text:
                display_text = f"${latex_text}$"
            else:
                display_text = latex_text

            self.ax.text(0.5, 0.5, display_text, size=16, color='white', ha='center', va='center')
            self.canvas.draw()
        except Exception:
            # Handle malformed LaTeX gracefully
            pass
