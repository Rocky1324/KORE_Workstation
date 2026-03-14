import sys
import os
import tkinter as tk
import traceback

# Setup path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    print("Importing...")
    from ui.latex_preview_view import LatexPreviewView
    print("Initialize root...")
    root = tk.Tk()
    
    print("Initialize LatexPreviewView...")
    # Mocking master as root
    lp = LatexPreviewView(root)
    lp.pack(fill="both", expand=True)
    root.update()
    
    print("Updating preview...")
    lp.update_preview()
    
    print("SUCCESS: No exceptions in initialization")
except Exception as e:
    print("FATAL ERROR CAUGHT")
    traceback.print_exc()
