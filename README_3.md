# 🎨 Paint Application — TSIS 2

Extended Paint application built with **Python + Pygame** covering all requirements from TSIS 2.

---

## Project Structure

```
TSIS2/
├── paint.py      ← Main application (UI, event loop, toolbar)
├── tools.py      ← All drawing tool classes + flood fill algorithm
└── README.md
```

---

## Features

| Feature | Details |
|---|---|
| ✅ Pencil (freehand) | Hold mouse and drag; uses `pygame.draw.line` between consecutive positions |
| ✅ Straight Line | Click to set start, drag for live preview, release to commit |
| ✅ Rectangle | Drag to define bounding box |
| ✅ Square | Constrains width = height |
| ✅ Circle | Drag to define diameter |
| ✅ Right Triangle | Corner at start, right angle at bottom-left |
| ✅ Equilateral Triangle | Computed apex using √3/2 height formula |
| ✅ Rhombus | 4-point diamond using midpoints |
| ✅ Eraser | Wide white brush that paints over canvas |
| ✅ Flood Fill | BFS pixel flood fill via `get_at()` / `set_at()` |
| ✅ Text Tool | Click to place cursor, type in real time, Enter to confirm, Esc to cancel |
| ✅ Brush Sizes | Small 2px / Medium 5px / Large 10px — applies to all shape tools |
| ✅ Save PNG | `Ctrl+S` saves timestamped `.png` (e.g. `canvas_20250424_153012.png`) |

---

## Keyboard Shortcuts

| Key | Action |
|---|---|
| `P` | Pencil tool |
| `L` | Straight line |
| `R` | Rectangle |
| `Q` | Square |
| `C` | Circle |
| `T` | Right Triangle |
| `E` | Equilateral Triangle |
| `D` | Rhombus (Diamond) |
| `X` | Eraser |
| `F` | Flood Fill |
| `A` | Text tool |
| `1` / `2` / `3` | Brush size: Small / Medium / Large |
| `Ctrl+S` | Save canvas as timestamped PNG |
| `Enter` | Confirm text (Text tool) |
| `Esc` | Cancel text (Text tool) |

---

## Requirements

```
pip install pygame
```

Python 3.8+ recommended.

## Run

```bash
cd TSIS2
python paint.py
```

---

## Implementation Notes

### Flood Fill (BFS)
Implemented in `tools.py → flood_fill()`. Uses a `collections.deque` queue. Reads the target color at the clicked pixel using `surface.get_at()`, then expands to all 4-connected neighbors that match that color, painting each with `surface.set_at()`.

### Live Preview
Shape tools (Line, Rect, Square, Circle, Triangles, Rhombus) copy the canvas to a temporary surface each frame and call `draw_preview()` on it before blitting to screen. The original canvas stays clean until `mouse_up`.

### Text Tool
Stores the cursor position and accumulates typed characters in a buffer. Each frame the preview layer renders `text + "|"` cursor. On `Enter`, the text is permanently blitted onto the canvas surface.

### Save
```python
from datetime import datetime
ts = datetime.now().strftime("%Y%m%d_%H%M%S")
pygame.image.save(canvas, f"canvas_{ts}.png")
```
