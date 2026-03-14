import sys
import os
import tkinter as tk
import traceback

# Setup path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    print("Importing...")
    from ui.graph_view import GraphView
    print("Initialize root...")
    root = tk.Tk()
    
    print("Initialize GraphView...")
    gv = GraphView(root)
    gv.pack(fill="both", expand=True)
    root.update()
    
    print("Loading graph data manually...")
    gv._load_graph()
    
    print("Running physics step 1...")
    gv._apply_physics()
    gv._apply_physics()
    
    print("Running draw...")
    gv._render_graph()
    
    print("SUCCESS: No exceptions in initialization and first frame")
except Exception as e:
    print("FATAL ERROR CAUGHT")
    traceback.print_exc()
