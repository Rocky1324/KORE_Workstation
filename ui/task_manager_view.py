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
        self.db.update_homework_status(hw_id, 'Fait')
        self.refresh_homework()

    def _delete_hw(self, hw_id):
        self.db.delete_homework(hw_id)
        self.refresh_homework()

    # --- PROJECTS TAB & KANBAN ---
    def _setup_projects_ui(self):
        self._active_project_id = None
        self._drag_data = {"id": None, "widget": None, "clone": None, "status": None}
        self.projects_map = {} # {name: id}
        
        self.tab_projects.grid_columnconfigure(0, weight=1)
        self.tab_projects.grid_rowconfigure(1, weight=1)
        
        # --- Top Bar ---
        self.p_top_bar = ctk.CTkFrame(self.tab_projects, fg_color="transparent")
        self.p_top_bar.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        
        ctk.CTkLabel(self.p_top_bar, text="Projet Actif:").pack(side="left", padx=10)
        
        self.p_combo = ctk.CTkOptionMenu(self.p_top_bar, values=["Aucun"], command=self._on_project_select)
        self.p_combo.pack(side="left", padx=10)
        
        ctk.CTkButton(self.p_top_bar, text="+ Projet", width=80, command=self._ui_create_project).pack(side="left", padx=10)
        ctk.CTkButton(self.p_top_bar, text="+ Tâche", width=80, fg_color="#1f538d", command=self._ui_add_task_to_project).pack(side="left", padx=10)
        
        ctk.CTkButton(self.p_top_bar, text="🗑️", width=40, fg_color="#dc3545", hover_color="#c82333", command=self._delete_active_project).pack(side="right", padx=10)

        # --- Kanban Board (Row 1) ---
        self.kanban_f = ctk.CTkFrame(self.tab_projects, fg_color="transparent")
        self.kanban_f.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        self.kanban_f.grid_columnconfigure((0, 1, 2), weight=1)
        self.kanban_f.grid_rowconfigure(1, weight=1)
        
        self.columns = {}
        for i, (status, col_col) in enumerate([("À faire", "#444444"), ("En cours", "#1f538d"), ("Fait", "#28a745")]):
            hdr = ctk.CTkFrame(self.kanban_f, fg_color=col_col, height=30, corner_radius=5)
            hdr.grid(row=0, column=i, sticky="ew", padx=5, pady=2)
            ctk.CTkLabel(hdr, text=status, font=ctk.CTkFont(weight="bold")).pack()
            
            scroll = ctk.CTkScrollableFrame(self.kanban_f, fg_color="#1e1e1e", corner_radius=5)
            scroll.grid(row=1, column=i, sticky="nsew", padx=5, pady=2)
            self.columns[status] = scroll
            
        self.refresh_projects()

    def _ui_create_project(self):
        dialog = ctk.CTkInputDialog(text="Nom du nouveau projet:", title="Nouveau Projet")
        name = dialog.get_input()
        if name:
            self.db.add_project(name, "")
            self.refresh_projects()
            self.p_combo.set(name)
            self._on_project_select(name)

    def _ui_add_task_to_project(self):
        if not self._active_project_id: return
        dialog = ctk.CTkInputDialog(text="Texte de la tâche:", title="Nouvelle Tâche")
        txt = dialog.get_input()
        if txt:
            self.db.add_task(txt, project_id=self._active_project_id, status="À faire")
            self._refresh_kanban()

    def _delete_active_project(self):
        if self._active_project_id:
            self.db.delete_project(self._active_project_id)
            self._active_project_id = None
            self.refresh_projects()

    def refresh_projects(self):
        projects = self.db.get_projects()
        self.projects_map = {p[1]: p[0] for p in projects}
        names = list(self.projects_map.keys())
        if not names:
            names = ["Aucun"]
            self._active_project_id = None
        
        self.p_combo.configure(values=names)
        
        if self.p_combo.get() not in names:
            self.p_combo.set(names[0])
            
        self._on_project_select(self.p_combo.get())

    def _on_project_select(self, name):
        self._active_project_id = self.projects_map.get(name)
        self._refresh_kanban()

    def _refresh_kanban(self):
        # Clear columns
        for col in self.columns.values():
            for widget in col.winfo_children():
                widget.destroy()
                
        if not self._active_project_id:
            return
            
        tasks = self.db.get_project_tasks(self._active_project_id)
        
        # tasks order: id, text, status, priority, deadline, dependency_id
        # Build map to check dependencies
        task_status_map = {t[0]: t[2] for t in tasks}
        
        for t in tasks:
            t_id, t_text, t_stat, t_prio, t_dl, dep_id = t
            if t_stat not in self.columns: t_stat = "À faire"
            
            parent_sc = self.columns[t_stat]
            
            # Check dependency lock
            locked = False
            if dep_id and task_status_map.get(dep_id, 'Fait') != 'Fait':
                locked = True
                
            card_color = "#333333" if not locked else "#2a2a2a"
            card = ctk.CTkFrame(parent_sc, fg_color=card_color, corner_radius=8, cursor="hand2")
            card.pack(fill="x", pady=5, padx=5, ipady=5)
            
            icon = "🔒 " if locked else ""
            lbl = ctk.CTkLabel(card, text=f"{icon}{t_text}", font=ctk.CTkFont(size=12, slant="italic" if locked else "roman"), text_color="gray" if locked else "white")
            lbl.pack(anchor="w", padx=10, pady=5)
            
            # Edit button
            btn_f = ctk.CTkFrame(card, fg_color="transparent", height=20)
            btn_f.pack(fill="x", padx=5)
            ctk.CTkButton(btn_f, text="⚙️", width=20, height=20, fg_color="transparent", hover_color="#555", command=lambda tid=t_id, txt=t_text, cur_dep=dep_id: self._edit_task(tid, txt, cur_dep)).pack(side="right")
            
            # Bind drag
            if not locked:
                card.bind("<ButtonPress-1>", lambda e, tid=t_id, c=card, s=t_stat, text=t_text: self._on_drag_start(e, tid, c, s, text))
                card.bind("<B1-Motion>", self._on_drag_motion)
                card.bind("<ButtonRelease-1>", self._on_drag_stop)
                lbl.bind("<ButtonPress-1>", lambda e, tid=t_id, c=card, s=t_stat, text=t_text: self._on_drag_start(e, tid, c, s, text))
                lbl.bind("<B1-Motion>", self._on_drag_motion)
                lbl.bind("<ButtonRelease-1>", self._on_drag_stop)

    def _edit_task(self, t_id, t_text, current_dep_id):
        popup = ctk.CTkToplevel(self)
        popup.title("Éditer Tâche")
        popup.geometry("300x250")
        popup.attributes("-topmost", True)
        
        ctk.CTkLabel(popup, text="Dépendant de :").pack(pady=(10, 0))
        
        tasks = self.db.get_project_tasks(self._active_project_id)
        # (id, name)
        opts = [("Aucune (0)", 0)] + [(f"{t[1][:20]} ({t[0]})", t[0]) for t in tasks if t[0] != t_id]
        opts_dict = {name: val for name, val in opts}
        
        def_val = opts[0][0]
        for name, val in opts:
            if val == current_dep_id:
                def_val = name
                break
                
        combo = ctk.CTkOptionMenu(popup, values=list(opts_dict.keys()))
        combo.set(def_val)
        combo.pack(pady=10)
        
        def save():
            dep = opts_dict[combo.get()]
            dep_id = dep if dep != 0 else None
            # Fetch current status to preserve it
            t_status = "À faire"
            for col_stat, sc in self.columns.items():
                pass # The DB will preserve it if we use update_task_detailed
            # Quick query to get status
            with self.db.get_connection() as conn:
                c = conn.cursor()
                c.execute("SELECT status FROM tasks WHERE id = ?", (t_id,))
                t_status = c.fetchone()[0]
                
            self.db.update_task_detailed(t_id, t_text, t_status, dep_id)
            popup.destroy()
            self._refresh_kanban()
            
        ctk.CTkButton(popup, text="Sauvegarder", command=save, fg_color="#1f538d").pack(pady=20)

    # --- DRAG AND DROP LOGIC ---
    def _on_drag_start(self, event, task_id, widget, status, text):
        self._drag_data["id"] = task_id
        self._drag_data["widget"] = widget
        self._drag_data["status"] = status
        
        # Determine the root window to place the clone correctly
        root = self.winfo_toplevel()
        
        # Dimensions and visual clone
        w_width = widget.winfo_width()
        w_height = widget.winfo_height()
        
        clone = ctk.CTkFrame(root, fg_color="#1f538d", corner_radius=8, width=w_width, height=w_height)
        clone.pack_propagate(False) # Prevent shrinking
        lbl = ctk.CTkLabel(clone, text=text, font=ctk.CTkFont(size=12))
        lbl.place(relx=0.5, rely=0.5, anchor="center")
        
        # Calculate cursor offset relative to the root window
        self._drag_data["offset_x"] = w_width // 2
        self._drag_data["offset_y"] = w_height // 2
        
        # Place clone centered on the mouse
        rx = event.x_root - root.winfo_rootx()
        ry = event.y_root - root.winfo_rooty()
        clone.place(x=rx - self._drag_data["offset_x"], y=ry - self._drag_data["offset_y"])
        
        self._drag_data["clone"] = clone
        
        # Lower opacity of original to show it's being moved
        widget.configure(fg_color="#1a1a1a")

    def _on_drag_motion(self, event):
        if self._drag_data["clone"]:
            root = self.winfo_toplevel()
            rx = event.x_root - root.winfo_rootx()
            ry = event.y_root - root.winfo_rooty()
            
            # Constrain to window bounds roughly
            self._drag_data["clone"].place(x=rx - self._drag_data["offset_x"], y=ry - self._drag_data["offset_y"])

    def _on_drag_stop(self, event):
        if not self._drag_data["clone"]: return
        
        self._drag_data["clone"].destroy()
        self._drag_data["clone"] = None
        
        # Restore color of original (though it will be destroyed momentarily on refresh)
        if self._drag_data["widget"].winfo_exists():
            self._drag_data["widget"].configure(fg_color="#333333")
        
        mx, my = event.x_root, event.y_root
        new_status = self._drag_data["status"]
        found = False
        
        # More robust hit testing: iterate over the columns and check absolute root bounds
        for st, col in self.columns.items():
            cx = col.winfo_rootx()
            cy = col.winfo_rooty()
            cw = col.winfo_width()
            ch = col.winfo_height()
            
            # If the mouse (mx, my) dropped within the bounding box of this scrollable column
            if cx <= mx <= cx + cw and cy <= my <= cy + ch:
                new_status = st
                found = True
                break
                
        # Fallback to X bounds if they drop slightly above/below the scroll view but within the vertical column
        if not found:
            for st, col in self.columns.items():
                cx = col.winfo_rootx()
                cw = col.winfo_width()
                if cx <= mx <= cx + cw:
                    new_status = st
                    break
                
        if new_status != self._drag_data["status"]:
            t_id = self._drag_data["id"]
            with self.db.get_connection() as conn:
                c = conn.cursor()
                c.execute("SELECT text, dependency_id FROM tasks WHERE id = ?", (t_id,))
                res = c.fetchone()
                if res:
                    t_text, t_dep = res
                    self.db.update_task_detailed(t_id, t_text, new_status, t_dep)
                    self._refresh_kanban()
                    self._force_refresh_all()


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
