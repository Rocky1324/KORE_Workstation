import customtkinter as ctk
import tkinter as tk
import math
import random
from core.graph_engine import GraphEngine

class GraphView(ctk.CTkFrame):
    def __init__(self, master, app_instance=None, **kwargs):
        super().__init__(master, **kwargs)
        self.app = app_instance
        self.engine = GraphEngine()
        
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Split screen: Left = Graph Canvas, Right = Details Panel
        self.main_split = ctk.CTkFrame(self, fg_color="transparent")
        self.main_split.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.main_split.grid_rowconfigure(0, weight=1)
        self.main_split.grid_columnconfigure(0, weight=1)
        
        # Canvas Container
        self.canvas_frame = ctk.CTkFrame(self.main_split, fg_color="#0b0b0b", corner_radius=10)
        self.canvas_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        
        self.canvas = tk.Canvas(self.canvas_frame, bg="#0b0b0b", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True, padx=2, pady=2)
        
        # Details Panel
        self.details_panel = ctk.CTkScrollableFrame(self.main_split, width=320, corner_radius=10)
        self.details_panel.grid(row=0, column=1, sticky="ns")
        
        ctk.CTkLabel(self.details_panel, text="Détails du Noeud", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=15)
        self.lbl_det_title = ctk.CTkLabel(self.details_panel, text="Sélectionnez un noeud", font=ctk.CTkFont(size=14), wraplength=280)
        self.lbl_det_title.pack(pady=10, padx=10)
        
        self.lbl_det_type = ctk.CTkLabel(self.details_panel, text="", text_color="gray")
        self.lbl_det_type.pack(pady=5)
        
        self.txt_det_desc = ctk.CTkTextbox(self.details_panel, height=200, wrap="word", font=ctk.CTkFont(size=13))
        self.txt_det_desc.pack(fill="x", padx=10, pady=10)
        self.txt_det_desc.configure(state="disabled")
        
        self.lbl_det_tags = ctk.CTkLabel(self.details_panel, text="", text_color="#0a84ff", wraplength=280)
        self.lbl_det_tags.pack(pady=10, padx=10)
        
        # Graph Controls overlaid on canvas
        self.controls = ctk.CTkFrame(self.canvas_frame, fg_color="#1a1a1a", corner_radius=8)
        self.controls.place(x=10, y=10)
        
        ctk.CTkButton(self.controls, text="🔄 Recharger", width=100, command=self._load_graph).pack(side="left", padx=5, pady=5)
        ctk.CTkButton(self.controls, text="⏸️ Pause", width=80, command=self._toggle_physics).pack(side="left", padx=5, pady=5)
        self.physics_running = True
        
        # Physics State
        self.nodes = {}
        self.edges = []
        self.selected_node = None
        self.dragged_node = None
        self.drag_offset = (0, 0)
        
        # Event bindings
        self.canvas.bind("<ButtonPress-1>", self._on_press)
        self.canvas.bind("<B1-Motion>", self._on_drag)
        self.canvas.bind("<ButtonRelease-1>", self._on_release)
        self.canvas.bind("<MouseWheel>", self._on_zoom) # Windows
        self.canvas.bind("<Button-4>", self._on_zoom) # Linux
        self.canvas.bind("<Button-5>", self._on_zoom) # Linux
        
        # Viewport params
        self.cam_x = 0
        self.cam_y = 0
        self.zoom = 1.0
        self.is_panning = False
        
        # Middle click or Right click to pan
        self.canvas.bind("<ButtonPress-2>", self._start_pan)
        self.canvas.bind("<B2-Motion>", self._do_pan)
        self.canvas.bind("<ButtonPress-3>", self._start_pan)
        self.canvas.bind("<B3-Motion>", self._do_pan)
        
        # Delay initial load to let canvas setup geometry
        self.after(200, self._load_graph)

    def _start_pan(self, event):
        self.is_panning = True
        self.pan_start_x = event.x
        self.pan_start_y = event.y

    def _do_pan(self, event):
        if self.is_panning:
            dx = event.x - self.pan_start_x
            dy = event.y - self.pan_start_y
            self.cam_x += dx / self.zoom
            self.cam_y += dy / self.zoom
            self.pan_start_x = event.x
            self.pan_start_y = event.y

    def _on_zoom(self, event):
        # Determine direction
        delta = 0
        if event.num == 5 or event.delta < 0: delta = -0.1
        if event.num == 4 or event.delta > 0: delta = 0.1
        
        # Zoom towards mouse
        px, py = event.x, event.y
        world_x = (px - self.canvas.winfo_width()/2) / self.zoom - self.cam_x
        world_y = (py - self.canvas.winfo_height()/2) / self.zoom - self.cam_y
        
        self.zoom = max(0.2, min(5.0, self.zoom + delta))
        
        self.cam_x = (px - self.canvas.winfo_width()/2) / self.zoom - world_x
        self.cam_y = (py - self.canvas.winfo_height()/2) / self.zoom - world_y

    def _w2s(self, wx, wy):
        """World to Screen coordinates"""
        w, h = self.canvas.winfo_width() / 2, self.canvas.winfo_height() / 2
        sx = (wx + self.cam_x) * self.zoom + w
        sy = (wy + self.cam_y) * self.zoom + h
        return sx, sy

    def _s2w(self, sx, sy):
        """Screen to World coordinates"""
        w, h = self.canvas.winfo_width() / 2, self.canvas.winfo_height() / 2
        wx = (sx - w) / self.zoom - self.cam_x
        wy = (sy - h) / self.zoom - self.cam_y
        return wx, wy

    def _load_graph(self):
        data = self.engine.build_graph_data()
        
        self.nodes = {}
        self.edges = data['edges']
        
        # Initialize physics properties for nodes
        w, h = self.canvas.winfo_width(), self.canvas.winfo_height()
        if w <= 1: w = 800
        if h <= 1: h = 600
        
        # Group nodes by type structure initially
        for idx, n in enumerate(data['nodes']):
            # Spawn in a random cluster near center
            n['x'] = random.uniform(-300, 300)
            n['y'] = random.uniform(-300, 300)
            n['vx'] = 0.0
            n['vy'] = 0.0
            n['fx'] = 0.0
            n['fy'] = 0.0
            radius_map = {
                "journal": 16, "project": 22, "topic": 14, "homework": 12, "tag": 8
            }
            n['r'] = radius_map.get(n['type'], 12) * min(2.0, max(0.5, n.get('mass', 1)))
            self.nodes[n['id']] = n
            
        # Center camera
        self.cam_x, self.cam_y = 0, 0
        self.zoom = 1.0
        
        if not hasattr(self, 'anim_job'):
            self.anim_job = self.after(30, self._simulation_loop)
            
        self._update_details(None)

    def _toggle_physics(self):
        self.physics_running = not self.physics_running
        self.controls.winfo_children()[1].configure(text="▶️ Reprendre" if not self.physics_running else "⏸️ Pause")

    def _simulation_loop(self):
        if self.physics_running:
            self._apply_physics()
        self._render_graph()
        self.anim_job = self.after(30, self._simulation_loop)

    def _apply_physics(self):
        # 1. Reset forces
        for nid, n in self.nodes.items():
            n['fx'] = 0
            n['fy'] = 0
            
            # Gentle gravity to center to keep things from flying away
            n['fx'] += -n['x'] * 0.01 * n['mass']
            n['fy'] += -n['y'] * 0.01 * n['mass']

        # 2. Coulomb Repulsion (N-Body)
        K_repulse = 8000.0
        node_list = list(self.nodes.values())
        for i in range(len(node_list)):
            for j in range(i+1, len(node_list)):
                n1, n2 = node_list[i], node_list[j]
                dx = n1['x'] - n2['x']
                dy = n1['y'] - n2['y']
                dist_sq = dx*dx + dy*dy
                
                if dist_sq < 0.1: # Prevent division by zero
                    dx, dy, dist_sq = random.random(), random.random(), 1.0
                    
                dist = math.sqrt(dist_sq)
                # Max repulsion distance to optimize slightly
                if dist < 600:
                    force = K_repulse * (n1['mass'] * n2['mass']) / dist_sq
                    fx = (dx / dist) * force
                    fy = (dy / dist) * force
                    
                    n1['fx'] += fx
                    n1['fy'] += fy
                    n2['fx'] -= fx
                    n2['fy'] -= fy

        # 3. Hooke Spring Attraction (Edges)
        K_spring = 0.03
        ideal_length = 80.0
        for edge in self.edges:
            n1 = self.nodes.get(edge['source'])
            n2 = self.nodes.get(edge['target'])
            if not n1 or not n2: continue
            
            dx = n2['x'] - n1['x']
            dy = n2['y'] - n1['y']
            dist = math.sqrt(dx*dx + dy*dy)
            
            if dist > 0:
                # Spring force
                force = K_spring * (dist - ideal_length) * edge.get('strength', 1.0)
                fx = (dx / dist) * force
                fy = (dy / dist) * force
                
                n1['fx'] += fx
                n1['fy'] += fy
                n2['fx'] -= fx
                n2['fy'] -= fy

        # 4. Integrate (Kinematics)
        friction = 0.85 # High friction = stable graph
        for nid, n in self.nodes.items():
            if n == self.dragged_node:
                n['vx'], n['vy'] = 0, 0
                continue
                
            n['vx'] = (n['vx'] + n['fx']/n['mass']) * friction
            n['vy'] = (n['vy'] + n['fy']/n['mass']) * friction
            
            # Speed limit
            speed = math.sqrt(n['vx']**2 + n['vy']**2)
            if speed > 20:
                n['vx'] = (n['vx'] / speed) * 20
                n['vy'] = (n['vy'] / speed) * 20
                
            n['x'] += n['vx']
            n['y'] += n['vy']

    def _render_graph(self):
        self.canvas.delete("all")
        
        # Draw edges
        for edge in self.edges:
            n1 = self.nodes.get(edge['source'])
            n2 = self.nodes.get(edge['target'])
            if n1 and n2:
                sx1, sy1 = self._w2s(n1['x'], n1['y'])
                sx2, sy2 = self._w2s(n2['x'], n2['y'])
                self.canvas.create_line(sx1, sy1, sx2, sy2, fill="#333333", width=round(2*self.zoom), tags="edge")

        # Draw nodes
        # Sort so selected node is drawn last (on top)
        draw_list = sorted(list(self.nodes.values()), key=lambda n: 1 if n == self.selected_node else 0)
        
        for n in draw_list:
            sx, sy = self._w2s(n['x'], n['y'])
            sr = n['r'] * self.zoom
            
            # Off-screen culling
            w, h = self.canvas.winfo_width(), self.canvas.winfo_height()
            if sx < -sr or sx > w + sr or sy < -sr or sy > h + sr:
                continue
            
            color = n['color']
            outline = "white" if n == self.selected_node else color
            width = 3 if n == self.selected_node else 0
            
            # Tag nodes are drawn differently (diamonds or smaller)
            if n['type'] == 'tag':
                self.canvas.create_oval(sx-sr, sy-sr, sx+sr, sy+sr, fill=color, outline=outline, width=width)
                if self.zoom > 0.6:
                    self.canvas.create_text(sx, sy-sr-10*self.zoom, text=n['label'], fill="gray", font=("Arial", max(8, int(10*self.zoom))))
            else:
                self.canvas.create_oval(sx-sr, sy-sr, sx+sr, sy+sr, fill="#1a1a1a", outline=outline, width=max(2, width))
                # Fill inner with transparent-ish color or solid
                self.canvas.create_oval(sx-sr+2, sy-sr+2, sx+sr-2, sy+sr-2, fill=color, outline="")
                
                # Truncate label if too long
                lbl = n['label']
                if len(lbl) > 15: lbl = lbl[:13] + ".."
                
                if self.zoom > 0.4:
                    self.canvas.create_text(sx, sy+sr+12*self.zoom, text=lbl, fill="white", font=("Arial", max(8, int(11*self.zoom))))
            
            # Store screen rect for picking
            n['sx'], n['sy'], n['sr'] = sx, sy, sr

    def _on_press(self, event):
        # Raycast for nodes
        hit = None
        for nid, n in reversed(list(self.nodes.items())):
            if 'sx' in n:
                dx = event.x - n['sx']
                dy = event.y - n['sy']
                if dx*dx + dy*dy <= n['sr']*n['sr']:
                    hit = n
                    break
        
        if hit:
            self.dragged_node = hit
            self.selected_node = hit
            wx, wy = self._s2w(event.x, event.y)
            self.drag_offset = (hit['x'] - wx, hit['y'] - wy)
            self._update_details(hit)
        else:
            self.selected_node = None
            self._update_details(None)

    def _on_drag(self, event):
        if self.dragged_node:
            wx, wy = self._s2w(event.x, event.y)
            self.dragged_node['x'] = wx + self.drag_offset[0]
            self.dragged_node['y'] = wy + self.drag_offset[1]
            self.dragged_node['vx'], self.dragged_node['vy'] = 0, 0

    def _on_release(self, event):
        self.dragged_node = None

    def _update_details(self, n):
        if not n:
            self.lbl_det_title.configure(text="Sélectionnez un noeud", text_color="white")
            self.lbl_det_type.configure(text="")
            self.txt_det_desc.configure(state="normal")
            self.txt_det_desc.delete("1.0", "end")
            self.txt_det_desc.configure(state="disabled")
            self.lbl_det_tags.configure(text="")
        else:
            self.lbl_det_title.configure(text=n['label'], text_color=n['color'])
            self.lbl_det_type.configure(text=str(n['type']).upper())
            
            self.txt_det_desc.configure(state="normal")
            self.txt_det_desc.delete("1.0", "end")
            self.txt_det_desc.insert("1.0", n.get('desc', 'Aucune description disponible.'))
            self.txt_det_desc.configure(state="disabled")
            
            tags = n.get('tags', [])
            self.lbl_det_tags.configure(text=" ".join(tags) if tags else "Aucun tag")
