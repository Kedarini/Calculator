# Scientific Calculator With GUI

A **full-featured scientific calculator** with a clean graphical user interface built using **Tkinter** in Python.

## Features

- Modern grid-based GUI layout (inspired by classic scientific calculators)
- **Basic operations**: +, −, ×, ÷, parentheses, percentage, negation
- **Scientific functions**:
  - Trigonometry: sin, cos, tan, asin, acos, atan (radian/degree toggle planned)
  - Logarithms: log (base 10), ln (natural log)
  - Powers & roots: x², xʸ, √, ∛, x⁻¹
  - Constants: π, e
  - Other: factorial (!), abs, floor/ceil (more coming)
- **Calculation history** panel — shows previous expressions + results
- **Persistent history** saved to `history.json` (loads on startup)
- Clear / All Clear buttons
- Input validation & friendly error messages (division by zero, domain errors, syntax errors)
- Responsive button styling (hover effects if implemented)

## Screenshots

![alt text](https://github.com/Kedarini/Calculator/raw/refs/heads/master/screenshots/calculatorGUI)

## Installation

```bash
git clone https://github.com/kedarini/calculator.git
cd calculator

# Recommended: virtual environment
python -m venv venv
source venv/bin/activate      # Linux / macOS
# or on Windows:
venv\Scripts\activate

# No external dependencies needed (only standard library + tkinter)
