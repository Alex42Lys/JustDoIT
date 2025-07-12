#!/usr/bin/env python3
"""
Main entry point for the Ants Game Visualizer.

This is the new modular version of the visualizer that has been split into
logical components for better maintainability and organization.
"""

import sys
import os

# Add the current directory to the Python path so we can import the visualizer package
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from visualizer import AntsGameVisualizer


def main():
    """Main entry point for the visualizer application."""
    # Default sqlite database file path - you can change this or pass as command line argument
    db_path = "./movie3.db"
    
    # Check if database path was provided as command line argument
    if len(sys.argv) > 1:
        db_path = sys.argv[1]
    
    # Check if database file exists
    if not os.path.exists(db_path):
        print(f"Error: Database file not found: {db_path}")
        print("Usage: python visualizer_main.py [database_path]")
        sys.exit(1)
    
    print(f"Starting Ants Game Visualizer with database: {db_path}")
    
    try:
        # Create and start the visualizer
        visualizer = AntsGameVisualizer(db_path)
    except Exception as e:
        print(f"Error starting visualizer: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 