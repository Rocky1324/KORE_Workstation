import os
import sys

# Ensure the database and core directories can be imported
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ui.app import MainWindow

def main():
    app = MainWindow()
    app.mainloop()

if __name__ == "__main__":
    main()
