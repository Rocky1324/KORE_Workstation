import customtkinter as ctk
from database.db_manager import DBManager

class JournalView(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.db = DBManager()
        
        # Grid Layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)

        # Header
        self.header_label = ctk.CTkLabel(self, text="Journal d'Ingénieur", font=ctk.CTkFont(size=24, weight="bold"))
        self.header_label.grid(row=0, column=0, pady=(0, 20), sticky="w")

        # --- Section: Add New Log ---
        self.add_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.add_frame.grid(row=1, column=0, sticky="ew", pady=(0, 20))
        self.add_frame.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(self.add_frame, text="Titre du log:").grid(row=0, column=0, padx=(0, 10), sticky="w")
        self.title_entry = ctk.CTkEntry(self.add_frame, placeholder_text="Ex: Résolution de l'erreur ValueError...")
        self.title_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        
        ctk.CTkLabel(self.add_frame, text="Contenu/Solution:").grid(row=1, column=0, padx=(0, 10), sticky="nw", pady=(5,0))
        self.content_text = ctk.CTkTextbox(self.add_frame, height=80)
        self.content_text.grid(row=1, column=1, sticky="ew", padx=5, pady=5)
        
        ctk.CTkLabel(self.add_frame, text="Mots-clés:").grid(row=2, column=0, padx=(0, 10), sticky="w")
        self.keywords_entry = ctk.CTkEntry(self.add_frame, placeholder_text="Ex: python, sql, bug")
        self.keywords_entry.grid(row=2, column=1, sticky="ew", padx=5, pady=5)
        
        # Add a submit button frame to align right
        self.btn_frame = ctk.CTkFrame(self.add_frame, fg_color="transparent")
        self.btn_frame.grid(row=3, column=1, sticky="e", pady=5)
        self.add_btn = ctk.CTkButton(self.btn_frame, text="Enregistrer le Log", command=self._add_log)
        self.add_btn.pack()

        # --- Section: Logs History ---
        # Search/Filter
        self.filter_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.filter_frame.grid(row=2, column=0, sticky="ew", pady=(10, 5))
        self.filter_frame.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(self.filter_frame, text="Historique", font=ctk.CTkFont(size=18, weight="bold")).grid(row=0, column=0, sticky="w")
        self.search_entry = ctk.CTkEntry(self.filter_frame, placeholder_text="Rechercher...")
        self.search_entry.grid(row=0, column=1, sticky="e", padx=5)
        self.search_entry.bind("<KeyRelease>", self._filter_logs)

        # Log List
        self.logs_frame = ctk.CTkScrollableFrame(self)
        self.logs_frame.grid(row=3, column=0, sticky="nsew")
        self.logs_frame.grid_columnconfigure(0, weight=1)
        
        # Bouton d'export en bas
        self.export_btn = ctk.CTkButton(self, text="Exporter tout en Markdown (Obsidian)", command=self._export_to_markdown, fg_color="#3A3A3A")
        self.export_btn.grid(row=4, column=0, pady=(10, 0), sticky="e")
        
        self.all_logs = []
        self.refresh_logs()

    def _export_to_markdown(self):
        import os
        from datetime import datetime
        
        # Créer le dossier d'export s'il n'existe pas
        export_dir = "exports"
        if not os.path.exists(export_dir):
            os.makedirs(export_dir)
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = os.path.join(export_dir, f"journal_export_{timestamp}.md")
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write("# Journal d'Ingénieur - KORE Workstation\n\n")
            f.write(f"*Export généré le {datetime.now().strftime('%d/%m/%Y à %H:%M:%S')}*\n\n---\n\n")
            
            for log in self.all_logs:
                _, date, title, content, keywords = log
                f.write(f"## {title} (_{date}_)\n\n")
                if keywords:
                    tags = " ".join([f"#{k.strip()}" for k in keywords.split(",")])
                    f.write(f"**Tags:** {tags}\n\n")
                f.write(f"{content}\n\n---\n\n")
                
        print(f"Export réussi : {filepath}")
        # Optionnel: Afficher un message de succès (tooltip ou messagebox)
        
    def _add_log(self):
        title = self.title_entry.get().strip()
        content = self.content_text.get("1.0", "end-1c").strip()
        keywords = self.keywords_entry.get().strip()
        
        if title and content:
            self.db.add_journal_entry(title, content, keywords)
            
            # Clear fields
            self.title_entry.delete(0, 'end')
            self.content_text.delete("1.0", "end")
            self.keywords_entry.delete(0, 'end')
            
            self.refresh_logs()

    def refresh_logs(self):
        self.all_logs = self.db.get_journal_entries()
        self._display_logs(self.all_logs)

    def _filter_logs(self, event=None):
        query = self.search_entry.get().lower()
        if not query:
            self._display_logs(self.all_logs)
            return
            
        filtered = []
        for log in self.all_logs:
            _, date, title, content, keywords = log
            if query in title.lower() or query in content.lower() or query in keywords.lower():
                filtered.append(log)
                
        self._display_logs(filtered)

    def _display_logs(self, logs):
        # Clear current list
        for widget in self.logs_frame.winfo_children():
            widget.destroy()
            
        if not logs:
            ctk.CTkLabel(self.logs_frame, text="Aucun log trouvé.", font=ctk.CTkFont(slant="italic")).pack(pady=20)
            return
            
        for log in logs:
            _, date, title, content, keywords = log
            
            card = ctk.CTkFrame(self.logs_frame)
            card.pack(fill="x", pady=5, padx=5)
            card.grid_columnconfigure(0, weight=1)
            
            # Header log: Title + Date
            header_frame = ctk.CTkFrame(card, fg_color="transparent")
            header_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 5))
            header_frame.grid_columnconfigure(0, weight=1)
            
            ctk.CTkLabel(header_frame, text=title, font=ctk.CTkFont(size=14, weight="bold")).grid(row=0, column=0, sticky="w")
            ctk.CTkLabel(header_frame, text=date, font=ctk.CTkFont(size=12)).grid(row=0, column=1, sticky="e")
            
            # Content snippet (limit to 3 lines approx)
            content_snippet = content if len(content) < 150 else content[:147] + "..."
            ctk.CTkLabel(card, text=content_snippet, justify="left", anchor="w").grid(row=1, column=0, sticky="ew", padx=10, pady=5)
            
            # Keywords
            if keywords:
                ctk.CTkLabel(card, text=f"Tags: {keywords}", text_color="gray", font=ctk.CTkFont(size=10)).grid(row=2, column=0, sticky="w", padx=10, pady=(0, 10))
