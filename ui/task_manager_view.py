import customtkinter as ctk
from database.db_manager import DBManager
from datetime import datetime, timedelta

class TaskManagerView(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.db = DBManager()
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # --- UI Header ---
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.grid(row=0, column=0, sticky="ew", padx=30, pady=(20, 10))
        
        self.title_label = ctk.CTkLabel(self.header_frame, text="Centre de Gestion des Études", 
                                       font=ctk.CTkFont(size=28, weight="bold"))
        self.title_label.pack(side="left")
        
        self.subtitle = ctk.CTkLabel(self.header_frame, text="Planifiez vos projets et suivez vos échéances", 
                                    text_color="gray", font=ctk.CTkFont(size=14))
        self.subtitle.pack(side="left", padx=20, pady=(10, 0))

        # --- TabView ---
        self.tabview = ctk.CTkTabview(self, segmented_button_fg_color="#1a1a1a", 
                                     segmented_button_selected_color="#1f538d",
                                     segmented_button_selected_hover_color="#2a6ab3")
        self.tabview.grid(row=1, column=0, sticky="nsew", padx=30, pady=(0, 20))
        
        self.tab_homework = self.tabview.add("📚 Devoirs")
        self.tab_projects = self.tabview.add("🏗️ Projets")
        self.tab_tasks = self.tabview.add("✅ To-do")
        
        self._setup_homework_ui()
        self._setup_projects_ui()
        self._setup_tasks_ui()

    # --- HOMEWORK TAB ---
    def _setup_homework_ui(self):
        self.tab_homework.grid_columnconfigure(0, weight=1)
        self.tab_homework.grid_rowconfigure(1, weight=1)
        
        # Quick Add Form
        form_f = ctk.CTkFrame(self.tab_homework, fg_color="#1a1a1a", corner_radius=10)
        form_f.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        
        ctk.CTkLabel(form_f, text="Nouveau Devoir :", font=ctk.CTkFont(size=12, weight="bold")).pack(side="left", padx=10)
        
        self.hw_sub_entry = ctk.CTkEntry(form_f, placeholder_text="Matière", width=120)
        self.hw_sub_entry.pack(side="left", padx=5, pady=10)
        
        self.hw_title_entry = ctk.CTkEntry(form_f, placeholder_text="Titre (ex: Série 4)", width=200)
        self.hw_title_entry.pack(side="left", padx=5)
        
        self.hw_date_entry = ctk.CTkEntry(form_f, placeholder_text="Date (AAAA-MM-JJ)", width=120)
        # Set default to next week
        next_week = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
        self.hw_date_entry.insert(0, next_week)
        self.hw_date_entry.pack(side="left", padx=5)
        
        ctk.CTkButton(form_f, text="+ Ajouter", width=80, command=self._ui_add_homework).pack(side="right", padx=10)

        # Scrollable area
        self.hw_scroll = ctk.CTkScrollableFrame(self.tab_homework, fg_color="transparent")
        self.hw_scroll.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        self.refresh_homework()

    def _ui_add_homework(self):
        sub = self.hw_sub_entry.get()
        title = self.hw_title_entry.get()
        date = self.hw_date_entry.get()
        if sub and title and date:
            self.db.add_homework(sub, title, date)
            self.hw_sub_entry.delete(0, 'end')
            self.hw_title_entry.delete(0, 'end')
            self.refresh_homework()

    def refresh_homework(self):
        for widget in self.hw_scroll.winfo_children():
            widget.destroy()
            
        homework = self.db.get_all_homework()
        if not homework:
            ctk.CTkLabel(self.hw_scroll, text="Aucun devoir pour le moment. 🎉", text_color="gray").pack(pady=50)
            return

        for hw in homework:
            h_id, sub, title, dl, prio, stat = hw
            card = ctk.CTkFrame(self.hw_scroll, fg_color="#242424", border_width=1, border_color="#333333")
            card.pack(fill="x", pady=8, padx=10)
            
            # Left side Info
            info_f = ctk.CTkFrame(card, fg_color="transparent")
            info_f.pack(side="left", padx=20, pady=15, fill="both", expand=True)
            
            # Urgency check
            dl_date = datetime.strptime(dl, "%Y-%m-%d")
            days_left = (dl_date - datetime.now()).days + 1
            
            urg_color = "white"
            urg_text = f"Due dans {days_left}j"
            if stat == 'Fait':
                urg_color = "#55aa55"
                urg_text = "COMPLÉTÉ ✅"
            elif days_left <= 2:
                urg_color = "#ff4444"
                urg_text = f"🔥 URGENT : {days_left} jour(s) !"

            ctk.CTkLabel(info_f, text=f"{sub.upper()}", text_color="#1f538d", 
                        font=ctk.CTkFont(size=10, weight="bold")).pack(anchor="w")
            ctk.CTkLabel(info_f, text=title, font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w")
            ctk.CTkLabel(info_f, text=f"échéance : {dl} • {urg_text}", text_color=urg_color,
                        font=ctk.CTkFont(size=12)).pack(anchor="w")

            # Right side actions
            act_f = ctk.CTkFrame(card, fg_color="transparent")
            act_f.pack(side="right", padx=20)
            
            if stat != 'Fait':
                ctk.CTkButton(act_f, text="Marquer Fait", width=100, fg_color="#28a745", hover_color="#218838",
                             command=lambda i=h_id: self._mark_hw_done(i)).pack(side="left", padx=5)
            
            ctk.CTkButton(act_f, text="🗑️", width=40, fg_color="#dc3545", hover_color="#c82333",
                         command=lambda i=h_id: self._delete_hw(i)).pack(side="left", padx=5)

    def _mark_hw_done(self, hw_id):
        with self.db.get_connection() as conn:
            conn.execute("UPDATE homework SET status = 'Fait' WHERE id = ?", (hw_id,))
            conn.commit()
        self.refresh_homework()

    def _delete_hw(self, hw_id):
        self.db.delete_homework(hw_id)
        self.refresh_homework()

    # --- PROJECTS TAB ---
    def _setup_projects_ui(self):
        self.tab_projects.grid_columnconfigure(0, weight=1)
        self.tab_projects.grid_rowconfigure(1, weight=1)
        
        # Form
        form_f = ctk.CTkFrame(self.tab_projects, fg_color="#1a1a1a", corner_radius=10)
        form_f.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        
        self.p_name_entry = ctk.CTkEntry(form_f, placeholder_text="Nom du projet (ex: MTU Prototype)", width=250)
        self.p_name_entry.pack(side="left", padx=15, pady=10)
        
        self.p_desc_entry = ctk.CTkEntry(form_f, placeholder_text="Description courte", width=300)
        self.p_desc_entry.pack(side="left", padx=5)
        
        ctk.CTkButton(form_f, text="+ Créer Projet", width=120, command=self._ui_create_project).pack(side="right", padx=15)

        self.proj_scroll = ctk.CTkScrollableFrame(self.tab_projects, fg_color="transparent")
        self.proj_scroll.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        self.refresh_projects()

    def _ui_create_project(self):
        n = self.p_name_entry.get()
        d = self.p_desc_entry.get()
        if n:
            self.db.add_project(n, d)
            self.p_name_entry.delete(0, 'end')
            self.p_desc_entry.delete(0, 'end')
            self.refresh_projects()

    def refresh_projects(self):
        for widget in self.proj_scroll.winfo_children():
            widget.destroy()
            
        projects = self.db.get_projects()
        if not projects:
            ctk.CTkLabel(self.proj_scroll, text="Aucun projet en cours. 🛠️", text_color="gray").pack(pady=50)
            return

        for p in projects:
            p_id, name, desc, stat, start = p
            card = ctk.CTkFrame(self.proj_scroll, fg_color="#242424", border_width=1, border_color="#333333")
            card.pack(fill="x", pady=10, padx=10)
            
            p_header = ctk.CTkFrame(card, fg_color="#2a2a2a", height=40)
            p_header.pack(fill="x")
            
            ctk.CTkLabel(p_header, text=f"🚀 {name}", font=ctk.CTkFont(size=16, weight="bold")).pack(side="left", padx=15, pady=10)
            ctk.CTkButton(p_header, text="Supprimer Projet", width=100, height=24, fg_color="#aa3333",
                         command=lambda i=p_id: self._delete_project(i)).pack(side="right", padx=10)

            ctk.CTkLabel(card, text=desc if desc else "Pas de description.", text_color="gray", 
                        font=ctk.CTkFont(size=12, slant="italic")).pack(anchor="w", padx=20, pady=(5, 10))

            # Add Task to this project
            task_add_f = ctk.CTkFrame(card, fg_color="transparent")
            task_add_f.pack(fill="x", padx=20, pady=5)
            
            t_entry = ctk.CTkEntry(task_add_f, placeholder_text="Nouvelle étape...", height=25, font=ctk.CTkFont(size=12))
            t_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
            ctk.CTkButton(task_add_f, text="+ Étape", width=60, height=25, 
                         command=lambda e=t_entry, pid=p_id: self._ui_add_project_task(e, pid)).pack(side="right")

            # Tasks list
            tasks = self.db.get_project_tasks(p_id)
            for t in tasks:
                t_id, t_text, t_stat, t_prio, t_dl = t
                t_f = ctk.CTkFrame(card, fg_color="transparent")
                t_f.pack(fill="x", padx=40, pady=4)
                
                check_char = "☑️" if t_stat == 'Fait' else "▫️"
                lbl_color = "gray" if t_stat == 'Fait' else "white"
                
                t_lbl = ctk.CTkLabel(t_f, text=f"{check_char} {t_text}", text_color=lbl_color, font=ctk.CTkFont(size=13))
                t_lbl.pack(side="left")
                
                if t_stat != 'Fait':
                    ctk.CTkButton(t_f, text="✓", width=30, height=20, fg_color="#1f538d",
                                 command=lambda tid=t_id: self._mark_task_done(tid, "project")).pack(side="right")

    def _ui_add_project_task(self, entry_widget, project_id):
        txt = entry_widget.get()
        if txt:
            self.db.add_task(txt, project_id=project_id)
            entry_widget.delete(0, 'end')
            self.refresh_projects()

    def _delete_project(self, p_id):
        self.db.delete_project(p_id)
        self.refresh_projects()

    # --- TASKS TAB ---
    def _setup_tasks_ui(self):
        self.tab_tasks.grid_columnconfigure(0, weight=1)
        self.tab_tasks.grid_rowconfigure(1, weight=1)
        
        # Quick Add Task
        form_f = ctk.CTkFrame(self.tab_tasks, fg_color="#1a1a1a", corner_radius=10)
        form_f.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        
        self.todo_entry = ctk.CTkEntry(form_f, placeholder_text="Tâche rapide à faire...", width=400)
        self.todo_entry.pack(side="left", padx=15, pady=10)
        
        ctk.CTkButton(form_f, text="+ Ajouter", width=100, command=self._ui_add_todo).pack(side="right", padx=15)

        self.task_scroll = ctk.CTkScrollableFrame(self.tab_tasks, fg_color="transparent")
        self.task_scroll.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        self.refresh_tasks()

    def _ui_add_todo(self):
        t = self.todo_entry.get()
        if t:
            self.db.add_task(t) # Independent task
            self.todo_entry.delete(0, 'end')
            self.refresh_tasks()

    def refresh_tasks(self):
        for widget in self.task_scroll.winfo_children():
            widget.destroy()
            
        tasks = self.db.get_pending_tasks(limit=50)
        if not tasks:
            ctk.CTkLabel(self.task_scroll, text="Tout est fait ! Profitez de votre temps libre. 🧘", text_color="gray").pack(pady=50)
            return

        for t in tasks:
            tid, txt, prio, dl, pid = t
            # Skip tasks that belong to projects (they are shown in the Project tab)
            if pid: continue

            card = ctk.CTkFrame(self.task_scroll, fg_color="#242424", border_width=1, border_color="#333333")
            card.pack(fill="x", pady=4, padx=10)
            
            ctk.CTkLabel(card, text=f"#{tid}", text_color="gray", font=ctk.CTkFont(size=10)).pack(side="left", padx=(10, 5))
            ctk.CTkLabel(card, text=txt, font=ctk.CTkFont(size=14)).pack(side="left", padx=10, pady=10)
            
            ctk.CTkButton(card, text="Terminer", width=80, fg_color="#1f538d",
                         command=lambda i=tid: self._mark_task_done(i, "todo")).pack(side="right", padx=15)

    def _mark_task_done(self, tid, from_tab):
        self.db.update_task_status(tid, 'Fait')
        if from_tab == "project":
            self.refresh_projects()
        else:
            self.refresh_tasks()
        # Also refresh projects if a task was done there
        if from_tab == "todo":
            self._force_refresh_all()

    def _force_refresh_all(self):
        self.refresh_homework()
        self.refresh_projects()
        self.refresh_tasks()
