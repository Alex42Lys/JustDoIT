import sqlite3
import json
import tkinter as tk
import math
import os
from datetime import datetime
from typing import Dict

class DatsPulseDBVisualizer:
    def __init__(self, db_path: str, refresh_interval=2000):
        self.db_path = db_path
        self.refresh_interval = refresh_interval  # milliseconds
        self.zoom_level = 1.0
        self.pan_x = 0
        self.pan_y = 0
        self.drag_data = {"x": 0, "y": 0, "item": None}
        self.last_state = None
        self.visible_hexes = set()
        self.map_bounds = {}  # Store min/max q/r coordinates
        
        # Initialize UI
        self.root = tk.Tk()
        self.root.title("DatsPulse DB Visualizer")
        self.root.minsize(1000, 800)
        
        # Create main frames
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        self.canvas_frame = tk.Frame(self.main_frame)
        self.canvas_frame.pack(fill=tk.BOTH, expand=True)
        
        self.control_frame = tk.Frame(self.main_frame, bg="#202020", height=120)
        self.control_frame.pack(fill=tk.X)
        
        # Game canvas
        self.canvas = tk.Canvas(self.canvas_frame, bg="black")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Add mouse bindings for pan and zoom
        self.canvas.bind("<ButtonPress-1>", self.start_pan)
        self.canvas.bind("<B1-Motion>", self.pan)
        self.canvas.bind("<MouseWheel>", self.zoom)  # Windows
        self.canvas.bind("<Button-4>", self.zoom)    # Linux
        self.canvas.bind("<Button-5>", self.zoom)    # Linux
        
        # Refresh controls
        self.button_frame = tk.Frame(self.control_frame, bg="#202020")
        self.button_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.refresh_button = tk.Button(
            self.button_frame, text="🔄 Refresh Now", 
            command=self.load_and_display_latest_state, width=20
        )
        self.refresh_button.pack(side=tk.LEFT, padx=5)
        
        # Reset view button
        self.reset_view_button = tk.Button(
            self.button_frame, text="⟲ Reset View", 
            command=self.reset_view, width=15
        )
        self.reset_view_button.pack(side=tk.LEFT, padx=5)
        
        # Zoom level display (without buttons)
        self.zoom_frame = tk.Frame(self.button_frame, bg="#202020")
        self.zoom_frame.pack(side=tk.LEFT, padx=10)
        
        # self.zoom_label = tk.Label(
        #     self.zoom_frame, text="Zoom: 100%", 
        #     bg="#202020", fg="white", width=10
        # )
        # self.zoom_label.pack(side=tk.LEFT, padx=5)
        
        # Auto-refresh toggle
        self.auto_refresh_var = tk.BooleanVar(value=True)
        self.auto_refresh_toggle = tk.Checkbutton(
            self.button_frame, text="Auto-Refresh",
            variable=self.auto_refresh_var,
            command=self.toggle_auto_refresh,
            bg="#202020", fg="white", selectcolor="#202020"
        )
        self.auto_refresh_toggle.pack(side=tk.LEFT, padx=5)
        
        # Refresh interval control
        self.interval_frame = tk.Frame(self.button_frame, bg="#202020")
        self.interval_frame.pack(side=tk.LEFT, padx=10)
        
        tk.Label(self.interval_frame, text="Interval (ms):", bg="#202020", fg="white").pack(side=tk.LEFT)
        self.interval_entry = tk.Entry(self.interval_frame, width=6)
        self.interval_entry.insert(0, str(self.refresh_interval))
        self.interval_entry.pack(side=tk.LEFT)
        
        self.set_interval_button = tk.Button(
            self.interval_frame, text="Set",
            command=self.update_refresh_interval,
            width=4
        )
        self.set_interval_button.pack(side=tk.LEFT, padx=5)
        
        # Info display
        self.info_frame = tk.Frame(self.control_frame, bg="#202020")
        self.info_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.turn_label = tk.Label(
            self.info_frame, text="Turn: -", bg="#202020", fg="white",
            font=("Arial", 10, "bold"), width=15, anchor="w"
        )
        self.turn_label.pack(side=tk.LEFT)
        
        self.datetime_label = tk.Label(
            self.info_frame, text="Time: -", bg="#202020", fg="white",
            font=("Arial", 10, "bold"), width=25, anchor="w"
        )
        self.datetime_label.pack(side=tk.LEFT)
        
        self.player_label = tk.Label(
            self.info_frame, text="Player: -", bg="#202020", fg="white",
            font=("Arial", 10, "bold"), width=25, anchor="w"
        )
        self.player_label.pack(side=tk.LEFT)
        
        self.status_label = tk.Label(
            self.info_frame, text="Status: Ready", bg="#202020", fg="lightgreen",
            font=("Arial", 10), anchor="w"
        )
        self.status_label.pack(side=tk.LEFT)
        
        # Legend
        self.legend_canvas = tk.Canvas(
            self.control_frame, bg="#202020", height=50, highlightthickness=0
        )
        self.legend_canvas.pack(fill=tk.X, padx=10, pady=5)
        
        # Initial load
        self.draw_legend()
        self.load_and_display_latest_state()
        
        # Start auto-refresh
        self.auto_refresh_id = None
        self.start_auto_refresh()
        
        self.root.mainloop()

    def start_pan(self, event):
        """Begin panning the map"""
        self.drag_data["x"] = event.x
        self.drag_data["y"] = event.y

    def pan(self, event):
        """Pan the map based on mouse movement"""
        dx = event.x - self.drag_data["x"]
        dy = event.y - self.drag_data["y"]
        
        self.pan_x += dx
        self.pan_y += dy
        
        self.drag_data["x"] = event.x
        self.drag_data["y"] = event.y
        
        self.canvas.move("all", dx, dy)

    def zoom(self, event):
        """Zoom the map based on mouse wheel"""
        if event.num == 5 or event.delta == -120:  # Zoom out
            self.adjust_zoom(0.9, event.x, event.y)
        elif event.num == 4 or event.delta == 120:  # Zoom in
            self.adjust_zoom(1.1, event.x, event.y)

    def adjust_zoom(self, factor, x=None, y=None):
        """Adjust zoom level with optional center point"""
        old_zoom = self.zoom_level
        self.zoom_level *= factor
        self.zoom_level = max(0.1, min(3.0, self.zoom_level))  # Limit zoom range
        
        if old_zoom != self.zoom_level:
            if x is not None and y is not None:
                # Zoom toward mouse position
                self.canvas.scale("all", x, y, factor, factor)
            else:
                # Zoom toward center
                w = self.canvas.winfo_width() / 2
                h = self.canvas.winfo_height() / 2
                self.canvas.scale("all", w, h, factor, factor)
            
            # self.zoom_label.config(text=f"Zoom: {int(self.zoom_level*100)}%")

    def reset_view(self):
        """Reset zoom and pan to default"""
        self.zoom_level = 1.0
        self.pan_x = 0
        self.pan_y = 0
        self.canvas.delete("all")
        if self.last_state:
            self.draw_game_state(self.last_state)
        # self.zoom_label.config(text="Zoom: 100%")

    def start_auto_refresh(self):
        """Start the auto-refresh timer"""
        if self.auto_refresh_var.get():
            self.auto_refresh_id = self.root.after(self.refresh_interval, self.auto_refresh)

    def stop_auto_refresh(self):
        """Stop the auto-refresh timer"""
        if self.auto_refresh_id:
            self.root.after_cancel(self.auto_refresh_id)
            self.auto_refresh_id = None

    def toggle_auto_refresh(self):
        """Toggle auto-refresh on/off"""
        if self.auto_refresh_var.get():
            self.start_auto_refresh()
        else:
            self.stop_auto_refresh()

    def update_refresh_interval(self):
        """Update the refresh interval from the entry field"""
        try:
            new_interval = int(self.interval_entry.get())
            if new_interval > 0:
                self.refresh_interval = new_interval
                if self.auto_refresh_var.get():
                    self.stop_auto_refresh()
                    self.start_auto_refresh()
                self.status_label.config(text=f"Status: Refresh interval set to {new_interval}ms", fg="lightgreen")
            else:
                self.status_label.config(text="Status: Interval must be > 0", fg="red")
        except ValueError:
            self.status_label.config(text="Status: Invalid interval value", fg="red")

    def auto_refresh(self):
        """Auto-refresh callback"""
        self.load_and_display_latest_state()
        if self.auto_refresh_var.get():
            self.auto_refresh_id = self.root.after(self.refresh_interval, self.auto_refresh)

    def load_and_display_latest_state(self):
        """Load the most recent state from DB and display it"""
        try:
            # First verify file exists
            if not os.path.exists(self.db_path):
                self.status_label.config(text="Status: DB file not found", fg="red")
                return
                
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Verify table exists (using correct name 'Areas')
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Areas';")
            if not cursor.fetchone():
                self.status_label.config(text="Status: 'Areas' table not found", fg="red")
                conn.close()
                return
                
            # Get the most recent record from Areas table
            cursor.execute("""
                SELECT Date, Json 
                FROM Areas 
                ORDER BY Date DESC
                LIMIT 1
            """)
            
            row = cursor.fetchone()
            conn.close()
            
            if not row:
                self.status_label.config(text="Status: No data in 'Areas' table", fg="yellow")
                return
                
            datetime_str, json_str = row
            try:
                game_data = json.loads(json_str)
                self.last_state = game_data
                
                # Update info labels
                self.datetime_label.config(text=f"Time: {datetime_str}")
                self.status_label.config(text="Status: Loaded successfully", fg="lightgreen")
                
                # Try to get turn number from the JSON if available
                turn_number = game_data.get("turnNumber", "-")
                self.turn_label.config(text=f"Turn: {turn_number}")
                
                # Try to get player name from the JSON if available
                player_name = game_data.get("playerName", "-")
                self.player_label.config(text=f"Player: {player_name}")
                
                # Draw the game state
                self.canvas.delete("all")
                self.draw_game_state(game_data)
                
            except json.JSONDecodeError as e:
                self.status_label.config(text=f"Status: JSON Error - {str(e)}", fg="red")
                
        except sqlite3.Error as e:
            self.status_label.config(text=f"Status: DB Error - {str(e)}", fg="red")
        except Exception as e:
            self.status_label.config(text=f"Status: Unexpected Error - {str(e)}", fg="red")

    def draw_game_state(self, state: Dict):
        """Draw the game state on canvas with current zoom and pan"""
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        
        # Get all visible hex coordinates
        self.visible_hexes = set()
        for ant in state.get("ants", []):
            q, r = ant.get("q", 0), ant.get("r", 0)
            self.visible_hexes.add((q, r))
            
            # Add hexes in ant's vision radius
            radius = self.get_ant_vision_radius(ant)
            for dq in range(-radius, radius + 1):
                for dr in range(max(-radius, -dq - radius), min(radius, -dq + radius) + 1):
                    self.visible_hexes.add((q + dq, r + dr))
        
        # Add hexes from movement paths
        for ant in state.get("ants", []):
            if "lastMove" in ant:
                for hex_coord in ant["lastMove"]:
                    self.visible_hexes.add((hex_coord["q"], hex_coord["r"]))
        
        if not self.visible_hexes:
            return
            
        # Find bounds of visible area
        self.map_bounds = {
            "min_q": min(q for q, r in self.visible_hexes),
            "max_q": max(q for q, r in self.visible_hexes),
            "min_r": min(r for q, r in self.visible_hexes),
            "max_r": max(r for q, r in self.visible_hexes)
        }
        
        # Calculate hex size to fit visible area
        base_hex_size = min(
            width / ((self.map_bounds["max_q"] - self.map_bounds["min_q"] + 2) * 1.5),
            height / ((self.map_bounds["max_r"] - self.map_bounds["min_r"] + 2) * math.sqrt(3))
        )
        hex_size = max(5, min(30, base_hex_size * self.zoom_level))  # Apply zoom
        
        vert_spacing = hex_size * math.sqrt(3)
        horiz_spacing = hex_size * 3 / 2
        
        # Only center the map initially if not panned
        if self.pan_x == 0 and self.pan_y == 0:
            map_width = (self.map_bounds["max_q"] - self.map_bounds["min_q"] + 1) * horiz_spacing
            map_height = (self.map_bounds["max_r"] - self.map_bounds["min_r"] + 1) * vert_spacing
            self.pan_x = (width - map_width) / 2
            self.pan_y = (height - map_height) / 2
        
        # Draw tiles
        for tile in state.get("map", []):
            q, r = tile.get("q", 0), tile.get("r", 0)
            if (q, r) not in self.visible_hexes:
                continue
                
            x = (q - self.map_bounds["min_q"]) * horiz_spacing + self.pan_x
            y = (r - self.map_bounds["min_r"]) * vert_spacing + self.pan_y
            if q % 2 == 1:
                y += vert_spacing / 2
                
            color = self.get_tile_color(tile.get("type", 2))
            self.draw_hexagon(x, y, hex_size, color)
            
            # Label coordinates for debugging
            self.canvas.create_text(
                x, y, text=f"{q},{r}", 
                fill="white", font=("Arial", 6)
            )
        
        # Draw food
        for food in state.get("food", []):
            q, r = food.get("q", 0), food.get("r", 0)
            if (q, r) not in self.visible_hexes:
                continue
                
            x = (q - self.map_bounds["min_q"]) * horiz_spacing + self.pan_x
            y = (r - self.map_bounds["min_r"]) * vert_spacing + self.pan_y
            if q % 2 == 1:
                y += vert_spacing / 2
                
            color = self.get_food_color(food.get("type", 1))
            self.draw_hexagon(x, y, hex_size * 0.4, color)
            
            # Show food amount
            self.canvas.create_text(
                x, y, text=str(food.get("amount", 0)), 
                fill="white", font=("Arial", 8, "bold")
            )
        
        # Draw home base
        for home in state.get("home", []):
            q, r = home.get("q", 0), home.get("r", 0)
            if (q, r) not in self.visible_hexes:
                continue
                
            x = (q - self.map_bounds["min_q"]) * horiz_spacing + self.pan_x
            y = (r - self.map_bounds["min_r"]) * vert_spacing + self.pan_y
            if q % 2 == 1:
                y += vert_spacing / 2
                
            self.draw_hexagon(x, y, hex_size * 0.8, "#8040ff", "#ffffff")
        
        # Draw ants
        for ant in state.get("ants", []):
            q, r = ant.get("q", 0), ant.get("r", 0)
            x = (q - self.map_bounds["min_q"]) * horiz_spacing + self.pan_x
            y = (r - self.map_bounds["min_r"]) * vert_spacing + self.pan_y
            if q % 2 == 1:
                y += vert_spacing / 2
                
            color = self.get_ant_color(ant.get("type", 0))
            self.draw_hexagon(x, y, hex_size * 0.6, color)
            
            # Show ant health and attack power
            health = ant.get("health", 0)
            attack = ant.get("attack", 0)
            self.canvas.create_text(
                x, y - hex_size * 0.4, 
                text=f"{health}/{attack}",  # Display both health and attack
                fill="white", font=("Arial", 8, "bold")
            )
            
            # Show carried food if any
            if ant.get("food") and ant["food"].get("amount", 0) > 0:
                food_color = self.get_food_color(ant["food"].get("type", 1))
                self.canvas.create_oval(
                    x - hex_size * 0.2, y + hex_size * 0.3,
                    x + hex_size * 0.2, y + hex_size * 0.7,
                    fill=food_color, outline="black"
                )
                self.canvas.create_text(
                    x, y + hex_size * 0.5, 
                    text=str(ant["food"].get("amount", 0)), 
                    fill="black", font=("Arial", 6, "bold")
                )
        
        # Draw enemies
        for enemy in state.get("enemies", []):
            q, r = enemy.get("q", 0), enemy.get("r", 0)
            if (q, r) not in self.visible_hexes:
                continue
                
            x = (q - self.map_bounds["min_q"]) * horiz_spacing + self.pan_x
            y = (r - self.map_bounds["min_r"]) * vert_spacing + self.pan_y
            if q % 2 == 1:
                y += vert_spacing / 2
                
            self.draw_hexagon(x, y, hex_size * 0.5, "#ff00ff")
            
            # Show enemy health
            self.canvas.create_text(
                x, y, text=str(enemy.get("health", 0)), 
                fill="white", font=("Arial", 8, "bold")
            )

    def draw_hexagon(self, x: float, y: float, size: float, color: str, outline: str = "#303030"):
        """Draw a hexagon at the specified coordinates"""
        angle_deg = 60
        angle_rad = math.pi / 180 * angle_deg
        points = []
        for i in range(6):
            angle = angle_rad * i
            px = x + size * math.cos(angle)
            py = y + size * math.sin(angle)
            points.extend((px, py))
        self.canvas.create_polygon(points, outline=outline, fill=color)

    def draw_legend(self):
        """Draw the color legend"""
        self.legend_canvas.delete("all")
        x_start, y_start = 10, 10
        box_size = 15
        spacing_x = 100
        
        # Legend sections
        sections = [
            ("Terrain", {
                1: ("Nest", "#8040ff"),
                2: ("Empty", "#202020"),
                3: ("Dirt", "#70543e"),
                4: ("Acid", "#00ff00"),
                5: ("Stone", "#7f7f7f")
            }),
            ("Ants", {
                0: ("Worker", "#ffff00"),
                1: ("Warrior", "#ff0000"),
                2: ("Scout", "#00ffff")
            }),
            ("Food", {
                1: ("Apple", "#ff0000"),
                2: ("Bread", "#ffcc00"),
                3: ("Nectar", "#ff66b2")
            }),
            ("Other", {
                -1: ("Enemy", "#ff00ff")
            })
        ]
        
        x = x_start
        y = y_start
        
        for section_name, items in sections:
            self.legend_canvas.create_text(
                x, y, anchor="nw",
                text=f"{section_name}:", fill="white", font=("Arial", 8, "bold")
            )
            x += 60
            
            for item_type, (item_name, color) in items.items():
                self.legend_canvas.create_rectangle(
                    x, y, x + box_size, y + box_size,
                    fill=color, outline="white"
                )
                self.legend_canvas.create_text(
                    x + box_size + 5, y + box_size / 2,
                    anchor="w", text=item_name, fill="white", font=("Arial", 8)
                )
                x += spacing_x
            
            x = x_start
            y += box_size + 5

    def get_tile_color(self, tile_type: int) -> str:
        """Get color for tile type"""
        colors = {
            1: "#8040ff",  # nest
            2: "#202020",  # empty
            3: "#70543e",  # dirt
            4: "#00ff00",  # acid
            5: "#7f7f7f"   # stone
        }
        return colors.get(tile_type, "#000000")

    def get_ant_color(self, ant_type: int) -> str:
        """Get color for ant type"""
        colors = {
            0: "#ffff00",  # worker
            1: "#ff0000",  # warrior
            2: "#00ffff"   # scout
        }
        return colors.get(ant_type, "#ffffff")

    def get_food_color(self, food_type: int) -> str:
        """Get color for food type"""
        colors = {
            1: "#ff0000",  # apple
            2: "#ffcc00",  # bread
            3: "#ff66b2"   # nectar
        }
        return colors.get(food_type, "#ffffff")

    def get_ant_vision_radius(self, ant: Dict) -> int:
        """Get vision radius based on ant type"""
        ant_type = ant.get("type", 0)
        if ant_type == 0:  # Worker
            return 1
        elif ant_type == 1:  # Soldier
            return 1
        elif ant_type == 2:  # Scout
            return 4
        return 1

if __name__ == "__main__":
    # the absolute PATH until main.db file
    db_path = "/home/starman/os/JustDoIT/Kairat/app.db"
    refresh_interval = 2000
    visualizer = DatsPulseDBVisualizer(db_path, refresh_interval)