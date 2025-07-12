"""
Hex utilities component that handles hex-related calculations and operations.
"""

import math
from typing import Dict, Tuple, List


class HexUtils:
    """Handles hex-related calculations and operations."""
    
    def __init__(self):
        pass

    def get_ant_vision_radius(self, ant: Dict) -> int:
        """Get vision radius based on ant type."""
        ant_type = ant.get("type", 0)
        if ant_type == 0:  # Worker
            return 1
        elif ant_type == 1:  # Warrior
            return 1
        elif ant_type == 2:  # Scout
            return 4
        return 1

    def calculate_hex_distance(self, q1: int, r1: int, q2: int, r2: int) -> int:
        """Calculate the distance between two hex coordinates."""
        return (abs(q1 - q2) + abs(q1 + r1 - q2 - r2) + abs(r1 - r2)) // 2

    def get_hex_neighbors(self, q: int, r: int) -> List[Tuple[int, int]]:
        """Get all six neighboring hex coordinates."""
        directions = [
            (1, 0), (1, -1), (0, -1),
            (-1, 0), (-1, 1), (0, 1)
        ]
        return [(q + dq, r + dr) for dq, dr in directions]

    def get_hexes_in_radius(self, q: int, r: int, radius: int) -> List[Tuple[int, int]]:
        """Get all hex coordinates within a given radius."""
        hexes = []
        for dq in range(-radius, radius + 1):
            for dr in range(max(-radius, -dq - radius), min(radius, -dq + radius) + 1):
                hexes.append((q + dq, r + dr))
        return hexes

    def hex_to_pixel(self, q: int, r: int, size: float) -> Tuple[float, float]:
        """Convert hex coordinates to pixel coordinates."""
        x = size * (3/2 * q)
        y = size * (math.sqrt(3)/2 * q + math.sqrt(3) * r)
        return x, y

    def pixel_to_hex(self, x: float, y: float, size: float) -> Tuple[int, int]:
        """Convert pixel coordinates to hex coordinates."""
        q = (2/3 * x) / size
        r = (-1/3 * x + math.sqrt(3)/3 * y) / size
        return self.round_hex(q, r)

    def round_hex(self, q: float, r: float) -> Tuple[int, int]:
        """Round fractional hex coordinates to nearest hex."""
        s = -q - r
        q_round = round(q)
        r_round = round(r)
        s_round = round(s)
        
        q_diff = abs(q_round - q)
        r_diff = abs(r_round - r)
        s_diff = abs(s_round - s)
        
        if q_diff > r_diff and q_diff > s_diff:
            q_round = -r_round - s_round
        elif r_diff > s_diff:
            r_round = -q_round - s_round
        else:
            s_round = -q_round - r_round
            
        return q_round, r_round

    def get_hex_center(self, q: int, r: int, size: float) -> Tuple[float, float]:
        """Get the center pixel coordinates of a hex."""
        return self.hex_to_pixel(q, r, size)

    def get_hex_corners(self, q: int, r: int, size: float) -> List[Tuple[float, float]]:
        """Get the corner pixel coordinates of a hex."""
        center_x, center_y = self.get_hex_center(q, r, size)
        corners = []
        
        for i in range(6):
            angle = math.pi / 3 * i
            x = center_x + size * math.cos(angle)
            y = center_y + size * math.sin(angle)
            corners.append((x, y))
            
        return corners

    def is_valid_hex(self, q: int, r: int) -> bool:
        """Check if hex coordinates are valid."""
        # Basic validation - could be extended with map bounds
        return True

    def get_hex_line(self, q1: int, r1: int, q2: int, r2: int) -> List[Tuple[int, int]]:
        """Get all hexes along a line between two points."""
        distance = self.calculate_hex_distance(q1, r1, q2, r2)
        if distance == 0:
            return [(q1, r1)]
            
        hexes = []
        for i in range(distance + 1):
            t = i / distance
            q = q1 + (q2 - q1) * t
            r = r1 + (r2 - r1) * t
            hexes.append(self.round_hex(q, r))
            
        return hexes

    def get_hex_area(self, center_q: int, center_r: int, radius: int) -> List[Tuple[int, int]]:
        """Get all hexes in a circular area around a center point."""
        area = []
        for dq in range(-radius, radius + 1):
            for dr in range(max(-radius, -dq - radius), min(radius, -dq + radius) + 1):
                q = center_q + dq
                r = center_r + dr
                if self.calculate_hex_distance(center_q, center_r, q, r) <= radius:
                    area.append((q, r))
        return area 