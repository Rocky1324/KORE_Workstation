import customtkinter as ctk
import json

class DraggableWidget(ctk.CTkFrame):
    def __init__(self, master, widget_id, db_manager, default_x=10, default_y=10, default_width=300, default_height=200, **kwargs):
        super().__init__(master, corner_radius=15, border_width=1, border_color="#333333", **kwargs)
        self.widget_id = widget_id
        self.db = db_manager
        
        # Load saved position and size or use default
        saved_pos_str = self.db.get_setting(f"widget_pos_{self.widget_id}")
        if saved_pos_str:
            try:
                pos = json.loads(saved_pos_str)
                self.x = pos.get('x', default_x)
                self.y = pos.get('y', default_y)
                self.width = max(150, pos.get('w', default_width))
                self.height = max(100, pos.get('h', default_height))
            except:
                self.x = default_x
                self.y = default_y
                self.width = default_width
                self.height = default_height
        else:
            self.x = default_x
            self.y = default_y
            self.width = default_width
            self.height = default_height

        self.configure(width=self.width, height=self.height)
        self.grid_propagate(False)
        self.pack_propagate(False)

        # Drag State
        self._drag_start_x = 0
        self._drag_start_y = 0
        
        # Resize State
        self._resize_start_x = 0
        self._resize_start_y = 0
        self._start_width = 0
        self._start_height = 0

        self.place(x=self.x, y=self.y)

        # Header for dragging
        self.header = ctk.CTkFrame(self, fg_color="#1E1E1E", height=30, corner_radius=15)
        self.header.pack(fill="x", side="top", padx=2, pady=2)
        self.header.pack_propagate(False)
        
        self.title_lbl = ctk.CTkLabel(self.header, text=widget_id.upper(), font=ctk.CTkFont(size=12, weight="bold"), text_color="#aaaaaa")
        self.title_lbl.pack(side="left", padx=10)

        # Content Frame
        self.content = ctk.CTkFrame(self, fg_color="transparent")
        self.content.pack(fill="both", expand=True, padx=5, pady=(5, 15)) # Give some bottom padding for the resize grip

        # Resize grip in the bottom right corner
        self.resize_grip = ctk.CTkFrame(self, width=15, height=15, fg_color="transparent", cursor="size_nw_se")
        self.resize_grip.place(relx=1.0, rely=1.0, anchor="se")
        
        # Draw a small icon for the resize grip
        grip_lbl = ctk.CTkLabel(self.resize_grip, text="↘", font=ctk.CTkFont(size=12, weight="bold"), text_color="#555555")
        grip_lbl.pack(fill="both", expand=True)

        # Bind events to the header and the widget background for dragging
        for widget in (self.header, self.title_lbl):
            widget.bind("<Button-1>", self.on_drag_start)
            widget.bind("<B1-Motion>", self.on_drag_motion)
            widget.bind("<ButtonRelease-1>", self.on_save_state)
            
        # Also allow clicking the body to bring to front without dragging
        self.bind("<Button-1>", lambda e: self.lift())

        # Bind events for resizing
        for widget in (self.resize_grip, grip_lbl):
            widget.bind("<Button-1>", self.on_resize_start)
            widget.bind("<B1-Motion>", self.on_resize_motion)
            widget.bind("<ButtonRelease-1>", self.on_save_state)

    def on_drag_start(self, event):
        self.lift() # Bring to front
        self._drag_start_x = event.x
        self._drag_start_y = event.y

    def on_drag_motion(self, event):
        # Calculate new coordinates
        dx = event.x - self._drag_start_x
        dy = event.y - self._drag_start_y
        
        self.x = self.x + dx
        self.y = self.y + dy
        
        # Prevent moving completely out of bounds (rough bounds)
        parent_w = self.master.winfo_width()
        parent_h = self.master.winfo_height()
        # Fallbacks in case window isn't fully drawn yet
        if parent_w <= 1: parent_w = 1000
        if parent_h <= 1: parent_h = 700
            
        self.x = max(0, min(self.x, parent_w - 50))
        self.y = max(0, min(self.y, parent_h - 50))

        self.place(x=self.x, y=self.y)

    def on_resize_start(self, event):
        self.lift()
        self._resize_start_x = event.x_root
        self._resize_start_y = event.y_root
        self._start_width = self.width
        self._start_height = self.height

    def on_resize_motion(self, event):
        dx = event.x_root - self._resize_start_x
        dy = event.y_root - self._resize_start_y
        
        self.width = max(150, self._start_width + dx)
        self.height = max(100, self._start_height + dy)
        
        self.configure(width=self.width, height=self.height)

    def on_save_state(self, event):
        # Enforce grid snapping for position
        snap = 20
        self.x = round(self.x / snap) * snap
        self.y = round(self.y / snap) * snap
        self.place(x=self.x, y=self.y)
        
        # Save new position and size to DB
        pos_str = json.dumps({'x': self.x, 'y': self.y, 'w': self.width, 'h': self.height})
        self.db.set_setting(f"widget_pos_{self.widget_id}", pos_str)
