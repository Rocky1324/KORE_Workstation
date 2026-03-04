import pint

class PhysicsEngine:
    def __init__(self):
        self.ureg = pint.UnitRegistry()
        
        # Dictionary of universal physical constants
        self.constants = {
            "c": (299792458, "m/s", "Vitesse de la lumière"),
            "G": (6.67430e-11, "m^3/kg/s^2", "Constante gravitationnelle"),
            "h": (6.62607015e-34, "J*s", "Constante de Planck"),
            "e": (1.602176634e-19, "C", "Charge élémentaire"),
            "kB": (1.380649e-23, "J/K", "Constante de Boltzmann"),
            "NA": (6.02214076e23, "mol^-1", "Nombre d'Avogadro"),
            "g": (9.80665, "m/s^2", "Pesanteur terrestre (standard)")
        }

    def convert(self, value, from_unit, to_unit):
        """Converts a value from one unit to another."""
        try:
            quantity = value * self.ureg(from_unit)
            result = quantity.to(to_unit)
            return {
                "success": True,
                "value": result.magnitude,
                "unit": str(result.units)
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_constant(self, name):
        """Returns a constant's value and unit."""
        if name in self.constants:
            val, unit, desc = self.constants[name]
            return {"success": True, "value": val, "unit": unit, "description": desc}
        return {"success": False, "error": f"Constante '{name}' inconnue."}

    def list_constants(self):
        """Returns the list of all constant keys."""
        return list(self.constants.keys())
