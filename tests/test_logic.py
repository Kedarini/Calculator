import pytest
import math
from src.calculator.logic import evaluate_expression, set_angle_mode


# ────────────────────────────────────────────────
# Helper for floating-point safe comparison
# ────────────────────────────────────────────────

def assert_result_close(actual: str, expected: float, rel: float = 1e-10, abs: float = 1e-12):
    try:
        actual_float = float(actual)
    except ValueError:
        pytest.fail(f"Cannot convert '{actual}' to float")
    assert actual_float == pytest.approx(expected, rel=rel, abs=abs)


# ────────────────────────────────────────────────
# Basic binary operations
# ────────────────────────────────────────────────

@pytest.mark.parametrize("expr, expected", [
    ("2 + 3",           "5.0"),
    ("10 - 4",          "6.0"),
    ("3 * 8",           "24.0"),
    ("15 / 3",          "5.0"),
    ("15 / 4",          "3.75"),
    ("2 ^ 3",           "8.0"),
    ("0.1 + 0.2",       "0.30000000000000004"),  # floating point reality
])
def test_basic_binary_operators(expr, expected):
    assert evaluate_expression(expr) == expected


# ────────────────────────────────────────────────
# Precedence and associativity
# ────────────────────────────────────────────────

@pytest.mark.parametrize("expr, expected", [
    ("2 + 3 * 4",       "14.0"),
    ("10 - 2 ^ 3",      "2.0"),
    ("5 * 2 ^ 3",       "40.0"),
    ("100 / 10 / 2",    "5.0"),           # left-associative
    ("2 ^ 3 ^ 2",       "512.0"),         # right-associative = 2^(3^2)
])
def test_precedence_and_associativity(expr, expected):
    assert evaluate_expression(expr) == expected


# ────────────────────────────────────────────────
# Unary functions and percent
# ────────────────────────────────────────────────

@pytest.mark.parametrize("expr, expected", [
    ("√16",             "4.0"),
    ("³√27",            "3.0"),
    ("x² 5",            "25.0"),
    ("x³ 2",            "8.0"),
    ("25 %",            "0.25"),
    ("1/x 8",           "0.125"),
    ("5 !",             "120"),
    ("ln e",            "1.0"),
    ("log 100",         "2.0"),
])
def test_unary_functions(expr, expected):
    assert evaluate_expression(expr) == expected


# ────────────────────────────────────────────────
# Trigonometry – DEG vs RAD mode
# ────────────────────────────────────────────────

def test_trigonometry_deg():
    set_angle_mode("DEG")
    assert_result_close(evaluate_expression("sin 30"),   0.5,      abs=1e-10)
    assert_result_close(evaluate_expression("cos 60"),   0.5,      abs=1e-10)
    assert_result_close(evaluate_expression("tan 45"),   1.0,      abs=1e-10)
    assert_result_close(evaluate_expression("asin 0.5"), 30.0,     abs=1e-8)
    assert_result_close(evaluate_expression("acos 0.5"), 60.0,     abs=1e-8)


def test_trigonometry_rad():
    set_angle_mode("RAD")
    # Use more precise value for π/2
    assert_result_close(evaluate_expression("sin 1.5707963267948966"), 1.0, abs=1e-10)
    assert_result_close(evaluate_expression("cos 1.5707963267948966"), 0.0, abs=1e-10)


# ────────────────────────────────────────────────
# Constants and Ans
# ────────────────────────────────────────────────

def test_constants_and_ans():
    assert_result_close(evaluate_expression("π"), math.pi)
    assert_result_close(evaluate_expression("e"), math.e)

    evaluate_expression("7 * 8")          # Ans ← 56.0
    assert evaluate_expression("Ans + 4") == "60.0"


# ────────────────────────────────────────────────
# Error handling
# ────────────────────────────────────────────────

@pytest.mark.parametrize("expr, expected_substring", [
    ("10 / 0",          "Division by zero"),
    ("√ -1",            "Error"),          # domain error
    ("2 + + 3",         "Error"),
    ("sin",             "Error"),          # missing argument
    ("abc",             "Error"),
    ("5 / 0 + 2",       "Division by zero"),
    ("√(abc)",          "Error"),
    ("",                ""),               # empty input → empty output
])
def test_error_cases(expr, expected_substring):
    result = evaluate_expression(expr)
    if expected_substring:
        assert expected_substring in result, f"Expected '{expected_substring}' in '{result}'"
    else:
        assert result == "", f"Expected empty string, got '{result}'"