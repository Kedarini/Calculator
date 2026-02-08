import operator
import math
import re

ANGLE_MODE = "DEG"

def set_angle_mode(mode: str):
    global ANGLE_MODE
    ANGLE_MODE = mode

def sin(x): return math.sin(math.radians(x)) if ANGLE_MODE == "DEG" else math.sin(x)
def cos(x): return math.cos(math.radians(x)) if ANGLE_MODE == "DEG" else math.cos(x)
def tan(x): return math.tan(math.radians(x)) if ANGLE_MODE == "DEG" else math.tan(x)

def asin(x):
    v = math.asin(x)
    return math.degrees(v) if ANGLE_MODE == "DEG" else v

def acos(x):
    v = math.acos(x)
    return math.degrees(v) if ANGLE_MODE == "DEG" else v

def atan(x):
    v = math.atan(x)
    return math.degrees(v) if ANGLE_MODE == "DEG" else v

OPS = {
    "+": operator.add,
    "-": operator.sub,
    "*": operator.mul,
    "/": operator.truediv,
    "^": operator.pow,
    "x²": lambda x: x ** 2,
    "x³": lambda x: x ** 3,
    "√": math.sqrt,
    "³√": lambda x: x ** (1 / 3),
    "1/x": lambda x: 1 / x,
    "%": lambda x: x / 100,
    "!": math.factorial,
    "sin": sin,
    "cos": cos,
    "tan": tan,
    "asin": asin,
    "acos": acos,
    "atan": atan,
    "ln": math.log,
    "log": math.log10,
    "exp": math.exp,
}

CONSTANTS = {
    "π": math.pi,
    "e": math.e,
    "Ans": 0,
}

PRECEDENCE = {
    "+": (1, "L"),
    "-": (1, "L"),
    "*": (2, "L"),
    "/": (2, "L"),
    "^": (3, "R"),
    "x²": (4, "R"),
    "x³": (4, "R"),
    "√": (4, "R"),
    "³√": (4, "R"),
    "1/x": (4, "R"),
    "%": (4, "R"),
    "!": (4, "L"),
    "sin": (4, "R"),
    "cos": (4, "R"),
    "tan": (4, "R"),
    "asin": (4, "R"),
    "acos": (4, "R"),
    "atan": (4, "R"),
    "ln": (4, "R"),
    "log": (4, "R"),
    "exp": (4, "R"),
}


def add_spaces(expr: str) -> str:
    if not expr:
        return ""

    # Step 1: Explicitly space out known multi-char and special unary operators
    special_unary = {
        "³√": " ³√ ",
        "√": " √ ",
        "1/x": " 1/ ",
        "x²": " x² ",
        "x³": " x³ ",
        "!": " ! ",  # postfix factorial
    }

    for op, spaced in special_unary.items():
        expr = expr.replace(op, spaced)

    # Step 2: Space single-char operators
    expr = re.sub(r'([+\-*/^()])', r' \1 ', expr)

    # Step 3: Space known functions and constants (with word boundaries)
    for func in OPS:
        expr = re.sub(rf'\b{re.escape(func)}\b', f' {func} ', expr, flags=re.IGNORECASE)

    for const in CONSTANTS:
        expr = re.sub(rf'\b{re.escape(const)}\b', f' {const} ', expr)

    # Step 4: Normalize spaces
    expr = re.sub(r'\s+', ' ', expr.strip())

    # Step 5: Handle implicit multiplication (number next to constant/function/parenthesis)
    expr = re.sub(r'(\d|\.)\s*([πeAns(])', r'\1 * \2', expr)
    expr = re.sub(r'([)])\s*(\d|\.|π|e|Ans|[a-zA-Z])', r'\1 * \2', expr)

    return expr.strip()

def shunting_yard(expr):
    output, stack = [], []
    tokens = add_spaces(expr).split()

    for token in tokens:
        if token in OPS:
            while stack and stack[-1] in PRECEDENCE:
                p1, a1 = PRECEDENCE[token]
                p2, _ = PRECEDENCE[stack[-1]]
                if (a1 == "L" and p1 <= p2) or (a1 == "R" and p1 < p2):
                    output.append(stack.pop())
                else:
                    break
            stack.append(token)
        elif token == '(':
            stack.append(token)
        elif token == ')':
            while stack and stack[-1] != '(':
                output.append(stack.pop())
            stack.pop()
        else:
            output.append(token)

    while stack:
        output.append(stack.pop())
    return output

def evaluate_rpn(tokens):
    stack = []
    for token in tokens:
        if token in OPS:
            func = OPS[token]
            if token in "+-*/^":
                b, a = stack.pop(), stack.pop()
                stack.append(func(a, b))
            else:
                stack.append(func(stack.pop()))
        elif token in CONSTANTS:
            stack.append(CONSTANTS[token])
        else:
            stack.append(float(token))
    return stack[0]

def evaluate_expression(expression: str) -> str:
    if not expression:
        return ""
    try:
        tokens = shunting_yard(expression)
        result = evaluate_rpn(tokens)
        CONSTANTS["Ans"] = result
        return str(result)
    except ZeroDivisionError:
        return "Division by zero"
    except Exception:
        return "Error"
