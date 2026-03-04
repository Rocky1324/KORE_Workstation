import customtkinter as ctk
import time
from database.db_manager import DBManager

class PomodoroView(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.db = DBManager()
        
        # State Machine Configurations
        self.WORK_TIME = 25 * 60
        self.SHORT_BREAK = 5 * 60
        self.LONG_BREAK = 15 * 60
        
        self.is_running = False
        self.cycles = 0           # How many focus sessions completed
        self.current_state = "FOCUS" # FOCUS, SHORT_BREAK, LONG_BREAK
        
        self.time_left = self.WORK_TIME
        self.after_id = None
        
        # Grid Layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure((0, 1, 2, 3), weight=1)

        # Session Tracker
        self.cycle_label = ctk.CTkLabel(self, text="Session: 1/4", font=ctk.CTkFont(size=18, weight="bold"), text_color="#A0A0A0")
        self.cycle_label.grid(row=0, column=0, pady=(20, 0))

        # State Display
        self.state_label = ctk.CTkLabel(self, text="🎯 FOCUS", font=ctk.CTkFont(size=24, weight="bold"), text_color="#ff3b30")
        self.state_label.grid(row=1, column=0, pady=(0, 0))

        # Timer Display
        self.timer_label = ctk.CTkLabel(self, text=self._format_time(self.time_left), font=ctk.CTkFont(family="Consolas", size=90, weight="bold"), text_color="#ff3b30")
        self.timer_label.grid(row=2, column=0, pady=(10, 20))
        
        # Controls setup
        self.controls_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.controls_frame.grid(row=3, column=0, pady=20)
        
        self.start_btn = ctk.CTkButton(self.controls_frame, text="Démarrer", font=ctk.CTkFont(size=18), width=150, height=50, command=self.toggle_timer)
        self.start_btn.grid(row=0, column=0, padx=10)
        
        self.skip_btn = ctk.CTkButton(self.controls_frame, text="Skip", font=ctk.CTkFont(size=18), width=100, height=50, fg_color="#555555", hover_color="#777777", command=self._trigger_end_phase)
        self.skip_btn.grid(row=0, column=1, padx=10)
        
        self.reset_btn = ctk.CTkButton(self.controls_frame, text="Reset", font=ctk.CTkFont(size=18), width=100, height=50, fg_color="#B71C1C", hover_color="#D32F2F", command=self.reset_to_start)
        self.reset_btn.grid(row=0, column=2, padx=10)

        self._update_colors()

    def _format_time(self, seconds):
        mins, secs = divmod(seconds, 60)
        return f"{mins:02d}:{secs:02d}"

    def _update_colors(self):
        if self.current_state == "FOCUS":
            color = "#ff3b30"  # Red
            txt = "🎯 FOCUS"
        elif self.current_state == "SHORT_BREAK":
            color = "#34c759"  # Green
            txt = "☕ PAUSE COURTE"
        else:
            color = "#007aff"  # Blue
            txt = "🛋️ PAUSE LONGUE"
            
        self.state_label.configure(text=txt, text_color=color)
        self.timer_label.configure(text_color=color)
        self.cycle_label.configure(text=f"Session: {(self.cycles % 4) + 1}/4")

    def toggle_timer(self):
        if not self.is_running:
            self.is_running = True
            self.start_btn.configure(text="Pause", fg_color="#F57C00", hover_color="#FF9800")
            self._update_timer()
        else:
            self.is_running = False
            self.start_btn.configure(text="Reprendre", fg_color=["#3B8ED0", "#1F6AA5"], hover_color=["#36719F", "#144870"])
            if self.after_id:
                self.after_cancel(self.after_id)

    def _update_timer(self):
        if self.is_running:
            if self.time_left > 0:
                self.time_left -= 1
                self.timer_label.configure(text=self._format_time(self.time_left))
                self.after_id = self.after(1000, self._update_timer)
            else:
                self._trigger_end_phase()

    def _trigger_end_phase(self):
        self.is_running = False
        if self.after_id:
            self.after_cancel(self.after_id)
        
        self.start_btn.configure(text="Démarrer", fg_color=["#3B8ED0", "#1F6AA5"], hover_color=["#36719F", "#144870"])
        
        if self.current_state == "FOCUS":
            # Log the 25 minutes of focus
            self.db.log_pomodoro_session(25)
            self.cycles += 1
            
            # Ask for journal entry on completing a focus session
            dialog = ctk.CTkInputDialog(text="Focus terminé ! (25 min ajoutées)\nQu'as-tu appris / fait ?", title="Bilan Pomodoro")
            result = dialog.get_input()
            if result and result.strip() != "":
                self.db.add_journal_entry(title="Bilan Session Focus", content=result.strip(), keywords="pomodoro, focus")
                
            # Transition to break
            if self.cycles % 4 == 0:
                self.current_state = "LONG_BREAK"
                self.time_left = self.LONG_BREAK
            else:
                self.current_state = "SHORT_BREAK"
                self.time_left = self.SHORT_BREAK
                
        else:
            # Break is over, back to focus
            self.current_state = "FOCUS"
            self.time_left = self.WORK_TIME
            
        self.timer_label.configure(text=self._format_time(self.time_left))
        self._update_colors()

    def reset_to_start(self):
        self.is_running = False
        if self.after_id:
            self.after_cancel(self.after_id)
        self.cycles = 0
        self.current_state = "FOCUS"
        self.time_left = self.WORK_TIME
        self.timer_label.configure(text=self._format_time(self.time_left))
        self.start_btn.configure(text="Démarrer", fg_color=["#3B8ED0", "#1F6AA5"], hover_color=["#36719F", "#144870"])
        self._update_colors()

