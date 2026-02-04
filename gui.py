import tkinter as tk
from engine import evaluate_expression
import random

class CalculatorGUI:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Calculator")
        self.root.geometry("320x575")
        self.root.resizable(False, False)

        self.entry_var = tk.StringVar()
        self.memory = 0  # Memory storage

        # Entry display
        self.entry = tk.Entry(
            self.root,
            font=("Arial", 16),
            textvariable=self.entry_var,
            justify="right",
            bd=5,
            relief="ridge"
        )
        self.entry.pack(fill="both", padx=10, pady=10)

        # Button frame
        self.frame = tk.Frame(self.root)
        self.frame.pack()

        # Button layout
        self.buttons = [
            ['sin','cos','tan'],
            ['sin⁻¹','cos⁻¹', 'tan⁻¹', 'π', 'e'],
            ['xʸ', 'x³', 'x²', 'eˣ', '10ˣ'],
            ['ⁿ√x', '³√x', '√x', 'ln', 'log'],
            ['(', ')', '1/x', '%', 'n!'],
            ['7', '8', '9', '+', 'Back'],
            ['4', '5', '6', '-', 'Ans'],
            ['1', '2', '3', '*', 'M+'],
            ['0', '.', 'EXP', '/', 'M-'],
            ['±', 'RND', 'AC', '=', 'MR']
        ]

        # Mapping GUI labels to engine symbols
        self.button_map = {
            'xʸ': '^',
            'x²': 'x²',
            'x³': 'x³',
            '√x': '√',
            '³√x': '³√',
            'ln': 'ln',
            'log': 'log',
            '1/x': '1/x',
            'n!': '!',
            'sin⁻¹': 'asin',
            'cos⁻¹': 'acos',
            'tan⁻¹': 'atan',
            'eˣ': 'exp',
            'π': 'π',
            'e': 'e',
            'Ans': 'Ans',
            'EXP': '*10^',
            'ⁿ√x': 'root',  # custom handling
        }

        self.create_buttons()

    def create_buttons(self):
        for r, row in enumerate(self.buttons):
            for c, char in enumerate(row):
                if char == "AC":
                    cmd = self.clear
                elif char == "=":
                    cmd = self.calculate
                elif char == "Back":
                    cmd = self.backspace
                elif char == "±":
                    cmd = self.toggle_sign
                elif char == "RND":
                    cmd = self.random_number
                elif char in ['M+', 'M-', 'MR']:
                    cmd = lambda ch=char: self.memory_control(ch)
                else:
                    cmd = lambda ch=char: self.append(ch)

                tk.Button(
                    self.frame,
                    text=char,
                    font=("Arial", 14),
                    height=1,
                    width=2,
                    bg="beige" if char.isdigit() or char in {'AC', '=', '.', 'Ans'} else "lightgray",
                    command=cmd
                ).grid(
                    row=r, column=c,
                    padx=5, pady=5
                )

    def append(self, char: str):
        mapped = self.button_map.get(char, char)

        # Clear the entry if it currently shows "Error" or "Division by zero"
        current = self.entry_var.get()
        if current in ["Error", "Division by zero"]:
            self.entry_var.set("")

        # Custom handling for root function (ⁿ√x)
        if mapped == 'root':
            self.entry_var.set(self.entry_var.get() + "^(1/")  # user will type n then close parenthesis
        else:
            self.entry_var.set(self.entry_var.get() + mapped)

    # Clear entry
    def clear(self):
        self.entry_var.set("")

    # Backspace
    def backspace(self):
        current = self.entry_var.get()
        self.entry_var.set(current[:-1])

    # Toggle sign of last number
    def toggle_sign(self):
        expr = self.entry_var.get()
        if not expr:
            return
        # Find last number in the string
        import re
        match = re.search(r'(\d+\.?\d*|\.\d+)$', expr)
        if match:
            num = match.group(1)
            start = match.start(1)
            if num.startswith('-'):
                num = num[1:]
            else:
                num = '-' + num
            self.entry_var.set(expr[:start] + num)

    # Insert random number
    def random_number(self):
        rnd = str(round(random.random(), 6))
        self.entry_var.set(self.entry_var.get() + rnd)

    # Memory control
    def memory_control(self, action):
        try:
            if action == 'M+':
                self.memory += float(evaluate_expression(self.entry_var.get()))
            elif action == 'M-':
                self.memory -= float(evaluate_expression(self.entry_var.get()))
            elif action == 'MR':
                self.entry_var.set(self.entry_var.get() + str(self.memory))
        except:
            self.entry_var.set("Error")

    # Calculate expression
    def calculate(self):
        expr = self.entry_var.get()
        try:
            # Replace custom root notation like ^(1/n) if needed
            result = evaluate_expression(expr)
            self.entry_var.set(result)
        except Exception:
            self.entry_var.set("Error")