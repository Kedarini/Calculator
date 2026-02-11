import tkinter as tk
from tkinter import ttk
import json
from pathlib import Path
from datetime import datetime
import random
import math
import re

# Zakładam, że masz moduł logic.py z funkcjami:
# evaluate_expression(expr) → zwraca string (wynik lub "Division by zero", "Error" itp.)
# set_angle_mode(mode)      → "DEG" / "RAD"
from .logic import evaluate_expression, set_angle_mode


class CalculatorGUI:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Calculator")
        self.root.resizable(False, False)

        # Nord theme colors
        self.BG = "#2e3440"
        self.ENTRY_BG = "#3b4252"
        self.BTN = "#434c5e"
        self.BTN_ALT = "#4c566a"
        self.TEXT = "#eceff4"

        self.root.configure(bg=self.BG)

        # State
        self.entry_var = tk.StringVar()
        self.angle_mode = "DEG"
        self.precision_mode = "FLOAT"
        self.fixed_decimals = 4
        self.memory = 0

        # Historia
        self.history_file = Path("history.json")
        self.history_entries = self.load_history()

        # Display
        self.entry = tk.Entry(
            root,
            font=("Arial", 24, "bold"),
            textvariable=self.entry_var,
            justify="right",
            bg=self.ENTRY_BG,
            fg=self.TEXT,
            insertbackground=self.TEXT,
            bd=0,
            relief="flat"
        )
        self.entry.pack(fill="x", padx=16, pady=(16, 8))

        self.paren_label = tk.Label(
            root,
            text="() depth: 0",
            bg=self.BG,
            fg="#81a1c1",
            anchor="e",
            font=("Arial", 10)
        )
        self.paren_label.pack(fill="x", padx=16)

        # Main container
        main = tk.Frame(root, bg=self.BG)
        main.pack(fill="both", expand=True, padx=12, pady=8)
        main.columnconfigure(1, weight=1)   # historia ma się rozciągać

        # Button frame (left side)
        btn_frame = tk.Frame(main, bg=self.BG)
        btn_frame.grid(row=0, column=0, sticky="n")

        # History frame (right side)
        hist_frame = tk.Frame(main, bg=self.BG)
        hist_frame.grid(row=0, column=1, sticky="nsew", padx=(12, 0))

        tk.Label(
            hist_frame,
            text="History",
            bg=self.BG,
            fg=self.TEXT,
            font=("Arial", 12, "bold")
        ).pack(anchor="w", pady=(0, 4))

        list_container = tk.Frame(hist_frame, bg=self.BG)
        list_container.pack(fill="both", expand=True)

        self.history_box = tk.Listbox(
            list_container,
            font=("Arial", 11),
            width=40,
            bg=self.ENTRY_BG,
            fg=self.TEXT,
            bd=0,
            highlightthickness=0,
            selectbackground=self.BTN_ALT,
            activestyle="none",
        )
        self.history_box.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(list_container, orient="vertical", command=self.history_box.yview)
        scrollbar.pack(side="right", fill="y")
        self.history_box.config(yscrollcommand=scrollbar.set)

        # Wczytujemy i wypełniamy historię
        for entry in self.history_entries:
            self.history_box.insert(tk.END, entry)
        if self.history_entries:
            self.history_box.see(tk.END)

        # ────────────────────────────────────────────────
        # Buttons layout
        # ────────────────────────────────────────────────
        self.buttons = [
            ['DEG',   'FLOAT',  'sin',    'cos',    'tan'],
            ['sin⁻¹', 'cos⁻¹',  'tan⁻¹',  'π',      'e'],
            ['^',     'x³',     'x²',     'eˣ',     '10ˣ'],
            ['ⁿ√x',   '³√x',    '√',      'ln',     'log'],
            ['(',     ')',      '1/x',    '%',      '!'],
            ['7',     '8',      '9',      '+',      'Back'],
            ['4',     '5',      '6',      '-',      'Ans'],
            ['1',     '2',      '3',      '*',      'M+'],
            ['0',     '.',      'EXP',    '/',      'M-'],
            ['±',     'RND',    'AC',     '=',      'MR']
        ]

        unary_immediate = {
            '1/x', '√', '³√x', 'x²', 'x³', '!', '%',
            'sin', 'cos', 'tan', 'sin⁻¹', 'cos⁻¹', 'tan⁻¹',
            'ln', 'log', 'eˣ', '10ˣ'
        }

        for r, row in enumerate(self.buttons):
            for c, char in enumerate(row):
                if char in unary_immediate:
                    cmd = lambda op=char: self.apply_unary(op)
                else:
                    cmd = self.get_command(char)

                bg = self.BTN if char.isdigit() or char == '.' else self.BTN_ALT

                btn = tk.Button(
                    btn_frame,
                    text=char,
                    width=5,
                    height=2,
                    font=("Arial", 14),
                    bg=bg,
                    fg=self.TEXT,
                    bd=0,
                    relief="flat",
                    activebackground="#5e81ac",
                    activeforeground=self.TEXT,
                    command=cmd
                )
                btn.grid(row=r, column=c, padx=4, pady=4, sticky="nsew")

                if char in ('DEG', 'RAD'):
                    self.angle_btn = btn
                if char in ('FLOAT', 'FIXED'):
                    self.precision_btn = btn

        btn_frame.columnconfigure(tuple(range(5)), weight=1)

    # ────────────────────────────────────────────────
    # Historia – metody
    # ────────────────────────────────────────────────

    def load_history(self):
        if not self.history_file.exists():
            return []
        try:
            with self.history_file.open("r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("entries", [])[-200:]
        except:
            return []

    def save_history(self):
        try:
            data = {
                "entries": self.history_entries,
                "last_updated": datetime.now().isoformat()
            }
            with self.history_file.open("w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except:
            pass

    def add_to_history(self, left: str, right: str):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry = f"[{timestamp}] {left} = {right}"
        self.history_entries.append(entry)
        self.history_box.insert(tk.END, entry)
        self.history_box.see(tk.END)
        self.save_history()

    # ────────────────────────────────────────────────
    # Unary operations
    # ────────────────────────────────────────────────

    def apply_unary(self, op):
        current = self.entry_var.get().strip()
        if not current or current == "Error":
            return

        try:
            value = float(current)

            if op == "1/x":
                result = 1 / value
                hist_text = f"1/x({current})"
            elif op in ("√", "√x"):
                result = math.sqrt(value)
                hist_text = f"√({current})"
            elif op == "³√x":
                result = value ** (1/3)
                hist_text = f"³√({current})"
            elif op == "x²":
                result = value ** 2
                hist_text = f"({current})²"
            elif op == "x³":
                result = value ** 3
                hist_text = f"({current})³"
            elif op in ("!", "n!"):
                if not value.is_integer() or value < 0:
                    raise ValueError("Factorial only for non-negative integers")
                result = math.factorial(int(value))
                hist_text = f"{int(value)}!"
            elif op == "%":
                result = value / 100
                hist_text = f"{current}%"
            elif op == "sin":
                rad = math.radians(value) if self.angle_mode == "DEG" else value
                result = math.sin(rad)
                hist_text = f"sin({current})"
            elif op == "cos":
                rad = math.radians(value) if self.angle_mode == "DEG" else value
                result = math.cos(rad)
                hist_text = f"cos({current})"
            elif op == "tan":
                rad = math.radians(value) if self.angle_mode == "DEG" else value
                result = math.tan(rad)
                hist_text = f"tan({current})"
            elif op == "sin⁻¹":
                result = math.degrees(math.asin(value)) if self.angle_mode == "DEG" else math.asin(value)
                hist_text = f"asin({current})"
            elif op == "cos⁻¹":
                result = math.degrees(math.acos(value)) if self.angle_mode == "DEG" else math.acos(value)
                hist_text = f"acos({current})"
            elif op == "tan⁻¹":
                result = math.degrees(math.atan(value)) if self.angle_mode == "DEG" else math.atan(value)
                hist_text = f"atan({current})"
            elif op == "ln":
                result = math.log(value)
                hist_text = f"ln({current})"
            elif op == "log":
                result = math.log10(value)
                hist_text = f"log({current})"
            elif op == "eˣ":
                result = math.exp(value)
                hist_text = f"e^({current})"
            elif op == "10ˣ":
                result = 10 ** value
                hist_text = f"10^({current})"
            else:
                return

            formatted = self.format_number(result)
            self.entry_var.set(formatted)
            self.add_to_history(hist_text, formatted)

        except Exception:
            self.entry_var.set("Error")

    # ────────────────────────────────────────────────
    # Pozostałe metody (bez zmian lub drobne poprawki)
    # ────────────────────────────────────────────────

    def get_command(self, char):
        commands = {
            'AC':     self.clear,
            '=':      self.calculate,
            'Back':   self.backspace,
            '±':      self.toggle_sign,
            'RND':    self.random_number,
            'DEG':    self.toggle_angle,
            'RAD':    self.toggle_angle,
            'FLOAT':  self.toggle_precision,
            'FIXED':  self.toggle_precision,
            'M+':     lambda: self.memory_op('M+'),
            'M-':     lambda: self.memory_op('M-'),
            'MR':     lambda: self.memory_op('MR'),
            'Ans':    lambda: self.append('Ans'),
        }
        return commands.get(char, lambda ch=char: self.append(ch))

    def append(self, ch):
        mapped = {
            'xʸ': '^', 'x²': 'x²', 'x³': 'x³', '√': '√', '³√x': '³√',
            '1/x': '1/x', '!': '!', 'sin⁻¹': 'asin', 'cos⁻¹': 'acos',
            'tan⁻¹': 'atan', 'eˣ': 'exp', '10ˣ': '10^x', 'EXP': '*10^',
        }.get(ch, ch)

        current = self.entry_var.get()
        if current == "Error":
            self.entry_var.set(mapped)
        else:
            self.entry_var.set(current + mapped)
        self.update_paren()

    def backspace(self):
        current = self.entry_var.get()
        if current == "Error":
            self.clear()
        else:
            self.entry_var.set(current[:-1])
        self.update_paren()

    def clear(self):
        self.entry_var.set("")
        self.update_paren()

    def toggle_sign(self):
        expr = self.entry_var.get()
        if expr == "Error":
            return
        m = re.search(r'(-?\d*\.?\d*)$', expr)
        if m:
            num = m.group(1)
            start = m.start(1)
            new_num = num[1:] if num.startswith('-') else '-' + num
            self.entry_var.set(expr[:start] + new_num)
        self.update_paren()

    def calculate(self):
        expr = self.entry_var.get().strip()
        if not expr:
            return

        raw_result = evaluate_expression(expr)
        if "Error" in str(raw_result) or raw_result in ("Division by zero",):
            self.entry_var.set("Error")
            return

        formatted = self.format_number(raw_result)
        self.entry_var.set(formatted)
        self.add_to_history(expr, formatted)

    def toggle_angle(self):
        self.angle_mode = "RAD" if self.angle_mode == "DEG" else "DEG"
        self.angle_btn.config(text=self.angle_mode)
        set_angle_mode(self.angle_mode)

    def toggle_precision(self):
        self.precision_mode = "FIXED" if self.precision_mode == "FLOAT" else "FLOAT"
        self.precision_btn.config(text=self.precision_mode)

    def random_number(self):
        rnd = round(random.random(), 6)
        self.entry_var.set(self.entry_var.get() + str(rnd))

    def memory_op(self, op):
        try:
            if op in ('M+', 'M-'):
                current = self.entry_var.get().strip()
                if not current or current == "Error":
                    return
                val = float(evaluate_expression(current))
                if op == 'M+':
                    self.memory += val
                elif op == 'M-':
                    self.memory -= val
            elif op == 'MR':
                self.entry_var.set(str(self.memory))
        except:
            self.entry_var.set("Error")

    def update_paren(self):
        expr = self.entry_var.get()
        depth = expr.count("(") - expr.count(")")
        color = "#bf616a" if depth < 0 else "#a3be8c" if depth > 0 else "#81a1c1"
        self.paren_label.config(text=f"() depth: {depth}", fg=color)

    def format_number(self, value):
        try:
            v = float(value)
        except:
            return str(value)

        if self.precision_mode == "FIXED":
            s = f"{v:.{self.fixed_decimals}f}"
            return s.rstrip('0').rstrip('.') if '.' in s else s
        if abs(v) >= 1e12 or (0 < abs(v) < 1e-8 and v != 0):
            return f"{v:.8e}"
        return f"{v:g}"


if __name__ == "__main__":
    root = tk.Tk()
    app = CalculatorGUI(root)
    root.mainloop()