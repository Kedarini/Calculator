import tkinter as tk
from tkinter import ttk
import json
from pathlib import Path
from datetime import datetime
import random
import math
import re
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

        hist_header = tk.Frame(hist_frame, bg=self.BG)
        hist_header.pack(fill="x", pady=(0, 4))

        tk.Label(
            hist_header,
            text="History",
            bg=self.BG,
            fg=self.TEXT,
            font=("Arial", 12, "bold")
        ).pack(side="left")

        clear_btn = tk.Button(
            hist_header,
            text="Clear",
            font=("Arial", 10, "bold"),
            bg=self.BTN_ALT,
            fg=self.TEXT,
            bd=0,
            padx=10,
            pady=2,
            relief="flat",
            activebackground="#5e81ac",
            activeforeground=self.TEXT,
            command=self.clear_history
        )
        clear_btn.pack(side="right")

        list_container = tk.Frame(hist_frame, bg=self.BG)
        list_container.pack(fill="both", expand=True)

        self.history_box = tk.Listbox(
            list_container,
            font=("Arial", 11),
            width=40,
            height=2,
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

    def clear_history(self):
            self.history_entries.clear()
            self.history_box.delete(0, tk.END)
            with self.history_file.open("w", encoding="utf-8") as f:
                json.dump({}, f, indent=2)

    # ────────────────────────────────────────────────
    # Unary operations
    # ────────────────────────────────────────────────

    def apply_unary(self, op):
        current = self.entry_var.get().strip()
        if not current or current == "Error":
            return

        try:
            value = float(current)

            # ─── Simple operations ───────────────────────────────────────────
            simple_ops = {
                "1/x": (lambda x: 1 / x, lambda c: f"1/x({c})"),
                "√": (math.sqrt, lambda c: f"√({c})"),
                "√x": (math.sqrt, lambda c: f"√({c})"),
                "³√x": (lambda x: x ** (1 / 3), lambda c: f"³√({c})"),
                "x²": (lambda x: x ** 2, lambda c: f"({c})²"),
                "x³": (lambda x: x ** 3, lambda c: f"({c})³"),
                "%": (lambda x: x / 100, lambda c: f"{c}%"),
                "ln": (math.log, lambda c: f"ln({c})"),
                "log": (math.log10, lambda c: f"log({c})"),
                "eˣ": (math.exp, lambda c: f"e^({c})"),
                "10ˣ": (lambda x: 10 ** x, lambda c: f"10^({c})"),
            }

            if op in simple_ops:
                func, hist_fmt = simple_ops[op]
                result = func(value)
                hist_text = hist_fmt(current)

            # ─── Factorial ──────────────────────────────────────────────────
            elif op in ("!", "n!"):
                if not value.is_integer() or value < 0:
                    raise ValueError("Factorial only for non-negative integers")
                result = math.factorial(int(value))
                hist_text = f"{int(value)}!"

            # ─── Trigonometric functions ────────────────────────────────────
            elif op in ("sin", "cos", "tan"):
                func = {"sin": math.sin, "cos": math.cos, "tan": math.tan}[op]
                rad = math.radians(value) if self.angle_mode == "DEG" else value
                result = func(rad)
                hist_text = f"{op}({current})"

            elif op in ("sin⁻¹", "cos⁻¹", "tan⁻¹"):
                func = {"sin⁻¹": math.asin, "cos⁻¹": math.acos, "tan⁻¹": math.atan}[op]
                val = func(value)
                result = math.degrees(val) if self.angle_mode == "DEG" else val
                # nicer history names: asin / acos / atan
                clean_op = {"sin⁻¹": "asin", "cos⁻¹": "acos", "tan⁻¹": "atan"}[op]
                hist_text = f"{clean_op}({current})"

            else:
                return

            formatted = self.format_number(result)
            self.entry_var.set(formatted)
            self.add_to_history(hist_text, formatted)

        except Exception:
            self.entry_var.set("Error")

    # ────────────────────────────────────────────────
    # Pozostałe metody
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

    def toggle_precision(self):
        self.precision_mode = "FIXED" if self.precision_mode == "FLOAT" else "FLOAT"
        self.precision_btn.config(text=self.precision_mode)

    def toggle_angle(self):
        self.angle_mode = "RAD" if self.angle_mode == "DEG" else "DEG"
        self.angle_btn.config(text=self.angle_mode)
        set_angle_mode(self.angle_mode)

    def random_number(self):
        self.entry_var.set(self.entry_var.get() + f"{random.random():.6f}")

    def memory_op(self, op):
        try:
            current = self.entry_var.get().strip()
            if not current or current == "Error":
                return

            if op == "MR":
                self.entry_var.set(str(self.memory))
                return

            # M+ / M-
            val = float(evaluate_expression(current))
            if op == "M+":
                self.memory += val
            else:  # M-
                self.memory -= val

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
        except (TypeError, ValueError):
            return str(value)

        if self.precision_mode == "FIXED":
            s = f"{v:.{self.fixed_decimals}f}"
            return s.rstrip("0").rstrip(".") if "." in s else s

        if v == 0:
            return "0"

        if abs(v) >= 1e12 or (0 < abs(v) < 1e-8):
            return f"{v:.8e}"

        return f"{v:g}"