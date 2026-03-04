import os
import tkinter as tk
from PIL import Image, ImageGrab, ImageOps, ImageFilter
import pytesseract

class Snipper:
    """A helper class to create a cross-platform screen selection UI."""
    def __init__(self, master=None):
        self.root = tk.Toplevel(master)
        self.root.attributes('-alpha', 0.15) 
        self.root.attributes('-fullscreen', True)
        self.root.attributes('-topmost', True)
        self.root.config(cursor="cross")
        
        self.canvas = tk.Canvas(self.root, cursor="cross", bg="grey", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        
        self.start_x = None
        self.start_y = None
        self.rect = None
        self.selection = None

        self.canvas.bind("<ButtonPress-1>", self.on_button_press)
        self.canvas.bind("<B1-Motion>", self.on_move_press)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)
        self.root.bind("<Escape>", lambda e: self.root.destroy())

    def on_button_press(self, event):
        self.start_x = self.root.winfo_pointerx()
        self.start_y = self.root.winfo_pointery()
        self.rect = self.canvas.create_rectangle(self.start_x, self.start_y, self.start_x, self.start_y, outline='red', width=2)

    def on_move_press(self, event):
        cur_x = self.root.winfo_pointerx()
        cur_y = self.root.winfo_pointery()
        self.canvas.coords(self.rect, self.start_x, self.start_y, cur_x, cur_y)

    def on_button_release(self, event):
        end_x = self.root.winfo_pointerx()
        end_y = self.root.winfo_pointery()
        
        x1 = min(self.start_x, end_x)
        y1 = min(self.start_y, end_y)
        x2 = max(self.start_x, end_x)
        y2 = max(self.start_y, end_y)
        
        if x2 - x1 > 5 and y2 - y1 > 5:
            self.selection = (x1, y1, x2, y2)
        
        self.root.destroy()

    def get_selection(self):
        self.root.wait_window() 
        return self.selection

class VisionEngine:
    """Handles screen capture and OCR for mathematical formulas."""
    
    def __init__(self):
        self.temp_dir = "temp"
        if not os.path.exists(self.temp_dir):
            os.makedirs(self.temp_dir)
        
        # Windows-specific Tesseract Configuration
        tess_path = r'C:\Users\khysh\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'
        if os.path.exists(tess_path):
            pytesseract.pytesseract.tesseract_cmd = tess_path
        else:
            fallback = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
            if os.path.exists(fallback):
                pytesseract.pytesseract.tesseract_cmd = fallback

    def capture_screen_area(self, master=None):
        """Launches a selection UI and captures the user-defined region."""
        snipper = Snipper(master)
        area = snipper.get_selection()
        
        if not area:
            return None
            
        img = ImageGrab.grab(bbox=area, all_screens=True)
        path = os.path.join(self.temp_dir, "capture.png")
        img.save(path)
        return path

    def _preprocess_image(self, image_path, mode="text"):
        """Applies advanced image processing to maximize Tesseract precision."""
        img = Image.open(image_path)
        img = ImageOps.grayscale(img)
        
        # Upscale x2 for better detection of small math symbols
        w, h = img.size
        img = img.resize((w*3, h*3), Image.Resampling.LANCZOS)
        
        if mode == "formula":
            # Adaptive-like thresholding for formulas
            img = img.point(lambda p: 255 if p > 165 else 0)
            img = img.filter(ImageFilter.EDGE_ENHANCE_MORE)
        else:
            img = img.point(lambda p: 255 if p > 130 else 0)
            img = img.filter(ImageFilter.SHARPEN)
        
        processed_path = os.path.join(self.temp_dir, f"processed_{mode}.png")
        img.save(processed_path)
        return processed_path

    def extract_formula(self, image_path):
        """Multi-pass OCR with post-processing correction logic."""
        if not image_path:
            return {"success": False, "error": "Capture annulée."}
            
        try:
            # Pass 1: Standard (Text alignment)
            p_text = self._preprocess_image(image_path, mode="text")
            try:
                res_text = pytesseract.image_to_string(p_text, lang='fra+eng', config='--psm 6').strip()
            except:
                res_text = pytesseract.image_to_string(p_text, lang='eng', config='--psm 6').strip()
            
            # Pass 2: Sparse/Math (Equation focus)
            p_math = self._preprocess_image(image_path, mode="formula")
            # PSM 11: Sparse text. Find as much text as possible in no particular order.
            res_math = pytesseract.image_to_string(p_math, lang='eng', config='--psm 11').strip()
            
            # Smart Selection & Post-processing
            final = res_text
            # If math found suspicious symbols like '=' or '+', it's likely a formula
            if any(c in res_math for c in "=+-*/^()"):
                final = res_math
            
            # Common Math OCR corrections
            corrections = {
                '|': '1',
                '©': '0',
                'O': '0', # Often confused in math
                'x': '*', # Sometimes better to standardize
                '—': '-',
                '¢': 'c'
            }
            # Only apply some if they look out of place (contextual logic could go here)
            
            return {"success": True, "text": final}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def mock_ocr(self, image_path):
        """Simulates recognition for testing purposes."""
        return {"success": True, "text": "E = m c^2", "is_mock": True}
