import csv
import numpy as np

class DataEngine:
    """Moteur de traitement de données pour le Cahier de Laboratoire."""
    
    def __init__(self):
        self.data = {} # { "NomColonne": [val1, val2, ...] }
        self.columns = []
        self.filename = None

    def load_csv(self, filepath):
        """Charge un fichier CSV et extrait les colonnes numériques."""
        try:
            self.data = {}
            self.columns = []
            self.filename = filepath.split('/')[-1].split('\\')[-1]
            
            with open(filepath, 'r', encoding='utf-8-sig') as f:
                # Automagically detect delimiter (comma or semicolon)
                sample = f.read(1024)
                f.seek(0)
                dialect = csv.Sniffer().sniff(sample, delimiters=',;')
                reader = csv.reader(f, dialect)
                
                rows = list(reader)
                if not rows:
                    return {"success": False, "error": "Le fichier CSV est vide."}
                
                # Assume first row is headers
                headers = rows[0]
                
                # Initialize data dict
                temp_data = {h.strip(): [] for h in headers}
                
                # Parse rows
                for row in rows[1:]:
                    for i, val in enumerate(row):
                        if i < len(headers):
                            h = headers[i].strip()
                            try:
                                # Replace comma with dot for French decimals
                                num_val = float(val.replace(',', '.'))
                                temp_data[h].append(num_val)
                            except ValueError:
                                # Ignore non-numeric rows or columns
                                pass
                
                # Keep only columns that have data
                for h in headers:
                    h = h.strip()
                    if len(temp_data[h]) > 0:
                        self.data[h] = np.array(temp_data[h])
                        self.columns.append(h)
                        
            if not self.columns:
                return {"success": False, "error": "Aucune colonne numérique trouvée dans le CSV."}
                
            return {"success": True, "columns": self.columns, "filename": self.filename}
            
        except Exception as e:
            return {"success": False, "error": f"Erreur de lecture CSV: {str(e)}"}

    def perform_regression(self, x_col, y_col, type_reg="Linéaire", degree=2):
        """
        Effectue une régression sur les données sélectionnées.
        type_reg: 'Linéaire' (deg 1) ou 'Polynomiale' (deg > 1)
        """
        if x_col not in self.data or y_col not in self.data:
            return {"success": False, "error": "Colonnes invalides."}
            
        x = self.data[x_col]
        y = self.data[y_col]
        
        # Ensure identical sizes
        min_len = min(len(x), len(y))
        x = x[:min_len]
        y = y[:min_len]

        if len(x) < 2:
            return {"success": False, "error": "Pas assez de points de données."}

        try:
            if type_reg == "Linéaire":
                # y = ax + b
                coeffs = np.polyfit(x, y, 1)
                p = np.poly1d(coeffs)
                
                a, b = coeffs
                eq_str = f"y = {a:.4f}x {'+' if b >= 0 else '-'} {abs(b):.4f}"
                
                # Calculate R-squared
                yhat = p(x)
                ybar = np.sum(y) / len(y)
                ssreg = np.sum((yhat - ybar)**2)
                sstot = np.sum((y - ybar)**2)
                r2 = ssreg / sstot if sstot != 0 else 0
                
                # Generate line points for plotting
                x_line = np.linspace(min(x), max(x), 100)
                y_line = p(x_line)
                
                return {
                    "success": True, 
                    "equation": eq_str, 
                    "r2": r2,
                    "x_line": x_line,
                    "y_line": y_line,
                    "x_data": x,
                    "y_data": y
                }
                
            elif type_reg == "Polynomiale":
                # y = c0*x^d + ... + cd
                coeffs = np.polyfit(x, y, degree)
                p = np.poly1d(coeffs)
                
                # Format equation string
                terms = []
                for i, c in enumerate(coeffs):
                    power = degree - i
                    if power == 0:
                        terms.append(f"{c:.4f}")
                    elif power == 1:
                        terms.append(f"{c:.4f}x")
                    else:
                        terms.append(f"{c:.4f}x^{power}")
                eq_str = "y = " + " + ".join(terms).replace("+ -", "- ")
                
                # Calculate R-squared
                yhat = p(x)
                ybar = np.sum(y) / len(y)
                ssreg = np.sum((yhat - ybar)**2)
                sstot = np.sum((y - ybar)**2)
                r2 = ssreg / sstot if sstot != 0 else 0
                
                x_line = np.linspace(min(x), max(x), 100)
                y_line = p(x_line)
                
                return {
                    "success": True, 
                    "equation": eq_str, 
                    "r2": r2,
                    "x_line": x_line,
                    "y_line": y_line,
                    "x_data": x,
                    "y_data": y
                }

        except np.linalg.LinAlgError:
            return {"success": False, "error": "Singularité matrix lors de la régression."}
        except Exception as e:
            return {"success": False, "error": f"Erreur de calcul: {str(e)}"}
