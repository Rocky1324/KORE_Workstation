import numpy as np
import sympy as sp  # Kept for get_custom_model (lambdify / symbolic parsing)

class LabEngine:
    """Computational engine for simulations (Circuits & Physics)."""
    
    # --- CIRCUIT SOLVER (NumPy / LAPACK) ---
    def solve_circuit(self, components):
       
        try:
            # ── 0. ERC — Electrical Rules Check ──────────────────────────
            for c in components:
                if c['n1'] == c['n2']:
                    type_label = {
                        'V':  "Source de tension",
                        'I':  "Source de courant",
                        'AM': "Ampèremètre",
                        'R':  "Résistance",
                        'VM': "Voltmètre",
                    }.get(c['type'], c['type'])
                    node_id = c['n1']
                    return {
                        "success": False,
                        "error": (
                            f"[ERC] {type_label} '{c['name']}' court-circuitée : "
                            f"les deux bornes sont sur le même nœud N{node_id}.\n"
                            f"→ Déplacez une borne sur un nœud différent."
                        )
                    }

            # ── 1. Determine matrix size ──────────────────────────────────
            nodes = set()
            for c in components:
                nodes.add(c['n1'])
                nodes.add(c['n2'])

            num_nodes = max(nodes)  # excludes ground (node 0)

            v_sources = [c for c in components if c['type'] in ['V', 'AM']]
            num_v = len(v_sources)
            size = num_nodes + num_v

            # ── 2. Build MNA matrices in float64 (NumPy) ─────────────────
            G = np.zeros((size, size), dtype=np.float64)
            I = np.zeros(size, dtype=np.float64)

            v_idx = 0
            for c in components:
                n1, n2 = c['n1'], c['n2']

                # Parse value: strip units if present
                try:
                    raw_val = str(c['value']).replace('Ω', '').replace('V', '').replace('A', '').strip()
                    f_val = float(raw_val)
                except (ValueError, TypeError):
                    f_val = 100.0  # safe default

                if c['type'] in ['R', 'VM']:
                    # Voltmeter modelled as 1 MΩ (high but finite, avoids singularity)
                    actual_val = 1_000_000.0 if c['type'] == 'VM' else f_val
                    cond = 1.0 / actual_val  # conductance

                    if n1 > 0:
                        G[n1-1, n1-1] += cond
                        if n2 > 0:
                            G[n1-1, n2-1] -= cond
                            G[n2-1, n1-1] -= cond
                    if n2 > 0:
                        G[n2-1, n2-1] += cond

                elif c['type'] in ['V', 'AM']:
                    # Ammeter = ideal 0 V voltage source
                    actual_val = 0.0 if c['type'] == 'AM' else f_val
                    ci = num_nodes + v_idx  # current variable row/col

                    if n1 > 0:
                        G[n1-1, ci] += 1.0
                        G[ci, n1-1] += 1.0
                    if n2 > 0:
                        G[n2-1, ci] -= 1.0
                        G[ci, n2-1] -= 1.0
                    I[ci] = actual_val
                    v_idx += 1

                elif c['type'] == 'I':
                    if n1 > 0:
                        I[n1-1] -= f_val  # current leaving node
                    if n2 > 0:
                        I[n2-1] += f_val  # current entering node

            # ── 3. Solve  G·x = I  (LAPACK via NumPy) ────────────────────
            # Primary solver: exact LU decomposition (microseconds for small circuits)
            try:
                sol = np.linalg.solve(G, I)
            except np.linalg.LinAlgError:
                # Fallback: least-squares — handles singular/near-singular matrices
                sol, _, _, _ = np.linalg.lstsq(G, I, rcond=None)

            # ── 4. Package results ────────────────────────────────────────
            results = {}
            for i in range(num_nodes):
                results[f"Node {i+1}"] = round(float(sol[i]), 10)

            for i, v in enumerate(v_sources):
                results[f"Current through {v['name']}"] = round(float(sol[num_nodes + i]), 10)

            return {"success": True, "results": results}

        except Exception as e:
            return {"success": False, "error": str(e)}

    # --- PHYSICS SIMULATOR (RK4) ---
    def simulate_dynamic_system(self, deriv_func, y0, t_span, dt=0.01):
        """
        Numerical integration using Runge-Kutta 4.
        deriv_func: f(t, y) returning dy/dt
        y0: initial state vector [pos, vel, ...]
        t_span: (t_start, t_end)
        """
        t = np.arange(t_span[0], t_span[1], dt)
        y = np.zeros((len(t), len(y0)))
        y[0] = y0
        
        for i in range(len(t) - 1):
            ti = t[i]
            yi = y[i]
            
            k1 = np.array(deriv_func(ti, yi))
            k2 = np.array(deriv_func(ti + dt/2, yi + dt*k1/2))
            k3 = np.array(deriv_func(ti + dt/2, yi + dt*k2/2))
            k4 = np.array(deriv_func(ti + dt, yi + dt*k3))
            
            y[i+1] = yi + (dt/6) * (k1 + 2*k2 + 2*k3 + k4)
            
        return t, y

    def get_preset_pendulum(self, L=1.0, g=9.81):
        """Returns deriv_func for a simple pendulum [theta, omega]."""
        def deriv(t, y):
            theta, omega = y
            d_theta = omega
            d_omega = -(g/L) * np.sin(theta)
            return [d_theta, d_omega]
        return deriv

    def get_preset_oscillator(self, k=10.0, m=1.0, b=0.1):
        """Returns deriv_func for a damped mass-spring system [x, v]."""
        def deriv(t, y):
            x, v = y
            dx = v
            dv = -(k/m)*x - (b/m)*v
            return [dx, dv]
        return deriv

    def get_preset_double_pendulum(self, L1=1.0, L2=1.0, M1=1.0, M2=1.0, g=9.81):
        """Returns deriv_func for a chaotic double pendulum [theta1, omega1, theta2, omega2]."""
        def deriv(t, y):
            th1, w1, th2, w2 = y
            
            # Equations using the standard Lagrangian formulation
            delta = th1 - th2
            den = (2*M1 + M2 - M2 * np.cos(2*th1 - 2*th2))
            
            d_th1 = w1
            d_w1 = (-g * (2*M1 + M2) * np.sin(th1) - M2 * g * np.sin(th1 - 2*th2) - 
                    2 * np.sin(th1 - th2) * M2 * (w2**2 * L2 + w1**2 * L1 * np.cos(th1 - th2))) / (L1 * den)
            
            d_th2 = w2
            d_w2 = (2 * np.sin(th1 - th2) * (w1**2 * L1 * (M1 + M2) + 
                    g * (M1 + M2) * np.cos(th1) + w2**2 * L2 * M2 * np.cos(th1 - th2))) / (L2 * den)
            
            return [d_th1, d_w1, d_th2, d_w2]
        return deriv

    def get_preset_lorenz(self, sigma=10.0, beta=8/3, rho=28.0):
        """Returns deriv_func for the Lorenz attractor (Chaos theory) [x, y, z]."""
        def deriv(t, state):
            x, y, z = state
            dx = sigma * (y - x)
            dy = x * (rho - z) - y
            dz = x * y - beta * z
            return [dx, dy, dz]
        return deriv

    def get_custom_model(self, formulas, vars=["x", "v"]):
        """
        Generates a deriv_func from string formulas.
        formulas: ["v", "-9.81 - 0.1*v"] (corresponds to dx/dt, dv/dt)
        """
        try:
            # Create symbols
            t_sym = sp.Symbol('t')
            var_syms = [sp.Symbol(v) for v in vars]
            
            # Parse formulas
            f_exprs = [sp.sympify(f) for f in formulas]
            
            # Create lambdas
            # lambdify expects (args, expr)
            funcs = [sp.lambdify([t_sym] + var_syms, expr, 'numpy') for expr in f_exprs]
            
            def deriv(t, y):
                # y is the state vector
                return [f(t, *y) for f in funcs]
            
            return deriv
        except Exception as e:
            raise ValueError(f"Erreur de parsing : {str(e)}")
