import customtkinter as ctk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from core.calculator import CalcEngine
import matplotlib.pyplot as plt

class CalculatorView(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        # Header
        self.header = ctk.CTkLabel(self, text="KORE-Calc", font=ctk.CTkFont(size=24, weight="bold"))
        self.header.pack(pady=10, padx=20, anchor="w")

        # Tab System
        self.tabs = ctk.CTkTabview(self, height=500)
        self.tabs.pack(fill="both", expand=True, padx=20, pady=10)
        
        self.tab_sci_graph = self.tabs.add("Moteur Symbolique & Graphes")
        self.tab_std = self.tabs.add("Calculatrice Scientifique")

        try:
            from core.calculator import CalcEngine
            self.engine = CalcEngine()
            self._create_symbolic_widgets()
            self._create_scientific_calculator_widgets()
            print("KORE-Calc widgets initialized")
        except Exception as e:
            err_msg = f"Erreur critique lors du chargement de KORE-Calc :\n{str(e)}"
            self.err_lbl = ctk.CTkLabel(self, text=err_msg, font=ctk.CTkFont(size=16), text_color="red", wraplength=400)
            self.err_lbl.pack(pady=50)

    def _create_symbolic_widgets(self):
        # Top Control Area
        self.control_frame = ctk.CTkFrame(self.tab_sci_graph)
        self.control_frame.pack(padx=10, pady=10, fill="x")

        ctk.CTkLabel(self.control_frame, text="Expression :", 
                     font=ctk.CTkFont(weight="bold")).pack(side="left", padx=10, pady=10)
        
        self.input_entry = ctk.CTkEntry(self.control_frame, placeholder_text="Ex: x**2 > 4, 3x+5=0, x+y=5, x-y=1 ou integre x**2")
        self.input_entry.pack(side="left", fill="x", expand=True, padx=10, pady=10)
        self.input_entry.bind("<Return>", lambda e: self.process_calculation())

        self.btn_calc = ctk.CTkButton(self.control_frame, text="Calculer / Tracer", command=self.process_calculation)
        self.btn_calc.pack(side="left", padx=5, pady=10)
        
        self.plot_mode = ctk.CTkSegmentedButton(self.control_frame, values=["Auto", "2D", "3D"])
        self.plot_mode.set("Auto")
        self.plot_mode.pack(side="left", padx=10, pady=10)

        self.btn_help = ctk.CTkButton(self.control_frame, text="?", width=30, fg_color="gray", command=self._show_help)
        self.btn_help.pack(side="left", padx=5, pady=10)

        # Plot and Results
        self.main_content = ctk.CTkFrame(self.tab_sci_graph, fg_color="transparent")
        self.main_content.pack(padx=10, pady=(0, 10), fill="both", expand=True)
        
        # ... (keep plot_frame and res_frame as they were) ...
        self.plot_frame = ctk.CTkFrame(self.main_content)
        self.plot_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        self.fig = Figure(figsize=(5, 4), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_title("Visualisation Graphique")
        self.ax.grid(True, alpha=0.3)
        self.fig.patch.set_facecolor('#2b2b2b')
        self.ax.set_facecolor('#2b2b2b')
        self.ax.tick_params(colors='white')
        for spine in self.ax.spines.values():
            spine.set_color('white')
            
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.plot_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=5, pady=5)

        # Mouse Interaction Logic (Zoom & Pan)
        self.canvas.mpl_connect("scroll_event", self._on_zoom)
        self.canvas.mpl_connect("button_press_event", self._on_press)
        self.canvas.mpl_connect("button_release_event", self._on_release)
        self.canvas.mpl_connect("motion_notify_event", self._on_motion)
        self._press_data = None

        # Navigation Toolbar
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.plot_frame, pack_toolbar=False)
        self.toolbar.update()
        self.toolbar.pack(side="bottom", fill="x", padx=5, pady=2)
        
        self.res_frame = ctk.CTkFrame(self.main_content, width=280)
        self.res_frame.pack(side="right", fill="both")
        self.res_frame.pack_propagate(False)
        
        ctk.CTkLabel(self.res_frame, text="Résultats & Analyses", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)
        self.res_text = ctk.CTkTextbox(self.res_frame, font=ctk.CTkFont(family="Consolas", size=13))
        self.res_text.pack(fill="both", expand=True, padx=10, pady=10)

    def _create_scientific_calculator_widgets(self):
        # Display
        self.std_display = ctk.CTkEntry(self.tab_std, font=ctk.CTkFont(size=32), justify="right", height=60)
        self.std_display.pack(padx=40, pady=20, fill="x")

        # Buttons Grid (Scientific)
        self.grid_frame = ctk.CTkFrame(self.tab_std, fg_color="transparent")
        self.grid_frame.pack(padx=40, pady=10, fill="both", expand=True)
        
        # 6-column Layout
        buttons = [
            'sin', 'cos', 'tan', '^', 'sqrt', 'C',
            '7', '8', '9', '/', '(', ')',
            '4', '5', '6', '*', 'log', 'ln',
            '1', '2', '3', '-', 'pi', 'e',
            '0', '.', '=', '+', 'exp', 'bin'
        ]
        
        row = 0
        col = 0
        for btn_text in buttons:
            cmd = lambda x=btn_text: self._on_calc_btn_click(x)
            
            # Color coding
            if btn_text in '0123456789.': color = "#444444"
            elif btn_text == '=': color = "#1f538d"
            elif btn_text == 'C': color = "#8d1f1f"
            elif btn_text in '+-*/^()': color = "#333333"
            else: color = "#222222" # Functions
            
            btn = ctk.CTkButton(self.grid_frame, text=btn_text, width=60, height=50, 
                                font=ctk.CTkFont(size=16, weight="bold"),
                                fg_color=color, command=cmd)
            btn.grid(row=row, column=col, padx=3, pady=3, sticky="nsew")
            
            col += 1
            if col > 5:
                col = 0
                row += 1
        
        for i in range(6): self.grid_frame.grid_columnconfigure(i, weight=1)
        for i in range(5): self.grid_frame.grid_rowconfigure(i, weight=1)
    def _on_zoom(self, event):
        """Handle mouse scroll for zooming."""
        if event.inaxes != self.ax: return
        base_scale = 1.1
        cur_xlim = self.ax.get_xlim()
        cur_ylim = self.ax.get_ylim()
        
        if event.button == 'up': scale_factor = 1 / base_scale
        elif event.button == 'down': scale_factor = base_scale
        else: scale_factor = 1
        
        new_width = (cur_xlim[1] - cur_xlim[0]) * scale_factor
        new_height = (cur_ylim[1] - cur_ylim[0]) * scale_factor
        
        rel_x = (cur_xlim[1] - event.xdata) / (cur_xlim[1] - cur_xlim[0])
        rel_y = (cur_ylim[1] - event.ydata) / (cur_ylim[1] - cur_ylim[0])
        
        self.ax.set_xlim([event.xdata - new_width * (1 - rel_x), event.xdata + new_width * rel_x])
        self.ax.set_ylim([event.ydata - new_height * (1 - rel_y), event.ydata + new_height * rel_y])
        self.canvas.draw()

    def _on_press(self, event):
        """Handle mouse click for panning."""
        if event.inaxes != self.ax: return
        self._press_data = (event.xdata, event.ydata)

    def _on_release(self, event):
        """Release panning data."""
        self._press_data = None

    def _on_motion(self, event):
        """Handle mouse movement for panning."""
        if self._press_data is None or event.inaxes != self.ax: return
        dx = event.xdata - self._press_data[0]
        dy = event.ydata - self._press_data[1]
        
        cur_xlim = self.ax.get_xlim()
        cur_ylim = self.ax.get_ylim()
        
        self.ax.set_xlim(cur_xlim - dx)
        self.ax.set_ylim(cur_ylim - dy)
        self.canvas.draw()

    def _show_help(self):
        help_win = ctk.CTkToplevel(self)
        help_win.title("Aide KORE-Calc")
        help_win.geometry("500x450")
        help_win.attributes("-topmost", True)
        
        txt = ctk.CTkTextbox(help_win, font=ctk.CTkFont(size=13))
        txt.pack(fill="both", expand=True, padx=20, pady=20)
        
        help_content = """--- GUIDE KORE-CALC ---

1. Équations & Graphes :
   Tapez simplement l'expression dans l'onglet 'Moteur Symbolique'.
   Ex: x**2 - 4   (donne x=2, x=-2)
   Ex: 3x + 5 = 0

2. Graphes 2D vs 3D :
   Si vous avez 2 variables (x et y), utilisez le bouton 'Auto / 2D / 3D' :
   - '3D' = Surface z = f(x,y)
   - '2D' = Courbe implicite f(x,y) = 0 (parfait pour le coeur !)

3. Inéquations & Régions :
   Supporte <, >, <=, >=. Les régions sont hachurées !
   Ex: x+y > 2, x-y < 4

4. Calcul Intégral :
   Ex: integre x**2
   Ex: integre sin(x) from 0 to pi

4. Calculatrice Scientifique :
   Utilisez le deuxième onglet pour les calculs rapides.
   Supporte : sin, cos, tan, log, ln, sqrt, exp, ^ (puissance).

5. Navigation Graphe :
   - Molette : Zoom avant/arrière
   - Clic-Glisser : Déplacer la vue (Pan)
"""
        txt.insert("1.0", help_content)
        txt.configure(state="disabled")

    def _on_calc_btn_click(self, char):
        current = self.std_display.get()
        if char == 'C':
            self.std_display.delete(0, "end")
        elif char == '=':
            res = self.engine.evaluate(current)
            self.std_display.delete(0, "end")
            if res["success"]:
                self.std_display.insert(0, str(res["result"]))
            else:
                self.std_display.insert(0, "Error")
        elif char in ['sin', 'cos', 'tan', 'sqrt', 'log', 'ln', 'exp']:
            self.std_display.insert("end", f"{char}(")
        elif char == '^':
            self.std_display.insert("end", "**")
        elif char == 'pi':
            self.std_display.insert("end", "pi")
        elif char == 'e':
            self.std_display.insert("end", "e")
        else:
            self.std_display.insert("end", char)

    def set_expression(self, expr_str):
        """Sets the expression in the input field and triggers calculation."""
        self.input_entry.delete(0, "end")
        self.input_entry.insert(0, expr_str)
        self.process_calculation()

    def process_calculation(self):
        raw_input = self.input_entry.get().strip()
        if not raw_input: return

        self.res_text.delete("1.0", "end")
        self.ax.clear()
        self.ax.grid(True, alpha=0.3)
        self.ax.set_title(f"Analyse : {raw_input}")

        # Check for integral first
        if 'integre' in raw_input.lower():
            clean_expr = raw_input.lower().replace('integre', '').strip()
            res = self.engine.calculate_integral(clean_expr)
            self._display_result(res)
            # Try to plot the integrand
            plot_res = self.engine.get_plot_data(clean_expr.split('from')[0].strip())
            if plot_res["success"]:
                self.ax.plot(plot_res["x"], plot_res["y"], color='#1f538d', linewidth=2)
                self.ax.set_title(f"Graphe de l'intégrande")
                self.canvas.draw()
            return

        # Handle Systems (Equations or Inequalities)
        if ',' in raw_input:
            eqs = [e.strip() for e in raw_input.split(',')]
            res = self.engine.solve_system(eqs)
            self._display_result(res)
            
            # Special Plotting for 2D Inequalities (Schema)
            has_y = 'y' in raw_input.lower()
            if has_y:
                self._plot_inequality_region(eqs)
        else:
            res_solve = self.engine.solve_equation(raw_input)
            self._display_result(res_solve)
            
            # Inequality check for single variable/multivariable
            if res_solve["type"] == "inequality":
                if 'y' in raw_input.lower():
                    self._plot_inequality_region([raw_input])
            
            # Standard Plotting
            has_x = 'x' in raw_input.lower()
            has_y = 'y' in raw_input.lower()

            mode = self.plot_mode.get()
            
            is_3d = False
            if mode == "3D":
                is_3d = True
            elif mode == "Auto" and (has_x and has_y):
                is_3d = True

            if is_3d:
                # 3D Plot
                plot_res = self.engine.get_plot3d_data(raw_input, points=50) # Use 3d data
                if plot_res["success"]:
                    self.fig.clear()
                    self.ax = self.fig.add_subplot(111, projection='3d')
                    self.ax.set_facecolor('#2b2b2b')
                    self.ax.tick_params(colors='white')
                    
                    # Plot surface
                    surf = self.ax.plot_surface(plot_res["X"], plot_res["Y"], plot_res["Z"], 
                                               cmap='viridis', edgecolor='none', alpha=0.8)
                    self.ax.set_xlabel('X', color='white')
                    self.ax.set_ylabel('Y', color='white')
                    self.ax.set_zlabel('Z', color='white')
                    self.ax.set_title(f"Surface : {raw_input}", color='white')
                    self.canvas.draw()
                return

            if mode == "2D" and (has_x and has_y):
                # Implicit 2D Plot
                plot_res = self.engine.get_plot3d_data(raw_input, points=200) # higher resolution for contour
                if plot_res["success"]:
                    if hasattr(self.ax, 'get_zlim'):
                        self.fig.clear()
                        self.ax = self.fig.add_subplot(111)
                        self.ax.set_facecolor('#2b2b2b')
                        self.ax.tick_params(colors='white')
                        self.ax.grid(True, alpha=0.3)
                    
                    # Check if all Z are positive or all negative to avoid contour errors
                    import numpy as np
                    z_min, z_max = np.nanmin(plot_res["Z"]), np.nanmax(plot_res["Z"])
                    if z_min <= 0 <= z_max:
                        self.ax.contour(plot_res["X"], plot_res["Y"], plot_res["Z"], levels=[0], colors=['#1f538d'], linewidths=2)
                        
                    self.ax.axhline(y=0, color='white', linestyle='-', alpha=0.5)
                    self.ax.axvline(x=0, color='white', linestyle='-', alpha=0.5)
                    self.ax.set_title(f"Courbe : {raw_input} = 0", color='white')
                    self.canvas.draw()
                return

            # fallback to standard 2D function y = f(x)
            plot_res = self.engine.get_plot_data(raw_input)
            if plot_res["success"]:
                # Ensure 2D axis
                if hasattr(self.ax, 'get_zlim'): # Was 3D
                    self.fig.clear()
                    self.ax = self.fig.add_subplot(111)
                    self.ax.set_facecolor('#2b2b2b')
                    self.ax.tick_params(colors='white')
                    self.ax.grid(True, alpha=0.3)
                
                self.ax.plot(plot_res["x"], plot_res["y"], color='#1f538d', linewidth=2)
                self.ax.axhline(y=0, color='white', linestyle='-', alpha=0.5)
                self.ax.axvline(x=0, color='white', linestyle='-', alpha=0.5)
                self.canvas.draw()
            else:
                if res_solve["type"] in ["equation", "inequality"]:
                    if not 'y' in raw_input.lower():
                        self.res_text.insert("end", f"\n[Note] Pas de graphe généré pour cette expression.\n")

    def _plot_inequality_region(self, ineq_list):
        """Plots the solution region for a system of 2D inequalities."""
        try:
            import numpy as np
            # Create a coordinate grid
            x_range = np.linspace(-10, 10, 200)
            y_range = np.linspace(-10, 10, 200)
            X, Y = np.meshgrid(x_range, y_range)
            
            # Initialize combined mask
            total_mask = np.ones_like(X, dtype=bool)
            
            import sympy as sp
            for ineq_str in ineq_list:
                cleaned = self.engine._clean_input(ineq_str)
                # Convert inequality to a numeric function (lambda)
                # We need to handle <, >, <=, >=
                for op in ['<=', '>=', '<', '>']:
                    if op in cleaned:
                        parts = cleaned.split(op)
                        # Expr op 0
                        expr = sp.sympify(f"({parts[0]}) - ({parts[1]})")
                        f_num = sp.lambdify((self.engine.x, self.engine.y), expr, 'numpy')
                        vals = f_num(X, Y)
                        
                        if op == '<': m = vals < 0
                        elif op == '>': m = vals > 0
                        elif op == '<=': m = vals <= 0
                        elif op == '>=': m = vals >= 0
                        
                        total_mask &= m
                        break
            
            # Plot the region
            self.ax.contourf(X, Y, total_mask, levels=[0.5, 1.5], colors=['#1f538d'], alpha=0.3)
            self.ax.contour(X, Y, total_mask, levels=[0.5], colors=['#1f538d'], linewidths=1)
            self.ax.set_title("Région Solution (Hachurée)")
            self.canvas.draw()
            
        except Exception as e:
            print(f"Plot error: {e}")

    def _display_result(self, res):
        if res["success"]:
            label = res['type'].replace('_', ' ').upper()
            self.res_text.insert("end", f"--- {label} ---\n")
            
            # Formatting SymPy objects nicely
            import sympy as sp
            result = res['result']
            if isinstance(result, list):
                if not result:
                    self.res_text.insert("end", "Aucune solution trouvée.\n\n")
                else:
                    for i, s in enumerate(result):
                        self.res_text.insert("end", f"S{i+1} : {s}\n")
                    self.res_text.insert("end", "\n")
            else:
                self.res_text.insert("end", f"Résultat :\n{result}\n")
                # Try numerical evaluation
                try:
                    num_val = float(result.evalf())
                    self.res_text.insert("end", f"≈ {num_val:.4f}\n")
                except:
                    pass
                self.res_text.insert("end", "\n")
        else:
            self.res_text.insert("end", f"Erreur : {str(res['error'])[:150]}\n")

