import tkinter as tk
from tkinter import messagebox
import math
import os
from typing import Dict, List, Optional
from datspulse_client import AntProtocolClient  # API client from previous code

# Constants
HEX_TYPE_COLORS = {
    1: "#8040ff",  # nest (purple)
    2: "#202020",  # empty (dark gray)
    3: "#70543e",  # dirt (brown)
    4: "#00ff00",  # acid (green)
    5: "#7f7f7f",  # stone (gray)
}

UNIT_TYPE_COLORS = {
    0: "#ffff00",  # worker (yellow)
    1: "#ff0000",  # warrior (red)
    2: "#00ffff",  # scout (cyan)
}

FOOD_TYPE_COLORS = {
    1: "#ff0000",  # apple (red)
    2: "#ffcc00",  # bread (yellow)
    3: "#ff66b2",  # nectar (pink)
}

class GameUI:
    def __init__(self, root):
        self.root = root
        self.root.title("DatsPulse - Connecting...")
        self.root.minsize(800, 800)
        
        # Initialize UI elements first
        self.setup_ui()
        
        # Try to initialize game client
        self.initialize_game()

    def setup_ui(self):
        """Setup all UI elements"""
        # Main layout
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Game canvas
        self.canvas = tk.Canvas(self.main_frame, bg="black")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Info panel at bottom
        self.info_frame = tk.Frame(self.main_frame, bg="#202020", height=150)
        self.info_frame.pack(fill=tk.X)
        
        # Legend canvas
        self.legend_canvas = tk.Canvas(
            self.info_frame, bg="#202020", height=150, highlightthickness=0
        )
        self.legend_canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Game stats display
        self.stats_frame = tk.Frame(self.info_frame, bg="#202020")
        self.stats_frame.pack(fill=tk.BOTH, expand=True)
        
        # Stats labels
        self.turn_label = tk.Label(
            self.stats_frame, text="Turn: -", bg="#202020", fg="white", 
            font=("Arial", 10, "bold"), anchor="w"
        )
        self.turn_label.pack(fill=tk.X, padx=10)
        
        self.score_label = tk.Label(
            self.stats_frame, text="Score: -", bg="#202020", fg="white", 
            font=("Arial", 10, "bold"), anchor="w"
        )
        self.score_label.pack(fill=tk.X, padx=10)
        
        self.ants_label = tk.Label(
            self.stats_frame, text="Ants: -", bg="#202020", fg="white", 
            font=("Arial", 10, "bold"), anchor="w"
        )
        self.ants_label.pack(fill=tk.X, padx=10)
        
        # Status label for connection/errors
        self.status_label = tk.Label(
            self.stats_frame, text="Connecting to game server...", bg="#202020", fg="#ff6666",
            font=("Arial", 9), anchor="w"
        )
        self.status_label.pack(fill=tk.X, padx=10)
        
        # Event bindings
        self.canvas.bind("<Configure>", self.on_canvas_resize)

    def initialize_game(self):
        """Initialize game client and register for the game"""
        try:
            # Get API key from environment variable
            self.api_key = os.getenv('DATSPULSE_API_KEY')
            if not self.api_key:
                raise ValueError("DATSPULSE_API_KEY environment variable not set")
            
            # Initialize client
            self.client = AntProtocolClient(self.api_key)
            
            # Try to register
            self.status_label.config(text="Registering for game...")
            self.root.update()  # Force UI update
            
            self.registration = self.client.register()
            if not self.registration:
                raise ValueError("Registration failed - no data received")
            
            # Update window title with player name
            self.root.title(f"DatsPulse - {self.registration.get('name', 'Unknown')}")
            self.status_label.config(text="Registration successful!")
            
            # Start the game loop after a brief pause
            self.root.after(1000, self.refresh_loop)
            
        except Exception as e:
            error_msg = f"Initialization failed: {str(e)}"
            self.status_label.config(text=error_msg)
            messagebox.showerror("Game Error", error_msg)
            print(error_msg)
            
            # Disable game functionality
            self.client = None

    def draw_legend(self):
        """Draw the color legend for map elements"""
        self.legend_canvas.delete("all")
        x_start, y_start = 10, 10
        box_size = 20
        spacing_x = 120  # horizontal space between legend items
        spacing_y = 30    # vertical space between rows
        
        # Create legend sections
        sections = [
            ("Terrain", HEX_TYPE_COLORS),
            ("Ant Types", UNIT_TYPE_COLORS),
            ("Food Types", FOOD_TYPE_COLORS)
        ]
        
        y = y_start
        for section_name, color_map in sections:
            self.legend_canvas.create_text(
                x_start, y, anchor="nw",
                text=f"{section_name}:", fill="white", font=("Arial", 10, "bold")
            )
            y += 20
            
            x = x_start
            for i, (name, color) in enumerate(color_map.items()):
                if i > 0 and i % 3 == 0:
                    x = x_start
                    y += spacing_y
                
                self.legend_canvas.create_rectangle(
                    x, y, x + box_size, y + box_size,
                    fill=color, outline="white"
                )
                text = ""
                if section_name == "Terrain":
                    text = {
                        1: "Nest", 2: "Empty", 3: "Dirt", 
                        4: "Acid", 5: "Stone"
                    }.get(name, str(name))
                elif section_name == "Ant Types":
                    text = {
                        0: "Worker", 1: "Warrior", 2: "Scout"
                    }.get(name, str(name))
                elif section_name == "Food Types":
                    text = {
                        1: "Apple", 2: "Bread", 3: "Nectar"
                    }.get(name, str(name))
                
                self.legend_canvas.create_text(
                    x + box_size + 5, y + box_size / 2,
                    anchor="w", text=text, fill="white", font=("Arial", 9)
                )
                x += spacing_x
            
            y += spacing_y + 10

    def draw_hex(self, x: float, y: float, size: float, color: str, outline: str = "#303030"):
        """Draw a hexagon at the specified coordinates"""
        angle_deg = 60
        angle_rad = math.pi / 180 * angle_deg
        points = []
        for i in range(6):
            angle = angle_rad * i
            px = x + size * math.cos(angle)
            py = y + size * math.sin(angle)
            points.extend((px, py))
        return self.canvas.create_polygon(points, outline=outline, fill=color)

    def draw_map(self):
        """Draw the entire game map based on current game state"""
        if not self.client or not self.client.current_state:
            return
            
        self.canvas.delete("all")
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        game_data = self.client.current_state
            
        # Update stats display
        self.turn_label.config(text=f"Turn: {game_data.get('turnNo', 0)}")
        self.score_label.config(text=f"Score: {game_data.get('score', 0)}")
        self.ants_label.config(text=f"Ants: {len(game_data.get('ants', []))}")
        
        # Calculate hex size based on visible map area
        visible_hexes = set()
        for ant in game_data.get("ants", []):
            q, r = ant["q"], ant["r"]
            visible_hexes.add((q, r))
            # Add hexes in ant's vision radius
            radius = self.client._get_ant_vision_radius(ant)
            for dq in range(-radius, radius + 1):
                for dr in range(max(-radius, -dq - radius), min(radius, -dq + radius) + 1):
                    visible_hexes.add((q + dq, r + dr))
        
        # Add hexes from movement paths
        for ant in game_data.get("ants", []):
            if "lastMove" in ant:
                for hex_coord in ant["lastMove"]:
                    visible_hexes.add((hex_coord["q"], hex_coord["r"]))
        
        if not visible_hexes:
            return
            
        # Find bounds of visible area
        min_q = min(q for q, r in visible_hexes)
        max_q = max(q for q, r in visible_hexes)
        min_r = min(r for q, r in visible_hexes)
        max_r = max(r for q, r in visible_hexes)
        
        # Calculate hex size to fit visible area
        hex_size = min(
            width / ((max_q - min_q + 2) * 1.5),
            height / ((max_r - min_r + 2) * math.sqrt(3))
        )
        hex_size = max(5, min(30, hex_size))  # Limit hex size
        
        vert_spacing = hex_size * math.sqrt(3)
        horiz_spacing = hex_size * 3 / 2
        
        # Draw tiles
        for tile in game_data.get("map", []):
            q, r = tile["q"], tile["r"]
            if (q, r) not in visible_hexes:
                continue
                
            x = (q - min_q) * horiz_spacing + 50
            y = (r - min_r) * vert_spacing + 50
            if q % 2 == 1:
                y += vert_spacing / 2
                
            color = HEX_TYPE_COLORS.get(tile["type"], "black")
            self.draw_hex(x, y, hex_size, color)
            
            # Label coordinates for debugging
            self.canvas.create_text(
                x, y, text=f"{q},{r}", 
                fill="white", font=("Arial", 6)
            )
        
        # Draw food
        for food in game_data.get("food", []):
            q, r = food["q"], food["r"]
            if (q, r) not in visible_hexes:
                continue
                
            x = (q - min_q) * horiz_spacing + 50
            y = (r - min_r) * vert_spacing + 50
            if q % 2 == 1:
                y += vert_spacing / 2
                
            color = FOOD_TYPE_COLORS.get(food["type"], "white")
            self.draw_hex(x, y, hex_size * 0.4, color)
            
            # Show food amount
            self.canvas.create_text(
                x, y, text=str(food["amount"]), 
                fill="white", font=("Arial", 8, "bold")
            )
        
        # Draw home base
        for home in game_data.get("home", []):
            q, r = home["q"], home["r"]
            if (q, r) not in visible_hexes:
                continue
                
            x = (q - min_q) * horiz_spacing + 50
            y = (r - min_r) * vert_spacing + 50
            if q % 2 == 1:
                y += vert_spacing / 2
                
            self.draw_hex(x, y, hex_size * 0.8, "#8040ff", "#ffffff")
        
        # Draw ants
        for ant in game_data.get("ants", []):
            q, r = ant["q"], ant["r"]
            x = (q - min_q) * horiz_spacing + 50
            y = (r - min_r) * vert_spacing + 50
            if q % 2 == 1:
                y += vert_spacing / 2
                
            color = UNIT_TYPE_COLORS.get(ant["type"], "white")
            ant_hex = self.draw_hex(x, y, hex_size * 0.6, color)
            
            # Show ant health
            self.canvas.create_text(
                x, y - hex_size * 0.4, 
                text=str(ant["health"]), 
                fill="white", font=("Arial", 8, "bold")
            )
            
            # Show carried food if any
            if ant.get("food") and ant["food"].get("amount", 0) > 0:
                food_color = FOOD_TYPE_COLORS.get(ant["food"]["type"], "white")
                self.canvas.create_oval(
                    x - hex_size * 0.2, y + hex_size * 0.3,
                    x + hex_size * 0.2, y + hex_size * 0.7,
                    fill=food_color, outline="black"
                )
                self.canvas.create_text(
                    x, y + hex_size * 0.5, 
                    text=str(ant["food"]["amount"]), 
                    fill="black", font=("Arial", 6, "bold")
                )
        
        # Draw enemies
        for enemy in game_data.get("enemies", []):
            q, r = enemy["q"], enemy["r"]
            if (q, r) not in visible_hexes:
                continue
                
            x = (q - min_q) * horiz_spacing + 50
            y = (r - min_r) * vert_spacing + 50
            if q % 2 == 1:
                y += vert_spacing / 2
                
            color = "#ff00ff"  # Magenta for enemies
            self.draw_hex(x, y, hex_size * 0.5, color)
            
            # Show enemy health
            self.canvas.create_text(
                x, y, text=str(enemy["health"]), 
                fill="white", font=("Arial", 8, "bold")
            )

    def refresh_loop(self):
        """Main game loop that updates the display"""
        if not self.client:
            return
            
        try:
            # Get current game state
            self.client.get_arena()
            
            # Make AI decisions and send moves
            moves = self.client.make_decisions()
            if moves:
                self.client.send_moves(moves)
            
            # Update display
            self.draw_map()
            self.draw_legend()
            
            # Schedule next update
            next_turn_in = self.client.current_state.get("nextTurnIn", 2.0)
            delay = max(100, int(next_turn_in * 1000 * 0.9))  # Update slightly before next turn
            self.root.after(delay, self.refresh_loop)
            
        except Exception as e:
            error_msg = f"Game error: {str(e)}"
            self.status_label.config(text=error_msg)
            print(error_msg)
            # Retry after a short delay
            self.root.after(1000, self.refresh_loop)

    def on_canvas_resize(self, event):
        """Handle canvas resize events"""
        self.draw_map()
        self.draw_legend()

if __name__ == "__main__":
    # Check if API key is set in environment
    if 'DATSPULSE_API_KEY' not in os.environ:
        print("Error: DATSPULSE_API_KEY environment variable not set")
        print("Please set your API key before running:")
        print("On Linux/Mac: export DATSPULSE_API_KEY='your-api-key'")
        print("On Windows: set DATSPULSE_API_KEY='your-api-key'")
        exit(1)
    
    root = tk.Tk()
    try:
        ui = GameUI(root)
        root.mainloop()
    except Exception as e:
        messagebox.showerror("Fatal Error", f"Failed to start game: {str(e)}")
        print(f"Fatal error: {e}")