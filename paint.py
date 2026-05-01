
import pygame
import sys
from datetime import datetime
from tools import (
    PencilTool, LineTool, RectTool, SquareTool, CircleTool,
    RightTriangleTool, EquilateralTriangleTool, RhombusTool,
    EraserTool, FillTool, TextTool, BRUSH_SIZES,
)

# ─── Constants ────────────────────────────────────────────────────────────────
WINDOW_W, WINDOW_H = 1200, 750
TOOLBAR_W = 180
CANVAS_X = TOOLBAR_W
CANVAS_W = WINDOW_W - TOOLBAR_W
CANVAS_H = WINDOW_H

BG_COLOR       = (30,  30,  38)
TOOLBAR_COLOR  = (22,  22,  30)
PANEL_BORDER   = (55,  55,  70)
ACCENT         = (100, 149, 237)   # cornflower blue
ACCENT_DARK    = (65,  100, 180)
TEXT_COLOR     = (220, 220, 230)
CANVAS_BG      = (255, 255, 255)

# Palette
PALETTE = [
    (0,   0,   0),    (255, 255, 255), (200,  50,  50),
    (220, 120,  40),  (220, 200,  40), (50,  180,  80),
    (40,  140, 220),  (130,  60, 200), (220,  80, 160),
    (150, 100,  60),  (100, 160, 160), (180, 180, 180),
    (80,   80,  80),  (255, 150, 150), (150, 255, 150),
    (150, 200, 255),
]

TOOLS = [
    ("Pencil",     "P", PencilTool()),
    ("Line",       "L", LineTool()),
    ("Rectangle",  "R", RectTool()),
    ("Square",     "Q", SquareTool()),
    ("Circle",     "C", CircleTool()),
    ("Rt.Triangle","T", RightTriangleTool()),
    ("Eq.Triangle","E", EquilateralTriangleTool()),
    ("Rhombus",    "D", RhombusTool()),
    ("Eraser",     "X", EraserTool()),
    ("Fill",       "F", FillTool()),
    ("Text",       "A", TextTool()),
]


# ─── UI Helpers ───────────────────────────────────────────────────────────────
def draw_rounded_rect(surf, color, rect, radius=8, border=0, border_color=None):
    pygame.draw.rect(surf, color, rect, border_radius=radius)
    if border and border_color:
        pygame.draw.rect(surf, border_color, rect, border, border_radius=radius)


def label(surf, font, text, pos, color=TEXT_COLOR, center=False):
    s = font.render(text, True, color)
    r = s.get_rect()
    if center:
        r.centerx = pos[0]
        r.y = pos[1]
    else:
        r.topleft = pos
    surf.blit(s, r)


# ─── Main ─────────────────────────────────────────────────────────────────────
def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_W, WINDOW_H))
    pygame.display.set_caption("Paint — TSIS 2")
    clock = pygame.time.Clock()

    font_sm  = pygame.font.SysFont("Segoe UI", 13)
    font_med = pygame.font.SysFont("Segoe UI", 14, bold=True)
    font_big = pygame.font.SysFont("Segoe UI", 16, bold=True)

    # Canvas surface (persistent drawing layer)
    canvas = pygame.Surface((CANVAS_W, CANVAS_H))
    canvas.fill(CANVAS_BG)

    # State
    active_tool_idx = 0
    active_color    = (0, 0, 0)
    brush_size_key  = 1           # 1=small, 2=medium, 3=large
    drawing         = False
    mouse_pos       = (0, 0)
    status_msg      = "Ready"
    status_timer    = 0

    def set_status(msg, ms=2500):
        nonlocal status_msg, status_timer
        status_msg   = msg
        status_timer = pygame.time.get_ticks() + ms

    def current_size():
        return BRUSH_SIZES[brush_size_key]

    def current_tool():
        return TOOLS[active_tool_idx][2]

    def canvas_pos(screen_pos):
        return (screen_pos[0] - CANVAS_X, screen_pos[1])

    def in_canvas(screen_pos):
        return screen_pos[0] >= CANVAS_X

    # ── Layout geometry ──────────────────────────────────────────────────────
    PAD = 10
    tool_buttons = []
    for i, (name, shortcut, _) in enumerate(TOOLS):
        row, col = divmod(i, 2)
        bx = PAD + col * (TOOLBAR_W // 2 - PAD)
        by = 50 + row * 42
        bw = TOOLBAR_W // 2 - PAD - 4
        bh = 34
        tool_buttons.append(pygame.Rect(bx, by, bw, bh))

    size_buttons = []
    size_labels = ["S", "M", "L"]
    for i in range(3):
        bx = PAD + i * ((TOOLBAR_W - PAD * 2) // 3)
        by = 50 + ((len(TOOLS) + 1) // 2) * 42 + 30
        bw = (TOOLBAR_W - PAD * 2) // 3 - 4
        bh = 30
        size_buttons.append(pygame.Rect(bx, by, bw, bh))

    palette_top = size_buttons[-1].bottom + 20
    swatch_size = 22
    swatches = []
    cols = 6
    for i, color in enumerate(PALETTE):
        row, col = divmod(i, cols)
        sx = PAD + col * (swatch_size + 3)
        sy = palette_top + 20 + row * (swatch_size + 3)
        swatches.append((pygame.Rect(sx, sy, swatch_size, swatch_size), color))

    # ── Main loop ─────────────────────────────────────────────────────────────
    running = True
    while running:
        now = pygame.time.get_ticks()
        mouse_screen = pygame.mouse.get_pos()
        mouse_canvas  = canvas_pos(mouse_screen)

        # ── Events ────────────────────────────────────────────────────────────
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # ── Keyboard ──────────────────────────────────────────────────────
            elif event.type == pygame.KEYDOWN:
                # Text tool intercepts keys when active
                tool = current_tool()
                if isinstance(tool, TextTool) and tool.active:
                    tool.handle_key(event, canvas, active_color, current_size())
                    continue

                mods = pygame.key.get_mods()
                if mods & pygame.KMOD_CTRL:
                    if event.key == pygame.K_s:
                        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                        fname = f"canvas_{ts}.png"
                        pygame.image.save(canvas, fname)
                        set_status(f"Saved: {fname}")
                    continue

                key_char = event.unicode.upper() if event.unicode else ""
                # Tool shortcuts
                for i, (name, shortcut, _) in enumerate(TOOLS):
                    if key_char == shortcut:
                        active_tool_idx = i
                        set_status(f"Tool: {name}")
                        break
                # Brush size
                if event.key in (pygame.K_1, pygame.K_KP1):
                    brush_size_key = 1; set_status("Brush: Small (2px)")
                elif event.key in (pygame.K_2, pygame.K_KP2):
                    brush_size_key = 2; set_status("Brush: Medium (5px)")
                elif event.key in (pygame.K_3, pygame.K_KP3):
                    brush_size_key = 3; set_status("Brush: Large (10px)")
                elif event.key == pygame.K_ESCAPE:
                    pass

            # ── Mouse Down ────────────────────────────────────────────────────
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                pos = event.pos
                # Tool buttons
                clicked_ui = False
                for i, rect in enumerate(tool_buttons):
                    if rect.collidepoint(pos):
                        active_tool_idx = i
                        set_status(f"Tool: {TOOLS[i][0]}")
                        clicked_ui = True
                        break
                # Size buttons
                if not clicked_ui:
                    for i, rect in enumerate(size_buttons):
                        if rect.collidepoint(pos):
                            brush_size_key = i + 1
                            set_status(f"Brush: {['Small','Medium','Large'][i]}")
                            clicked_ui = True
                            break
                # Swatches
                if not clicked_ui:
                    for rect, color in swatches:
                        if rect.collidepoint(pos):
                            active_color = color
                            clicked_ui = True
                            break
                # Canvas
                if not clicked_ui and in_canvas(pos):
                    drawing = True
                    current_tool().on_mouse_down(canvas, canvas_pos(pos), active_color, current_size())

            # ── Mouse Move ────────────────────────────────────────────────────
            elif event.type == pygame.MOUSEMOTION:
                if drawing and in_canvas(event.pos):
                    current_tool().on_mouse_move(canvas, canvas_pos(event.pos), active_color, current_size())

            # ── Mouse Up ──────────────────────────────────────────────────────
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if drawing:
                    current_tool().on_mouse_up(canvas, canvas_pos(event.pos), active_color, current_size())
                    drawing = False

        # ── Draw frame ────────────────────────────────────────────────────────
        screen.fill(BG_COLOR)

        # ── Toolbar background ────────────────────────────────────────────────
        pygame.draw.rect(screen, TOOLBAR_COLOR, (0, 0, TOOLBAR_W, WINDOW_H))
        pygame.draw.line(screen, PANEL_BORDER, (TOOLBAR_W, 0), (TOOLBAR_W, WINDOW_H), 2)

        # Title
        label(screen, font_big, "🎨 Paint", (PAD, 12), ACCENT)

        # Tool buttons
        label(screen, font_sm, "TOOLS", (PAD, 36), (140, 140, 160))
        for i, (name, shortcut, _) in enumerate(TOOLS):
            rect = tool_buttons[i]
            is_active = (i == active_tool_idx)
            bg = ACCENT if is_active else (45, 45, 58)
            border_c = ACCENT if is_active else PANEL_BORDER
            draw_rounded_rect(screen, bg, rect, radius=6, border=1, border_color=border_c)
            col = (255, 255, 255) if is_active else TEXT_COLOR
            # Center text inside button
            txt = font_sm.render(f"{shortcut} {name}", True, col)
            tr = txt.get_rect(center=rect.center)
            screen.blit(txt, tr)

        # Brush size buttons
        size_label_y = size_buttons[0].y - 18
        label(screen, font_sm, "BRUSH SIZE  (1/2/3)", (PAD, size_label_y), (140, 140, 160))
        size_names = ["S  2px", "M  5px", "L  10px"]
        for i, rect in enumerate(size_buttons):
            is_active = (brush_size_key == i + 1)
            bg = ACCENT if is_active else (45, 45, 58)
            draw_rounded_rect(screen, bg, rect, radius=6, border=1,
                              border_color=ACCENT if is_active else PANEL_BORDER)
            col = (255,255,255) if is_active else TEXT_COLOR
            txt = font_sm.render(size_names[i], True, col)
            tr = txt.get_rect(center=rect.center)
            screen.blit(txt, tr)

        # Color palette
        label(screen, font_sm, "COLOR PALETTE", (PAD, palette_top), (140, 140, 160))
        for rect, color in swatches:
            pygame.draw.rect(screen, color, rect, border_radius=3)
            if color == active_color:
                pygame.draw.rect(screen, (255, 255, 255), rect, 2, border_radius=3)
                pygame.draw.rect(screen, ACCENT, rect.inflate(4, 4), 2, border_radius=5)

        # Active color preview
        preview_top = swatches[-1][0].bottom + 14
        label(screen, font_sm, "ACTIVE COLOR", (PAD, preview_top), (140, 140, 160))
        pygame.draw.rect(screen, active_color,
                         (PAD, preview_top + 16, TOOLBAR_W - PAD * 2, 28), border_radius=6)
        pygame.draw.rect(screen, PANEL_BORDER,
                         (PAD, preview_top + 16, TOOLBAR_W - PAD * 2, 28), 1, border_radius=6)

        # Shortcuts reminder
        shortcut_top = preview_top + 56
        label(screen, font_sm, "SHORTCUTS", (PAD, shortcut_top), (140, 140, 160))
        hints = ["Ctrl+S — Save PNG", "1/2/3 — Brush size"]
        for j, hint in enumerate(hints):
            label(screen, font_sm, hint, (PAD, shortcut_top + 16 + j * 16), (110, 110, 130))

        # ── Canvas area ───────────────────────────────────────────────────────
        screen.blit(canvas, (CANVAS_X, 0))

        # Preview overlay (drawn on top of canvas, not committed)
        if drawing or (isinstance(current_tool(), TextTool) and current_tool().active):
            preview = canvas.copy()
            current_tool().draw_preview(preview, canvas_pos(mouse_screen), active_color, current_size())
            screen.blit(preview, (CANVAS_X, 0))

        # Status bar at bottom of canvas
        status_rect = pygame.Rect(CANVAS_X, WINDOW_H - 26, CANVAS_W, 26)
        pygame.draw.rect(screen, (240, 240, 245), status_rect)
        pygame.draw.line(screen, (200, 200, 200), (CANVAS_X, WINDOW_H - 26), (WINDOW_W, WINDOW_H - 26))
        if now < status_timer:
            label(screen, font_sm, status_msg, (CANVAS_X + 8, WINDOW_H - 19), (60, 60, 80))
        else:
            tool_name = TOOLS[active_tool_idx][0]
            size_str  = ["Small", "Medium", "Large"][brush_size_key - 1]
            info = f"Tool: {tool_name}   |   Brush: {size_str} ({current_size()}px)   |   Ctrl+S to save"
            label(screen, font_sm, info, (CANVAS_X + 8, WINDOW_H - 19), (120, 120, 130))

        # Cursor position
        if in_canvas(mouse_screen):
            cx, cy = canvas_pos(mouse_screen)
            coord = f"({cx}, {cy})"
            label(screen, font_sm, coord, (WINDOW_W - 90, WINDOW_H - 19), (150, 150, 160))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
