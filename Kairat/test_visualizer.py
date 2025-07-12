#!/usr/bin/env python3
"""
Simple test script to verify the new modular visualizer structure.
"""

import sys
import os

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all components can be imported correctly."""
    try:
        print("Testing imports...")
        
        # Test main package import
        from visualizer import AntsGameVisualizer
        print("✓ Main package import successful")
        
        # Test individual component imports
        from visualizer.core.visualizer import AntsGameVisualizer
        print("✓ Core visualizer import successful")
        
        from visualizer.ui.control_panel import ControlPanel
        print("✓ Control panel import successful")
        
        from visualizer.ui.game_canvas import GameCanvas
        print("✓ Game canvas import successful")
        
        from visualizer.data.database_manager import DatabaseManager
        print("✓ Database manager import successful")
        
        from visualizer.utils.color_scheme import ColorScheme
        print("✓ Color scheme import successful")
        
        from visualizer.utils.hex_utils import HexUtils
        print("✓ Hex utils import successful")
        
        print("\nAll imports successful! ✅")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_components():
    """Test that components can be instantiated."""
    try:
        print("\nTesting component instantiation...")
        
        # Import components for testing
        from visualizer.utils.color_scheme import ColorScheme
        from visualizer.utils.hex_utils import HexUtils
        from visualizer.data.database_manager import DatabaseManager
        
        # Test utility components
        color_scheme = ColorScheme()
        print("✓ ColorScheme instantiated")
        
        hex_utils = HexUtils()
        print("✓ HexUtils instantiated")
        
        # Test database manager
        db_manager = DatabaseManager("test.db")
        print("✓ DatabaseManager instantiated")
        
        # Test color scheme methods
        tile_color = color_scheme.get_tile_color(1)
        print(f"✓ Color scheme method test: {tile_color}")
        
        # Test hex utils methods
        neighbors = hex_utils.get_hex_neighbors(0, 0)
        print(f"✓ Hex utils method test: {neighbors}")
        
        print("\nAll component tests successful! ✅")
        return True
        
    except Exception as e:
        print(f"❌ Component test error: {e}")
        return False

def test_structure():
    """Test that the directory structure is correct."""
    print("\nTesting directory structure...")
    
    required_files = [
        "visualizer/__init__.py",
        "visualizer/core/__init__.py",
        "visualizer/core/visualizer.py",
        "visualizer/ui/__init__.py",
        "visualizer/ui/control_panel.py",
        "visualizer/ui/game_canvas.py",
        "visualizer/data/__init__.py",
        "visualizer/data/database_manager.py",
        "visualizer/utils/__init__.py",
        "visualizer/utils/color_scheme.py",
        "visualizer/utils/hex_utils.py"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
        else:
            print(f"✓ {file_path}")
    
    if missing_files:
        print(f"\n❌ Missing files: {missing_files}")
        return False
    else:
        print("\nAll required files present! ✅")
        return True

def main():
    """Run all tests."""
    print("Testing Ants Game Visualizer - Modular Version")
    print("=" * 50)
    
    # Run tests
    structure_ok = test_structure()
    imports_ok = test_imports()
    components_ok = test_components()
    
    print("\n" + "=" * 50)
    print("Test Results:")
    print(f"Directory Structure: {'✅ PASS' if structure_ok else '❌ FAIL'}")
    print(f"Import Tests: {'✅ PASS' if imports_ok else '❌ FAIL'}")
    print(f"Component Tests: {'✅ PASS' if components_ok else '❌ FAIL'}")
    
    if all([structure_ok, imports_ok, components_ok]):
        print("\n🎉 All tests passed! The modular visualizer is ready to use.")
        print("\nTo run the visualizer:")
        print("python visualizer_main.py [database_path]")
    else:
        print("\n❌ Some tests failed. Please check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main() 