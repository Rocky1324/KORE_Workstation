import customtkinter as ctk
from database.db_manager import DBManager
from ui.draggable_widget import DraggableWidget
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime, timedelta
import time
import json
from core.theme_manager import theme_manager

class DashboardView(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.db = DBManager()
        self.theme = theme_manager
        
        # Performance Cache
        self._data_cache = None
        self._last_refresh = 0
        self._cache_duration = 300 # 5 minutes
        
        self.available_widgets = {
            "kpis": "Statistiques (KPIs)",
            "charts": "Graphiques d'Activité",
            "tasks": "Tâches Prioritaires",
            "homework": "Échéances (Devoirs)",
            "quick_log": "Saisie Rapide Journal",
            "timer": "Mini Timer Pomodoro"
        }
        
        self.widget_instances = {}
        self.kpi_labels = {}
        
        # Toolbar for Dashboard
        self.toolbar = ctk.CTkFrame(self, height=40, fg_color="transparent")
        self.toolbar.pack(fill="x", padx=10, pady=(10, 0))
        
        self.title_lbl = ctk.CTkLabel(self.toolbar, text="DASHBOARD MODULAIRE", font=ctk.CTkFont(size=16, weight="bold"), text_color=self.theme.get_color("text_secondary"))
        self.title_lbl.pack(side="left", padx=10)
        
        self.btn_manage = ctk.CTkButton(self.toolbar, text="⚙️ Gérer les Widgets", width=120, height=28,
                                        fg_color=self.theme.get_color("card"), text_color=self.theme.get_color("text_primary"),
                                        hover_color=self.theme.get_color("bg_secondary"), command=self._show_widget_manager)
        self.btn_manage.pack(side="right", padx=10)
        
        # Absolute Canvas Area
        self.canvas_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.canvas_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Initial Build
        self._load_active_widgets()

    def _load_active_widgets(self):
        # Clear existing
        for w_id, w_inst in self.widget_instances.items():
            w_inst.destroy()
        self.widget_instances.clear()
        
        saved = self.db.get_setting("active_dashboard_widgets")
        if saved:
            try:
                self.active_keys = json.loads(saved)
            except:
                self.active_keys = ["kpis", "charts", "tasks", "homework"]
        else:
            self.active_keys = ["kpis", "charts", "tasks", "homework"]
            
        self._init_ui_structure()
        self.refresh_dashboard(force=True)

    def _show_widget_manager(self):
        popup = ctk.CTkToplevel(self)
        popup.title("Gestion des Widgets")
        popup.geometry("300x400")
        popup.attributes("-topmost", True)
        
        ctk.CTkLabel(popup, text="Widgets Actifs", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=10)
        
        vars_dict = {}
        for w_id, w_name in self.available_widgets.items():
            var = ctk.BooleanVar(value=(w_id in self.active_keys))
            vars_dict[w_id] = var
            chk = ctk.CTkCheckBox(popup, text=w_name, variable=var, fg_color=self.theme.get_color("fg_button"))
            chk.pack(anchor="w", padx=40, pady=5)
            
        def save():
            new_active = [w_id for w_id, var in vars_dict.items() if var.get()]
            self.db.set_setting("active_dashboard_widgets", json.dumps(new_active))
            popup.destroy()
            self._load_active_widgets()
            
        ctk.CTkButton(popup, text="Sauvegarder", command=save, fg_color=self.theme.get_color("fg_button_success")).pack(pady=20)

    def _init_ui_structure(self):
        """Builds only the active widgets."""
        if "kpis" in self.active_keys:
            w = DraggableWidget(self.canvas_frame, "kpis", self.db, 10, 10, 600, 120)
            self.widget_instances["kpis"] = w
            f = ctk.CTkFrame(w.content, fg_color="transparent")
            f.pack(fill="both", expand=True)
            f.grid_columnconfigure((0, 1, 2, 3), weight=1)
            for i, (title, icon, color) in enumerate([("CARTES DUES", "🃏", "#ff4444"), ("STREAK ACTIVÉ", "🔥", "#ff9500"), ("DERNIER LOG", "📔", "#4cd964"), ("SYNC STATUS", "🔄", "#5856d6")]):
                card = ctk.CTkFrame(f, fg_color=self.theme.get_color("card"), corner_radius=10)
                card.grid(row=0, column=i, sticky="nsew", padx=5, pady=5)
                header_f = ctk.CTkFrame(card, fg_color="transparent")
                header_f.pack(fill="x", padx=10, pady=(10, 0))
                ctk.CTkLabel(header_f, text=icon, font=ctk.CTkFont(size=14)).pack(side="left")
                ctk.CTkLabel(header_f, text=title, text_color=self.theme.get_color("text_secondary"), font=ctk.CTkFont(size=10, weight="bold")).pack(side="left", padx=5)
                val_lbl = ctk.CTkLabel(card, text="--", text_color=color, font=ctk.CTkFont(size=24, weight="bold"))
                val_lbl.pack(pady=(0, 10), padx=10, anchor="w")
                self.kpi_labels[title] = val_lbl

        if "charts" in self.active_keys:
            w = DraggableWidget(self.canvas_frame, "charts", self.db, 10, 140, 450, 250)
            self.widget_instances["charts"] = w
            plt.style.use('dark_background')
            self.fig, (self.ax1, self.ax2) = plt.subplots(1, 2, figsize=(4.5, 2.0), dpi=100)
            self.fig.patch.set_facecolor(self.theme.get_color("card"))
            for ax in (self.ax1, self.ax2):
                ax.set_facecolor(self.theme.get_color("card"))
                ax.tick_params(axis='both', colors=self.theme.get_color("text_secondary"), labelsize=7)
                for spine in ['top', 'right']: ax.spines[spine].set_visible(False)
                ax.set_yticks([])
            self.canvas = FigureCanvasTkAgg(self.fig, master=w.content)
            self.canvas.get_tk_widget().pack(fill="both", expand=True)

        if "tasks" in self.active_keys:
            self.widget_instances["tasks"] = DraggableWidget(self.canvas_frame, "tasks", self.db, 480, 140, 250, 250)

        if "homework" in self.active_keys:
            self.widget_instances["homework"] = DraggableWidget(self.canvas_frame, "homework", self.db, 10, 410, 720, 150)

        if "quick_log" in self.active_keys:
            w = DraggableWidget(self.canvas_frame, "quick_log", self.db, 630, 10, 250, 120)
            self.widget_instances["quick_log"] = w
            self.ql_entry = ctk.CTkEntry(w.content, placeholder_text="Note rapide...")
            self.ql_entry.pack(fill="x", padx=10, pady=(10, 5))
            def save_ql():
                txt = self.ql_entry.get().strip()
                if txt:
                    self.db.add_journal_entry("Quick Log", txt, "quick-log")
                    self.ql_entry.delete(0, 'end')
                    # Update KPI if present
                    self.refresh_dashboard(force=True)
            ctk.CTkButton(w.content, text="Enregistrer", height=24, command=save_ql, fg_color=self.theme.get_color("fg_button")).pack(pady=5, padx=10, fill="x")

        if "timer" in self.active_keys:
            w = DraggableWidget(self.canvas_frame, "timer", self.db, 750, 140, 200, 150)
            self.widget_instances["timer"] = w
            
            # Simple UI for Timer
            self.timer_lbl = ctk.CTkLabel(w.content, text="25:00", font=ctk.CTkFont(size=36, weight="bold"), text_color=self.theme.get_color("text_primary"))
            self.timer_lbl.pack(pady=(10, 0))
            self.timer_running = False
            self.timer_seconds = 25 * 60
            
            def toggle_timer():
                self.timer_running = not self.timer_running
                if self.timer_running:
                    btn_timer.configure(text="Pause", fg_color=self.theme.get_color("fg_button_danger"))
                    self._tick_timer()
                else:
                    btn_timer.configure(text="Start", fg_color=self.theme.get_color("fg_button_success"))
                    
            btn_timer = ctk.CTkButton(w.content, text="Start", width=80, height=24, command=toggle_timer, fg_color=self.theme.get_color("fg_button_success"))
            btn_timer.pack(pady=10)

    def _tick_timer(self):
        if self.timer_running and self.timer_seconds > 0:
            self.timer_seconds -= 1
            m, s = divmod(self.timer_seconds, 60)
            if hasattr(self, 'timer_lbl') and self.timer_lbl.winfo_exists():
                self.timer_lbl.configure(text=f"{m:02d}:{s:02d}")
                self.after(1000, self._tick_timer)
        elif self.timer_seconds <= 0:
            self.timer_running = False
            self.timer_seconds = 25 * 60
            if hasattr(self, 'timer_lbl') and self.timer_lbl.winfo_exists():
                self.timer_lbl.configure(text="25:00")
            self.db.log_pomodoro_session(25) # Log it
            self.refresh_dashboard(force=True)

    def refresh_dashboard(self, force=False):
        now = time.time()
        if not force and self._data_cache and (now - self._last_refresh < self._cache_duration):
            return 
            
        data = self.db.get_dashboard_data()
        
        if "kpis" in self.active_keys:
            self.kpi_labels["CARTES DUES"].configure(text=str(data["due_cards"]))
            self.kpi_labels["STREAK ACTIVÉ"].configure(text=f"{data['streak']} j")
            log_title = data["latest_log"]
            if len(log_title) > 15: log_title = log_title[:12] + "..."
            self.kpi_labels["DERNIER LOG"].configure(text=log_title)
            self.kpi_labels["SYNC STATUS"].configure(text=data["sync_status"])

        if "charts" in self.active_keys:
            today = datetime.now()
            last_7_days = [(today - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(6, -1, -1)]
            dates = [d[-5:] for d in last_7_days] 
            sessions_counts = [data["sessions"].get(d, 0) for d in last_7_days]
            tasks_counts = [data["completed_tasks"].get(d, 0) for d in last_7_days]
            pomo_hours = [round(data["pomodoro"].get(d, 0) / 60.0, 1) for d in last_7_days]
            
            self.ax1.clear()
            self.ax1.bar(dates, pomo_hours, color=self.theme.get_color("fg_button_danger"), alpha=0.8)
            self.ax1.set_title("FOCUS (H)", color=self.theme.get_color("text_secondary"), fontdict={'fontsize': 8, 'weight': 'bold'}, pad=5)
            
            self.ax2.clear()
            self.ax2.bar(dates, tasks_counts, color=self.theme.get_color("fg_button_success"), label='Tâches', alpha=0.8)
            self.ax2.bar(dates, sessions_counts, bottom=tasks_counts, color=self.theme.get_color("fg_button"), label='SRS', alpha=0.8)
            self.ax2.set_title("ACTIVITÉ", color=self.theme.get_color("text_secondary"), fontdict={'fontsize': 8, 'weight': 'bold'}, pad=5)
            self.ax2.legend(loc='upper left', fontsize=7, frameon=False, labelcolor=self.theme.get_color("text_secondary"))

            for ax in (self.ax1, self.ax2):
                ax.tick_params(axis='both', colors=self.theme.get_color("text_secondary"), labelsize=7)
                for spine in ['top', 'right']: ax.spines[spine].set_visible(False)
                ax.set_yticks([])

            self.fig.tight_layout()
            self.canvas.draw()

        if "tasks" in self.active_keys:
            w = self.widget_instances["tasks"]
            for widget in w.content.winfo_children(): widget.destroy()
            if not data["tasks"]:
                ctk.CTkLabel(w.content, text="Zéro tâches ! Zen. 🧘", text_color="gray").pack(pady=20)
            else:
                for t_text in data["tasks"]:
                    t_f = ctk.CTkFrame(w.content, fg_color="transparent")
                    t_f.pack(fill="x", padx=5, pady=2)
                    display_text = t_text if len(t_text) < 25 else t_text[:22]+"..."
                    ctk.CTkLabel(t_f, text=f"• {display_text}", font=ctk.CTkFont(size=12)).pack(side="left")

        if "homework" in self.active_keys:
            w = self.widget_instances["homework"]
            for widget in w.content.winfo_children(): widget.destroy()
            if not data["homework"]:
                ctk.CTkLabel(w.content, text="Aucune échéance critique. ✨", text_color=self.theme.get_color("text_secondary"), font=ctk.CTkFont(size=13, slant="italic")).pack(pady=20)
            else:
                for hw in data["homework"]:
                    sub, title, dl = hw
                    dl_date = datetime.strptime(dl, "%Y-%m-%d")
                    days_left = (dl_date - datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)).days
                    color = self.theme.get_color("fg_button_danger") if days_left <= 2 else self.theme.get_color("text_primary")
                    f = ctk.CTkFrame(w.content, fg_color=self.theme.get_color("card"), height=30, corner_radius=8)
                    f.pack(fill="x", pady=2, padx=10)
                    ctk.CTkLabel(f, text=f"{sub.upper()} : {title}", text_color=color, font=ctk.CTkFont(size=11, weight="bold")).pack(side="left", padx=10)
                    ctk.CTkLabel(f, text=f"J-{days_left}", text_color=color).pack(side="right", padx=10)

        self._data_cache = data
        self._last_refresh = now
