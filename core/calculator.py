import sympy as sp
import numpy as np

class CalcEngine:
    """Core engine for symbolic and numerical calculations using SymPy."""
    
    def __init__(self):
        self.x = sp.Symbol('x')
        self.y = sp.Symbol('y')

    def _clean_input(self, text):
        """Cleans input: removes 'f(x)=', 'y=', handles '=' and adds * for implicit multiplication."""
        import re
        t = text.lower().strip()
        
        # Remove common function prefixes
        t = re.sub(r'^(f\(x\)|y|g\(x\))\s*=\s*', '', t)
        
        # Handle the '=' sign: convert 'a = b' into 'a - (b)'
        # This allows SymPy to solve it as an expression equal to zero.
        if '=' in t:
            # Handle '==' if user typed it
            t = t.replace('==', '=')
            if '=' in t and not any(op in t for op in ['<', '>', '<=', '>=']):
                parts = t.split('=')
                if len(parts) == 2:
                    t = f"({parts[0]}) - ({parts[1]})"
        
        # Replace implicit multiplication (number followed by variable)
        # 3x -> 3*x, 5(x+1) -> 5*(x+1)
        t = re.sub(r'(\d)([a-z\(])', r'\1*\2', t)
        # (x+1)y -> (x+1)*y
        t = re.sub(r'(\))([a-z])', r'\1*\2', t)
        
        return t

    def evaluate(self, expr_str):
        """Evaluates a basic arithmetic expression."""
        try:
            cleaned = self._clean_input(expr_str)
            expr = sp.sympify(cleaned)
            return {"success": True, "result": float(expr.evalf()), "type": "result"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def solve_equation(self, eq_str):
        """Solves a single equation or inequality."""
        try:
            cleaned = self._clean_input(eq_str)
            # Check if it's an inequality
            if any(op in cleaned for op in ['<', '>', '<=', '>=']):
                expr = sp.sympify(cleaned)
                # Try to solve as univariate inequality first
                try:
                    solutions = sp.solve_univariate_inequality(expr, self.x, relational=False)
                except:
                    solutions = sp.reduce_inequalities(expr, [self.x, self.y])
                return {"success": True, "result": solutions, "type": "inequality"}
            
            expr = sp.sympify(cleaned)
            solutions = sp.solve(expr, self.x)
            return {"success": True, "result": solutions, "type": "equation"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def solve_system(self, eq_list):
        """Solves a system of equations or inequalities."""
        try:
            cleaned_eqs = [self._clean_input(eq) for eq in eq_list]
            # Check if any input is an inequality
            has_ineq = any(any(op in eq for op in ['<', '>', '<=', '>=']) for eq in cleaned_eqs)
            
            exprs = [sp.sympify(eq) for eq in cleaned_eqs]
            
            if has_ineq:
                # sp.reduce_inequalities with [x, y] often fails with "more than one symbol"
                # We try to reduce it to a primary relationship for x
                try:
                    solutions = sp.reduce_inequalities(exprs, self.x)
                except Exception:
                    # Fallback: try to just keep the set of inequalities if reduction fails
                    solutions = exprs
                return {"success": True, "result": solutions, "type": "system_ineq"}
            else:
                # sp.solve is standard for systems of equations
                solutions = sp.solve(exprs, (self.x, self.y))
                return {"success": True, "result": solutions, "type": "system"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def calculate_integral(self, expr_str, var='x'):
        """Calculates the indefinite or definite integral."""
        try:
            cleaned = self._clean_input(expr_str)
            # Basic check for definite integral syntax: "x**2 from 0 to 1"
            import re
            match = re.search(r'(.+)\s+from\s+(.+)\s+to\s+(.+)', cleaned)
            if match:
                expr = sp.sympify(match.group(1).strip())
                low = sp.sympify(match.group(2).strip())
                high = sp.sympify(match.group(3).strip())
                v = sp.Symbol(var)
                result = sp.integrate(expr, (v, low, high))
                return {"success": True, "result": result, "type": "definite_integral"}

            expr = sp.sympify(cleaned)
            v = sp.Symbol(var)
            result = sp.integrate(expr, v)
            return {"success": True, "result": f"{result} + C", "type": "integral"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_plot_data(self, expr_str, x_range=(-10, 10), points=200):
        """Generates (x, y) coordinates for plotting a 2D function."""
        try:
            cleaned = self._clean_input(expr_str)
            expr = sp.sympify(cleaned)
            # Ensure it's simplified
            expr = sp.simplify(expr)
            
            # Use 'x' as default if no variables found (constant)
            vars = list(expr.free_symbols)
            v = vars[0] if vars else self.x
            
            f = sp.lambdify(v, expr, 'numpy')
            
            x_vals = np.linspace(x_range[0], x_range[1], points)
            y_vals = f(x_vals)
            
            # Handle possible complex/inf results from numpy
            if isinstance(y_vals, (np.ndarray, list)):
                y_vals = np.nan_to_num(y_vals, nan=np.nan, posinf=np.nan, neginf=np.nan)
            
            return {"success": True, "x": x_vals, "y": y_vals}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_plot3d_data(self, expr_str, x_range=(-5, 5), y_range=(-5, 5), points=50):
        """Generates (X, Y, Z) meshgrid for plotting a 3D surface."""
        try:
            cleaned = self._clean_input(expr_str)
            expr = sp.sympify(cleaned)
            
            # lambdify for two variables
            f = sp.lambdify((self.x, self.y), expr, 'numpy')
            
            x = np.linspace(x_range[0], x_range[1], points)
            y = np.linspace(y_range[0], y_range[1], points)
            X, Y = np.meshgrid(x, y)
            Z = f(X, Y)
            
            # Clean Z values
            Z = np.nan_to_num(Z, nan=np.nan, posinf=np.nan, neginf=np.nan)
            
            return {"success": True, "X": X, "Y": Y, "Z": Z}
        except Exception as e:
            return {"success": False, "error": str(e)}
