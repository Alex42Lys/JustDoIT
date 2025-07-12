"""
Game canvas component that handles all drawing operations for the game visualization.
"""

import tkinter as tk
import math
from typing import Dict, Tuple, Set

from ..utils.color_scheme import ColorScheme
from ..utils.hex_utils import HexUtils


class GameCanvas:
    """Handles all drawing operations for the game visualization."""
    
    def __init__(self, parent, color_scheme: ColorScheme, hex_utils: HexUtils):
        self.parent = parent
        self.color_scheme = color_scheme
        self.hex_utils = hex_utils
        
        # Canvas setup
        self.canvas = tk.Canvas(parent, bg="black")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Drawing state
        self.zoom_level = 1.0
        self.pan_x = 0
        self.pan_y = 0
        self.map_bounds = {}
        self.visible_hexes = set()

    def setup_bindings(self, visualizer):
        """Setup mouse and keyboard bindings for the canvas."""
        self.canvas.bind("<ButtonPress-1>", visualizer.start_pan)
        self.canvas.bind("<B1-Motion>", visualizer.pan)
        self.canvas.bind("<MouseWheel>", visualizer.zoom)
        self.canvas.bind("<Button-4>", visualizer.zoom)
        self.canvas.bind("<Button-5>", visualizer.zoom)
        self.canvas.bind("<Button-3>", visualizer.show_hex_info)

    def draw_legend(self, parent):
        """Draw the color legend."""
        legend_canvas = tk.Canvas(
            parent, 
            bg="#202020", 
            height=100, 
            highlightthickness=0
        )
        legend_canvas.pack(fill=tk.X, padx=10, pady=5)
        
        x_start, y_start = 10, 10
        box_size = 15
        spacing_x = 120
        row_spacing = 25
        
        # Legend sections
        sections = [
            ("Terrain", {
                1: ("Nest", "#FF00FF", "#FFFFFF"),
                2: ("Empty", "#404040", "#FFFFFF"),
                3: ("Dirt", "#8B4513", "#FFFFFF"),
                4: ("Acid", "#00FF00", "#000000"),
                5: ("Stone", "#C0C0C0", "#000000")
            }),
            ("Ants", {
                0: ("Worker", "#FFFF00", "#000000"),
                1: ("Warrior", "#8A2BE2", "#FFFFFF"),
                2: ("Scout", "#00FFFF", "#000000")
            }),
            ("Food", {
                1: ("Apple", "#FF4500", "#FFFFFF"),
                2: ("Bread", "#32CD32", "#000000"),
                3: ("Nectar", "#FF69B4", "#000000")
            }),
            ("Enemies", {
                -1: ("Enemy", "#FF0000", "#000000"),
            }),
            ("Other", {
                -2: ("Home", "#9370DB", "#FFFFFF")
            })
        ]
        
        x = x_start
        y = y_start
        
        for section_name, items in sections:
            # Draw section header
            legend_canvas.create_text(
                x, y, anchor="nw",
                text=f"{section_name}:", fill="white", font=("Arial", 9, "bold")
            )
            x += 70
            
            for item_type, (item_name, color, text_color) in items.items():
                legend_canvas.create_rectangle(
                    x, y, x + box_size, y + box_size,
                    fill=color, outline="white"
                )
                legend_canvas.create_text(
                    x + box_size + 5, y + box_size / 2,
                    anchor="w", text=item_name, fill=text_color, font=("Arial", 8)
                )
                x += spacing_x
            
            x = x_start
            y += row_spacing

    def draw_game_state(self, state: Dict, visualizer):
        """Draw the complete game state."""
        self.canvas.delete("all")
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        
        # Get visible hexes from visualizer
        self.visible_hexes = visualizer.get_visible_hexes(state)
        
        if not self.visible_hexes:
            return
            
        # Calculate hex size and positions
        self.calculate_map_bounds()
        hex_size = self.calculate_hex_size(width, height)
        vert_spacing = hex_size * math.sqrt(3)
        horiz_spacing = hex_size * 3 / 2
        
        # Center map if not panned
        if visualizer.pan_x == 0 and visualizer.pan_y == 0:
            self.center_map(horiz_spacing, vert_spacing, width, height, visualizer)
        
        # Draw all visible elements
        self.draw_map_tiles(state, horiz_spacing, vert_spacing, hex_size, visualizer)
        self.draw_food(state, horiz_spacing, vert_spacing, hex_size, visualizer)
        self.draw_home_bases(state, horiz_spacing, vert_spacing, hex_size, visualizer)
        self.draw_ants(state, horiz_spacing, vert_spacing, hex_size, visualizer)
        self.draw_enemies(state, horiz_spacing, vert_spacing, hex_size, visualizer)

    def calculate_map_bounds(self):
        """Calculate min/max coordinates of visible hexes."""
        if not self.visible_hexes:
            return
            
        q_coords = [q for q, r in self.visible_hexes]
        r_coords = [r for q, r in self.visible_hexes]
        
        self.map_bounds = {
            "min_q": min(q_coords),
            "max_q": max(q_coords),
            "min_r": min(r_coords),
            "max_r": max(r_coords)
        }

    def calculate_hex_size(self, width, height):
        """Calculate appropriate hex size based on visible area."""
        if not self.map_bounds:
            return 20
            
        hex_width = (self.map_bounds["max_q"] - self.map_bounds["min_q"] + 1) * 1.5
        hex_height = (self.map_bounds["max_r"] - self.map_bounds["min_r"] + 1) * math.sqrt(3)
        
        base_hex_size = min(
            width / hex_width,
            height / hex_height
        )
        
        return max(5, min(30, base_hex_size * self.zoom_level))

    def center_map(self, horiz_spacing, vert_spacing, width, height, visualizer):
        """Center the map on the canvas."""
        map_width = (self.map_bounds["max_q"] - self.map_bounds["min_q"] + 1) * horiz_spacing
        map_height = (self.map_bounds["max_r"] - self.map_bounds["min_r"] + 1) * vert_spacing
        visualizer.pan_x = (width - map_width) / 2
        visualizer.pan_y = (height - map_height) / 2

    def calculate_hex_position(self, q, r, horiz_spacing, vert_spacing, visualizer):
        """Calculate screen position for a hex."""
        x = (q - self.map_bounds["min_q"]) * horiz_spacing + visualizer.pan_x
        y = (r - self.map_bounds["min_r"]) * vert_spacing + visualizer.pan_y
        if q % 2 == 1:
            y += vert_spacing / 2
        return x, y

    def draw_map_tiles(self, state, horiz_spacing, vert_spacing, hex_size, visualizer):
        """Draw all visible map tiles."""
        for tile in state.get("map", []):
            q, r = tile.get("q", 0), tile.get("r", 0)
            if (q, r) not in self.visible_hexes:
                continue
                
            x, y = self.calculate_hex_position(q, r, horiz_spacing, vert_spacing, visualizer)
            color, text_color = self.color_scheme.get_tile_color(tile.get("type", 2))
            self.draw_hexagon(x, y, hex_size, color)
            
            self.canvas.create_text(
                x, y, text=f"{q},{r}", 
                fill=text_color, font=("Arial", 6)
            )

    def draw_food(self, state, horiz_spacing, vert_spacing, hex_size, visualizer):
        """Draw all visible food."""
        for food in state.get("food", []):
            q, r = food.get("q", 0), food.get("r", 0)
            if (q, r) not in self.visible_hexes:
                continue
                
            x, y = self.calculate_hex_position(q, r, horiz_spacing, vert_spacing, visualizer)
            color, text_color = self.color_scheme.get_food_color(food.get("type", 1))
            self.draw_hexagon(x, y, hex_size * 0.4, color)
            
            self.canvas.create_text(
                x, y, text=str(food.get("amount", 0)), 
                fill=text_color, font=("Arial", 8, "bold")
            )

    def draw_home_bases(self, state, horiz_spacing, vert_spacing, hex_size, visualizer):
        """Draw home bases."""
        for home in state.get("home", []):
            q, r = home.get("q", 0), home.get("r", 0)
            if (q, r) not in self.visible_hexes:
                continue
                
            x, y = self.calculate_hex_position(q, r, horiz_spacing, vert_spacing, visualizer)
            self.draw_hexagon(x, y, hex_size * 0.8, "#9370DB", "#FFFFFF")

    def draw_ants(self, state, horiz_spacing, vert_spacing, hex_size, visualizer):
        """Draw all ants with detailed information."""
        for ant in state.get("ants", []):
            q, r = ant.get("q", 0), ant.get("r", 0)
            x, y = self.calculate_hex_position(q, r, horiz_spacing, vert_spacing, visualizer)
            
            color, text_color = self.color_scheme.get_ant_color(ant.get("type", 0))
            self.draw_hexagon(x, y, hex_size * 0.6, color)
            
            ant_type = {0: "Worker", 1: "Warrior", 2: "Scout"}.get(ant.get("type", 0), "Unknown")
            health = ant.get("health", 0)
            attack = ant.get("attack", 0)
            
            self.canvas.create_text(
                x, y - hex_size * 0.3, 
                text=f"{ant_type[:1]} H:{health} A:{attack}", 
                fill=text_color, font=("Arial", 8, "bold")
            )
            
            if ant.get("food") and ant["food"].get("amount", 0) > 0:
                food_type = ant["food"].get("type", 1)
                food_amount = ant["food"].get("amount", 0)
                food_color, food_text_color = self.color_scheme.get_food_color(food_type)
                
                self.canvas.create_oval(
                    x - hex_size * 0.2, y + hex_size * 0.3,
                    x + hex_size * 0.2, y + hex_size * 0.7,
                    fill=food_color, outline="black"
                )
                self.canvas.create_text(
                    x, y + hex_size * 0.5, 
                    text=str(food_amount), 
                    fill=food_text_color, font=("Arial", 6, "bold")
                )
                
            if "move" in ant and len(ant["move"]) > 0:
                path_coords = []
                for step in ant["move"]:
                    step_x, step_y = self.calculate_hex_position(
                        step["q"], step["r"], horiz_spacing, vert_spacing, visualizer
                    )
                    path_coords.extend([step_x, step_y])
                
                if len(path_coords) >= 4:
                    self.canvas.create_line(
                        x, y, *path_coords,
                        fill="yellow", arrow=tk.LAST, dash=(3, 3), width=1
                    )

    def draw_enemies(self, state, horiz_spacing, vert_spacing, hex_size, visualizer):
        """Draw all visible enemies."""
        enemies = state.get("enemies", [])
        
        for enemy in enemies:
            q, r = enemy.get("q", 0), enemy.get("r", 0)
            if (q, r) not in self.visible_hexes:
                continue
                
            x, y = self.calculate_hex_position(q, r, horiz_spacing, vert_spacing, visualizer)
            self.draw_hexagon(x, y, hex_size * 0.5, "#FF0000", "#FFFFFF")
            
            self.canvas.create_text(
                x, y, text=str(enemy.get("health", 0)), 
                fill="#000000", font=("Arial", 8, "bold")
            )

    def draw_hexagon(self, x: float, y: float, size: float, color: str, outline: str = "#303030"):
        """Draw a hexagon at the specified coordinates."""
        angle_deg = 60
        angle_rad = math.pi / 180 * angle_deg
        points = []
        for i in range(6):
            angle = angle_rad * i
            px = x + size * math.cos(angle)
            py = y + size * math.sin(angle)
            points.extend((px, py))
        self.canvas.create_polygon(points, outline=outline, fill=color)

    def reset_view(self):
        """Reset the canvas view."""
        self.canvas.delete("all") 