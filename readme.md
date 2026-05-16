# Computer Graphics Project

A comprehensive computer graphics application implementing fundamental 2D graphics algorithms including line/circle drawing, geometric transformations, clipping algorithms, and curve generation.

## Table of Contents

- [Features](#features)
- [Algorithms Implemented](#algorithms-implemented)
- [Installation](#installation)
- [How to Run](#how-to-run)
- [User Guide](#user-guide)
- [File Structure](#file-structure)
- [Performance Analysis](#performance-analysis)
- [Troubleshooting](#troubleshooting)
- [Credits](#credits)
- [License](#license)

## Features

### Drawing Algorithms

- DDA (Digital Differential Analyzer) Line Algorithm
- Bresenham's Line Algorithm
- Midpoint Circle Algorithm
- Bresenham's Circle Algorithm

### 2D Transformations

- Translation (move shapes)
- Rotation (spin shapes around center)
- Scaling (resize shapes)
- Reflection (mirror across X/Y axes)
- Shearing (slant shapes)

### Clipping Algorithms

- Cohen-Sutherland Line Clipping
- Sutherland-Hodgman Polygon Clipping

### Curve Generation

- Bezier Curves
- B-Spline Curves

### Additional Features

- Interactive mouse input for drawing
- Smooth animation for transformations
- Performance comparison charts
- Save/Load drawings to JSON files
- Export drawings as PNG/JPEG images
- Real-time output log

## Algorithms Implemented

### Line Drawing

| Algorithm | Method                  | Complexity | Best For             |
| --------- | ----------------------- | ---------- | -------------------- |
| DDA       | Floating-point stepping | O(n)       | Understanding basics |
| Bresenham | Integer error term      | O(n)       | Speed and efficiency |

### Circle Drawing

| Algorithm | Method                            | Complexity | Best For                  |
| --------- | --------------------------------- | ---------- | ------------------------- |
| Midpoint  | 8-way symmetry with midpoint test | O(r)       | Accurate circles          |
| Bresenham | Integer decision parameter        | O(r)       | Fast integer-only drawing |

### Transformations

| Type        | Formula                                | Description          |
| ----------- | -------------------------------------- | -------------------- |
| Translation | x' = x + dx, y' = y + dy               | Move shape           |
| Rotation    | x' = cx + (x-cx)cosθ - (y-cy)sinθ      | Rotate around center |
| Scaling     | x' = cx + (x-cx)sx, y' = cy + (y-cy)sy | Resize shape         |
| Reflection  | x' = -x or y' = -y                     | Mirror shape         |
| Shearing    | x' = x + sh·y or y' = y + sh·x         | Slant shape          |

### Clipping Algorithms

| Algorithm          | Type             | Complexity | Best For             |
| ------------------ | ---------------- | ---------- | -------------------- |
| Cohen-Sutherland   | Line clipping    | O(n)       | Simple line segments |
| Sutherland-Hodgman | Polygon clipping | O(n·m)     | Complex polygons     |

### Curves

| Algorithm | Control Points   | Property       |
| --------- | ---------------- | -------------- |
| Bezier    | n+1 points       | Global control |
| B-Spline  | n+1 points (n≥3) | Local control  |

## Installation

### Prerequisites

- Python 3.7 or higher
- pip package manager

### Step 1: Clone or Download

Download all project files to a folder on your computer.

### Step 2: Install Dependencies

Open a terminal/command prompt in the project folder and run:

```bash
pip install -r requirements.txt
```
## Credits
- MohannadIsCoding