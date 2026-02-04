import operator

OPS = {
    "+": operator.add,
    "-": operator.sub,
    "*": operator.mul,
    "/": operator.truediv,
}

import re

def add_spaces(expr: str) -> str:
    expr = re.sub(r'([\+\-\*/\(\)])', r' \1 ', expr)
    expr = re.sub(r'\s+', ' ', expr)
    return expr.strip()


def evaluate_rpn(tokens):
    stack = []
    for token in tokens:
        if token in OPS:
            b = stack.pop()
            a = stack.pop()
            stack.append(OPS[token](a, b))
        else:
            stack.append(float(token))
    return stack[0]

def shunting_yard(expr):
    output = []
    stack = []
    precedence = {'+': 1, '-': 1, '*': 2, '/': 2}

    tokens = add_spaces(expr).split()

    for token in tokens:
        if token in OPS:
            while stack and precedence.get(stack[-1], 0) >= precedence[token]:
                output.append(stack.pop())
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


def evaluate_expression(expression: str) -> str:
    if not expression:
        return ""

    try:
        tokens = shunting_yard(expression)
        result = evaluate_rpn(tokens)
        return str(result)
    except ZeroDivisionError:
        return "Division by zero"
    except Exception:
        return "Error"
