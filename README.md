# ProgressBar - Desktop Time Progress Bar

A sleek and elegant desktop time progress bar tool that displays current time and completion percentage in real-time.

## Features

- ✨ **Real-time Progress** - Shows current progress percentage based on configured time range
- 🎨 **Customizable Appearance** - Adjust window size, opacity, and colors
- 📍 **Edge Snapping** - Auto-snap to screen edges
- 🔝 **Always on Top** - Optional window pinning
- ⏰ **Time Range Settings** - Customize start and end times
- 📊 **Scale Display** - Optional time scale marks
- 🚀 **Auto-start** - Boot with Windows support
- 💾 **Portable** - Single executable file, no installation required

## Usage

### Direct Run

Simply double-click `ProgressBar.exe` (located in the `dist` folder).

### Run from Source

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the program:
```bash
python main.py
```

## Features Overview

### Context Menu

Right-click on the progress bar to open the menu:

| Menu Item | Description |
|-----------|-------------|
| **Set Time Range** | Configure start and end times (default: 10:00-22:00) |
| **Set Size** | Adjust progress bar width (200-2000px) and height (20-200px) |
| **Set Opacity** | Adjust window opacity (10-100%) |
| **✓ Snap Toggle** | Enable/disable auto-snap to screen edges |
| **✓ Pin Toggle** | Enable/disable always-on-top window |
| **✓ Show Ticks** | Show/hide time scale marks (12 segments) |
| **✓ Auto-start** | Enable/disable startup with Windows |

> ✓ indicates the option is currently enabled

### Window Dragging

- Hold left mouse button and drag to move the window
- Release to auto-snap to nearest screen edge (if snap is enabled)

### Display Content

The progress bar center displays:
- Current time (24-hour format)
- Completion percentage

Example: `15:30 65%`

## Build Instructions

Package as a single executable using PyInstaller:

```bash
python -m PyInstaller --onefile --windowed --name "ProgressBar" main.py
```

The generated exe file will be in the `dist` folder.

## System Requirements

- Windows 7 or later
- Python 3.9+ (for development only)

## Dependencies

- PyQt6 - GUI framework
- PyInstaller - Packaging tool

## License

This project is for personal learning purposes only.

## Changelog

### v1.0
- Basic progress bar functionality
- Time range customization
- Window pinning and snapping
- Opacity adjustment
- Scale display
- Auto-start support
