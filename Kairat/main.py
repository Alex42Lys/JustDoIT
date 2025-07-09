import tkinter as tk

GRID_ROWS = 20
GRID_COLS = 20

def shape_from_text(text: str) -> list:
    lines = text.split('|')
    height = len(lines)
    width = max(len(line) for line in lines)
    center_row = height // 2
    center_col = width // 2
    shape = []
    for row_idx, line in enumerate(lines):
        for col_idx, char in enumerate(line.ljust(width)):
            if char == '#':
                rel_row = row_idx - center_row
                rel_col = col_idx - center_col
                shape.append((rel_row, rel_col))
    return shape

class ToolTip:
    def __init__(self, widget, text_func):
        self.widget = widget
        self.text_func = text_func
        self.tip_window = None
        widget.bind("<Enter>", self.show_tip)
        widget.bind("<Leave>", self.hide_tip)

    def show_tip(self, event=None):
        if self.tip_window:
            return
        text = self.text_func()
        if not text:
            return
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 5
        self.tip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(tw, text=text, justify=tk.LEFT,
                         background="#ffffe0", relief=tk.SOLID, borderwidth=1,
                         font=("Arial", 10))
        label.pack(ipadx=5, ipady=2)

    def hide_tip(self, event=None):
        if self.tip_window:
            self.tip_window.destroy()
            self.tip_window = None

class GameUI:
    def __init__(self, root):
        self.root = root
        self.cell_tags = {}
        self.objects = []
        self.selected_cell = None

        self.root.title("Tank Game")
        self.root.minsize(600, 600)

        self.main_frame = tk.Frame(root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self.top_frame = tk.Frame(self.main_frame)
        self.top_frame.grid(row=0, column=0, sticky="nsew")

        self.canvas = tk.Canvas(self.top_frame, bg="black")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.bottom_frame = tk.Frame(self.main_frame, bg="#202020")
        self.bottom_frame.grid(row=1, column=0, sticky="nsew")

        self.main_frame.rowconfigure(0, weight=8)
        self.main_frame.rowconfigure(1, weight=2)
        self.main_frame.columnconfigure(0, weight=1)

        self.canvas.bind("<Configure>", self.on_canvas_resize)
        self.canvas.bind("<Button-1>", self.on_canvas_click)

        self.create_grid()
        self._setup_controls()

    def create_grid(self):
        self.cell_tags.clear()
        width = self.canvas.winfo_width() or 600
        height = self.canvas.winfo_height() or 480
        self.cell_width = max(width // GRID_COLS, 1)
        self.cell_height = max(height // GRID_ROWS, 1)

        for row in range(GRID_ROWS):
            for col in range(GRID_COLS):
                x1 = col * self.cell_width
                y1 = row * self.cell_height
                x2 = x1 + self.cell_width
                y2 = y1 + self.cell_height
                tag = f"cell_{row}_{col}"
                self.canvas.create_rectangle(x1, y1, x2, y2,
                                             outline="#333", fill="black", tags=tag)
                self.cell_tags[(row, col)] = tag

    def on_canvas_resize(self, event):
        self.cell_width = max(event.width // GRID_COLS, 1)
        self.cell_height = max(event.height // GRID_ROWS, 1)
        for row in range(GRID_ROWS):
            for col in range(GRID_COLS):
                x1 = col * self.cell_width
                y1 = row * self.cell_height
                x2 = x1 + self.cell_width
                y2 = y1 + self.cell_height
                tag = self.cell_tags.get((row, col))
                if tag:
                    self.canvas.coords(tag, x1, y1, x2, y2)
        for obj in self.objects:
            obj.render()
        if self.selected_cell:
            self.highlight_selected_cell()

    def set_cell(self, row, col, color):
        tag = self.cell_tags.get((row, col))
        if tag:
            self.canvas.itemconfig(tag, fill=color)

    def clear_cell(self, row, col):
        self.set_cell(row, col, "black")

    def highlight_selected_cell(self):
        for (r, c), tag in self.cell_tags.items():
            if (r, c) == self.selected_cell:
                self.canvas.itemconfig(tag, outline="yellow", width=3)
            else:
                self.canvas.itemconfig(tag, outline="#333", width=1)

    def on_canvas_click(self, event):
        col = event.x // self.cell_width
        row = event.y // self.cell_height
        if 0 <= row < GRID_ROWS and 0 <= col < GRID_COLS:
            self.selected_cell = (row, col)
            self.highlight_selected_cell()
            print(f"Selected cell: {self.selected_cell}")

    def _setup_controls(self):
        control_frame = tk.Frame(self.bottom_frame, bg="#202020")
        control_frame.grid(row=0, column=0, sticky="nsew")
        btn_font = ("Arial", 18)

        self.btn_up = tk.Button(control_frame, text="⬆", font=btn_font, width=5, height=2)
        self.btn_left = tk.Button(control_frame, text="⬅", font=btn_font, width=5, height=2)
        self.btn_down = tk.Button(control_frame, text="⬇", font=btn_font, width=5, height=2)
        self.btn_right = tk.Button(control_frame, text="➡", font=btn_font, width=5, height=2)
        self.btn_fire = tk.Button(control_frame, text="🔫", font=btn_font, width=5, height=2)
        self.btn_auto = tk.Button(control_frame, text="🤖", font=btn_font, width=5, height=2, bg="#404040", fg="white")

        self.btn_up.grid(row=0, column=1, padx=5, pady=2)
        self.btn_left.grid(row=1, column=0, padx=5, pady=2)
        self.btn_down.grid(row=1, column=1, padx=5, pady=2)
        self.btn_right.grid(row=1, column=2, padx=5, pady=2)
        self.btn_fire.grid(row=1, column=3, padx=15, pady=2)
        self.btn_auto.grid(row=1, column=4, padx=5, pady=2)

        self.btn_auto_bg = "#404040"

        ToolTip(self.btn_up, lambda: "Вверх")
        ToolTip(self.btn_down, lambda: "Вниз")
        ToolTip(self.btn_left, lambda: "Влево")
        ToolTip(self.btn_right, lambda: "Вправо")
        ToolTip(self.btn_fire, lambda: "Стрелять")
        ToolTip(self.btn_auto, lambda: f"Автопилот: {'Включён' if self.btn_auto_bg == 'green' else 'Выключен'}")

    def register_control_handlers(self, up, down, left, right, fire, toggle_autopilot):
        self.btn_up.config(command=up)
        self.btn_down.config(command=down)
        self.btn_left.config(command=left)
        self.btn_right.config(command=right)
        self.btn_fire.config(command=fire)
        self.btn_auto.config(command=toggle_autopilot)

    def set_autopilot_button_state(self, enabled: bool):
        color = "green" if enabled else "#404040"
        self.btn_auto.config(bg=color, fg="white")
        self.btn_auto_bg = color

    def add_object(self, obj):
        self.objects.append(obj)
        obj.render()

class GameObject:
    def __init__(self, ui: GameUI, row, col, color="gray", shape=None):
        self.ui = ui
        self.row = row
        self.col = col
        self.color = color
        self.shape = shape if shape else [(0, 0)]

    def get_absolute_coords(self):
        return [(self.row + dr, self.col + dc) for dr, dc in self.shape]

    def render(self):
        for r, c in self.get_absolute_coords():
            if 0 <= r < GRID_ROWS and 0 <= c < GRID_COLS:
                self.ui.set_cell(r, c, self.color)

    def clear(self):
        for r, c in self.get_absolute_coords():
            if 0 <= r < GRID_ROWS and 0 <= c < GRID_COLS:
                self.ui.clear_cell(r, c)

class PlayerTank(GameObject):
    def __init__(self, ui: GameUI, row, col, obj_form: str = " # |###"):
        shape = shape_from_text(obj_form)
        super().__init__(ui, row, col, color="green", shape=shape)
        self.autopilot = False
        self.radar_radius = 3
        self.radar_cells = []

    def render(self):
        self.render_radar()
        super().render()

    def clear(self):
        self.clear_radar()
        super().clear()

    def render_radar(self):
        self.clear_radar()
        center = (self.row, self.col)
        radius = self.radar_radius
        for dr in range(-radius, radius + 1):
            for dc in range(-radius, radius + 1):
                r = center[0] + dr
                c = center[1] + dc
                if 0 <= r < GRID_ROWS and 0 <= c < GRID_COLS:
                    # Можно использовать манхэттенское расстояние для формы квадрата
                    if abs(dr) + abs(dc) <= radius:
                        self.ui.set_cell(r, c, "#203040")
                        self.radar_cells.append((r, c))

    def clear_radar(self):
        for r, c in self.radar_cells:
            self.ui.clear_cell(r, c)
        self.radar_cells.clear()

    def move(self, d_row, d_col):
        if self.ui.selected_cell:
            target_row, target_col = self.ui.selected_cell
            new_coords = [(target_row + dr, target_col + dc) for dr, dc in self.shape]
            if all(0 <= r < GRID_ROWS and 0 <= c < GRID_COLS for r, c in new_coords):
                self.clear()
                self.row = target_row
                self.col = target_col
                self.render()
            else:
                print("Target out of bounds")
            self.ui.selected_cell = None
            self.ui.highlight_selected_cell()
        else:
            new_row = self.row + d_row
            new_col = self.col + d_col
            new_coords = [(new_row + dr, new_col + dc) for dr, dc in self.shape]
            if all(0 <= r < GRID_ROWS and 0 <= c < GRID_COLS for r, c in new_coords):
                self.clear()
                self.row = new_row
                self.col = new_col
                self.render()

    def shoot(self):
        if self.ui.selected_cell is None:
            print("No target selected!")
        else:
            print(f"Shooting from ({self.row},{self.col}) to {self.ui.selected_cell}")

    def toggle_autopilot(self):
        self.autopilot = not self.autopilot
        print("Autopilot:", "ON" if self.autopilot else "OFF")
        self.ui.set_autopilot_button_state(self.autopilot)

if __name__ == "__main__":
    root = tk.Tk()
    ui = GameUI(root)
    player = PlayerTank(ui, 5, 5, obj_form=" # |###|# #")
    ui.add_object(player)
    enemy = GameObject(ui, 10, 10, color="red", shape=shape_from_text(" # |###| #"))
    ui.add_object(enemy)

    ui.register_control_handlers(
        up=lambda: player.move(-1, 0),
        down=lambda: player.move(1, 0),
        left=lambda: player.move(0, -1),
        right=lambda: player.move(0, 1),
        fire=player.shoot,
        toggle_autopilot=player.toggle_autopilot
    )

    root.mainloop()
