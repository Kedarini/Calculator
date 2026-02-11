# Scientific Calculator With GUI

A **full-featured scientific calculator** with a clean graphical user interface built using **Tkinter** in Python.

## Features

- Modern grid-based GUI layout (inspired by classic scientific calculators)
- **Basic operations**: +, −, ×, ÷, parentheses, percentage, negation
- **Scientific functions**:
  - Trigonometry: sin, cos, tan, asin, acos, atan, radian/degree toggle
  - Logarithms: log (base 10), ln (natural log)
  - Powers & roots: x², xʸ, √, ∛, x⁻¹
  - Constants: π, e
  - Other: factorial (!), abs, floor/ceil and more
- **Calculation history** panel — shows previous expressions + results
- **Persistent history** saved to `history.json` (loads on startup)
- Input validation & friendly error messages (division by zero, domain errors, syntax errors)
- Responsive button styling, hover effects

## Screenshots

![alt text](https://github.com/Kedarini/Calculator/raw/refs/heads/master/screenshots/calculatorGUI.png)

## Installation

```bash
# 1. Clone the repository
git clone https://github.com/kedarini/calculator.git
cd calculator/src

# 2. (recommended) create virtual environment
python -m venv .venv
source .venv/bin/activate      # Linux / macOS
# or on Windows:
# .venv\Scripts\activate

# 3. Run the calculator
python -m calculator
