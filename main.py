import tkinter as tk

root = tk.Tk()
root.title("Calculator")
root.geometry("300x400")

entry_var = tk.StringVar()
value = entry_var.get()

entry = tk.Entry(root, width=20,font=('Arial', 30), bg="white", fg="black", textvariable=entry_var)
entry.pack(fill="both", padx=10, pady=10)

frame = tk.Frame(root, bg="white")
frame.pack()

buttons = [
    ['7', '8', '9', '/'],
    ['4', '5', '6', '*'],
    ['1', '2', '3', '-'],
    ['C', '0', '=', '+']
]

def calculate():
    try:
        if entry_var.get() == '':
            entry_var.set('')
        else:
            # Evaluate the expression from entry_var
            result = eval(entry_var.get())
            entry_var.set(result)  # Update the entry with result
    except Exception:
        entry_var.set("Error")  # Show error if expression is invalid

def clear():
    try:
        if entry_var.get() == "":
            entry_var.set('')
        else:
            entry_var.set('')  # Update the entry with result
    except Exception:
        entry_var.set("Error")  # Show error if expression is invalid

for j, row in enumerate(buttons):       # j = row index
    for i, char in enumerate(row):      # i = column index
        if char == 'C':
            button = tk.Button(
                frame, text=char, bg="white",
                fg="black", font=("Arial", 16),
                width=2, height=1,
                command=clear
            )
        elif char == '=':
            button = tk.Button(
                frame, text=char, bg="white", fg="black",
                font=("Arial", 16),
                width=2, height=1,
                command=calculate  # call calculate() when pressed
            )
        else:
            button = tk.Button(
                frame, text=char, bg="white",
                fg="black", font=("Arial", 16),
                width=2, height=1,
                command=lambda char=char: entry_var.set(entry_var.get() + char)
            )
        button.grid(row=j, column=i, padx=5, pady=5)

root.mainloop()