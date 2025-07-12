"""
Control panel component that handles all UI controls and video playback functionality.
"""

import tkinter as tk
from tkinter import ttk
from typing import Dict, List, Tuple

from ..data.database_manager import DatabaseManager


class ControlPanel:
    """Handles all control panel UI elements and video playback."""
    
    def __init__(self, parent, visualizer, db_manager: DatabaseManager):
        self.parent = parent
        self.visualizer = visualizer
        self.db_manager = db_manager
        
        # Video playback state
        self.video_playing = False
        self.video_speed = 1.0
        self.current_state_index = 0
        self.all_states = []
        
        # Setup UI components
        self.setup_control_panel()

    def setup_control_panel(self):
        """Setup control panel with buttons and info displays."""
        # Button frame
        self.button_frame = tk.Frame(self.parent, bg="#202020")
        self.button_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Control buttons
        self.refresh_button = tk.Button(
            self.button_frame, text="🔄 Refresh Now", 
            command=self.visualizer.load_and_display_latest_state, width=15
        )
        self.refresh_button.pack(side=tk.LEFT, padx=5)
        
        self.reset_view_button = tk.Button(
            self.button_frame, text="⟲ Reset View", 
            command=self.visualizer.reset_view, width=15
        )
        self.reset_view_button.pack(side=tk.LEFT, padx=5)
        
        self.video_mode_button = tk.Button(
            self.button_frame, text="▶ Enable Video", 
            command=self.visualizer.toggle_video_mode, width=15
        )
        self.video_mode_button.pack(side=tk.LEFT, padx=5)
        
        # Refresh interval control
        self.interval_frame = tk.Frame(self.button_frame, bg="#202020")
        self.interval_frame.pack(side=tk.LEFT, padx=10)
        
        tk.Label(self.interval_frame, text="Interval (ms):", bg="#202020", fg="white").pack(side=tk.LEFT)
        self.interval_entry = tk.Entry(self.interval_frame, width=6)
        self.interval_entry.insert(0, str(self.visualizer.refresh_interval))
        self.interval_entry.pack(side=tk.LEFT)
        
        self.set_interval_button = tk.Button(
            self.interval_frame, text="Set",
            command=self.update_refresh_interval,
            width=4
        )
        self.set_interval_button.pack(side=tk.LEFT, padx=5)
        
        # Timeline slider
        self.timeline_frame = tk.Frame(self.parent, bg="#202020")
        self.timeline_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.timeline_label = tk.Label(
            self.timeline_frame, text="Timeline:", 
            bg="#202020", fg="#FF5733", width=8
        )
        self.timeline_label.pack(side=tk.LEFT)
        
        self.timeline_slider = ttk.Scale(
            self.timeline_frame, from_=0, to=100, 
            command=self.on_timeline_change,
            orient=tk.HORIZONTAL
        )
        self.timeline_slider.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        self.timeline_value = tk.Label(
            self.timeline_frame, text="0/0", 
            bg="#202020", fg="#33FF57", width=10
        )
        self.timeline_value.pack(side=tk.LEFT)
        
        # Video controls
        self.video_control_frame = tk.Frame(self.timeline_frame, bg="#202020")
        self.video_control_frame.pack(side=tk.LEFT, padx=5)
        
        self.play_button = tk.Button(
            self.video_control_frame, text="▶ Play", 
            command=self.toggle_play, width=6, state=tk.DISABLED
        )
        self.play_button.pack(side=tk.LEFT)
        
        self.speed_label = tk.Label(
            self.video_control_frame, text="Speed:", 
            bg="#202020", fg="#3357FF"
        )
        self.speed_label.pack(side=tk.LEFT, padx=(5,0))
        
        self.speed_combobox = ttk.Combobox(
            self.video_control_frame, 
            values=["1.0x", "2.0x", "3.0x"],
            width=5,
            state="readonly"
        )
        self.speed_combobox.current(1)
        self.speed_combobox.pack(side=tk.LEFT)
        self.speed_combobox.bind("<<ComboboxSelected>>", self.change_speed)
        
        # Info display
        self.info_frame = tk.Frame(self.parent, bg="#202020")
        self.info_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.turn_label = tk.Label(
            self.info_frame, text="Turn: -", bg="#202020", fg="#FF5733",
            font=("Arial", 10, "bold"), width=15, anchor="w"
        )
        self.turn_label.pack(side=tk.LEFT)
        
        self.datetime_label = tk.Label(
            self.info_frame, text="Time: -", bg="#202020", fg="#00FFFF",
            font=("Arial", 10, "bold"), width=25, anchor="w"
        )
        self.datetime_label.pack(side=tk.LEFT)
        
        self.player_label = tk.Label(
            self.info_frame, text="Player: -", bg="#202020", fg="#FF69B4",
            font=("Arial", 10, "bold"), width=25, anchor="w"
        )
        self.player_label.pack(side=tk.LEFT)
        
        self.status_label = tk.Label(
            self.info_frame, text="Status: Ready", bg="#202020", fg="#32CD32",
            font=("Arial", 10), anchor="w"
        )
        self.status_label.pack(side=tk.LEFT)

    def update_refresh_interval(self):
        """Update the refresh interval from the entry field."""
        try:
            new_interval = int(self.interval_entry.get())
            self.visualizer.update_refresh_interval(new_interval)
        except ValueError:
            self.update_status("Invalid interval value", "red")

    def update_info_display(self, game_data: Dict, datetime_str: str = None):
        """Update the information display labels."""
        if datetime_str:
            self.datetime_label.config(text=f"Time: {datetime_str}")
        
        turn_number = game_data.get("turnNumber", "-")
        self.turn_label.config(text=f"Turn: {turn_number}")
        
        player_name = game_data.get("playerName", "-")
        self.player_label.config(text=f"Player: {player_name}")

    def update_status(self, message: str, color: str = "lightgreen"):
        """Update the status label."""
        self.status_label.config(text=f"Status: {message}", fg=color)

    def enable_video_mode(self):
        """Enable video mode controls."""
        self.video_mode_button.config(text="◼ Disable Video")
        self.play_button.config(state=tk.NORMAL)
        self.all_states = self.visualizer.all_states
        self.current_state_index = self.visualizer.current_state_index
        self.timeline_slider.config(from_=0, to=len(self.all_states)-1)
        self.timeline_slider.set(self.current_state_index)
        self.update_timeline_display()

    def disable_video_mode(self):
        """Disable video mode controls."""
        self.video_mode_button.config(text="▶ Enable Video")
        self.play_button.config(state=tk.DISABLED)
        self.stop_playback()
        self.all_states = []

    def update_timeline_controls(self, video_mode: bool, all_states: List):
        """Enable/disable timeline controls based on mode."""
        if video_mode and all_states:
            self.timeline_slider.config(state=tk.NORMAL)
            self.timeline_value.config(state=tk.NORMAL)
        else:
            self.timeline_slider.config(state=tk.DISABLED)
            self.timeline_value.config(state=tk.DISABLED)

    def on_timeline_change(self, value):
        """Handle timeline slider change."""
        if not self.visualizer.video_mode or not self.all_states:
            return
            
        index = int(float(value))
        if 0 <= index < len(self.all_states) and index != self.current_state_index:
            self.current_state_index = index
            self.visualizer.current_state_index = index
            self.visualizer.display_state(self.all_states[index])
            self.update_timeline_display()
            
            if self.video_playing:
                self.toggle_play()

    def update_timeline_display(self):
        """Update timeline label with current position."""
        if self.all_states:
            self.timeline_value.config(text=f"{self.current_state_index+1}/{len(self.all_states)}")

    def toggle_play(self):
        """Toggle playback of video mode."""
        self.video_playing = not self.video_playing
        self.visualizer.video_playing = self.video_playing
        
        if self.video_playing:
            self.play_button.config(text="❚❚ Pause")
            self.play_next_frame()
        else:
            self.play_button.config(text="▶ Play")

    def play_next_frame(self):
        """Play the next frame in video playback."""
        if not self.video_playing or not self.all_states:
            return
            
        if self.current_state_index < len(self.all_states) - 1:
            self.current_state_index += 1
            self.visualizer.current_state_index = self.current_state_index
            self.timeline_slider.set(self.current_state_index)
            self.visualizer.display_state(self.all_states[self.current_state_index])
            self.update_timeline_display()
            
            delay = int(self.visualizer.refresh_interval / self.video_speed)
            self.visualizer.root.after(delay, self.play_next_frame)
        else:
            self.toggle_play()

    def stop_playback(self):
        """Stop video playback."""
        if self.video_playing:
            self.video_playing = False
            self.visualizer.video_playing = False
            self.play_button.config(text="▶ Play")

    def change_speed(self, event):
        """Change playback speed."""
        speed_text = self.speed_combobox.get()
        speed_value = float(speed_text.replace("x", ""))
        
        # Map UI speed values to actual speed multipliers
        speed_mapping = {
            1.0: 3.0,  # UI 1x = actual 3x speed
            2.0: 6.0,  # UI 2x = actual 6x speed  
            3.0: 9.0   # UI 3x = actual 9x speed
        }
        
        self.video_speed = speed_mapping.get(speed_value, speed_value)
        self.visualizer.video_speed = self.video_speed 