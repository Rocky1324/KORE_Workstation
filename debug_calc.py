import os
import sys

# Ensure we can import from the current directory
sys.path.append(os.getcwd())

try:
    print("Attempting to import dependencies...")
    import customtkinter as ctk
    print(f"customtkinter version: {ctk.__version__}")
    import sympy as sp
    print(f"sympy version: {sp.__version__}")
    import numpy as np
    print(f"numpy version: {np.__version__}")
    import matplotlib
    print(f"matplotlib version: {matplotlib.__version__}")
    
    from ui.calculator_view import CalculatorView
    print("CalculatorView import success")
    
    root = ctk.CTk()
    root.withdraw() # Don't show the window
    
    print("Instantiating CalculatorView...")
    view = CalculatorView(root)
    print("Success: CalculatorView instantiated.")
    
    # Check widgets
    children = view.winfo_children()
    print(f"Number of child widgets: {len(children)}")
    for i, child in enumerate(children):
        print(f"  Child {i}: {type(child).__name__}")
        
except Exception as e:
    print(f"DIAGNOSTIC FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("DIAGNOSTIC PASSED: CalculatorView seems healthy.")
sys.exit(0)
