import operator
import math
import re

# Operator functions
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
    "sin": math.sin,
    "cos": math.cos,
    "tan": math.tan,
    "asin": math.asin,
    "acos": math.acos,
    "atan": math.atan,
    "ln": math.log,
    "log": math.log10,
    "exp": math.exp,
}

# Constants
CONSTANTS = {
    "π": math.pi,
    "e": math.e,
    "Ans": 0,
}

# Operator precedence and associativity
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
    # Separate operators and parentheses
    expr = re.sub(r'([\+\-\*/\(\)\^!])', r' \1 ', expr)
    # Separate functions
    for func in ["sin", "cos", "tan", "asin", "acos", "atan", "ln", "log", "exp", "x²", "x³", "√", "³√", "1/x", "%"]:
        expr = expr.replace(func, f" {func} ")
    # Separate constants
    for const in ["π", "e", "Ans"]:
        expr = expr.replace(const, f" {const} ")
    expr = re.sub(r'\s+', ' ', expr)

    # Handle implicit multiplication (e.g., 2π → 2 * π, 3(4+5) → 3 * (4+5))
    expr = re.sub(r'(\d)(\s*)(π|e|Ans|\()', r'\1 * \3', expr)
    expr = re.sub(r'(\))(\s*)(\d|π|e|Ans|\()', r'\1 * \3', expr)

    return expr.strip()


# Convert infix expression to RPN using Shunting Yard algorithm
def shunting_yard(expr):
    output = []
    stack = []

    tokens = add_spaces(expr).split()

    for token in tokens:
        if token in OPS:
            while stack and stack[-1] in PRECEDENCE:
                p1, assoc1 = PRECEDENCE[token]
                p2, _ = PRECEDENCE[stack[-1]]
                if (assoc1 == "L" and p1 <= p2) or (assoc1 == "R" and p1 < p2):
                    output.append(stack.pop())
                else:
                    break
            stack.append(token)
        elif token == '(':
            stack.append(token)
        elif token == ')':
            while stack and stack[-1] != '(':
                output.append(stack.pop())
            stack.pop()  # Remove '('
        else:
            output.append(token)

    while stack:
        output.append(stack.pop())
    return output


# Evaluate RPN expression
def evaluate_rpn(tokens):
    stack = []
    for token in tokens:
        if token in OPS:
            func = OPS[token]
            if token in ["+", "-", "*", "/", "^"]:  # binary operators
                b = stack.pop()
                a = stack.pop()
                stack.append(func(a, b))
            else:  # unary operators
                a = stack.pop()
                stack.append(func(a))
        elif token in CONSTANTS:
            stack.append(CONSTANTS[token])
        else:
            stack.append(float(token))
    return stack[0]


# Main evaluation
def evaluate_expression(expression: str) -> str:
    if not expression:
        return ""
    try:
        tokens = shunting_yard(expression)
        result = evaluate_rpn(tokens)
        CONSTANTS["Ans"] = result  # store last answer
        return str(result)
    except ZeroDivisionError:
        return "Division by zero"
    except Exception:
        return "Error"