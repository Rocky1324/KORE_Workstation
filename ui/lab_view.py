import customtkinter as ctk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import tkinter as tk
from core.lab_engine import LabEngine

class LabView(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.engine = LabEngine()
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        self.tabview = ctk.CTkTabview(self)
        self.tabview.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        self.tab_circuits = self.tabview.add("Analyse de Circuits")
        self.tab_physique = self.tabview.add("Simulation Physique")
        
        self._setup_circuit_tab()
        self._setup_physics_tab()

    # --- CIRCUIT TAB (Visual Designer V2.5) ---
    def _setup_circuit_tab(self):
        self.tab_circuits.grid_columnconfigure(0, weight=1)
        self.tab_circuits.grid_rowconfigure(0, weight=1)
        
        self.circuit_tabs = ctk.CTkTabview(self.tab_circuits)
        self.circuit_tabs.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.tab_vis = self.circuit_tabs.add("Éditeur Visuel (Pro)")
        self.tab_text = self.circuit_tabs.add("Netlist & Log")
        
        self._setup_circuit_text_tab()
        self._setup_circuit_visual_tab()

    def _setup_circuit_text_tab(self):
        self.tab_text.grid_columnconfigure(1, weight=1)
        self.tab_text.grid_rowconfigure(0, weight=1)
        
        in_frame = ctk.CTkFrame(self.tab_text)
        in_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        ctk.CTkLabel(in_frame, text="Log de Résolution", font=ctk.CTkFont(weight="bold")).pack(pady=5)
        self.res_text = ctk.CTkTextbox(self.tab_text, font=ctk.CTkFont(family="Consolas", size=13))
        self.res_text.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

    def _setup_circuit_visual_tab(self):
        self.tab_vis.grid_columnconfigure(1, weight=1)
        self.tab_vis.grid_rowconfigure(0, weight=1)
        
        self.active_tool = None
        self.components_visual = []
        self.points = []
        # Electron animation state
        self.electron_job = None
        self.electron_wires = []
        
        tools = ctk.CTkScrollableFrame(self.tab_vis, width=180)
        tools.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        ctk.CTkLabel(tools, text="COMPOSANTS", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=10)
        
        self.tool_btns = {}
        items = [('R', "Résistance"), ('V', "Source Tension"), ('I', "Source Courant"), 
                 ('C', "Condensateur"), ('AM', "Ampèremètre"), ('VM', "Voltmètre"),
                 ('GND', "Masse"), ('WIRE', "Lien / Câble")]
        
        for t, label in items:
            btn = ctk.CTkButton(tools, text=label, height=32, fg_color="#333", 
                               command=lambda tool=t: self._set_tool(tool))
            btn.pack(pady=3, padx=10, fill="x")
            self.tool_btns[t] = btn
            
        ctk.CTkButton(tools, text="⚡ RÉSOUDRE", fg_color="green", height=45, font=ctk.CTkFont(weight="bold"),
                     command=self._solve_visual_circuit).pack(pady=(20, 5), padx=10, fill="x")

        ctk.CTkButton(tools, text="📖 Charger Exemple", fg_color="#444", height=32, 
                     command=self._load_preset_wheatstone).pack(pady=5, padx=10, fill="x")

        ctk.CTkButton(tools, text="Effacer", fg_color="#cc3333", height=30, 
                     command=self._clear_canvas).pack(side="bottom", pady=10, padx=10, fill="x")

        self.circuit_canvas = tk.Canvas(self.tab_vis, bg="#111", highlightthickness=0)
        self.circuit_canvas.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.circuit_canvas.bind("<Button-1>", self._on_canvas_click)
        self.circuit_canvas.bind("<Double-Button-1>", self._on_canvas_double_click)
        
        for i in range(0, 2000, 40):
            self.circuit_canvas.create_line(i, 0, i, 2000, fill="#1a1a1a")
            self.circuit_canvas.create_line(0, i, 2000, i, fill="#1a1a1a")

    def _set_tool(self, tool):
        for btn in self.tool_btns.values(): btn.configure(fg_color="#333")
        if self.active_tool == tool:
            self.active_tool = None
            self.points = []
        else:
            self.active_tool = tool
            self.tool_btns[tool].configure(fg_color="#1f538d")

    def _clear_canvas(self):
        # Stop electron animation
        if self.electron_job:
            self.circuit_canvas.after_cancel(self.electron_job)
            self.electron_job = None
        self.electron_wires = []
        self.circuit_canvas.delete("comp")
        self.circuit_canvas.delete("electron")
        self.components_visual = []
        self.points = []

    def _on_canvas_click(self, event):
        if not self.active_tool: return
        x, y = round(event.x / 40) * 40, round(event.y / 40) * 40
        
        if self.active_tool == 'WIRE':
            self.points.append((x, y))
            if len(self.points) == 2:
                p1, p2 = self.points
                self.circuit_canvas.create_line(p1[0], p1[1], p2[0], p2[1], fill="#4cd964", width=2, tags="comp")
                self.components_visual.append({'type': 'WIRE', 'p1': p1, 'p2': p2})
                self.points = []
        else:
            self._place_component(self.active_tool, x, y)

    def _on_canvas_double_click(self, event):
        """Phase 39: Edit component value."""
        x, y = round(event.x / 40) * 40, round(event.y / 40) * 40
        
        # Find closest component
        target = None
        for c in self.components_visual:
            if c['type'] != 'WIRE' and abs(c['x']-x) < 40 and abs(c['y']-y) < 40:
                target = c
                break
        
        if target:
            units = {"R": "Ω", "V": "V", "I": "A", "C": "F", "AC": "V", "AM": "", "VM": ""}
            unit = units.get(target['type'], "")
            
            if target['type'] in ["AM", "VM"]:
                # Measurement tools are usually ideal (0V or infinite R), no value to edit
                return

            dialog = ctk.CTkInputDialog(text=f"Entrez la valeur pour {target['type']} ({unit}):", title="Éditeur de Valeur")
            new_val = dialog.get_input()
            
            if new_val:
                target['val'] = new_val
                # Update visual label
                self.circuit_canvas.itemconfig(target['label_id'], text=f"{new_val}{unit}")

    def _place_component(self, type, x, y):
        # Grid snap
        x = int(round(x/20)*20)
        y = int(round(y/20)*20)
        
        tags = ("comp", f"comp_{len(self.components_visual)}")
        
        # Colors
        colors = {"R": "#ff9500", "V": "#5856d6", "I": "#ff2d55", "C": "#ffcc00", "AM": "#4cd964", "VM": "#4cd964"}
        color = colors.get(type, "#ffffff")
        
        # Components that have a meaningful polarity (MNA: n1=left/top=+, n2=right/bottom=-)
        POLAR_TYPES = {'V', 'AM', 'VM', 'I'}
        
        if type == 'GND':
            id = self.circuit_canvas.create_line(x-20, y, x+20, y, fill="white", width=3, tags=tags)
            self.circuit_canvas.create_line(x-15, y+5, x+15, y+5, fill="white", width=2, tags=tags)
            self.circuit_canvas.create_line(x-10, y+10, x+10, y+10, fill="white", width=1, tags=tags)
        else:
            id = self.circuit_canvas.create_oval(x-30, y-30, x+30, y+30, outline=color, width=3, fill="#1a1a1a", tags=tags)
            sym = "A" if type == 'AM' else "V" if type == 'VM' else type[0]
            self.circuit_canvas.create_text(x, y, text=sym, fill="white", font=("Arial", 14, "bold"), tags=tags)
            
            # --- 4 CONNECTION PADS ---
            pad_offsets = [(-40, 0), (40, 0), (0, -40), (0, 40)]
            for i, (dx, dy) in enumerate(pad_offsets):
                px, py = x + dx, y + dy
                
                if type in POLAR_TYPES:
                    # Left pad  (dx=-40) → POSITIVE terminal (red)
                    # Right pad (dx=+40) → NEGATIVE terminal (blue)
                    if (dx, dy) == (-40, 0):   # LEFT = +
                        pad_color = "#ff3b30"
                        self.circuit_canvas.create_oval(px-5, py-5, px+5, py+5, fill=pad_color, outline="", tags=tags)
                        self.circuit_canvas.create_text(px+12, py, text="+", fill="#ff3b30",
                                                        font=("Arial", 11, "bold"), tags=tags)
                    elif (dx, dy) == (40, 0):  # RIGHT = −
                        pad_color = "#007aff"
                        self.circuit_canvas.create_oval(px-5, py-5, px+5, py+5, fill=pad_color, outline="", tags=tags)
                        self.circuit_canvas.create_text(px-12, py, text="−", fill="#007aff",
                                                        font=("Arial", 13, "bold"), tags=tags)
                    else:                       # TOP / BOTTOM = neutral
                        self.circuit_canvas.create_oval(px-4, py-4, px+4, py+4, fill="#555", outline="", tags=tags)
                else:
                    # Non-polar components: all pads are neutral blue
                    self.circuit_canvas.create_oval(px-4, py-4, px+4, py+4, fill="#007aff", outline="", tags=tags)

        # Labels
        units = {"R": "Ω", "V": "V", "I": "A", "C": "F", "AM": " A", "VM": " V"}
        vals  = {"R": "100", "V": "10", "I": "1", "C": "10u", "AM": "...", "VM": "..."}
        
        unit = units.get(type, "")
        val  = vals.get(type, "")
        
        label_id = self.circuit_canvas.create_text(x, y+45, text=f"{val}{unit}" if type != 'GND' else "",
                                                 fill="#888", font=("Arial", 10), tags=tags)
            
        self.components_visual.append({'type': type, 'x': x, 'y': y, 'id': id, 'label_id': label_id, 'val': val})


    def _is_on_segment(self, p, s1, s2):
        """Phase 6.5: Robust point-on-segment detection with normalized distance."""
        dx, dy = s2[0] - s1[0], s2[1] - s1[1]
        line_len_sq = dx**2 + dy**2
        if line_len_sq < 1: 
            return (p[0]-s1[0])**2 + (p[1]-s1[1])**2 < 144 # 12px proximity
            
        t = ((p[0] - s1[0]) * dx + (p[1] - s1[1]) * dy) / line_len_sq
        # Clamp t for segments
        t_clamped = max(0, min(1, t))
        
        proj_x = s1[0] + t_clamped * dx
        proj_y = s1[1] + t_clamped * dy
        dist_sq = (p[0] - proj_x)**2 + (p[1] - proj_y)**2
        return dist_sq < 225 # 15px lateral tolerance

    def _solve_visual_circuit(self):
        """Phase 6.5: Intelligent Axis Selection & Aggressive Snap."""
        self.circuit_canvas.delete("debug")
        def snap(p): 
            if isinstance(p, (list, tuple)):
                return (int(round(p[0]/10)*10), int(round(p[1]/10)*10))
            return int(round(p/10)*10)
        
        parent = {}
        def find(i):
            if i not in parent: parent[i] = i
            if parent[i] == i: return i
            parent[i] = find(parent[i])
            return parent[i]
        
        def union(i, j):
            ri, rj = find(i), find(j)
            if ri != rj: parent[ri] = rj

        self.res_text.delete("1.0", "end")
        for c in self.components_visual:
            if c['type'] in ['AM', 'VM']:
                self.circuit_canvas.itemconfig(c['label_id'], text="...", fill="#888")

        all_pins = set()
        wires = []
        gnd_pins = []
        
        # 1. Collect all points
        for c in self.components_visual:
            ctype = c['type']
            if ctype == 'WIRE':
                p1, p2 = snap(c['p1']), snap(c['p2'])
                all_pins.update([p1, p2]); wires.append((p1, p2)); union(p1, p2)
            elif ctype in ['R', 'V', 'I', 'C', 'AM', 'VM']:
                cx, cy = snap(c['x']), snap(c['y'])
                for dx, dy in [(-40, 0), (40, 0), (0, -40), (0, 40)]:
                    all_pins.add((cx+dx, cy+dy))
            elif ctype == 'GND':
                p = snap((c['x'], c['y']))
                all_pins.add(p); gnd_pins.append(p)

        # 2. PHASE 1.5: AGGRESSIVE PIN-TO-WIRE SNAPPING (User Recommendation)
        pins_list = list(all_pins)
        for p in pins_list:
            for s1, s2 in wires:
                if self._is_on_segment(p, s1, s2):
                    union(p, s1) # Weld pin to wire mid-segment

        # 3. GLOBAL PROXIMITY (40px magnetic pull)
        for i in range(len(pins_list)):
            for j in range(i + 1, len(pins_list)):
                p1, p2 = pins_list[i], pins_list[j]
                if (p1[0]-p2[0])**2 + (p1[1]-p2[1])**2 < 1600: union(p1, p2)

        # 4. NODAL ASSIGNMENT
        gnd_roots = set(find(p) for p in gnd_pins)
        if not gnd_roots:
            self.res_text.insert("end", "ERREUR: Pas de GND. Reliez le circuit à la terre.")
            return

        root_to_node = {r: 0 for r in gnd_roots}
        next_id = 1
        for p in pins_list:
            r = find(p)
            if r not in root_to_node:
                root_to_node[r] = next_id; next_id += 1
                
        # 5. VISUAL DEBUG (Labels N0, N1, ...)
        for p in pins_list:
            nid = root_to_node.get(find(p), "?")
            self.circuit_canvas.create_text(p[0], p[1]-15, text=f"N{nid}", 
                                          fill="#ff3b30", font=("Arial", 9, "bold"), tags="debug")

        # 6. NETLIST & SMART AXIS HEURISTIC
        netlist = []
        comp_log = "--- ANALYSE TOPOLOGIQUE v6.5 ---\n"
        measurement_components = []
        
        # Identify "Wired" roots (roots connected to a wire or gnd)
        wired_points = set()
        for s1, s2 in wires: wired_points.update([s1, s2])
        for gp in gnd_pins: wired_points.add(gp)
        wired_roots = set(find(p) for p in wired_points)

        for idx, c in enumerate(self.components_visual):
            if c['type'] in ['R', 'V', 'I', 'C', 'AM', 'VM']:
                cx, cy, ctype = snap(c['x']), snap(c['y']), c['type']
                h_terms = [snap((cx+dx, cy)) for dx in [-40, 40]]
                v_terms = [snap((cx, cy+dy)) for dy in [-40, 40]]
                
                h_nodes = [root_to_node[find(p)] for p in h_terms]
                v_nodes = [root_to_node[find(p)] for p in v_terms]
                
                # Heuristic: Count how many wired terminals each axis has
                h_wired = sum(1 for p in h_terms if find(p) in wired_roots)
                v_wired = sum(1 for p in v_terms if find(p) in wired_roots)
                
                # Pick axis with better actual connectivity
                if v_wired > h_wired: u_nodes = v_nodes
                elif h_wired > v_wired: u_nodes = h_nodes
                elif h_nodes[0] != h_nodes[1]: u_nodes = h_nodes # Tie-breaker
                else: u_nodes = v_nodes
                
                n1, n2 = u_nodes
                comp_log += f"{ctype}: [N{n1}, N{n2}] (Active: H={h_wired} V={v_wired})\n"
                
                if ctype == 'AM':
                    netlist.append({'type': 'AM', 'name': f"AM{idx}", 'n1': n1, 'n2': n2, 'value': '0'})
                    measurement_components.append({'obj': c, 'type': 'AM', 'name': f"AM{idx}"})
                elif ctype == 'VM':
                    netlist.append({'type': 'VM', 'name': f"VM{idx}", 'n1': n1, 'n2': n2, 'value': '1e9'})
                    measurement_components.append({'obj': c, 'type': 'VM', 'n1': n1, 'n2': n2})
                else:
                    v = c['val']
                    if ctype == 'C': v = '1e7'
                    netlist.append({'type': ctype[0], 'name': f"{ctype}{idx}", 'n1': n1, 'n2': n2, 'value': v})

        self.res_text.insert("end", comp_log + "\n")
        res = self.engine.solve_circuit(netlist)
        if res["success"]:
            results = res["results"]
            output = "--- SOLUTION DU CIRCUIT ---\n"
            for k, v in results.items(): output += f"{k:25}: {v}\n"
            self.res_text.insert("end", output)
            self.circuit_tabs.set("Netlist & Log")
            for m in measurement_components:
                if m['type'] == 'AM':
                    val = results.get(f"Current through {m['name']}", 0)
                    self.circuit_canvas.itemconfig(m['obj']['label_id'], text=f"{float(val):.3f} A", fill="#4cd964")
                elif m['type'] == 'VM':
                    v1 = float(results.get(f"Node {m['n1']}", 0)) if m['n1'] > 0 else 0
                    v2 = float(results.get(f"Node {m['n2']}", 0)) if m['n2'] > 0 else 0
                    self.circuit_canvas.itemconfig(m['obj']['label_id'], text=f"{abs(v1-v2):.3f} V", fill="#4cd964")
            # Start electron animation
            self._start_electron_animation(results)
        else:
            self.res_text.insert("end", f"ERREUR: {res['error']}\n\nCONSEIL: Regardez les N rouges (Vérifiez la soudure).")
            self.circuit_tabs.set("Netlist & Log")

    def _load_preset_wheatstone(self):
        """Pont de Wheatstone équilibré — VM doit afficher 0.000 V."""
        self._clear_canvas()
        def s(v): return int(round(v / 10) * 10)

        self._place_component('V', s(80), s(280))
        self.components_visual[-1]['val'] = "10"
        self.circuit_canvas.itemconfig(self.components_visual[-1]['label_id'], text="10V")

        # GND1 — sits EXACTLY on V bottom pad (80,320) → zero-length snap to GND
        self._place_component('GND', s(80), s(320))

        # Four resistors — all VERTICAL (top/bottom pads used)
        res = [('R', 280, 160, "100"), ('R', 520, 160, "100"),
               ('R', 280, 400, "200"), ('R', 520, 400, "200")]
        for t, x, y, v in res:
            self._place_component(t, s(x), s(y))
            self.components_visual[-1]['val'] = v
            self.circuit_canvas.itemconfig(self.components_visual[-1]['label_id'], text=f"{v}Ω")

        # Voltmeter — HORIZONTAL, centre-milieu (pads: left=360,280  right=440,280)
        self._place_component('VM', s(400), s(280))

        # GND2 — anchors the bottom GND rail at (400,480)
        self._place_component('GND', s(400), s(480))

        # ── Wires ───────────────────────────────────────────────────────
        ws = [
            # ── A rail: V+ (80,240) → top rail → R1 top (280,120) & R2 top (520,120)
            ((80,  240), (80,  80)),    # V+ straight up left side
            ((80,  80),  (280, 80)),    # across to left column
            ((280, 80),  (280, 120)),   # down to R1 top pad
            ((280, 80),  (520, 80)),    # continue across
            ((520, 80),  (520, 120)),   # down to R2 top pad

            # ── Node B: R1 bottom (280,200) ↔ VM left pad (360,280) ↔ R3 top (280,360)
            ((280, 200), (280, 280)),   # R1 bottom → junction B
            ((280, 280), (360, 280)),   # junction B → VM left pad
            ((280, 280), (280, 360)),   # junction B → R3 top pad (y=360)

            # ── Node C: R2 bottom (520,200) ↔ VM right pad (440,280) ↔ R4 top (520,360)
            ((520, 200), (520, 280)),   # R2 bottom → junction C
            ((520, 280), (440, 280)),   # junction C → VM right pad
            ((520, 280), (520, 360)),   # junction C → R4 top pad (y=360)

            # ── GND rail: R3/R4 bottoms → GND2 at (400,480)
            ((280, 440), (280, 480)),   # R3 bottom → rail
            ((520, 440), (520, 480)),   # R4 bottom → rail
            ((280, 480), (520, 480)),   # bottom rail (GND2 sits on this segment)

            # ── GND1 ↔ GND2: connect left GND to bottom rail
            ((80,  320), (80,  480)),   # GND1 down
            ((80,  480), (280, 480)),   # join bottom rail
        ]
        for p1, p2 in ws:
            self._draw_wire(p1, p2)


    def _draw_wire(self, p1, p2):
        def snap_p(p): return (int(round(p[0]/10)*10), int(round(p[1]/10)*10))
        sp1, sp2 = snap_p(p1), snap_p(p2)
        self.circuit_canvas.create_line(sp1[0], sp1[1], sp2[0], sp2[1], fill="#4cd964", width=2, tags="comp")
        self.components_visual.append({'type': 'WIRE', 'p1': sp1, 'p2': sp2})

    def _start_electron_animation(self, results):
        """Launch animated electron dots on all wires after a solve."""
        # Cancel any previous animation
        if self.electron_job:
            self.circuit_canvas.after_cancel(self.electron_job)
            self.electron_job = None
        self.circuit_canvas.delete("electron")

        # Source current → speed (px per frame, capped)
        source_i = 0.0
        for k, v in results.items():
            if "Current through" in k:
                source_i = max(source_i, abs(float(v)))
        if source_i < 1e-9:
            return  # Dead circuit — no animation

        speed = min(source_i * 150, 4.0)   # scale mA → px/frame, max 4px

        # Build per-wire data
        self.electron_wires = []
        for i, c in enumerate(self.components_visual):
            if c['type'] != 'WIRE':
                continue
            p1, p2 = c['p1'], c['p2']
            length = ((p2[0]-p1[0])**2 + (p2[1]-p1[1])**2) ** 0.5
            if length < 1:
                continue
            self.electron_wires.append({
                'p1': p1, 'p2': p2,
                'length': length,
                'phase': (i * 13.7) % 40,  # stagger dots so they don't all overlap
                'speed': speed,
            })

        self.electron_job = self.circuit_canvas.after(33, self._tick_electrons)

    def _tick_electrons(self):
        """One animation frame: erase old dots, draw new ones, schedule next."""
        self.circuit_canvas.delete("electron")
        DOT_SPACING = 40   # pixels between consecutive dots on a wire
        DOT_R       = 3    # dot radius in pixels

        for w in self.electron_wires:
            p1, p2 = w['p1'], w['p2']
            dx = p2[0] - p1[0]
            dy = p2[1] - p1[1]
            L  = w['length']

            # Advance phase
            w['phase'] = (w['phase'] + w['speed']) % DOT_SPACING

            # Place dots along the wire
            t = w['phase'] / L
            while t <= 1.0:
                px = int(p1[0] + dx * t)
                py = int(p1[1] + dy * t)
                self.circuit_canvas.create_oval(
                    px - DOT_R, py - DOT_R,
                    px + DOT_R, py + DOT_R,
                    fill="white", outline="", tags="electron"
                )
                t += DOT_SPACING / L

        # Schedule next frame (~30 fps)
        self.electron_job = self.circuit_canvas.after(33, self._tick_electrons)


    # --- PHYSICS TAB (Expert V2.5) ---
    def _setup_physics_tab(self):
        self.tab_physique.grid_columnconfigure(1, weight=1)
        self.tab_physique.grid_rowconfigure(0, weight=1)
        
        self.ctrl_frame = ctk.CTkScrollableFrame(self.tab_physique, width=300)
        self.ctrl_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        ctk.CTkLabel(self.ctrl_frame, text="SYSTÈME PHYSIQUE", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=10)
        
        self.sys_var = ctk.StringVar(value="Pendule Simple")
        self.sys_menu = ctk.CTkOptionMenu(self.ctrl_frame, 
                                        values=["Pendule Simple", "Double Pendule", "Harmonique", "Lorenz", "MODE CUSTOM"], 
                                        command=self._update_parameter_ui, variable=self.sys_var)
        self.sys_menu.pack(pady=10, fill="x", padx=10)
        
        # Formula Display
        self.formula_frame = ctk.CTkFrame(self.ctrl_frame, fg_color="#1a1a1a", corner_radius=10)
        self.formula_frame.pack(fill="x", padx=10, pady=5)
        self.formula_lbl = ctk.CTkLabel(self.formula_frame, text="", font=ctk.CTkFont(family="Consolas", size=11), justify="left")
        self.formula_lbl.pack(pady=10, padx=10)
        
        self.param_frame = ctk.CTkFrame(self.ctrl_frame, fg_color="transparent")
        self.param_frame.pack(fill="x", padx=10)
        
        self.sliders = {}
        self.custom_inputs = {}
        self._update_parameter_ui()
        
        ctk.CTkButton(self.ctrl_frame, text="🚀 SIMULER", command=self._run_physics, 
                     fg_color="green", font=ctk.CTkFont(weight="bold")).pack(pady=20, fill="x", padx=10)
        
        self.plot_container = ctk.CTkFrame(self.tab_physique, fg_color="#0b0b0b")
        self.plot_container.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.plot_container.grid_rowconfigure(0, weight=1)
        self.plot_container.grid_columnconfigure(0, weight=1)

    def _update_parameter_ui(self, *args):
        for widget in self.param_frame.winfo_children(): widget.destroy()
        sys = self.sys_var.get()
        self.sliders = {}
        self.custom_inputs = {}
        
        # Formula map
        formulas = {
            "Pendule Simple": "θ'' = -(g/L) sin(θ)\n[θ: Angle, ω: Vitesse]",
            "Double Pendule": "Système d'équations de Lagrange\n(Mouvement Chaotique)",
            "Harmonique": "x'' = -(k/m)x - (b/m)v\n[Oscillation Amortie]",
            "Lorenz": "x' = σ(y-x)\ny' = x(ρ-z) - y\nz' = xy - βz",
            "MODE CUSTOM": "Définis tes propres ODE\ndy/dt = f(t, y)"
        }
        self.formula_lbl.configure(text=formulas.get(sys, ""))
        
        if sys == "MODE CUSTOM":
            ctk.CTkLabel(self.param_frame, text="Variables (sép. virgule):").pack(pady=(10, 0))
            self.custom_vars = ctk.CTkEntry(self.param_frame, placeholder_text="x, v")
            self.custom_vars.pack(fill="x")
            self.custom_vars.insert(0, "x, v")
            
            ctk.CTkLabel(self.param_frame, text="Équations (un par var):").pack(pady=(10, 0))
            self.custom_eqs = ctk.CTkTextbox(self.param_frame, height=80)
            self.custom_eqs.pack(fill="x")
            self.custom_eqs.insert("1.0", "v\n-9.81*sin(x) - 0.5*v")
            
            ctk.CTkLabel(self.param_frame, text="Conditions Initiales:").pack(pady=(10, 0))
            self.custom_init = ctk.CTkEntry(self.param_frame, placeholder_text="0.5, 0")
            self.custom_init.pack(fill="x")
            self.custom_init.insert(0, "0.5, 0")
        else:
            # Add sliders for presets
            if sys == "Pendule Simple":
                self._add_slider("Longueur (L)", "L", 0.5, 5, 2.0)
                self._add_slider("Gravité (g)", "g", 1, 20, 9.81)
            elif sys == "Double Pendule":
                self._add_slider("L1 (m)", "L1", 0.5, 3.0, 1.0)
                self._add_slider("L2 (m)", "L2", 0.5, 3.0, 1.0)
                self._add_slider("M1 (kg)", "M1", 0.5, 10.0, 2.0)
                self._add_slider("M2 (kg)", "M2", 0.5, 10.0, 1.0)
            elif sys == "Harmonique":
                self._add_slider("Raideur (k)", "k", 1, 100, 20.0)
                self._add_slider("Masse (m)", "m", 0.1, 10, 1.0)
                self._add_slider("Amort. (b)", "b", 0, 5, 0.2)
            elif sys == "Lorenz":
                self._add_slider("Sigma (σ)", "sigma", 0, 50, 10.0)
                self._add_slider("Rho (ρ)", "rho", 0, 100, 28.0)
                self._add_slider("Beta (β)", "beta", 0, 10, 2.66)

    def _add_slider(self, label, key, min_val, max_val, start):
        f = ctk.CTkFrame(self.param_frame, fg_color="transparent")
        f.pack(fill="x", pady=2)
        ctk.CTkLabel(f, text=label).pack(side="left")
        v_l = ctk.CTkLabel(f, text=str(start))
        v_l.pack(side="right")
        s = ctk.CTkSlider(self.param_frame, from_=min_val, to=max_val, 
                         command=lambda v, l=v_l, k=key: (l.configure(text=f"{float(v):.2f}"), self.sliders.update({k: float(v)})))
        s.set(start)
        s.pack(fill="x", pady=(0, 10))
        self.sliders[key] = start

    def _run_physics(self):
        sys = self.sys_var.get()
        for w in self.plot_container.winfo_children(): w.destroy()
        
        fig = plt.figure(figsize=(5, 4), dpi=100)
        fig.patch.set_facecolor('#0b0b0b')
        is_3d = (sys == "Lorenz")
        ax = fig.add_subplot(111, projection='3d' if is_3d else None)
        ax.set_facecolor('#0b0b0b')
        ax.tick_params(colors='white')

        try:
            if sys == "MODE CUSTOM":
                vars = [v.strip() for v in self.custom_vars.get().split(",")]
                eqs = self.custom_eqs.get("1.0", "end").strip().split('\n')
                y0 = [float(i.strip()) for i in self.custom_init.get().split(",")]
                deriv = self.engine.get_custom_model(eqs, vars)
                t, y = self.engine.simulate_dynamic_system(deriv, y0, (0, 20))
                ax.plot(t, y[:, 0], label=f"{vars[0]}(t)", color="cyan")
                if len(vars) > 1: ax.plot(t, y[:, 1], label=f"{vars[1]}(t)", color="orange")
            elif sys == "Pendule Simple":
                deriv = self.engine.get_preset_pendulum(L=self.sliders.get('L',2), g=self.sliders.get('g', 9.81))
                t, y = self.engine.simulate_dynamic_system(deriv, [1.0, 0], (0, 20))
                ax.plot(t, y[:,0], color="cyan", label="θ (rad)")
                ax.set_title("Pendule Simple", color="white")
                ax.set_xlabel("Temps (s)", color="gray")
                ax.set_ylabel("Angle (rad)", color="gray")
            
            elif sys == "Double Pendule":
                deriv = self.engine.get_preset_double_pendulum(
                    L1=self.sliders.get('L1', 1.0), L2=self.sliders.get('L2', 1.0),
                    M1=self.sliders.get('M1', 2.0), M2=self.sliders.get('M2', 1.0)
                )
                # Initial conditions: th1=pi/2, w1=0, th2=pi/2, w2=0
                t, y = self.engine.simulate_dynamic_system(deriv, [np.pi/2, 0, np.pi/2, 0], (0, 20), dt=0.02)
                ax.plot(t, y[:, 0], label="θ1 (Angle haut)", color="cyan", alpha=0.8)
                ax.plot(t, y[:, 2], label="θ2 (Angle bas)", color="#ff9500", alpha=0.8)
                ax.set_title("Chaos : Double Pendule", color="white")
                ax.set_xlabel("Temps (s)", color="gray")

            elif sys == "Lorenz":
                deriv = self.engine.get_preset_lorenz(
                    sigma=self.sliders.get('sigma', 10.0), 
                    rho=self.sliders.get('rho', 28.0), 
                    beta=self.sliders.get('beta', 2.66)
                )
                t, y = self.engine.simulate_dynamic_system(deriv, [0.1, 0.1, 0.1], (0, 50), dt=0.01)
                ax.plot(y[:, 0], y[:, 1], y[:, 2], color="#ff2d55", lw=0.8)
                ax.set_title("Attracteur de Lorenz (3D State Space)", color="white")
                ax.set_xlabel("X", color="gray")
                ax.set_ylabel("Y", color="gray")
                ax.set_zlabel("Z", color="gray")

            elif sys == "Harmonique":
                deriv = self.engine.get_preset_oscillator(
                    k=self.sliders.get('k', 20.0), 
                    m=self.sliders.get('m', 1.0), 
                    b=self.sliders.get('b', 0.2)
                )
                t, y = self.engine.simulate_dynamic_system(deriv, [2.0, 0], (0, 20))
                ax.plot(t, y[:,0], color="#5ac8fa", label="Position (x)")
                ax.set_title("Oscillateur Harmonique Amorti", color="white")
                ax.set_xlabel("Temps (s)", color="gray")
                ax.set_ylabel("Position (m)", color="gray")

            ax.grid(True, alpha=0.2)
            canvas = FigureCanvasTkAgg(fig, master=self.plot_container)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)
        except Exception as e:
            tk.messagebox.showerror("Erreur Simulation", str(e))
