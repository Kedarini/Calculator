import pytest
import tkinter as tk
from src.calculator.ui import CalculatorGUI


@pytest.fixture(scope="function")
def gui():
    """Tworzy GUI i zamyka po teście"""
    root = tk.Tk()
    gui_obj = CalculatorGUI(root)
    yield gui_obj
    root.destroy()


def test_window_title(gui):
    assert gui.root.title() == "Calculator"


def test_entry_exists_and_is_editable(gui):
    entry = gui.entry
    assert entry is not None
    assert entry.cget("state") == "normal"


def test_digit_button_appends_text(gui):
    gui.entry_var.set("")  # czysto na początek

    btn_5 = gui.buttons_dict.get("5")
    assert btn_5 is not None, "Przycisk '5' nie znaleziony"

    btn_5.invoke()  # symuluje kliknięcie
    assert gui.entry_var.get() == "5"


def test_ac_clears_entry(gui):
    gui.entry_var.set("999999")

    ac_btn = gui.buttons_dict.get("AC")
    assert ac_btn is not None

    ac_btn.invoke()
    assert gui.entry_var.get() == ""


def test_unary_sqrt_immediate_action(gui):
    gui.entry_var.set("16")

    sqrt_btn = gui.buttons_dict.get("√")
    assert sqrt_btn is not None

    sqrt_btn.invoke()
    result = gui.entry_var.get()
    assert result in ("4", "4.0", "4.0000")


def test_unary_one_over_x_immediate_action(gui):
    gui.entry_var.set("8")

    one_over_x_btn = gui.buttons_dict.get("1/x")
    assert one_over_x_btn is not None

    one_over_x_btn.invoke()
    result = gui.entry_var.get()
    assert result in ("0.125", "0.1250")


def test_calculate_simple_addition(gui):
    gui.entry_var.set("")

    # Symulacja kliknięć: 2 + 3 =
    gui.buttons_dict["2"].invoke()
    gui.buttons_dict["+"].invoke()   # jeśli masz spację w tekście przycisku
    gui.buttons_dict["3"].invoke()
    gui.buttons_dict["="].invoke()

    assert gui.entry_var.get() in ("5", "5.0")


def test_history_updates_on_calculate(gui):
    gui.entry_var.set("5 * 6")

    old_count = gui.history_box.size()

    gui.buttons_dict["="].invoke()

    new_count = gui.history_box.size()
    assert new_count == old_count + 1

    last_line = gui.history_box.get(tk.END)
    assert "5 * 6" in last_line
    assert "= 30" in last_line or "= 30.0" in last_line


def test_toggle_sign_changes_number(gui):
    gui.entry_var.set("42")

    sign_btn = gui.buttons_dict.get("±")
    assert sign_btn is not None

    sign_btn.invoke()
    assert gui.entry_var.get() == "-42"

    sign_btn.invoke()
    assert gui.entry_var.get() == "42"


def test_memory_mr_recall(gui, qtbot):
    # Zapisz do pamięci
    gui.entry_var.set("100.0")
    m_plus_btn = gui.buttons_dict.get("M+")
    m_plus_btn.invoke()

    # Wyczyść pole
    gui.entry_var.set("")

    # Odczytaj pamięć
    mr_btn = gui.buttons_dict.get("MR")
    mr_btn.invoke()

    assert gui.entry_var.get() == "100.0"