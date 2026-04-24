import pygame
import collections

# ─── Brush Sizes ──────────────────────────────────────────────────────────────
BRUSH_SIZES = {1: 2, 2: 5, 3: 10}


# ─── Pencil Tool ──────────────────────────────────────────────────────────────
class PencilTool:
    def __init__(self):
        self.last_pos = None

    def on_mouse_down(self, canvas, pos, color, size):
        self.last_pos = pos
        pygame.draw.circle(canvas, color, pos, size // 2)

    def on_mouse_move(self, canvas, pos, color, size):
        if self.last_pos:
            pygame.draw.line(canvas, color, self.last_pos, pos, size)
            self.last_pos = pos

    def on_mouse_up(self, canvas, pos, color, size):
        self.last_pos = None

    def draw_preview(self, surface, pos, color, size):
        pass  # No preview needed for pencil


# ─── Straight Line Tool ───────────────────────────────────────────────────────
class LineTool:
    def __init__(self):
        self.start_pos = None

    def on_mouse_down(self, canvas, pos, color, size):
        self.start_pos = pos

    def on_mouse_move(self, canvas, pos, color, size):
        pass  # preview handled separately

    def on_mouse_up(self, canvas, pos, color, size):
        if self.start_pos:
            pygame.draw.line(canvas, color, self.start_pos, pos, size)
        self.start_pos = None

    def draw_preview(self, surface, pos, color, size):
        if self.start_pos:
            pygame.draw.line(surface, color, self.start_pos, pos, size)


# ─── Rectangle Tool ───────────────────────────────────────────────────────────
class RectTool:
    def __init__(self):
        self.start_pos = None

    def on_mouse_down(self, canvas, pos, color, size):
        self.start_pos = pos

    def on_mouse_move(self, canvas, pos, color, size):
        pass

    def on_mouse_up(self, canvas, pos, color, size):
        if self.start_pos:
            x = min(self.start_pos[0], pos[0])
            y = min(self.start_pos[1], pos[1])
            w = abs(pos[0] - self.start_pos[0])
            h = abs(pos[1] - self.start_pos[1])
            pygame.draw.rect(canvas, color, (x, y, w, h), size)
        self.start_pos = None

    def draw_preview(self, surface, pos, color, size):
        if self.start_pos:
            x = min(self.start_pos[0], pos[0])
            y = min(self.start_pos[1], pos[1])
            w = abs(pos[0] - self.start_pos[0])
            h = abs(pos[1] - self.start_pos[1])
            pygame.draw.rect(surface, color, (x, y, w, h), size)


# ─── Square Tool ──────────────────────────────────────────────────────────────
class SquareTool:
    def __init__(self):
        self.start_pos = None

    def on_mouse_down(self, canvas, pos, color, size):
        self.start_pos = pos

    def on_mouse_move(self, canvas, pos, color, size):
        pass

    def _get_rect(self, pos):
        if not self.start_pos:
            return None
        dx = pos[0] - self.start_pos[0]
        dy = pos[1] - self.start_pos[1]
        side = max(abs(dx), abs(dy))
        x = self.start_pos[0] if dx >= 0 else self.start_pos[0] - side
        y = self.start_pos[1] if dy >= 0 else self.start_pos[1] - side
        return (x, y, side, side)

    def on_mouse_up(self, canvas, pos, color, size):
        r = self._get_rect(pos)
        if r:
            pygame.draw.rect(canvas, color, r, size)
        self.start_pos = None

    def draw_preview(self, surface, pos, color, size):
        r = self._get_rect(pos)
        if r:
            pygame.draw.rect(surface, color, r, size)


# ─── Circle Tool ──────────────────────────────────────────────────────────────
class CircleTool:
    def __init__(self):
        self.start_pos = None

    def on_mouse_down(self, canvas, pos, color, size):
        self.start_pos = pos

    def on_mouse_move(self, canvas, pos, color, size):
        pass

    def _get_circle(self, pos):
        if not self.start_pos:
            return None, None
        cx = (self.start_pos[0] + pos[0]) // 2
        cy = (self.start_pos[1] + pos[1]) // 2
        r = int(((pos[0] - self.start_pos[0])**2 + (pos[1] - self.start_pos[1])**2)**0.5 / 2)
        return (cx, cy), r

    def on_mouse_up(self, canvas, pos, color, size):
        center, r = self._get_circle(pos)
        if center and r > 0:
            pygame.draw.circle(canvas, color, center, r, size)
        self.start_pos = None

    def draw_preview(self, surface, pos, color, size):
        center, r = self._get_circle(pos)
        if center and r > 0:
            pygame.draw.circle(surface, color, center, r, size)


# ─── Right Triangle Tool ──────────────────────────────────────────────────────
class RightTriangleTool:
    def __init__(self):
        self.start_pos = None

    def on_mouse_down(self, canvas, pos, color, size):
        self.start_pos = pos

    def on_mouse_move(self, canvas, pos, color, size):
        pass

    def _get_points(self, pos):
        if not self.start_pos:
            return None
        x0, y0 = self.start_pos
        x1, y1 = pos
        return [(x0, y1), (x0, y0), (x1, y1)]

    def on_mouse_up(self, canvas, pos, color, size):
        pts = self._get_points(pos)
        if pts:
            pygame.draw.polygon(canvas, color, pts, size)
        self.start_pos = None

    def draw_preview(self, surface, pos, color, size):
        pts = self._get_points(pos)
        if pts:
            pygame.draw.polygon(surface, color, pts, size)


# ─── Equilateral Triangle Tool ────────────────────────────────────────────────
class EquilateralTriangleTool:
    def __init__(self):
        self.start_pos = None

    def on_mouse_down(self, canvas, pos, color, size):
        self.start_pos = pos

    def on_mouse_move(self, canvas, pos, color, size):
        pass

    def _get_points(self, pos):
        if not self.start_pos:
            return None
        import math
        x0, y0 = self.start_pos
        x1, y1 = pos
        base = ((x1 - x0)**2 + (y1 - y0)**2)**0.5
        mx, my = (x0 + x1) / 2, (y0 + y1) / 2
        h = base * math.sqrt(3) / 2
        dx, dy = x1 - x0, y1 - y0
        length = (dx**2 + dy**2)**0.5 or 1
        nx, ny = -dy / length, dx / length
        apex = (mx + nx * h, my + ny * h)
        return [(x0, y0), (x1, y1), apex]

    def on_mouse_up(self, canvas, pos, color, size):
        pts = self._get_points(pos)
        if pts:
            pygame.draw.polygon(canvas, color, [(int(p[0]), int(p[1])) for p in pts], size)
        self.start_pos = None

    def draw_preview(self, surface, pos, color, size):
        pts = self._get_points(pos)
        if pts:
            pygame.draw.polygon(surface, color, [(int(p[0]), int(p[1])) for p in pts], size)


# ─── Rhombus Tool ─────────────────────────────────────────────────────────────
class RhombusTool:
    def __init__(self):
        self.start_pos = None

    def on_mouse_down(self, canvas, pos, color, size):
        self.start_pos = pos

    def on_mouse_move(self, canvas, pos, color, size):
        pass

    def _get_points(self, pos):
        if not self.start_pos:
            return None
        x0, y0 = self.start_pos
        x1, y1 = pos
        cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
        return [(cx, y0), (x1, cy), (cx, y1), (x0, cy)]

    def on_mouse_up(self, canvas, pos, color, size):
        pts = self._get_points(pos)
        if pts:
            pygame.draw.polygon(canvas, color, pts, size)
        self.start_pos = None

    def draw_preview(self, surface, pos, color, size):
        pts = self._get_points(pos)
        if pts:
            pygame.draw.polygon(surface, color, pts, size)


# ─── Eraser Tool ──────────────────────────────────────────────────────────────
class EraserTool:
    def __init__(self):
        self.last_pos = None

    def on_mouse_down(self, canvas, pos, color, size):
        self.last_pos = pos
        pygame.draw.circle(canvas, (255, 255, 255), pos, size * 2)

    def on_mouse_move(self, canvas, pos, color, size):
        if self.last_pos:
            pygame.draw.line(canvas, (255, 255, 255), self.last_pos, pos, size * 4)
            self.last_pos = pos

    def on_mouse_up(self, canvas, pos, color, size):
        self.last_pos = None

    def draw_preview(self, surface, pos, color, size):
        pygame.draw.circle(surface, (200, 200, 200), pos, size * 2, 1)


# ─── Flood Fill Tool ──────────────────────────────────────────────────────────
class FillTool:
    def on_mouse_down(self, canvas, pos, color, size):
        flood_fill(canvas, pos, color)

    def on_mouse_move(self, canvas, pos, color, size):
        pass

    def on_mouse_up(self, canvas, pos, color, size):
        pass

    def draw_preview(self, surface, pos, color, size):
        pass


def flood_fill(surface, start_pos, fill_color):
    """BFS flood fill on a pygame Surface."""
    x, y = start_pos
    w, h = surface.get_size()
    if x < 0 or x >= w or y < 0 or y >= h:
        return

    target_color = surface.get_at((x, y))[:3]
    fill_rgb = fill_color[:3] if len(fill_color) > 3 else fill_color

    if target_color == fill_rgb:
        return

    queue = collections.deque()
    queue.append((x, y))
    visited = set()
    visited.add((x, y))

    while queue:
        cx, cy = queue.popleft()
        if surface.get_at((cx, cy))[:3] != target_color:
            continue
        surface.set_at((cx, cy), fill_rgb)
        for nx, ny in ((cx+1, cy), (cx-1, cy), (cx, cy+1), (cx, cy-1)):
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in visited:
                visited.add((nx, ny))
                queue.append((nx, ny))


# ─── Text Tool ────────────────────────────────────────────────────────────────
class TextTool:
    def __init__(self):
        self.active = False
        self.pos = None
        self.text = ""
        self.font = None

    def _get_font(self, size):
        font_size = {2: 16, 5: 24, 10: 36}.get(size, 24)
        if self.font is None or self.font.size("A")[1] != font_size:
            self.font = pygame.font.SysFont("Arial", font_size)
        return self.font

    def on_mouse_down(self, canvas, pos, color, size):
        # Commit any existing text first
        if self.active and self.text:
            self._render(canvas, color, size)
        self.active = True
        self.pos = pos
        self.text = ""

    def on_mouse_move(self, canvas, pos, color, size):
        pass

    def on_mouse_up(self, canvas, pos, color, size):
        pass

    def handle_key(self, event, canvas, color, size):
        """Returns True if the event was consumed."""
        if not self.active:
            return False
        if event.key == pygame.K_RETURN:
            if self.text:
                self._render(canvas, color, size)
            self.active = False
            self.text = ""
            return True
        elif event.key == pygame.K_ESCAPE:
            self.active = False
            self.text = ""
            return True
        elif event.key == pygame.K_BACKSPACE:
            self.text = self.text[:-1]
            return True
        else:
            if event.unicode and event.unicode.isprintable():
                self.text += event.unicode
            return True

    def _render(self, canvas, color, size):
        font = self._get_font(size)
        surf = font.render(self.text, True, color)
        canvas.blit(surf, self.pos)

    def draw_preview(self, surface, pos, color, size):
        if not self.active or self.pos is None:
            return
        font = self._get_font(size)
        display_text = self.text + "|"
        surf = font.render(display_text, True, color)
        surface.blit(surf, self.pos)
