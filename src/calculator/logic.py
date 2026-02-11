import operator
import math
import re
import json
import os
from datetime import datetime

# ────────────────────────────────────────────────
# KONFIGURACJA
# ────────────────────────────────────────────────

ANGLE_MODE = "DEG"
HISTORY_FILE = "history.json"
MAX_HISTORY = 100


# ────────────────────────────────────────────────
# FUNKCJE TRYGONOMETRYCZNE
# ────────────────────────────────────────────────

def set_angle_mode(mode: str):
    global ANGLE_MODE
    if mode not in ("DEG", "RAD"):
        raise ValueError("Mode must be 'DEG' or 'RAD'")
    ANGLE_MODE = mode


def sin(x):    return math.sin(math.radians(x)) if ANGLE_MODE == "DEG" else math.sin(x)


def cos(x):    return math.cos(math.radians(x)) if ANGLE_MODE == "DEG" else math.cos(x)


def tan(x):    return math.tan(math.radians(x)) if ANGLE_MODE == "DEG" else math.tan(x)


def asin(x):   v = math.asin(x);   return math.degrees(v) if ANGLE_MODE == "DEG" else v


def acos(x):   v = math.acos(x);   return math.degrees(v) if ANGLE_MODE == "DEG" else v


def atan(x):   v = math.atan(x);   return math.degrees(v) if ANGLE_MODE == "DEG" else v


# ────────────────────────────────────────────────
# OPERATORY, FUNKCJE, STAŁE
# ────────────────────────────────────────────────

OPS = {
    "+": operator.add, "-": operator.sub, "*": operator.mul, "/": operator.truediv, "^": operator.pow,
    "x²": lambda x: x ** 2, "x³": lambda x: x ** 3,
    "√": math.sqrt, "³√": lambda x: x ** (1 / 3), "1/x": lambda x: 1 / x,
    "%": lambda x: x / 100, "!": math.factorial,
    "sin": sin, "cos": cos, "tan": tan,
    "asin": asin, "acos": acos, "atan": atan,
    "ln": math.log, "log": math.log10, "exp": math.exp,
}

CONSTANTS = {"π": math.pi, "e": math.e, "Ans": 0.0}

PRECEDENCE = {
    "+": (1, "L"), "-": (1, "L"),
    "*": (2, "L"), "/": (2, "L"),
    "^": (3, "R"),
    "x²": (4, "R"), "x³": (4, "R"), "√": (4, "R"), "³√": (4, "R"),
    "1/x": (4, "R"), "%": (4, "R"), "!": (4, "L"),
    "sin": (4, "R"), "cos": (4, "R"), "tan": (4, "R"),
    "asin": (4, "R"), "acos": (4, "R"), "atan": (4, "R"),
    "ln": (4, "R"), "log": (4, "R"), "exp": (4, "R"),
}


# ────────────────────────────────────────────────
# HISTORIA JSON
# ────────────────────────────────────────────────

def load_history() -> list[str]:
    if not os.path.exists(HISTORY_FILE):
        return []
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("history", [])[-MAX_HISTORY:]
    except Exception:
        return []


def save_history(history: list[str]):
    try:
        data = {
            "history": history[-MAX_HISTORY:],
            "last_updated": datetime.now().isoformat()
        }
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception:
        pass  # cicho ignorujemy błędy zapisu


def format_history_entry(expr: str, result: str) -> str:
    time_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    return f"[{time_str}] {expr} = {result}"


# ────────────────────────────────────────────────
# PARSER + EVALUATOR (oryginalna sygnatura!)
# ────────────────────────────────────────────────

def add_spaces(expr: str) -> str:
    if not expr.strip():
        return ""

    replacements = {"³√": " 3√ ", "√": " √ ", "1/x": " 1/ ", "x²": " x² ", "x³": " x³ ", "!": " ! "}
    for old, new in replacements.items():
        expr = expr.replace(old, new)

    expr = re.sub(r'([+\-*/^()])', r' \1 ', expr)

    for name in list(OPS) + list(CONSTANTS):
        expr = re.sub(rf'\b{re.escape(name)}\b', f' {name} ', expr, flags=re.IGNORECASE)

    expr = re.sub(r'\s+', ' ', expr.strip())

    expr = re.sub(r'(\d|\.)\s*([πeAns(])', r'\1 * \2', expr)
    expr = re.sub(r'([)])\s*(\d|\.|π|e|Ans|[a-zA-Z])', r'\1 * \2', expr)

    return expr.strip()


def shunting_yard(expr: str) -> list[str]:
    output, stack = [], []
    tokens = add_spaces(expr).split()

    for token in tokens:
        if token in OPS:
            while stack and stack[-1] != '(' and stack[-1] in PRECEDENCE:
                p1, assoc = PRECEDENCE[token]
                p2, _ = PRECEDENCE[stack[-1]]
                if (assoc == "L" and p1 <= p2) or (assoc == "R" and p1 < p2):
                    output.append(stack.pop())
                else:
                    break
            stack.append(token)
        elif token == '(':
            stack.append(token)
        elif token == ')':
            while stack and stack[-1] != '(':
                output.append(stack.pop())
            stack.pop() if stack else None
        else:
            output.append(token)

    while stack:
        output.append(stack.pop())

    return output


def evaluate_rpn(tokens: list[str]) -> float:
    stack = []
    for token in tokens:
        if token in OPS:
            func = OPS[token]
            if token in {"+", "-", "*", "/", "^"}:
                b, a = stack.pop(), stack.pop()
                stack.append(func(a, b))
            elif token == "!":
                a = stack.pop()
                if not (isinstance(a, (int, float)) and a == int(a) and a >= 0):
                    raise ValueError("Factorial tylko dla nieujemnych liczb całkowitych")
                stack.append(func(int(a)))
            else:
                stack.append(func(stack.pop()))
        elif token in CONSTANTS:
            stack.append(CONSTANTS[token])
        else:
            stack.append(float(token))

    return stack[0]


def evaluate_expression(expression: str) -> str:
    """Oryginalna sygnatura – zwraca tylko string (wynik lub błąd)"""
    if not expression.strip():
        return ""

    try:
        rpn = shunting_yard(expression)
        result = evaluate_rpn(rpn)
        CONSTANTS["Ans"] = result

        # ─── Dodajemy do historii ───────────────────────────────
        history = load_history()
        entry = format_history_entry(expression.strip(), str(result))
        history.append(entry)
        save_history(history)
        # ─────────────────────────────────────────────────────────

        return str(result)

    except ZeroDivisionError:
        return "Division by zero"
    except ValueError as e:
        return f"Error: {str(e)}"
    except Exception:
        return "Error"