import tkinter as tk
from engine import evaluate_expression
import random
import re

class CalculatorGUI:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Calculator")
        self.root.geometry("320x575")
        self.root.resizable(False, False)

        # =====================
        # Nord color palette
        # =====================
        self.BG = "#2e3440"
        self.ENTRY_BG = "#3b4252"
        self.BTN = "#434c5e"
        self.BTN_ALT = "#4c566a"
        self.TEXT = "#eceff4"

        self.root.configure(bg=self.BG)

        self.entry_var = tk.StringVar()
        self.memory = 0

        # =====================
        # Entry display
        # =====================
        self.entry = tk.Entry(
            self.root,
            font=("Arial", 18),
            textvariable=self.entry_var,
            justify="right",
            bg=self.ENTRY_BG,
            fg=self.TEXT,
            insertbackground=self.TEXT,
            bd=0,
            relief="flat"
        )
        self.entry.pack(fill="both", padx=10, pady=(10, 15))

        # =====================
        # Button frame
        # =====================
        self.frame = tk.Frame(self.root, bg=self.BG)
        self.frame.pack()

        # =====================
        # Button layout
        # =====================
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
            'ⁿ√x': 'root',
        }

        self.create_buttons()

    # =====================
    # Buttons
    # =====================
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

                # Color logic
                if char.isdigit() or char == '.':
                    bg = self.BTN
                elif char in {'+', '-', '*', '/', '='}:
                    bg = self.BTN_ALT
                else:
                    bg = self.BTN_ALT

                tk.Button(
                    self.frame,
                    text=char,
                    font=("Arial", 14),
                    height=1,
                    width=2,
                    bg=bg,
                    fg=self.TEXT,
                    activebackground=self.BTN,
                    activeforeground=self.TEXT,
                    bd=0,
                    relief="flat",
                    command=cmd
                ).grid(row=r, column=c, padx=4, pady=4)

    # =====================
    # Calculator logic
    # =====================
    def append(self, char: str):
        mapped = self.button_map.get(char, char)
        current = self.entry_var.get()
        if current in ["Error", "Division by zero"]:
            self.entry_var.set("")

        if mapped == 'root':
            self.entry_var.set(self.entry_var.get() + "^(1/")
        else:
            self.entry_var.set(self.entry_var.get() + mapped)

    def clear(self):
        self.entry_var.set("")

    def backspace(self):
        self.entry_var.set(self.entry_var.get()[:-1])

    def toggle_sign(self):
        expr = self.entry_var.get()
        match = re.search(r'(\d+\.?\d*|\.\d+)$', expr)
        if match:
            num = match.group(1)
            start = match.start(1)
            num = num[1:] if num.startswith('-') else '-' + num
            self.entry_var.set(expr[:start] + num)

    def random_number(self):
        self.entry_var.set(self.entry_var.get() + str(round(random.random(), 6)))

    def memory_control(self, action):
        try:
            value = float(evaluate_expression(self.entry_var.get()))
            if action == 'M+':
                self.memory += value
            elif action == 'M-':
                self.memory -= value
            elif action == 'MR':
                self.entry_var.set(self.entry_var.get() + str(self.memory))
        except:
            self.entry_var.set("Error")

    def calculate(self):
        try:
            result = evaluate_expression(self.entry_var.get())
            self.entry_var.set(result)
        except:
            self.entry_var.set("Error")
