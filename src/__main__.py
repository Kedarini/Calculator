import tkinter as tk
from calculator.ui import CalculatorGUI   # adjust import if needed

if __name__ == "__main__":
    root = tk.Tk()                     # ← create the root window here
    app = CalculatorGUI(root)          # ← pass root to the class
    root.mainloop()                    # ← start the event loop
