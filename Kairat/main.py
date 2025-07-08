import tkinter as tk

# Game settings
GRID_SIZE = 20
CELL_SIZE = 20

# Initialize main window
root = tk.Tk()
root.title("Grid-Based Game")

# Create a 2D list to store references to grid widgets (buttons)
cells = [[None for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]

# Function to handle cell click
def on_cell_click(row, col):
    print(f"Cell clicked: Row={row}, Col={col}")
    # Change text and background color of the clicked cell
    cells[row][col].config(text=f"{row},{col}", bg="lightblue")

# Create grid of buttons
for row in range(GRID_SIZE):
    for col in range(GRID_SIZE):
        # Create a button at each grid position
        btn = tk.Button(
            root,
            text="",
            width=CELL_SIZE//10,
            height=CELL_SIZE//20,
            font=("Arial", 14),
            command=lambda r=row, c=col: on_cell_click(r, c)
        )
        btn.grid(row=row, column=col, padx=2, pady=2)
        cells[row][col] = btn

# Run the app
root.mainloop()