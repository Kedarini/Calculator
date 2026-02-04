import tkinter as tk
from engine import evaluate_expression
import re

class CalculatorGUI:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Calculator")
        self.root.geometry("300x400")

        self.entry_var = tk.StringVar()

        self.entry = tk.Entry(
            self.root,
            font=("Arial", 12),
            textvariable=self.entry_var
        )
        self.entry.pack(fill="both", padx=10, pady=10)

        self.frame = tk.Frame(self.root)
        self.frame.pack()

        self.buttons = [
            ['7', '8', '9', '/'],
            ['4', '5', '6', '*'],
            ['1', '2', '3', '-'],
            ['C', '0', '=', '+']
        ]

        self.create_buttons()

    def create_buttons(self):
        for r, row in enumerate(self.buttons):
            for c, char in enumerate(row):
                if char == "C":
                    cmd = self.clear
                elif char == "=":
                    cmd = self.calculate
                else:
                    cmd = lambda ch=char: self.append(ch)

                (tk.Button(
                    self.frame,
                    text=char,
                    font=("Arial", 12),
                    width=2,
                    command=cmd
                ).grid(
                    row=r, column=c,
                    padx=5, pady=5)
                )
    def append(self, char: str):
        self.entry_var.set(self.entry_var.get() + char)

    def clear(self):
        self.entry_var.set("")

    def calculate(self):
        expr = self.entry_var.get()
        result = evaluate_expression(expr)
        self.entry_var.set(result)