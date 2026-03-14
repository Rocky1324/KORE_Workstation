import json
import os
import glob
from database.db_manager import DBManager

class ThemeManager:
    _instance = None
    
    # Default fallback colors in case a theme is missing keys
    DEFAULT_COLORS = {
        "bg_primary": "#1A1A1A",
        "bg_secondary": "#2D2D2D",
        "bg_tertiary": "#3A3A3A",
        "fg_button": "#1f538d",
        "fg_button_hover": "#2a6ab3",
        "fg_button_success": "#2db34a",
        "fg_button_danger": "#cc0000",
        "text_primary": "#FFFFFF",
        "text_secondary": "#A0AEC0",
        "accent": "#00F3FF",
        "sidebar": "#1E1E1E",
        "card": "#242424",
        "border": "#444444"
    }

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ThemeManager, cls).__new__(cls)
            cls._instance.initialize()
        return cls._instance

    def initialize(self):
        self.db = DBManager()
        self.themes_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "themes")
        if not os.path.exists(self.themes_dir):
            os.makedirs(self.themes_dir)
            
        self.available_themes = {}
        self.current_theme_name = "default_dark"
        self.colors = self.DEFAULT_COLORS.copy()
        
        self.load_all_themes()
        
        # Load saved theme preference
        saved_theme = self.db.get_setting("active_theme", "default_dark")
        self.set_theme(saved_theme)

    def load_all_themes(self):
        self.available_themes.clear()
        
        # Always inject a built-in default if file doesn't exist
        self.available_themes["default_dark"] = {
            "name": "Default Dark",
            "colors": self.DEFAULT_COLORS.copy()
        }
        
        for filepath in glob.glob(os.path.join(self.themes_dir, "*.json")):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    theme_data = json.load(f)
                    theme_id = os.path.basename(filepath).replace('.json', '')
                    self.available_themes[theme_id] = theme_data
            except Exception as e:
                print(f"Error loading theme {filepath}: {e}")

    def list_themes(self):
        """Return a list of tuples: (theme_id, display_name)"""
        return [(tid, data.get("name", tid)) for tid, data in self.available_themes.items()]

    def set_theme(self, theme_id):
        if theme_id in self.available_themes:
            self.current_theme_name = theme_id
            theme_data = self.available_themes[theme_id]
            
            # Update colors, falling back to defaults for missing keys
            new_colors = theme_data.get("colors", {})
            for key in self.DEFAULT_COLORS:
                self.colors[key] = new_colors.get(key, self.DEFAULT_COLORS[key])
                
            self.db.set_setting("active_theme", theme_id)
            return True
        return False

    def get_color(self, color_name):
        return self.colors.get(color_name, self.DEFAULT_COLORS.get(color_name, "#FFFFFF"))

# Expose a singleton instance easily
theme_manager = ThemeManager()
