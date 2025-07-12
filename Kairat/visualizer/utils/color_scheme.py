"""
Color scheme utility that manages all color mappings for the visualizer.
"""

from typing import Dict, Tuple


class ColorScheme:
    """Manages color schemes for different game elements."""
    
    def __init__(self):
        # Tile colors with text colors
        self.tile_colors = {
            1: ("#FF00FF", "#FFFFFF"),  # Nest
            2: ("#404040", "#FFFFFF"),  # Empty
            3: ("#8B4513", "#FFFFFF"),  # Dirt
            4: ("#00FF00", "#000000"),  # Acid
            5: ("#C0C0C0", "#000000")   # Stone
        }
        
        # Ant colors with text colors
        self.ant_colors = {
            0: ("#FFFF00", "#000000"),  # Worker
            1: ("#8A2BE2", "#FFFFFF"),  # Warrior
            2: ("#00FFFF", "#000000")   # Scout
        }
        
        # Food colors with text colors
        self.food_colors = {
            1: ("#FF4500", "#FFFFFF"),  # Apple
            2: ("#32CD32", "#000000"),  # Bread
            3: ("#FF69B4", "#000000")   # Nectar
        }
        
        # Enemy colors
        self.enemy_colors = {
            -1: ("#FF0000", "#000000"),  # Enemy
        }
        
        # Home base colors
        self.home_colors = {
            -2: ("#9370DB", "#FFFFFF")  # Home
        }

    def get_tile_color(self, tile_type: int) -> Tuple[str, str]:
        """Get color for tile type with text color."""
        return self.tile_colors.get(tile_type, ("#000000", "#FFFFFF"))

    def get_ant_color(self, ant_type: int) -> Tuple[str, str]:
        """Get color for ant type with text color."""
        return self.ant_colors.get(ant_type, ("#FFFFFF", "#000000"))

    def get_food_color(self, food_type: int) -> Tuple[str, str]:
        """Get color for food type with text color."""
        return self.food_colors.get(food_type, ("#FFFFFF", "#000000"))

    def get_enemy_color(self, enemy_type: int) -> Tuple[str, str]:
        """Get color for enemy type with text color."""
        return self.enemy_colors.get(enemy_type, ("#FF0000", "#000000"))

    def get_home_color(self, home_type: int) -> Tuple[str, str]:
        """Get color for home type with text color."""
        return self.home_colors.get(home_type, ("#9370DB", "#FFFFFF"))

    def get_all_colors(self) -> Dict[str, Dict[int, Tuple[str, str]]]:
        """Get all color schemes for legend display."""
        return {
            "Terrain": self.tile_colors,
            "Ants": self.ant_colors,
            "Food": self.food_colors,
            "Enemies": self.enemy_colors,
            "Other": self.home_colors
        }

    def get_type_name(self, category: str, type_id: int) -> str:
        """Get the name for a specific type ID in a category."""
        type_names = {
            "Terrain": {
                1: "Nest",
                2: "Empty", 
                3: "Dirt",
                4: "Acid",
                5: "Stone"
            },
            "Ants": {
                0: "Worker",
                1: "Warrior",
                2: "Scout"
            },
            "Food": {
                1: "Apple",
                2: "Bread", 
                3: "Nectar"
            },
            "Enemies": {
                -1: "Enemy"
            },
            "Other": {
                -2: "Home"
            }
        }
        
        return type_names.get(category, {}).get(type_id, "Unknown") 