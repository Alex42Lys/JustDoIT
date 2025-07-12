# Ants Game Visualizer - Modular Version

This is the modular version of the Ants Game Visualizer that has been split into logical components for better maintainability and organization.

## Project Structure

```
visualizer/
├── __init__.py                 # Main package initialization
├── core/
│   ├── __init__.py            # Core module initialization
│   └── visualizer.py          # Main visualizer orchestrator class
├── ui/
│   ├── __init__.py            # UI module initialization
│   ├── control_panel.py       # Control panel and video playback
│   └── game_canvas.py         # Game canvas and drawing operations
├── data/
│   ├── __init__.py            # Data module initialization
│   └── database_manager.py    # Database operations and management
└── utils/
    ├── __init__.py            # Utils module initialization
    ├── color_scheme.py        # Color schemes and mappings
    └── hex_utils.py           # Hex coordinate calculations and utilities
```

## Component Overview

### Core (`visualizer/core/`)
- **`visualizer.py`**: Main orchestrator class that manages all components and coordinates the application flow

### UI (`visualizer/ui/`)
- **`control_panel.py`**: Handles all UI controls, buttons, timeline, video playback controls, and status displays
- **`game_canvas.py`**: Manages the game canvas, drawing operations, and visual representation of the game state

### Data (`visualizer/data/`)
- **`database_manager.py`**: Handles all database operations including loading game states, validation, and data retrieval

### Utils (`visualizer/utils/`)
- **`color_scheme.py`**: Manages color mappings for different game elements (ants, food, terrain, etc.)
- **`hex_utils.py`**: Provides hex coordinate calculations, distance measurements, and hex-related utilities

## Key Improvements

### 1. **Separation of Concerns**
- Each component has a single responsibility
- Clear interfaces between components
- Easier to test and maintain individual parts

### 2. **Modularity**
- Components can be easily replaced or extended
- New features can be added without affecting existing code
- Better code reusability

### 3. **Maintainability**
- Smaller, focused files are easier to understand and modify
- Clear dependencies between components
- Better error isolation

### 4. **Extensibility**
- New UI components can be added easily
- Database backends can be swapped
- Color schemes can be customized

## Usage

### Running the Visualizer

```bash
# Run with default database
python visualizer_main.py

# Run with specific database
python visualizer_main.py /path/to/your/database.db
```

### Importing Components

```python
from visualizer import AntsGameVisualizer
from visualizer.core.visualizer import AntsGameVisualizer
from visualizer.ui.control_panel import ControlPanel
from visualizer.data.database_manager import DatabaseManager
from visualizer.utils.color_scheme import ColorScheme
from visualizer.utils.hex_utils import HexUtils
```

## Migration from Original

The original `UI_DB.py` file has been split into these logical components:

| Original Functionality | New Location |
|----------------------|--------------|
| Main visualizer class | `core/visualizer.py` |
| UI controls and buttons | `ui/control_panel.py` |
| Canvas drawing | `ui/game_canvas.py` |
| Database operations | `data/database_manager.py` |
| Color schemes | `utils/color_scheme.py` |
| Hex calculations | `utils/hex_utils.py` |

## Benefits of the New Structure

1. **Easier Debugging**: Issues can be isolated to specific components
2. **Better Testing**: Each component can be unit tested independently
3. **Team Development**: Multiple developers can work on different components
4. **Code Reuse**: Components can be reused in other projects
5. **Documentation**: Each component has clear responsibilities and interfaces

## Future Enhancements

With this modular structure, it's now easier to:

- Add new visualization modes
- Support different database formats
- Implement new UI themes
- Add export functionality
- Create plugins for different game types
- Add unit tests for each component
- Implement configuration management
- Add logging and error handling

## Dependencies

The visualizer requires:
- Python 3.7+
- tkinter (usually included with Python, but may need to be installed separately)
- sqlite3 (usually included with Python)

### Installing tkinter

On some systems, `tkinter` is not installed by default. You can install it using your system's package manager:

- **Ubuntu/Debian:**
  ```bash
  sudo apt-get install python3-tk
  ```
- **Arch Linux:**
  ```bash
  sudo pacman -S tk
  ```
- **Fedora:**
  ```bash
  sudo dnf install python3-tkinter
  ```
- **macOS (Homebrew):**
  ```bash
  brew install python-tk
  ```

If you use a virtual environment, make sure your Python installation includes tkinter support. 