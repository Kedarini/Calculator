import operator
import math
import re


# ────────────────────────────────────────────────
# FUNKCJE TRYGONOMETRYCZNE
# ────────────────────────────────────────────────
ANGLE_MODE = "DEG"

def set_angle_mode(mode: str):
    global ANGLE_MODE
    if mode not in ("DEG", "RAD"):
        raise ValueError("Mode must be 'DEG' or 'RAD'")
    ANGLE_MODE = mode


def _to_rad(x: float) -> float:
    return math.radians(x) if ANGLE_MODE == "DEG" else x


def _from_rad(x: float) -> float:
    return math.degrees(x) if ANGLE_MODE == "DEG" else x


def sin(x):    return math.sin(_to_rad(x))
def cos(x):    return math.cos(_to_rad(x))
def tan(x):    return math.tan(_to_rad(x))

def asin(x):   return _from_rad(math.asin(x))
def acos(x):   return _from_rad(math.acos(x))
def atan(x):   return _from_rad(math.atan(x))


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
# PARSER + EVALUATOR
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
    if not expression.strip():
        return ""

    try:
        rpn = shunting_yard(expression)
        result = evaluate_rpn(rpn)
        CONSTANTS["Ans"] = result


        return str(result)

    except ZeroDivisionError:
        return "Division by zero"
    except ValueError as e:
        return f"Error: {str(e)}"
    except Exception():
        return "Error"