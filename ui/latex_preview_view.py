import customtkinter as ctk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class LatexPreviewView(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Header
        self.header = ctk.CTkLabel(self, text="LaTeX Live Preview", font=ctk.CTkFont(size=24, weight="bold"))
        self.header.grid(row=0, column=0, columnspan=2, pady=10, sticky="w")

        # Left Side: Editor
        self.editor_frame = ctk.CTkFrame(self)
        self.editor_frame.grid(row=1, column=0, sticky="nsew", padx=(0, 10), pady=10)
        self.editor_frame.grid_columnconfigure(0, weight=1)
        self.editor_frame.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(self.editor_frame, text="Code LaTeX", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, pady=5)
        
        self.textbox = ctk.CTkTextbox(self.editor_frame, font=ctk.CTkFont(family="Consolas", size=14))
        self.textbox.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        self.textbox.insert("1.0", r"\int_{a}^{b} f(x) dx = F(b) - F(a)")
        self.textbox.bind("<KeyRelease>", self.update_preview)

        # Right Side: Preview
        self.preview_frame = ctk.CTkFrame(self)
        self.preview_frame.grid(row=1, column=1, sticky="nsew", pady=10)
        self.preview_frame.grid_columnconfigure(0, weight=1)
        self.preview_frame.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(self.preview_frame, text="Aperçu", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, pady=5)
        
        self.canvas_frame = ctk.CTkFrame(self.preview_frame, fg_color="#2B2B2B")
        self.canvas_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        
        self.fig, self.ax = plt.subplots(figsize=(5, 4), dpi=100)
        self.fig.patch.set_facecolor('#2B2B2B')
        self.ax.set_facecolor('#2B2B2B')
        self.ax.axis('off')
        
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.canvas_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        self.update_preview()

    def update_preview(self, event=None):
        latex_text = self.textbox.get("1.0", "end-1c").strip()
        if not latex_text:
            return

        self.ax.clear()
        self.ax.axis('off')
        
        try:
            # Wrap in $ for math mode if not present
            if not latex_text.startswith("$"):
                display_text = f"${latex_text}$"
            else:
                display_text = latex_text

            self.ax.text(0.5, 0.5, display_text, size=20, color='white', ha='center', va='center')
            self.canvas.draw()
        except Exception:
            # Handle malformed LaTeX gracefully
            pass
