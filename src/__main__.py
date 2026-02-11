# src/calculator/__main__.py

import sys
import tkinter as tk

from src.calculator.ui import CalculatorGUI


def main():
    if len(sys.argv) > 1 and sys.argv[1] in ("--help", "-h"):
        print("Scientific Calculator")
        print("Usage: python -m calculator")
        return 0

    root = tk.Tk()
    app = CalculatorGUI(root)
    root.mainloop()
    return 0


if __name__ == "__main__":
    sys.exit(main())