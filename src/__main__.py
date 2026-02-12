import tkinter as tk
from calculator.ui import CalculatorGUI

def main():
    root = tk.Tk()
    CalculatorGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()