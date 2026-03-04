import customtkinter as ctk

class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configuration de la fenêtre
        self.title("KORE-Workstation")
        self.geometry("1100x700")
        
        # Thème global
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")
        
        # Initialisation Core
        from database.db_manager import DBManager
        from core.calculator import CalcEngine
        from core.latex_exporter import LaTeXExporter
        from core.srs_intelligence import SRSIntelligence
        from core.git_sync import GitSyncManager
        from core.vision_engine import VisionEngine
        self.db = DBManager()
        self.engine = CalcEngine()
        self.exporter = LaTeXExporter(self.db)
        self.srs_intel = SRSIntelligence()
        self.git_sync = GitSyncManager()
        self.vision = VisionEngine()
        
        # Configuration de la grille
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self._create_sidebar()
        self._create_main_frame()
        
        # Initialiser avec le dashboard
        self.show_dashboard()

    def _create_sidebar(self):
        # Frame de la sidebar
        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(7, weight=1) # Espace vide en bas

        # Titre
        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="KORE\nWorkstation", font=ctk.CTkFont(size=22, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 30))

        # Boutons de navigation
        self.btn_dashboard = ctk.CTkButton(self.sidebar_frame, text="Dashboard", command=self.show_dashboard)
        self.btn_dashboard.grid(row=1, column=0, padx=20, pady=10)

        self.btn_tracker = ctk.CTkButton(self.sidebar_frame, text="Math-Physics Tracker", command=self.show_tracker)
        self.btn_tracker.grid(row=2, column=0, padx=20, pady=10)

        self.btn_journal = ctk.CTkButton(self.sidebar_frame, text="Journal d'Ingénieur", command=self.show_journal)
        self.btn_journal.grid(row=3, column=0, padx=20, pady=10)
        
        self.btn_pomodoro = ctk.CTkButton(self.sidebar_frame, text="Focus Timer", command=self.show_pomodoro)
        self.btn_pomodoro.grid(row=4, column=0, padx=20, pady=10)

        self.btn_latex = ctk.CTkButton(self.sidebar_frame, text="LaTeX Live Preview", command=self.show_latex)
        self.btn_latex.grid(row=5, column=0, padx=20, pady=10)

        self.btn_calc = ctk.CTkButton(self.sidebar_frame, text="KORE-Calc", command=self.show_calculator)
        self.btn_calc.grid(row=6, column=0, padx=20, pady=10)

        self.btn_lab = ctk.CTkButton(self.sidebar_frame, text="Simulation Lab", command=self.show_lab)
        self.btn_lab.grid(row=7, column=0, padx=20, pady=10)
        
        self.tasks_button = ctk.CTkButton(self.sidebar_frame, text="Gestion d'Études", 
                                        command=self.show_tasks)
        self.tasks_button.grid(row=8, column=0, padx=20, pady=10)
        
        self.btn_library = ctk.CTkButton(self.sidebar_frame, text="Garde-Document", command=self.show_library)
        self.btn_library.grid(row=9, column=0, padx=20, pady=10)
        
        # Espace vide en bas
        self.sidebar_frame.grid_rowconfigure(10, weight=1)

    def _create_main_frame(self):
        # Frame principale pour le contenu
        self.main_frame = ctk.CTkFrame(self, corner_radius=10, fg_color="transparent")
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(1, weight=1)
        
        # Barre de commande (Terminal) qui sera toujours au-dessus
        from ui.command_bar import CommandBar
        self.cmd_bar = CommandBar(self.main_frame, app_instance=self)
        self.cmd_bar.grid(row=0, column=0, sticky="ew", pady=(0, 20))

        # Conteneur dynamique (là où les vues changent)
        self.content_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.content_frame.grid(row=1, column=0, sticky="nsew")

        # Status Bar
        self.status_bar = ctk.CTkFrame(self.main_frame, height=30, fg_color="#1E1E1E", corner_radius=5)
        self.status_bar.grid(row=2, column=0, sticky="ew", pady=(10, 0))
        self.status_bar.grid_columnconfigure(0, weight=1)
        
        self.status_label = ctk.CTkLabel(self.status_bar, text="", font=ctk.CTkFont(size=12, slant="italic"), text_color="gray")
        self.status_label.grid(row=0, column=0, padx=10, pady=2, sticky="ew")
        
        self.quotes = [
            "L'ingénieur fait pour un sou ce que n'importe qui fait pour un écu.",
            "La théorie, c'est quand on sait tout et que rien ne fonctionne.",
            "La pratique, c'est quand tout fonctionne et que personne ne sait pourquoi.",
            "On ne résout pas les problèmes avec les modes de pensée qui les ont engendrés.",
            "La vraie folie est de faire toujours la même chose et de s'attendre à un résultat différent.",
            "Tout doit être rendu aussi simple que possible, mais pas plus simple."
        ]
        import random
        self.current_quote = random.choice(self.quotes)
        self._update_status_bar()

    def _update_status_bar(self):
        from datetime import datetime
        now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        self.status_label.configure(text=f"{now}  |  {self.current_quote}")
        self.after(1000, self._update_status_bar)

    def _clear_content(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def show_dashboard(self):
        self._clear_content()
        from ui.dashboard_view import DashboardView
        
        dashboard_view = DashboardView(self.content_frame, fg_color="transparent")
        dashboard_view.pack(fill="both", expand=True)

    def show_tracker(self):
        self._clear_content()
        from ui.tracker_view import TrackerView
        
        tracker_view = TrackerView(self.content_frame, fg_color="transparent")
        tracker_view.pack(fill="both", expand=True)

    def show_journal(self):
        self._clear_content()
        from ui.journal_view import JournalView
        
        journal_view = JournalView(self.content_frame, fg_color="transparent")
        journal_view.pack(fill="both", expand=True)
        
    def show_pomodoro(self):
        self._clear_content()
        from ui.pomodoro_view import PomodoroView
        
        pomodoro_view = PomodoroView(self.content_frame, fg_color="transparent")
        pomodoro_view.pack(fill="both", expand=True)

    def show_latex(self):
        self._clear_content()
        from ui.latex_preview_view import LatexPreviewView
        
        latex_view = LatexPreviewView(self.content_frame, fg_color="transparent")
        latex_view.pack(fill="both", expand=True)

    def show_calculator(self, expression=None):
        self._clear_content()
        from ui.calculator_view import CalculatorView
        
        calc_view = CalculatorView(self.content_frame, fg_color="transparent")
        calc_view.pack(fill="both", expand=True)
        
        if expression:
            calc_view.set_expression(expression)
        self._highlight_button(self.btn_calc)

    def show_lab(self):
        self._clear_content()
        from ui.lab_view import LabView
        
        lab_view = LabView(self.content_frame, fg_color="transparent")
        lab_view.pack(fill="both", expand=True)
        self._highlight_button(self.btn_lab)

    def show_tasks(self):
        self._clear_content()
        from ui.task_manager_view import TaskManagerView
        task_view = TaskManagerView(self.content_frame, fg_color="transparent")
        task_view.pack(fill="both", expand=True)
        if hasattr(self, '_highlight_button'):
            self._highlight_button(self.tasks_button)

    def show_library(self):
        self._clear_content()
        from ui.library_view import LibraryView
        lib_view = LibraryView(self.content_frame, app_instance=self, fg_color="transparent")
        lib_view.pack(fill="both", expand=True)
        if hasattr(self, '_highlight_button'):
            self._highlight_button(self.btn_library)

    def _show_srs_validation(self, cards):
        if not cards:
            self.cmd_bar._show_feedback("Aucune carte trouvée dans ce document.", is_error=True)
            return

        popup = ctk.CTkToplevel(self)
        popup.title("SRS Intelligence : Validation des Cartes")
        popup.geometry("800x600")
        popup.attributes("-topmost", True)
        
        ctk.CTkLabel(popup, text="Sélectionnez les concepts à ajouter au Tracker", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=10)
        
        scroll_frame = ctk.CTkScrollableFrame(popup, width=750, height=450)
        scroll_frame.pack(padx=20, pady=10, fill="both", expand=True)
        
        card_vars = []
        for i, card in enumerate(cards):
            f = ctk.CTkFrame(scroll_frame)
            f.pack(fill="x", pady=5, padx=5)
            
            var = ctk.BooleanVar(value=True)
            chk = ctk.CTkCheckBox(f, text=f"[{card['category']}]", variable=var, width=100)
            chk.pack(side="left", padx=10)
            
            details = ctk.CTkLabel(f, text=f"Q: {card['q'][:100]}\nA: {card['a'][:100]}...", font=ctk.CTkFont(size=12), anchor="w", justify="left")
            details.pack(side="left", fill="x", expand=True, padx=10)
            
            card_vars.append((var, card))
            
        def save_selected():
            count = 0
            for var, card in card_vars:
                if var.get():
                    self.db.add_topic(card['q'], card['category'])
                    # We might want to store the answer as a note or a specific review field
                    # For now, we add them as topics to be reviewed
                    count += 1
            self.cmd_bar._show_feedback(f"{count} cartes ajoutées au Tracker !")
            popup.destroy()
            if hasattr(self, 'current_view') and self.current_view == 'tracker':
                self.show_tracker()

        ctk.CTkButton(popup, text="Ajouter les sélectionnées", command=save_selected, fg_color="green").pack(pady=20)

    # Le traitement des commandes est maintenant géré par CommandBar


if __name__ == "__main__":
    app = MainWindow()
    app.mainloop()
