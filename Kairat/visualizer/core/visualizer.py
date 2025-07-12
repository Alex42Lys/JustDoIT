"""
Main visualizer class that orchestrates the entire visualization system.
"""

import tkinter as tk
from typing import Dict, List, Tuple
import os
import math

from ..ui.control_panel import ControlPanel
from ..ui.game_canvas import GameCanvas
from ..data.database_manager import DatabaseManager
from ..utils.color_scheme import ColorScheme
from ..utils.hex_utils import HexUtils


class AntsGameVisualizer:
    """Main visualizer class that manages the entire visualization system."""
    
    def __init__(self, db_path: str, refresh_interval=2000):
        self.db_path = db_path
        self.refresh_interval = refresh_interval
        self.zoom_level = 1.0
        self.pan_x = 0
        self.pan_y = 0
        self.drag_data = {"x": 0, "y": 0, "item": None}
        self.last_state = None
        self.visible_hexes = set()
        self.map_bounds = {}
        self.all_states = []
        self.current_state_index = 0
        self.video_mode = False
        self.video_playing = False
        self.video_speed = 1.0
        self.selected_hex = None
        self.hex_info_window = None

        # Initialize components
        self._init_ui()
        self._init_components()
        self._setup_bindings()
        
        # Start the application
        self._start_application()

    def _init_ui(self):
        """Initialize the main UI components."""
        self.root = tk.Tk()
        self.root.title("Ants Game Visualizer")
        self.root.minsize(1000, 800)
        
        # Create main frames
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        self.canvas_frame = tk.Frame(self.main_frame)
        self.canvas_frame.pack(fill=tk.BOTH, expand=True)
        
        self.control_frame = tk.Frame(self.main_frame, bg="#202020", height=140)
        self.control_frame.pack(fill=tk.X)

    def _init_components(self):
        """Initialize all component classes."""
        # Initialize utility classes
        self.color_scheme = ColorScheme()
        self.hex_utils = HexUtils()
        self.db_manager = DatabaseManager(self.db_path)
        
        # Initialize UI components
        self.game_canvas = GameCanvas(
            self.canvas_frame, 
            self.color_scheme, 
            self.hex_utils
        )
        self.control_panel = ControlPanel(
            self.control_frame,
            self,
            self.db_manager
        )

    def _setup_bindings(self):
        """Setup event bindings for the canvas."""
        self.game_canvas.setup_bindings(self)

    def _start_application(self):
        """Start the application and main loop."""
        # Initial load
        self.game_canvas.draw_legend(self.control_frame)
        self.load_and_display_latest_state()
        self.start_auto_refresh()
        
        self.root.mainloop()

    def load_and_display_latest_state(self):
        """Load the most recent state from DB and display it."""
        if self.video_mode:
            return
            
        try:
            game_data = self.db_manager.get_latest_state()
            if game_data:
                self.last_state = game_data
                self.game_canvas.draw_game_state(game_data, self)
                self.control_panel.update_info_display(game_data)
            else:
                self.control_panel.update_status("No data available", "yellow")
                
        except Exception as e:
            self.control_panel.update_status(f"Error: {str(e)}", "red")

    def start_auto_refresh(self):
        """Start the auto-refresh timer."""
        if not self.video_mode:
            self.auto_refresh_id = self.root.after(
                self.refresh_interval, 
                self.auto_refresh
            )

    def stop_auto_refresh(self):
        """Stop the auto-refresh timer."""
        if hasattr(self, 'auto_refresh_id') and self.auto_refresh_id:
            self.root.after_cancel(self.auto_refresh_id)
            self.auto_refresh_id = None

    def auto_refresh(self):
        """Auto-refresh callback."""
        self.load_and_display_latest_state()
        if not self.video_mode:
            self.auto_refresh_id = self.root.after(
                self.refresh_interval, 
                self.auto_refresh
            )

    def update_refresh_interval(self, new_interval: int):
        """Update the refresh interval."""
        if new_interval > 0:
            self.refresh_interval = new_interval
            self.stop_auto_refresh()
            self.start_auto_refresh()
            self.control_panel.update_status(
                f"Refresh interval set to {new_interval}ms", 
                "lightgreen"
            )
        else:
            self.control_panel.update_status("Interval must be > 0", "red")

    def reset_view(self):
        """Reset zoom and pan to default."""
        self.zoom_level = 1.0
        self.pan_x = 0
        self.pan_y = 0
        self.game_canvas.reset_view()
        if self.last_state:
            self.game_canvas.draw_game_state(self.last_state, self)

    def toggle_video_mode(self):
        """Toggle between video mode and live mode."""
        self.video_mode = not self.video_mode
        
        if self.video_mode:
            self.all_states = self.db_manager.get_all_states()
            self.current_state_index = len(self.all_states) - 1 if self.all_states else 0
            self.control_panel.enable_video_mode()
            self.stop_auto_refresh()
        else:
            self.control_panel.disable_video_mode()
            self.all_states = []
            self.start_auto_refresh()
        
        self.control_panel.update_timeline_controls(self.video_mode, self.all_states)

    def display_state(self, state_data):
        """Display a specific state (for video mode)."""
        if isinstance(state_data, tuple):
            datetime_str, game_data = state_data
            self.last_state = game_data
        else:
            game_data = state_data
            datetime_str = "Unknown"
        
        self.control_panel.update_info_display(game_data, datetime_str)
        self.game_canvas.draw_game_state(game_data, self)

    def get_visible_hexes(self, state: Dict) -> set:
        """Calculate visible hexes based on game state."""
        visible_hexes = set()
        
        # Always show home bases
        for home in state.get("home", []):
            q, r = home.get("q", 0), home.get("r", 0)
            visible_hexes.add((q, r))
        
        # Show all our ants and their vision areas
        for ant in state.get("ants", []):
            q, r = ant.get("q", 0), ant.get("r", 0)
            visible_hexes.add((q, r))
            
            radius = self.hex_utils.get_ant_vision_radius(ant)
            for dq in range(-radius, radius + 1):
                for dr in range(max(-radius, -dq - radius), min(radius, -dq + radius) + 1):
                    visible_hexes.add((q + dq, r + dr))
        
        # Add hexes from movement paths
        for ant in state.get("ants", []):
            if "lastMove" in ant:
                for hex_coord in ant["lastMove"]:
                    visible_hexes.add((hex_coord["q"], hex_coord["r"]))
        
        # Add enemy positions
        for enemy in state.get("enemies", []):
            q, r = enemy.get("q", 0), enemy.get("r", 0)
            visible_hexes.add((q, r))
        
        # Add food positions
        for food in state.get("food", []):
            q, r = food.get("q", 0), food.get("r", 0)
            visible_hexes.add((q, r))
        
        return visible_hexes

    # Mouse interaction methods
    def start_pan(self, event):
        """Begin panning the map."""
        self.drag_data["x"] = event.x
        self.drag_data["y"] = event.y

    def pan(self, event):
        """Pan the map based on mouse movement."""
        dx = event.x - self.drag_data["x"]
        dy = event.y - self.drag_data["y"]
        
        self.pan_x += dx
        self.pan_y += dy
        
        self.drag_data["x"] = event.x
        self.drag_data["y"] = event.y
        
        self.game_canvas.canvas.move("all", dx, dy)

    def zoom(self, event):
        """Zoom the map based on mouse wheel."""
        if event.num == 5 or event.delta == -120:  # Zoom out
            self.adjust_zoom(0.9, event.x, event.y)
        elif event.num == 4 or event.delta == 120:  # Zoom in
            self.adjust_zoom(1.1, event.x, event.y)

    def adjust_zoom(self, factor, x=None, y=None):
        """Adjust zoom level with optional center point."""
        old_zoom = self.zoom_level
        self.zoom_level *= factor
        self.zoom_level = max(0.1, min(3.0, self.zoom_level))
        
        if old_zoom != self.zoom_level:
            if x is not None and y is not None:
                self.game_canvas.canvas.scale("all", x, y, factor, factor)
            else:
                w = self.game_canvas.canvas.winfo_width() / 2
                h = self.game_canvas.canvas.winfo_height() / 2
                self.game_canvas.canvas.scale("all", w, h, factor, factor)

    def show_hex_info(self, event):
        """Show detailed info for hex under cursor."""
        # Find closest hex to click position
        closest_hex = None
        min_dist = float('inf')
        
        for item in self.game_canvas.canvas.find_all():
            tags = self.game_canvas.canvas.gettags(item)
            if "hex" in tags:
                coords = self.game_canvas.canvas.coords(item)
                center_x = sum(coords[0::2]) / (len(coords) // 2)
                center_y = sum(coords[1::2]) / (len(coords) // 2)
                
                dist = math.sqrt((event.x - center_x)**2 + (event.y - center_y)**2)
                if dist < min_dist:
                    min_dist = dist
                    closest_hex = tags[1] if len(tags) > 1 else None
        
        if closest_hex:
            q, r = map(int, closest_hex.split(','))
            self.show_hex_details(q, r)

    def show_hex_details(self, q: int, r: int):
        """Show details for specific hex coordinates."""
        if not self.last_state:
            return
            
        # Create or update info window
        if self.hex_info_window and self.hex_info_window.winfo_exists():
            self.hex_info_window.destroy()
        
        self.hex_info_window = tk.Toplevel(self.root)
        self.hex_info_window.title(f"Hex Info ({q},{r})")
        self.hex_info_window.geometry("300x400")
        
        # Create text widget for info
        text = tk.Text(self.hex_info_window, wrap=tk.WORD)
        text.pack(fill=tk.BOTH, expand=True)
        
        # Collect info about this hex
        info_lines = [f"Hex Coordinates: {q},{r}"]
        
        # Check if it's a home base
        for home in self.last_state.get("home", []):
            if home.get("q", -1) == q and home.get("r", -1) == r:
                info_lines.append("\nHome Base:")
                info_lines.append(f"Type: {'Main' if home.get('spot', False) else 'Secondary'}")
                break
        
        # Check for tile
        for tile in self.last_state.get("map", []):
            if tile.get("q", -1) == q and tile.get("r", -1) == r:
                tile_type = tile.get("type", 2)
                type_names = {
                    1: "Nest",
                    2: "Empty",
                    3: "Dirt",
                    4: "Acid",
                    5: "Stone"
                }
                info_lines.append(f"\nTile Type: {type_names.get(tile_type, 'Unknown')}")
                break
        
        # Check for food
        for food in self.last_state.get("food", []):
            if food.get("q", -1) == q and food.get("r", -1) == r:
                food_type = food.get("type", 1)
                type_names = {
                    1: "Apple",
                    2: "Bread",
                    3: "Nectar"
                }
                info_lines.append(f"\nFood: {type_names.get(food_type, 'Unknown')}")
                info_lines.append(f"Amount: {food.get('amount', 0)}")
                break
        
        # Check for ants
        ants_here = []
        for ant in self.last_state.get("ants", []):
            if ant.get("q", -1) == q and ant.get("r", -1) == r:
                ants_here.append(ant)
        
        if ants_here:
            info_lines.append("\nAnts:")
            for ant in ants_here:
                ant_type = {0: "Worker", 1: "Warrior", 2: "Scout"}.get(ant.get("type", -1), "Unknown")
                info_lines.append(f"- {ant_type} (ID: {ant.get('id', '?')})")
                info_lines.append(f"  Health: {ant.get('health', 0)}")
                info_lines.append(f"  Attack: {ant.get('attack', 0)}")
                if ant.get("food"):
                    food_type = {1: "Apple", 2: "Bread", 3: "Nectar"}.get(ant["food"].get("type", -1), "Unknown")
                    info_lines.append(f"  Carrying: {ant['food'].get('amount', 0)} {food_type}")
        
        # Check for enemies
        enemies_here = []
        for enemy in self.last_state.get("enemies", []):
            if enemy.get("q", -1) == q and enemy.get("r", -1) == r:
                enemies_here.append(enemy)
        
        if enemies_here:
            info_lines.append("\nEnemies:")
            for enemy in enemies_here:
                info_lines.append(f"- Health: {enemy.get('health', 0)}")
                info_lines.append(f"  Attack: {enemy.get('attack', 0)}")
        
        # Display all collected info
        text.insert(tk.END, "\n".join(info_lines))
        text.config(state=tk.DISABLED) 