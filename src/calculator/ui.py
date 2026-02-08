import tkinter as tk
from tkinter import ttk
from logic import evaluate_expression, set_angle_mode
import random
import re

class CalculatorGUI:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Calculator")
        self.root.geometry("600x530")
        self.root.resizable(False, False)

        # ===== Nord colors =====
        self.BG = "#2e3440"
        self.ENTRY_BG = "#3b4252"
        self.BTN = "#434c5e"
        self.BTN_ALT = "#4c566a"
        self.TEXT = "#eceff4"

        self.root.configure(bg=self.BG)

        # ===== State =====
        self.entry_var = tk.StringVar()
        self.angle_mode = "DEG"
        self.precision_mode = "FLOAT"
        self.fixed_decimals = 4
        self.memory = 0

        # ===== Display =====
        self.entry = tk.Entry(
            root,
            font=("Arial", 18),
            textvariable=self.entry_var,
            justify="right",
            bg=self.ENTRY_BG,
            fg=self.TEXT,
            insertbackground=self.TEXT,
            bd=0
        )
        self.entry.pack(fill="x", padx=10, pady=(10, 5))

        self.paren_label = tk.Label(
            root,
            text="() depth: 0",
            bg=self.BG,
            fg=self.TEXT,
            anchor="e"
        )
        self.paren_label.pack(fill="x", padx=10)

        # ===== Main container =====
        main = tk.Frame(root, bg=self.BG)
        main.pack(fill="both", expand=True, padx=8, pady=8)

        # ===== Button frame =====
        btn_frame = tk.Frame(main, bg=self.BG)
        btn_frame.grid(row=0, column=0, sticky="n")

        # ===== History frame =====
        hist_frame = tk.Frame(main, bg=self.BG)
        hist_frame.grid(row=0, column=1, sticky="n", padx=(8, 0))

        # ===== Buttons (FULL SET RESTORED) =====
        self.buttons = [
            ['DEG','FLOAT','sin','cos','tan'],
            ['sin⁻¹','cos⁻¹','tan⁻¹','π','e'],
            ['xʸ','x³','x²','eˣ','10ˣ'],
            ['ⁿ√x','³√x','√x','ln','log'],
            ['(',')','1/x','%','n!'],
            ['7','8','9','+','Back'],
            ['4','5','6','-','Ans'],
            ['1','2','3','*','M+'],
            ['0','.','EXP','/','M-'],
            ['±','RND','AC','=','MR']
        ]

        self.button_map = {
            'xʸ':'^','x²':'x²','x³':'x³',
            '√x':'√','³√x':'³√','ln':'ln','log':'log',
            '1/x':'1/x','n!':'!',
            'sin⁻¹':'asin','cos⁻¹':'acos','tan⁻¹':'atan',
            'eˣ':'exp','EXP':'*10^','ⁿ√x':'root'
        }

        for r, row in enumerate(self.buttons):
            for c, char in enumerate(row):

                cmd = self.get_command(char)

                bg = self.BTN if char.isdigit() or char == '.' else self.BTN_ALT

                btn = tk.Button(
                    btn_frame,
                    text=char,
                    width=2,
                    height=1,
                    font=("Arial", 13),
                    bg=bg,
                    fg=self.TEXT,
                    bd=0,
                    relief="flat",
                    activebackground=self.BTN,
                    activeforeground=self.TEXT,
                    command=cmd
                )
                btn.grid(row=r, column=c, padx=3, pady=3)

                if char in ('DEG','RAD'):
                    self.angle_btn = btn
                if char in ('FLOAT','FIXED'):
                    self.precision_btn = btn

        # ===== History =====
        tk.Label(
            hist_frame,
            text="History",
            bg=self.BG,
            fg=self.TEXT,
            font=("Arial", 11, "bold")
        ).pack(anchor="w")

        self.history_box = tk.Listbox(
            hist_frame,
            width=38,
            height=20,
            bg=self.ENTRY_BG,
            fg=self.TEXT,
            bd=0,
            highlightthickness=0,
            selectbackground=self.BTN_ALT
        )
        self.history_box.pack(side="left", fill="y")

        self.history_scrollbar = tk.Scrollbar(
            hist_frame,
            orient="vertical",
            command=self.history_box.yview,
            bg=self.BTN_ALT,
            troughcolor=self.BG,
            activebackground=self.BTN,
            highlightthickness=0,
            bd=0
        )
        self.history_scrollbar.pack(side="right", fill="y")

        self.history_box.config(yscrollcommand=self.history_scrollbar.set)

    # ===== Command routing =====
    def get_command(self, char):
        return {
            'AC': self.clear,
            '=': self.calculate,
            'Back': self.backspace,
            '±': self.toggle_sign,
            'RND': self.random_number,
            'DEG': self.toggle_angle,
            'RAD': self.toggle_angle,
            'FLOAT': self.toggle_precision,
            'FIXED': self.toggle_precision,
            'M+': lambda: self.memory_op('M+'),
            'M-': lambda: self.memory_op('M-'),
            'MR': lambda: self.memory_op('MR'),
        }.get(char, lambda ch=char: self.append(ch))

    # ===== Logic =====
    def toggle_angle(self):
        self.angle_mode = "RAD" if self.angle_mode == "DEG" else "DEG"
        self.angle_btn.config(text=self.angle_mode)
        set_angle_mode(self.angle_mode)

    def toggle_precision(self):
        self.precision_mode = "FIXED" if self.precision_mode == "FLOAT" else "FLOAT"
        self.precision_btn.config(text=self.precision_mode)

    def append(self, ch):
        mapped = self.button_map.get(ch, ch)
        if mapped == 'root':
            self.entry_var.set(self.entry_var.get() + "^(1/")
        elif self.entry_var.get() == "Error":
            self.entry_var.set("")
            self.entry_var.set(mapped)
        else:
            self.entry_var.set(self.entry_var.get() + mapped)
        self.update_paren()

    def backspace(self):
        self.entry_var.set(self.entry_var.get()[:-1])
        self.update_paren()

    def clear(self):
        self.entry_var.set("")
        self.update_paren()

    def toggle_sign(self):
        expr = self.entry_var.get()
        m = re.search(r'(\d+\.?\d*|\.\d+)$', expr)
        if m:
            num = m.group(1)
            start = m.start(1)
            num = num[1:] if num.startswith('-') else '-' + num
            self.entry_var.set(expr[:start] + num)

    def random_number(self):
        self.entry_var.set(self.entry_var.get() + str(round(random.random(), 6)))

    def memory_op(self, op):
        try:
            val = float(evaluate_expression(self.entry_var.get()))
            if op == 'M+':
                self.memory += val
            elif op == 'M-':
                self.memory -= val
            elif op == 'MR':
                self.entry_var.set(self.entry_var.get() + str(self.memory))
        except:
            self.entry_var.set("Error")

    def update_paren(self):
        d = self.entry_var.get().count("(") - self.entry_var.get().count(")")
        self.paren_label.config(text=f"() depth: {d}")

    def format_number(self, value):
        v = float(value)
        if self.precision_mode == "FIXED":
            return f"{v:.{self.fixed_decimals}f}"
        if abs(v) >= 1e10 or (0 < abs(v) < 1e-6):
            return f"{v:.6e}"
        return str(v)

    def calculate(self):
        expr = self.entry_var.get()
        try:
            result = self.format_number(evaluate_expression(expr))
            self.entry_var.set(result)
            self.history_box.insert(tk.END, f"{expr} = {result}")
        except:
            self.entry_var.set("Error")
