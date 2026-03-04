import customtkinter as ctk

class DesktopWidget(ctk.CTkToplevel):
    """Base class for translucent, topmost desktop widgets."""
    
    def __init__(self, master, title="KORE Widget", size=(250, 150), **kwargs):
        super().__init__(master, **kwargs)
        self.title(title)
        self.geometry(f"{size[0]}x{size[1]}+100+100")
        
        # UI Styling: Translucent and Topmost
        self.attributes("-topmost", True)
        self.attributes("-alpha", 0.85) # Slight transparency
        
        # Remove title bar for a "widget" feel (optional, depends on OS)
        # self.overrideredirect(True) 
        
        self.configure(fg_color="#1a1a1a")
        
        self.header = ctk.CTkFrame(self, height=30, fg_color="#333333")
        self.header.pack(fill="x", side="top")
        
        self.title_lbl = ctk.CTkLabel(self.header, text=title, font=ctk.CTkFont(size=12, weight="bold"))
        self.title_lbl.pack(side="left", padx=10)
        
        self.close_btn = ctk.CTkButton(self.header, text="×", width=30, height=20, 
                                      fg_color="transparent", hover_color="#ff5555", 
                                      command=self.destroy)
        self.close_btn.pack(side="right", padx=5)

from database.db_manager import DBManager

class PomodoroWidget(DesktopWidget):
    def __init__(self, master):
        super().__init__(master, title="Focus Timer", size=(220, 140))
        self.db = DBManager()
        
        # State Machine Configurations
        self.WORK_TIME = 25 * 60
        self.SHORT_BREAK = 5 * 60
        self.LONG_BREAK = 15 * 60
        
        self.is_running = False
        self.cycles = 0
        self.current_state = "FOCUS"
        self.time_left = self.WORK_TIME
        self.after_id = None
        
        # UI
        self.state_label = ctk.CTkLabel(self, text="🎯 FOCUS", font=ctk.CTkFont(size=14, weight="bold"), text_color="#ff3b30")
        self.state_label.pack(pady=(5, 0))
        
        self.timer_label = ctk.CTkLabel(self, text="25:00", font=ctk.CTkFont(size=36, weight="bold"), text_color="#ff3b30")
        self.timer_label.pack(pady=5)
        
        # Controls
        self.ctrl_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.ctrl_frame.pack(pady=0)
        
        self.play_btn = ctk.CTkButton(self.ctrl_frame, text="▶", width=40, font=ctk.CTkFont(size=16), command=self.toggle_timer)
        self.play_btn.pack(side="left", padx=5)
        
        self.skip_btn = ctk.CTkButton(self.ctrl_frame, text="⏭", width=40, font=ctk.CTkFont(size=16), fg_color="#555", hover_color="#777", command=self._trigger_end_phase)
        self.skip_btn.pack(side="left", padx=5)
        
        self._update_colors()

    def _update_colors(self):
        if self.current_state == "FOCUS":
            color = "#ff3b30"
            txt = "🎯 FOCUS"
        elif self.current_state == "SHORT_BREAK":
            color = "#34c759"
            txt = "☕ PAUSE COURTE"
        else:
            color = "#007aff"
            txt = "🛋️ PAUSE LONG"
            
        self.state_label.configure(text=txt, text_color=color)
        self.timer_label.configure(text_color=color)
        self.title_lbl.configure(text=f"Session {self.cycles % 4 + 1}/4")

    def toggle_timer(self):
        if not self.is_running:
            self.is_running = True
            self.play_btn.configure(text="⏸", fg_color="#F57C00", hover_color="#FF9800")
            self._update_timer()
        else:
            self.is_running = False
            self.play_btn.configure(text="▶", fg_color=["#3B8ED0", "#1F6AA5"], hover_color=["#36719F", "#144870"])
            if self.after_id:
                self.after_cancel(self.after_id)

    def _update_timer(self):
        if self.is_running:
            if self.time_left > 0:
                self.time_left -= 1
                mins, secs = divmod(self.time_left, 60)
                self.timer_label.configure(text=f"{mins:02d}:{secs:02d}")
                self.after_id = self.after(1000, self._update_timer)
            else:
                self._trigger_end_phase()

    def _trigger_end_phase(self):
        self.is_running = False
        if self.after_id:
            self.after_cancel(self.after_id)
        
        self.play_btn.configure(text="▶", fg_color=["#3B8ED0", "#1F6AA5"], hover_color=["#36719F", "#144870"])
        
        if self.current_state == "FOCUS":
            self.db.log_pomodoro_session(25)
            self.cycles += 1
            
            if self.cycles % 4 == 0:
                self.current_state = "LONG_BREAK"
                self.time_left = self.LONG_BREAK
            else:
                self.current_state = "SHORT_BREAK"
                self.time_left = self.SHORT_BREAK
        else:
            self.current_state = "FOCUS"
            self.time_left = self.WORK_TIME
            
        mins, secs = divmod(self.time_left, 60)
        self.timer_label.configure(text=f"{mins:02d}:{secs:02d}")
        self._update_colors()


class ConstantsWidget(DesktopWidget):
    def __init__(self, master):
        super().__init__(master, title="Quick Constants", size=(250, 200))
        
        self.scroll = ctk.CTkScrollableFrame(self)
        self.scroll.pack(fill="both", expand=True, padx=5, pady=5)
        
        from core.physics import PhysicsEngine
        pe = PhysicsEngine()
        constants = pe.list_constants()
        
        for name in constants:
            res = pe.get_constant(name)
            btn = ctk.CTkButton(self.scroll, text=f"{name}: {res['value']:.3e}", 
                               font=ctk.CTkFont(size=11), height=25,
                               command=lambda v=res['value']: self._copy(v))
            btn.pack(fill="x", pady=2)

    def _copy(self, val):
        self.clipboard_clear()
        self.clipboard_append(str(val))

class NoteWidget(DesktopWidget):
    def __init__(self, master):
        super().__init__(master, title="Quick Note", size=(300, 250))
        self.text = ctk.CTkTextbox(self, font=ctk.CTkFont(family="Consolas", size=12))
        self.text.pack(fill="both", expand=True, padx=10, pady=10)
        self.text.insert("1.0", "Notes temporaires...")
