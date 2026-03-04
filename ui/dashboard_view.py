import customtkinter as ctk
from database.db_manager import DBManager
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime, timedelta
import time

class DashboardView(ctk.CTkScrollableFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.db = DBManager()
        
        # Performance Cache
        self._data_cache = None
        self._last_refresh = 0
        self._cache_duration = 300 # 5 minutes
        
        # Persistence for Matplotlib
        self.fig = None
        self.ax = None
        self.canvas = None
        self.bars = None
        
        # Persistent UI References
        self.kpi_labels = {} # {title: label_widget}
        
        # Grid Layout
        self.grid_columnconfigure(0, weight=3) # Chart area
        self.grid_columnconfigure(1, weight=2) # Quick Tasks area
        
        # --- Row 0: KPI Header ---
        self.stats_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.stats_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 20), padx=10)
        self.stats_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

        # --- Row 1: Chart & Preview ---
        self.chart_frame = ctk.CTkFrame(self, fg_color="#121212", corner_radius=15, border_width=1, border_color="#333333")
        self.chart_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        
        self.tasks_preview_frame = ctk.CTkFrame(self, fg_color="#121212", corner_radius=15, border_width=1, border_color="#333333")
        self.tasks_preview_frame.grid(row=1, column=1, sticky="nsew", padx=10, pady=5)
        
        # --- Row 2: Homework Urgency ---
        self.hw_frame = ctk.CTkFrame(self, fg_color="#121212", corner_radius=15, border_width=1, border_color="#333333")
        self.hw_frame.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(15, 20), padx=10)
        
        # Initial Build
        self._init_ui_structure()
        self.refresh_dashboard()

    def _init_ui_structure(self):
        """Initializes empty UI components to be updated later."""
        # 1. KPI Cards
        for i, (title, icon, color) in enumerate([
            ("CARTES DUES", "🃏", "#ff4444"),
            ("STREAK ACTIVÉ", "🔥", "#ff9500"),
            ("DERNIER LOG", "📔", "#4cd964"),
            ("SYNC STATUS", "🔄", "#5856d6")
        ]):
            card = ctk.CTkFrame(self.stats_frame, fg_color="#1e1e1e", corner_radius=15, border_width=1, border_color="#333333")
            card.grid(row=0, column=i, sticky="nsew", padx=10, pady=5)
            header_f = ctk.CTkFrame(card, fg_color="transparent")
            header_f.pack(fill="x", padx=15, pady=(15, 0))
            ctk.CTkLabel(header_f, text=icon, font=ctk.CTkFont(size=20)).pack(side="left")
            ctk.CTkLabel(header_f, text=title, text_color="#888888", font=ctk.CTkFont(size=12, weight="bold")).pack(side="left", padx=10)
            
            val_lbl = ctk.CTkLabel(card, text="--", text_color=color, font=ctk.CTkFont(size=32, weight="bold"))
            val_lbl.pack(pady=(5, 15), padx=15, anchor="w")
            self.kpi_labels[title] = val_lbl

        # 2. Matplotlib Figure (Two Charts)
        plt.style.use('dark_background')
        self.fig, (self.ax1, self.ax2) = plt.subplots(1, 2, figsize=(8, 2.5), dpi=100)
        self.fig.patch.set_facecolor('#0b0b0b')
        
        for ax in (self.ax1, self.ax2):
            ax.set_facecolor('#0b0b0b')
            ax.tick_params(axis='both', colors='#666666', labelsize=8)
            for spine in ['top', 'right']: ax.spines[spine].set_visible(False)
            ax.set_yticks([])
            
        self.ax1.set_title("TEMPS DE FOCUS (H)", color='#888888', fontdict={'fontsize': 10, 'weight': 'bold'}, pad=10)
        self.ax2.set_title("ACTIVITÉ (Tâches + SRS)", color='#888888', fontdict={'fontsize': 10, 'weight': 'bold'}, pad=10)
        
        self.fig.tight_layout()

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.chart_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

    def refresh_dashboard(self, force=False):
        """Optimized refresh using batch SQL, caching and incremental plot updates."""
        now = time.time()
        if not force and self._data_cache and (now - self._last_refresh < self._cache_duration):
            return # Use existing UI
            
        # 1. Batch SQL Query
        data = self.db.get_dashboard_data()
        
        # 2. Update KPI Labels
        self.kpi_labels["CARTES DUES"].configure(text=str(data["due_cards"]))
        self.kpi_labels["STREAK ACTIVÉ"].configure(text=f"{data['streak']} j")
        
        log_title = data["latest_log"]
        if len(log_title) > 15: log_title = log_title[:12] + "..."
        self.kpi_labels["DERNIER LOG"].configure(text=log_title)
        
        # Git status is now part of the batched data
        self.kpi_labels["SYNC STATUS"].configure(text=data["sync_status"])

        # 3. Quick Update Matplotlib
        today = datetime.now()
        last_7_days = [(today - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(6, -1, -1)]
        dates = [d[-5:] for d in last_7_days] 
        
        # Data extraction
        sessions_counts = [data["sessions"].get(d, 0) for d in last_7_days]
        tasks_counts = [data["completed_tasks"].get(d, 0) for d in last_7_days]
        pomo_minutes = [data["pomodoro"].get(d, 0) for d in last_7_days]
        pomo_hours = [round(m / 60.0, 1) for m in pomo_minutes]
        
        # Total activity (Revisions + Tasks)
        total_activity = [s + t for s, t in zip(sessions_counts, tasks_counts)]

        # Chart 1: Pomodoro Time
        self.ax1.clear()
        self.ax1.bar(dates, pomo_hours, color='#ff3b30', edgecolor='#cc3333', linewidth=1, alpha=0.8)
        self.ax1.set_title("TEMPS DE FOCUS (Heures)", color='#888888', fontdict={'fontsize': 10, 'weight': 'bold'}, pad=10)
        
        # Chart 2: Activity (Stacked: Tasks bottom, SRS top)
        self.ax2.clear()
        self.ax2.bar(dates, tasks_counts, color='#34c759', label='Tâches', edgecolor='#2db34a', linewidth=1, alpha=0.8)
        self.ax2.bar(dates, sessions_counts, bottom=tasks_counts, color='#1f538d', label='SRS', edgecolor='#2a6ab3', linewidth=1, alpha=0.8)
        self.ax2.set_title("PRODUCTIVITÉ (Tâches + SRS)", color='#888888', fontdict={'fontsize': 10, 'weight': 'bold'}, pad=10)
        self.ax2.legend(loc='upper left', fontsize=8, frameon=False, labelcolor='#888888')

        for ax in (self.ax1, self.ax2):
            ax.tick_params(axis='both', colors='#666666', labelsize=8)
            for spine in ['top', 'right']: ax.spines[spine].set_visible(False)
            ax.set_yticks([])

        self.fig.tight_layout()
        self.canvas.draw()

        # 4. Update Tasks Preview (Destroy/Rebuild is fine for small lists)
        for widget in self.tasks_preview_frame.winfo_children(): widget.destroy()
        ctk.CTkLabel(self.tasks_preview_frame, text="✅ TÂCHES PRIORITAIRES", 
                    font=ctk.CTkFont(size=14, weight="bold"), text_color="#1f538d").pack(pady=(15, 10))
        
        if not data["tasks"]:
            ctk.CTkLabel(self.tasks_preview_frame, text="Zéro tâches ! Zen. 🧘", text_color="gray").pack(pady=20)
        else:
            for t_text in data["tasks"]:
                t_f = ctk.CTkFrame(self.tasks_preview_frame, fg_color="transparent")
                t_f.pack(fill="x", padx=15, pady=2)
                display_text = t_text if len(t_text) < 25 else t_text[:22]+"..."
                ctk.CTkLabel(t_f, text=f"• {display_text}", font=ctk.CTkFont(size=12)).pack(side="left")

        # 5. Update Homework Urgency
        for widget in self.hw_frame.winfo_children(): widget.destroy()
        header_f = ctk.CTkFrame(self.hw_frame, fg_color="transparent")
        header_f.pack(fill="x", pady=(15, 5))
        ctk.CTkLabel(header_f, text="🚨 RÉCAPITULATIF DES ÉCHÉANCES", 
                    font=ctk.CTkFont(size=14, weight="bold"), text_color="#cc3333").pack(side="left", padx=20)
        
        if not data["homework"]:
            ctk.CTkLabel(self.hw_frame, text="Aucune échéance critique. ✨", 
                        text_color="#666666", font=ctk.CTkFont(size=13, slant="italic")).pack(pady=20)
        else:
            for hw in data["homework"]:
                # hw: (subject, title, deadline)
                sub, title, dl = hw
                dl_date = datetime.strptime(dl, "%Y-%m-%d")
                days_left = (dl_date - datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)).days
                color = "#ff4444" if days_left <= 2 else "#ffffff"
                
                f = ctk.CTkFrame(self.hw_frame, fg_color="#1e1e1e", height=40, corner_radius=8)
                f.pack(fill="x", pady=2, padx=20)
                ctk.CTkLabel(f, text=f"{sub.upper()} : {title}", text_color=color, font=ctk.CTkFont(size=11, weight="bold")).pack(side="left", padx=15)
                ctk.CTkLabel(f, text=f"J-{days_left}", text_color=color).pack(side="right", padx=15)

        # Update cache state
        self._data_cache = data
        self._last_refresh = now
