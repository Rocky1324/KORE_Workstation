import customtkinter as ctk
from database.db_manager import DBManager
from core.srs import SRSAlgorithm

class TrackerView(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.db = DBManager()
        
        # grid layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # Header
        self.header_label = ctk.CTkLabel(self, text="Math-Physics Tracker (Répétition Espacée)", font=ctk.CTkFont(size=24, weight="bold"))
        self.header_label.grid(row=0, column=0, pady=(0, 20), sticky="w")

        # --- Section: Add New Topic ---
        self.add_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.add_frame.grid(row=1, column=0, sticky="ew", pady=(0, 20))
        self.add_frame.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(self.add_frame, text="Nouveau Concept:").grid(row=0, column=0, padx=(0, 10))
        self.topic_name_entry = ctk.CTkEntry(self.add_frame, placeholder_text="Ex: Théorème de Gauss...")
        self.topic_name_entry.grid(row=0, column=1, sticky="ew", padx=5)
        
        self.category_var = ctk.StringVar(value="Maths")
        self.category_opt = ctk.CTkOptionMenu(self.add_frame, values=["Maths", "Physique", "CS"], variable=self.category_var)
        self.category_opt.grid(row=0, column=2, padx=5)
        
        self.add_btn = ctk.CTkButton(self.add_frame, text="Ajouter", command=self._add_topic)
        self.add_btn.grid(row=0, column=3, padx=(5, 0))

        # --- Section: Reviews Due ---
        self.reviews_frame = ctk.CTkScrollableFrame(self)
        self.reviews_frame.grid(row=2, column=0, sticky="nsew")
        self.reviews_frame.grid_columnconfigure(0, weight=1)
        
        self.refresh_reviews()

    def _add_topic(self):
        name = self.topic_name_entry.get().strip()
        cat = self.category_var.get()
        if name:
            self.db.add_topic(name, cat)
            self.topic_name_entry.delete(0, 'end')
            self.refresh_reviews()

    def refresh_reviews(self):
        # Clear current reviews
        for widget in self.reviews_frame.winfo_children():
            widget.destroy()
            
        due_reviews = self.db.get_due_reviews()
        
        if not due_reviews:
            ctk.CTkLabel(self.reviews_frame, text="Aucune révision prévue pour aujourd'hui ! 🎉", font=ctk.CTkFont(size=16, slant="italic")).pack(pady=40)
            return

        ctk.CTkLabel(self.reviews_frame, text=f"Révisions du jour ({len(due_reviews)})", font=ctk.CTkFont(size=18, weight="bold")).pack(anchor="w", pady=(0, 10))

        for row_index, review in enumerate(due_reviews):
            topic_id, name, cat, current_interval, current_ease = review
            
            card = ctk.CTkFrame(self.reviews_frame)
            card.pack(fill="x", pady=5, padx=5)
            card.grid_columnconfigure(1, weight=1)
            
            # Info
            info_text = f"[{cat}] {name}"
            ctk.CTkLabel(card, text=info_text, font=ctk.CTkFont(size=14, weight="bold")).grid(row=0, column=0, sticky="w", padx=10, pady=10)
            
            # Action buttons for SM-2
            btn_frame = ctk.CTkFrame(card, fg_color="transparent")
            btn_frame.grid(row=0, column=1, sticky="e", padx=10, pady=10)
            
            # Quality ratings (0-5)
            # 0: Oubli (Rouge) ... 5: Parfait (Vert)
            colors = ["#FF4C4C", "#FF8C42", "#FFC300", "#4CAF50", "#2E7D32", "#1B5E20"]
            labels = ["0: Oubli", "1: Dur", "2", "3: OK", "4", "5: Parfait"]
            
            for q in range(6):
                btn = ctk.CTkButton(
                    btn_frame, 
                    text=labels[q], 
                    width=60,
                    fg_color=colors[q],
                    hover_color=colors[max(0, q-1)], # rough hover
                    command=lambda t_id=topic_id, qual=q, inv=current_interval, ease=current_ease: self._process_review(t_id, qual, inv, ease)
                )
                btn.grid(row=0, column=q, padx=2)

    def _process_review(self, topic_id, quality, current_interval, current_ease):
        # Calculate next review using SM-2
        next_date, new_interval, new_ease = SRSAlgorithm.calculate_next_review(quality, current_interval, current_ease)
        
        # Update database
        self.db.update_review(topic_id, next_date, new_interval, new_ease)
        
        # Refresh UI
        self.refresh_reviews()
