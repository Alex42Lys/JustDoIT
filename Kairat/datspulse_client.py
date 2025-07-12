import requests
import time
from typing import List, Dict, Optional
import uuid
import math
from collections import defaultdict

class AntProtocolClient:
    def __init__(self, api_key: str, server_url: str = "https://games.datsteam.dev"):
        self.api_key = api_key
        self.server_url = server_url
        self.headers = {"X-Auth-Token": api_key}
        
        # Game state cache
        self.current_state = None
        self.ants = []
        self.enemies = []
        self.food = []
        self.home = []
        self.map_tiles = []
        self.visible_tiles = set()
        
        # Rate limiting
        self.last_request_time = 0
        self.request_interval = 0.34  # ~3 requests per second

    def _rate_limit(self):
        """Ensure we don't exceed the API rate limit"""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.request_interval:
            time.sleep(self.request_interval - elapsed)
        self.last_request_time = time.time()

    def register(self) -> Dict:
        """Register for a game round"""
        self._rate_limit()
        url = f"{self.server_url}/api/register"
        response = requests.post(url, headers=self.headers)
        response.raise_for_status()
        return response.json()

    def get_arena(self) -> Dict:
        """Get current game state"""
        self._rate_limit()
        url = f"{self.server_url}/api/arena"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        
        self.current_state = response.json()
        self._update_game_state()
        return self.current_state

    def get_logs(self) -> List[Dict]:
        """Get game logs"""
        self._rate_limit()
        url = f"{self.server_url}/api/logs"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()

    def send_moves(self, moves: List[Dict]) -> Dict:
        """Send movement commands for ants"""
        self._rate_limit()
        url = f"{self.server_url}/api/move"
        payload = {"moves": moves}
        response = requests.post(url, json=payload, headers=self.headers)
        response.raise_for_status()
        return response.json()

    def _update_game_state(self):
        """Update internal game state from the current arena response"""
        if not self.current_state:
            return
            
        self.ants = self.current_state.get("ants", [])
        self.enemies = self.current_state.get("enemies", [])
        self.food = self.current_state.get("food", [])
        self.home = self.current_state.get("home", [])
        self.map_tiles = self.current_state.get("map", [])
        
        # Update visible tiles
        self.visible_tiles = set()
        for ant in self.ants:
            self._add_visible_hexes(ant["q"], ant["r"], self._get_ant_vision_radius(ant))
        
        # Add tiles from ant movement paths
        for ant in self.ants:
            if "lastMove" in ant:
                for hex_coord in ant["lastMove"]:
                    self.visible_tiles.add((hex_coord["q"], hex_coord["r"]))
    
    def _get_ant_vision_radius(self, ant: Dict) -> int:
        """Get vision radius based on ant type"""
        ant_type = ant.get("type", 0)
        if ant_type == 0:  # Worker
            return 1
        elif ant_type == 1:  # Soldier
            return 1
        elif ant_type == 2:  # Scout
            return 4
        return 1
    
    def _add_visible_hexes(self, q: int, r: int, radius: int):
        """Add all hexes within radius to visible tiles"""
        for dq in range(-radius, radius + 1):
            for dr in range(max(-radius, -dq - radius), min(radius, -dq + radius) + 1):
                ds = -dq - dr
                if abs(ds) <= radius:
                    self.visible_tiles.add((q + dq, r + dr))
    
    def is_visible(self, q: int, r: int) -> bool:
        """Check if a hex is currently visible"""
        return (q, r) in self.visible_tiles
    
    def get_tile(self, q: int, r: int) -> Optional[Dict]:
        """Get tile information for specific coordinates"""
        for tile in self.map_tiles:
            if tile["q"] == q and tile["r"] == r:
                return tile
        return None
    
    def get_food_at(self, q: int, r: int) -> Optional[Dict]:
        """Get food information at specific coordinates"""
        for food_item in self.food:
            if food_item["q"] == q and food_item["r"] == r:
                return food_item
        return None
    
    def get_ant_by_id(self, ant_id: str) -> Optional[Dict]:
        """Get ant by its ID"""
        for ant in self.ants:
            if ant["id"] == ant_id:
                return ant
        return None
    
    def get_enemies_near(self, q: int, r: int, radius: int = 1) -> List[Dict]:
        """Get enemies within a certain radius of a hex"""
        nearby = []
        for enemy in self.enemies:
            if self.hex_distance(q, r, enemy["q"], enemy["r"]) <= radius:
                nearby.append(enemy)
        return nearby
    
    @staticmethod
    def hex_distance(q1: int, r1: int, q2: int, r2: int) -> int:
        """Calculate distance between two hexes"""
        return (abs(q1 - q2) + abs(q1 + r1 - q2 - r2) + abs(r1 - r2)) // 2
    
    @staticmethod
    def get_neighbor_hexes(q: int, r: int) -> List[Dict]:
        """Get all neighboring hexes"""
        return [
            {"q": q + 1, "r": r},     # Right
            {"q": q - 1, "r": r},     # Left
            {"q": q, "r": r + 1},     # Bottom right
            {"q": q, "r": r - 1},     # Top left
            {"q": q + 1, "r": r - 1}, # Top right
            {"q": q - 1, "r": r + 1}, # Bottom left
        ]
    
    def find_path(self, start_q: int, start_r: int, target_q: int, target_r: int, ant_type: int) -> List[Dict]:
        """
        A* pathfinding algorithm for hexagonal grid
        Returns a path from start to target coordinates
        """
        # Simple implementation - for a real game you'd want a more robust pathfinder
        # This is just a placeholder that moves directly toward the target
        
        path = []
        current_q, current_r = start_q, start_r
        
        while current_q != target_q or current_r != target_r:
            # Determine direction to move
            dq = target_q - current_q
            dr = target_r - current_r
            
            # Choose which axis to move along
            if abs(dq) > abs(dr):
                next_q = current_q + (1 if dq > 0 else -1)
                next_r = current_r
            else:
                next_q = current_q
                next_r = current_r + (1 if dr > 0 else -1)
            
            # Check if the move is valid
            tile = self.get_tile(next_q, next_r)
            if not tile or tile["type"] == 5:  # Skip if tile doesn't exist or is a rock
                break
                
            # Check for blocking ants/enemies
            blocking_ant = False
            for ant in self.ants:
                if ant["q"] == next_q and ant["r"] == next_r and ant.get("type", -1) == ant_type:
                    blocking_ant = True
                    break
            
            if blocking_ant:
                break
                
            path.append({"q": next_q, "r": next_r})
            current_q, current_r = next_q, next_r
            
            # Prevent infinite loops
            if len(path) > 20:
                break
                
        return path
    
    def make_decisions(self) -> List[Dict]:
        """
        Main decision-making logic for the AI
        Returns a list of move commands for ants
        """
        moves = []
        
        if not self.current_state:
            return moves
            
        # Get home base coordinates
        home_hex = self.current_state.get("spot", {})
        home_q, home_r = home_hex.get("q", 0), home_hex.get("r", 0)
        
        for ant in self.ants:
            ant_id = ant["id"]
            current_q, current_r = ant["q"], ant["r"]
            ant_type = ant.get("type", 0)
            
            # Skip if ant already has moves queued
            if "move" in ant and len(ant["move"]) > 0:
                continue
                
            # Different behavior based on ant type
            if ant_type == 0:  # Worker
                # Workers focus on gathering food
                best_food = self._find_best_food_target(current_q, current_r)
                if best_food:
                    path = self.find_path(current_q, current_r, best_food["q"], best_food["r"], ant_type)
                    if path:
                        moves.append({
                            "ant": ant_id,
                            "path": path
                        })
                elif ant.get("food", {}).get("amount", 0) > 0:
                    # If carrying food, return to base
                    path = self.find_path(current_q, current_r, home_q, home_r, ant_type)
                    if path:
                        moves.append({
                            "ant": ant_id,
                            "path": path
                        })
                else:
                    # Explore if no food found
                    self._explore(moves, ant, ant_type)
                    
            elif ant_type == 1:  # Soldier
                # Soldiers focus on combat
                enemies = self.get_enemies_near(current_q, current_r, 2)
                if enemies:
                    # Attack nearest enemy
                    closest = min(enemies, key=lambda e: self.hex_distance(current_q, current_r, e["q"], e["r"]))
                    path = self.find_path(current_q, current_r, closest["q"], closest["r"], ant_type)
                    if path:
                        moves.append({
                            "ant": ant_id,
                            "path": path
                        })
                else:
                    # Patrol near home if no enemies
                    self._patrol(moves, ant, ant_type, home_q, home_r)
                    
            elif ant_type == 2:  # Scout
                # Scouts focus on exploration
                self._explore(moves, ant, ant_type)
                
        return moves
    
    def _find_best_food_target(self, current_q: int, current_r: int) -> Optional[Dict]:
        """Find the best food target considering distance and food type"""
        if not self.food:
            return None
            
        # Prefer higher value food types (nectar > bread > apple)
        food_scores = {3: 3, 2: 2, 1: 1}  # nectar:3, bread:2, apple:1
        
        best_score = -1
        best_food = None
        
        for food in self.food:
            if food["amount"] <= 0:
                continue
                
            distance = self.hex_distance(current_q, current_r, food["q"], food["r"])
            score = food_scores.get(food["type"], 0) / (distance + 1)
            
            if score > best_score:
                best_score = score
                best_food = food
                
        return best_food
    
    def _explore(self, moves: List[Dict], ant: Dict, ant_type: int):
        """Explore unknown areas of the map"""
        ant_id = ant["id"]
        current_q, current_r = ant["q"], ant["r"]
        
        # Find the closest unexplored hex
        closest_unexplored = None
        min_distance = float('inf')
        
        # Check neighbors first
        for neighbor in self.get_neighbor_hexes(current_q, current_r):
            n_q, n_r = neighbor["q"], neighbor["r"]
            if not self.is_visible(n_q, n_r):
                distance = 1
                if distance < min_distance:
                    min_distance = distance
                    closest_unexplored = neighbor
        
        # If no unexplored neighbors, pick a random direction
        if not closest_unexplored:
            directions = self.get_neighbor_hexes(current_q, current_r)
            closest_unexplored = directions[0]  # Just pick first direction for simplicity
            
        if closest_unexplored:
            path = self.find_path(current_q, current_r, closest_unexplored["q"], closest_unexplored["r"], ant_type)
            if path:
                moves.append({
                    "ant": ant_id,
                    "path": path
                })
    
    def _patrol(self, moves: List[Dict], ant: Dict, ant_type: int, home_q: int, home_r: int):
        """Patrol around home base"""
        ant_id = ant["id"]
        current_q, current_r = ant["q"], ant["r"]
        
        # Define patrol points around home base
        patrol_points = [
            {"q": home_q + 2, "r": home_r},
            {"q": home_q + 1, "r": home_r + 1},
            {"q": home_q - 1, "r": home_r + 1},
            {"q": home_q - 2, "r": home_r},
            {"q": home_q - 1, "r": home_r - 1},
            {"q": home_q + 1, "r": home_r - 1},
        ]
        
        # Find closest patrol point
        closest_point = min(patrol_points, key=lambda p: self.hex_distance(current_q, current_r, p["q"], p["r"]))
        
        path = self.find_path(current_q, current_r, closest_point["q"], closest_point["r"], ant_type)
        if path:
            moves.append({
                "ant": ant_id,
                "path": path
            })


def main():
    # Replace with your actual API key
    API_KEY = "your-api-key-here"
    
    client = AntProtocolClient(API_KEY)
    
    # Register for a game
    registration = client.register()
    print("Registered for game:", registration)
    
    # Main game loop
    while True:
        try:
            # Get current game state
            arena = client.get_arena()
            turn_no = arena.get("turnNo", 0)
            next_turn_in = arena.get("nextTurnIn", 2.0)
            
            print(f"Turn {turn_no}, next turn in {next_turn_in:.1f}s")
            
            # Make decisions and send moves
            moves = client.make_decisions()
            if moves:
                result = client.send_moves(moves)
                print(f"Sent {len(moves)} move commands")
                if "errors" in result and result["errors"]:
                    print("Move errors:", result["errors"])
            
            # Wait for next turn
            time.sleep(max(0.1, next_turn_in - 0.1))
            
        except requests.exceptions.RequestException as e:
            print("API error:", e)
            time.sleep(1)
        except KeyboardInterrupt:
            print("Game loop interrupted")
            break


if __name__ == "__main__":
    main()