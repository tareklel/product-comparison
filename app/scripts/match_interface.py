from app.setup_comparison import setup_comparison
import argparse
import tkinter as tk
from app.interface import LoadPage

# Create Tkinter window and the app instance
if __name__ == '__main__':
    root = tk.Tk()
    app = LoadPage(root)
    root.mainloop()
