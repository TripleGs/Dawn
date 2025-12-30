import pygame
import random
import os
import json
from dataclasses import dataclass, field
from typing import Dict, Optional, Tuple
from src.registry import Registry
from src.content import register_all

# -------- Minimal engine inlined into main --------

Color = Tuple[int, int, int]


CELL_SIZE = 8
UI_ROW_HEIGHT = 48

# -------- Modern Theme System --------
class Theme:
    # Background colors
    BG_DARK = (18, 18, 24)
    BG_MEDIUM = (28, 28, 38)
    BG_LIGHT = (38, 40, 52)

    # Accent colors
    PRIMARY = (100, 140, 220)
    PRIMARY_HOVER = (120, 160, 240)
    PRIMARY_DARK = (70, 100, 180)
    SECONDARY = (80, 200, 160)
    SECONDARY_HOVER = (100, 220, 180)
    DANGER = (220, 80, 80)
    DANGER_HOVER = (240, 100, 100)

    # Text colors
    TEXT_PRIMARY = (240, 240, 250)
    TEXT_SECONDARY = (160, 165, 180)
    TEXT_DIM = (100, 105, 120)

    # UI element colors
    PANEL_BG = (32, 34, 44)
    PANEL_BORDER = (55, 58, 72)
    INPUT_BG = (22, 24, 32)
    INPUT_BORDER = (60, 65, 80)
    INPUT_FOCUS = (100, 140, 220)

    # Button colors
    BTN_DEFAULT = (50, 54, 68)
    BTN_HOVER = (65, 70, 88)
    BTN_PRESSED = (40, 44, 56)

    # Special
    GLOW = (100, 140, 220, 60)
    SHADOW = (0, 0, 0, 80)


def draw_rounded_rect(surface, color, rect, radius=8, border=0, border_color=None):
    """Draw a rounded rectangle with optional border."""
    pygame.draw.rect(surface, color, rect, border_radius=radius)
    if border > 0 and border_color:
        pygame.draw.rect(surface, border_color, rect, border, border_radius=radius)


def draw_button(surface, rect, text, font, hovered=False, pressed=False, style="default"):
    """Draw a styled button with hover/press states."""
    if style == "primary":
        bg = Theme.PRIMARY_HOVER if hovered else Theme.PRIMARY
        border_color = Theme.PRIMARY_DARK
    elif style == "secondary":
        bg = Theme.SECONDARY_HOVER if hovered else Theme.SECONDARY
        border_color = (60, 160, 130)
    elif style == "danger":
        bg = Theme.DANGER_HOVER if hovered else Theme.DANGER
        border_color = (180, 60, 60)
    else:
        bg = Theme.BTN_HOVER if hovered else Theme.BTN_DEFAULT
        border_color = Theme.PANEL_BORDER

    if pressed:
        bg = Theme.BTN_PRESSED

    # Draw button background
    draw_rounded_rect(surface, bg, rect, radius=6, border=2, border_color=border_color)

    # Draw text centered
    txt_surf = font.render(text, True, Theme.TEXT_PRIMARY)
    tx = rect.x + (rect.w - txt_surf.get_width()) // 2
    ty = rect.y + (rect.h - txt_surf.get_height()) // 2
    surface.blit(txt_surf, (tx, ty))

    return rect


def draw_panel(surface, rect, title=None, title_font=None):
    """Draw a styled panel with optional title bar."""
    # Panel shadow (subtle offset)
    shadow_rect = pygame.Rect(rect.x + 3, rect.y + 3, rect.w, rect.h)
    pygame.draw.rect(surface, (0, 0, 0), shadow_rect, border_radius=10)

    # Main panel
    draw_rounded_rect(surface, Theme.PANEL_BG, rect, radius=10, border=2, border_color=Theme.PANEL_BORDER)

    if title and title_font:
        # Title bar
        title_rect = pygame.Rect(rect.x, rect.y, rect.w, 32)
        pygame.draw.rect(surface, Theme.BG_LIGHT, title_rect, border_top_left_radius=10, border_top_right_radius=10)
        pygame.draw.line(surface, Theme.PANEL_BORDER, (rect.x, rect.y + 32), (rect.right, rect.y + 32), 1)

        title_surf = title_font.render(title, True, Theme.TEXT_PRIMARY)
        surface.blit(title_surf, (rect.x + 12, rect.y + 8))
        return 32
    return 0


def ensure_pygame() -> None:
    if not pygame.get_init():
        pygame.init()


def create_surface(world, ui_height: int = UI_ROW_HEIGHT) -> pygame.Surface:
    width = world.width * CELL_SIZE
    height = world.height * CELL_SIZE + ui_height
    return pygame.display.set_mode((width, height))


def _slot_paths() -> dict:
    base = os.path.dirname(os.path.abspath(__file__))
    return {
        1: os.path.join(base, "save_slot1.json"),
        2: os.path.join(base, "save_slot2.json"),
        3: os.path.join(base, "save_slot3.json"),
    }


def draw_world(surface: pygame.Surface, world, registry) -> None:
    surface.fill((20, 20, 24))
    for x in range(world.width):
        for y in range(world.height):
            cell = world.grid[x][y]
            if cell.item_id == 0:
                continue
            item = registry.get_by_id(cell.item_id)
            if not item:
                continue
            beh = item.behavior
            # Per-cell overrides from content (pattern/palette)
            cell_pat = cell.meta.get("pattern_override")
            cell_pal = cell.meta.get("palette_override")
            use_pat = cell_pat if cell_pat is not None else getattr(beh, "pattern", None)
            use_pal = cell_pal if cell_pal is not None else getattr(beh, "palette", None)
            if use_pat is not None and use_pal is not None:
                # Draw pattern using palette indices
                pat = use_pat
                pal = use_pal
                cell_x = x * CELL_SIZE
                cell_y = y * CELL_SIZE
                # Clamp pattern to CELL_SIZE
                for py in range(min(CELL_SIZE, len(pat))):
                    row = pat[py]
                    for px in range(min(CELL_SIZE, len(row))):
                        ci = row[px]
                        if 0 <= ci < len(pal):
                            pygame.draw.rect(surface, pal[ci], (cell_x + px, cell_y + py, 1, 1))
            else:
                color = beh.color
                pygame.draw.rect(surface, color, (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))


def draw_palette(surface: pygame.Surface, registry, palette_state: dict, mouse_pos: Tuple[int, int] = (0, 0)) -> None:
    rect = palette_state["rect"]
    title_h = 32
    search_h = 32
    pad = 10

    # Panel shadow
    shadow_rect = pygame.Rect(rect.x + 3, rect.y + 3, rect.w, rect.h)
    pygame.draw.rect(surface, (0, 0, 0, 100), shadow_rect, border_radius=12)

    # Panel background with rounded corners
    draw_rounded_rect(surface, Theme.PANEL_BG, rect, radius=12, border=2, border_color=Theme.PANEL_BORDER)

    # Title bar (drag handle)
    title_rect = pygame.Rect(rect.x, rect.y, rect.w, title_h)
    pygame.draw.rect(surface, Theme.BG_LIGHT, title_rect, border_top_left_radius=12, border_top_right_radius=12)
    pygame.draw.line(surface, Theme.PANEL_BORDER, (rect.x, rect.y + title_h), (rect.right, rect.y + title_h), 1)

    # Drag handle dots
    for i in range(3):
        dot_x = rect.x + 12 + i * 6
        pygame.draw.circle(surface, Theme.TEXT_DIM, (dot_x, rect.y + title_h // 2), 2)

    title_font = pygame.font.SysFont(None, 20)
    title_surf = title_font.render("Materials", True, Theme.TEXT_PRIMARY)
    surface.blit(title_surf, (rect.x + 36, rect.y + 8))

    # Minimize button on title bar
    min_rect = pygame.Rect(rect.right - 28, rect.y + 6, 20, 20)
    min_hovered = min_rect.collidepoint(mouse_pos)
    min_bg = Theme.BTN_HOVER if min_hovered else Theme.BTN_DEFAULT
    draw_rounded_rect(surface, min_bg, min_rect, radius=4)
    minus_y = min_rect.y + min_rect.h // 2
    pygame.draw.line(surface, Theme.TEXT_PRIMARY, (min_rect.x + 5, minus_y), (min_rect.right - 5, minus_y), 2)

    # Search box with icon
    search_rect = pygame.Rect(rect.x + pad, rect.y + title_h + 8, rect.w - 2 * pad, search_h)
    is_search_active = palette_state.get("input_active", False)
    search_border = Theme.INPUT_FOCUS if is_search_active else Theme.INPUT_BORDER
    draw_rounded_rect(surface, Theme.INPUT_BG, search_rect, radius=6, border=1, border_color=search_border)

    # Search icon (magnifying glass)
    pygame.draw.circle(surface, Theme.TEXT_DIM, (search_rect.x + 14, search_rect.y + 12), 6, 1)
    pygame.draw.line(surface, Theme.TEXT_DIM, (search_rect.x + 18, search_rect.y + 16),
                    (search_rect.x + 22, search_rect.y + 20), 1)

    search_text = palette_state.get("search", "")
    font = pygame.font.SysFont(None, 18)
    display_text = search_text if search_text else "Search materials..."
    text_color = Theme.TEXT_PRIMARY if search_text else Theme.TEXT_DIM
    txt = font.render(display_text, True, text_color)
    surface.blit(txt, (search_rect.x + 28, search_rect.y + 8))

    # Resize grip (bottom-right) with better styling
    grip = pygame.Rect(rect.right - 16, rect.bottom - 16, 14, 14)
    # Draw diagonal lines for grip
    for i in range(3):
        offset = i * 4
        pygame.draw.line(surface, Theme.TEXT_DIM,
                        (grip.right - 3 - offset, grip.bottom - 3),
                        (grip.right - 3, grip.bottom - 3 - offset), 1)

    # Content grid area
    content_y = search_rect.bottom + 8
    content_h = rect.bottom - content_y - 18
    content_rect = pygame.Rect(rect.x + pad, content_y, rect.w - 2 * pad, content_h)
    draw_rounded_rect(surface, Theme.BG_DARK, content_rect, radius=8)

    # Filter items - match against key, display name, or behavior name
    q = (search_text or "").lower().strip()
    if q:
        items = [i for i in registry.all_items()
                 if q in i.key.lower()
                 or q in i.behavior.display_name.lower()
                 or q in getattr(i.behavior, 'name', '').lower()]
        # Reset scroll when searching
        palette_state["scroll"] = 0
    else:
        items = list(registry.all_items())

    # Grid metrics - larger cells for better visibility
    grid_pad = 8
    cell_w = 60
    cell_h = 72
    cols = max(1, (content_rect.w - grid_pad * 2) // cell_w)
    start_row = palette_state.get("scroll", 0)

    # Draw grid
    visible_rows = max(1, (content_rect.h - grid_pad * 2) // cell_h)
    first = start_row * cols
    last = min(len(items), first + visible_rows * cols)

    for i in range(first, last):
        rel = i - first
        row = rel // cols
        col = rel % cols
        bx = content_rect.x + grid_pad + col * cell_w
        by = content_rect.y + grid_pad + row * cell_h

        idef = items[i]
        is_selected = palette_state.get("selected_id") == idef.id

        # Item cell background on hover/selection
        cell_rect = pygame.Rect(bx, by, cell_w - 4, cell_h - 4)
        if is_selected:
            draw_rounded_rect(surface, Theme.PRIMARY_DARK, cell_rect, radius=6, border=2, border_color=Theme.PRIMARY)
        elif cell_rect.collidepoint(mouse_pos):
            draw_rounded_rect(surface, Theme.BG_LIGHT, cell_rect, radius=6)

        # Icon - centered in cell with room for label below
        label_h = 16  # Space reserved for label
        pad = 4  # Padding around icon
        available_h = cell_rect.h - label_h - pad  # Height available for icon
        icon_size = min(cell_rect.w - pad * 2, available_h)  # Square icon that fits
        ix = cell_rect.x + (cell_rect.w - icon_size) // 2  # Center horizontally
        iy = cell_rect.y + pad  # Top padding
        icon_rect = pygame.Rect(ix, iy, icon_size, icon_size)

        # Draw material icon
        beh = idef.behavior
        pal = getattr(beh, "palette", None)
        pat = getattr(beh, "pattern", None)

        # Create a surface for the icon
        icon_surface = pygame.Surface((icon_size, icon_size), pygame.SRCALPHA)

        if pal and pat:
            rows_p = len(pat)
            cols_p = len(pat[0]) if rows_p > 0 else 0
            if rows_p > 0 and cols_p > 0:
                sx = max(1, icon_size // cols_p)
                sy = max(1, icon_size // rows_p)
                for py in range(rows_p):
                    prow = pat[py]
                    for px in range(min(cols_p, len(prow))):
                        ci = prow[px]
                        if 0 <= ci < len(pal):
                            pygame.draw.rect(icon_surface, pal[ci], (px * sx, py * sy, sx, sy))
            else:
                icon_surface.fill(beh.color)
        else:
            icon_surface.fill(beh.color)

        # Blit icon with border
        surface.blit(icon_surface, icon_rect.topleft)
        pygame.draw.rect(surface, Theme.PANEL_BORDER, icon_rect, 1, border_radius=2)

        # Label centered below icon
        label_font = pygame.font.SysFont(None, 14)
        name = idef.behavior.display_name
        if len(name) > 8:
            name = name[:7] + ".."
        label_surf = label_font.render(name, True, Theme.TEXT_SECONDARY)
        lw = label_surf.get_width()
        label_y = icon_rect.bottom + 2
        surface.blit(label_surf, (cell_rect.x + (cell_rect.w - lw) // 2, label_y))

    # Scrollbar if needed
    total_rows = (len(items) + cols - 1) // cols
    if total_rows > visible_rows:
        scrollbar_h = content_rect.h - 8
        scrollbar_x = content_rect.right - 6
        scrollbar_y = content_rect.y + 4

        # Track
        pygame.draw.rect(surface, Theme.BG_MEDIUM, (scrollbar_x, scrollbar_y, 4, scrollbar_h), border_radius=2)

        # Thumb
        thumb_h = max(20, scrollbar_h * visible_rows // total_rows)
        thumb_y = scrollbar_y + (scrollbar_h - thumb_h) * start_row // max(1, total_rows - visible_rows)
        pygame.draw.rect(surface, Theme.TEXT_DIM, (scrollbar_x, thumb_y, 4, thumb_h), border_radius=2)

    # Save hit regions for input
    palette_state["_search_rect"] = search_rect
    palette_state["_title_rect"] = title_rect
    palette_state["_content_rect"] = content_rect
    palette_state["_grip_rect"] = grip
    palette_state["_min_rect"] = min_rect


def draw_main_menu(surface: pygame.Surface, mouse_pos: Tuple[int, int] = (0, 0)) -> dict:
    width, height = surface.get_size()

    # Fonts
    title_font = pygame.font.SysFont(None, 72)
    subtitle_font = pygame.font.SysFont(None, 24)
    btn_font = pygame.font.SysFont(None, 28)

    # Background is drawn by caller (demo world), so no fill here

    # Title with glow effect
    title_y = height // 3 - 50

    # Glow behind title
    glow_font = pygame.font.SysFont(None, 76)
    glow_surf = glow_font.render("Dawn", True, Theme.PRIMARY_DARK)
    surface.blit(glow_surf, (width // 2 - glow_surf.get_width() // 2 + 2, title_y + 2))

    # Main title
    title = title_font.render("Dawn", True, Theme.TEXT_PRIMARY)
    surface.blit(title, (width // 2 - title.get_width() // 2, title_y))

    # Subtitle
    subtitle = subtitle_font.render("A Falling Sand Sandbox", True, Theme.TEXT_SECONDARY)
    surface.blit(subtitle, (width // 2 - subtitle.get_width() // 2, title_y + 60))

    # Start button - larger and centered
    start_rect = pygame.Rect(width // 2 - 100, height // 2 + 20, 200, 50)
    hovered = start_rect.collidepoint(mouse_pos)
    draw_button(surface, start_rect, "Play", btn_font, hovered=hovered, style="primary")

    # Version/credits at bottom
    credits_font = pygame.font.SysFont(None, 18)
    credits = credits_font.render("v0.1 - A sandbox simulation", True, Theme.TEXT_DIM)
    surface.blit(credits, (width // 2 - credits.get_width() // 2, height - 30))

    return {"start": start_rect}


def _scan_slots() -> dict:
    paths = _slot_paths()
    info = {}
    for i, path in paths.items():
        if os.path.exists(path):
            try:
                with open(path, "r") as f:
                    data = json.load(f)
                    info[i] = {"exists": True, "name": data.get("name", "Untitled")}
            except Exception:
                info[i] = {"exists": True, "name": "Corrupted"}
        else:
            info[i] = {"exists": False, "name": "Empty"}
    return info


def draw_slot_menu(surface: pygame.Surface, selected_slot: int | None = None, mouse_pos: Tuple[int, int] = (0, 0)) -> dict:
    width, height = surface.get_size()

    # Fonts
    title_font = pygame.font.SysFont(None, 36)
    font = pygame.font.SysFont(None, 24)
    small_font = pygame.font.SysFont(None, 20)
    icon_font = pygame.font.SysFont(None, 28)

    # Background is drawn by caller (demo world), so no fill here

    # Title
    title = title_font.render("Select World", True, Theme.TEXT_PRIMARY)
    surface.blit(title, (width // 2 - title.get_width() // 2, height // 4 - 40))

    # Subtitle
    subtitle = small_font.render("Choose a save slot to continue or start fresh", True, Theme.TEXT_SECONDARY)
    surface.blit(subtitle, (width // 2 - subtitle.get_width() // 2, height // 4))

    slots_info = _scan_slots()
    actions = {}

    # Calculate card dimensions
    card_width = 320
    card_height = 70
    card_spacing = 16
    start_y = height // 3 + 20

    for i in range(1, 4):
        y = start_y + (i - 1) * (card_height + card_spacing)

        # Main card/slot button
        card_rect = pygame.Rect(width // 2 - card_width // 2, y, card_width, card_height)
        is_selected = selected_slot == i
        is_hovered = card_rect.collidepoint(mouse_pos)

        info = slots_info[i]
        exists = info["exists"]

        # Card background with selection/hover states
        if is_selected:
            bg_color = Theme.BG_LIGHT
            border_color = Theme.PRIMARY
        elif is_hovered:
            bg_color = Theme.BG_MEDIUM
            border_color = Theme.PANEL_BORDER
        else:
            bg_color = Theme.PANEL_BG
            border_color = Theme.PANEL_BORDER

        draw_rounded_rect(surface, bg_color, card_rect, radius=10, border=2, border_color=border_color)

        # Slot icon/number on the left
        icon_rect = pygame.Rect(card_rect.x + 12, card_rect.y + 12, 46, 46)
        icon_bg = Theme.PRIMARY if exists else Theme.BTN_DEFAULT
        draw_rounded_rect(surface, icon_bg, icon_rect, radius=8)

        slot_num = icon_font.render(str(i), True, Theme.TEXT_PRIMARY)
        surface.blit(slot_num, (icon_rect.x + (icon_rect.w - slot_num.get_width()) // 2,
                                icon_rect.y + (icon_rect.h - slot_num.get_height()) // 2))

        # Slot info text
        text_x = icon_rect.right + 16
        if exists:
            name_text = info["name"]
            if len(name_text) > 18:
                name_text = name_text[:15] + "..."
            name_surf = font.render(name_text, True, Theme.TEXT_PRIMARY)
            surface.blit(name_surf, (text_x, card_rect.y + 16))

            status_surf = small_font.render("Click to load world", True, Theme.TEXT_DIM)
            surface.blit(status_surf, (text_x, card_rect.y + 40))
        else:
            name_surf = font.render("Empty Slot", True, Theme.TEXT_SECONDARY)
            surface.blit(name_surf, (text_x, card_rect.y + 16))

            status_surf = small_font.render("Click to create new world", True, Theme.TEXT_DIM)
            surface.blit(status_surf, (text_x, card_rect.y + 40))

        actions[f"select_{i}"] = card_rect

        # Action buttons on the right (only for existing saves)
        if exists:
            btn_size = 36
            btn_y = card_rect.y + (card_height - btn_size) // 2

            # Rename button
            ren_rect = pygame.Rect(card_rect.right - btn_size * 2 - 20, btn_y, btn_size, btn_size)
            ren_hovered = ren_rect.collidepoint(mouse_pos)
            ren_bg = Theme.SECONDARY_HOVER if ren_hovered else Theme.SECONDARY
            draw_rounded_rect(surface, ren_bg, ren_rect, radius=6)
            # Pencil icon (simple lines)
            pygame.draw.line(surface, Theme.TEXT_PRIMARY, (ren_rect.x + 10, ren_rect.y + 24),
                           (ren_rect.x + 24, ren_rect.y + 10), 2)
            pygame.draw.line(surface, Theme.TEXT_PRIMARY, (ren_rect.x + 10, ren_rect.y + 26),
                           (ren_rect.x + 10, ren_rect.y + 24), 2)
            actions[f"rename_{i}"] = ren_rect

            # Delete button
            del_rect = pygame.Rect(card_rect.right - btn_size - 10, btn_y, btn_size, btn_size)
            del_hovered = del_rect.collidepoint(mouse_pos)
            del_bg = Theme.DANGER_HOVER if del_hovered else Theme.DANGER
            draw_rounded_rect(surface, del_bg, del_rect, radius=6)
            # X icon
            pygame.draw.line(surface, Theme.TEXT_PRIMARY, (del_rect.x + 10, del_rect.y + 10),
                           (del_rect.x + 26, del_rect.y + 26), 2)
            pygame.draw.line(surface, Theme.TEXT_PRIMARY, (del_rect.x + 26, del_rect.y + 10),
                           (del_rect.x + 10, del_rect.y + 26), 2)
            actions[f"delete_{i}"] = del_rect

    # Back button at bottom
    back_rect = pygame.Rect(width // 2 - 60, height - 80, 120, 40)
    back_hovered = back_rect.collidepoint(mouse_pos)
    draw_button(surface, back_rect, "Back", font, hovered=back_hovered)
    actions["back"] = back_rect

    return actions


def draw_input_dialog(surface: pygame.Surface, prompt: str, current_text: str) -> None:
    width, height = surface.get_size()

    # Semi-transparent overlay
    overlay = pygame.Surface((width, height), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    surface.blit(overlay, (0, 0))

    # Dialog box with shadow
    box_w, box_h = 380, 160
    box_x, box_y = (width - box_w) // 2, (height - box_h) // 2
    box_rect = pygame.Rect(box_x, box_y, box_w, box_h)

    # Shadow
    shadow_rect = pygame.Rect(box_x + 4, box_y + 4, box_w, box_h)
    pygame.draw.rect(surface, (0, 0, 0), shadow_rect, border_radius=12)

    # Main dialog
    draw_rounded_rect(surface, Theme.PANEL_BG, box_rect, radius=12, border=2, border_color=Theme.PRIMARY)

    # Title
    title_font = pygame.font.SysFont(None, 28)
    t_surf = title_font.render(prompt, True, Theme.TEXT_PRIMARY)
    surface.blit(t_surf, (box_x + (box_w - t_surf.get_width()) // 2, box_y + 20))

    # Input field
    input_rect = pygame.Rect(box_x + 24, box_y + 60, box_w - 48, 44)
    draw_rounded_rect(surface, Theme.INPUT_BG, input_rect, radius=8, border=2, border_color=Theme.INPUT_FOCUS)

    # Text with cursor
    font = pygame.font.SysFont(None, 24)
    display_text = current_text + "|"  # Blinking cursor effect
    i_surf = font.render(display_text, True, Theme.TEXT_PRIMARY)
    surface.blit(i_surf, (input_rect.x + 12, input_rect.y + 12))

    # Instructions
    inst_font = pygame.font.SysFont(None, 18)
    inst_surf = inst_font.render("ENTER to confirm  |  ESC to cancel", True, Theme.TEXT_DIM)
    surface.blit(inst_surf, (box_x + (box_w - inst_surf.get_width()) // 2, box_y + 120))


def draw_game_hud(surface: pygame.Surface, world, palette_visible: bool, mouse_pos: Tuple[int, int] = (0, 0)) -> dict:
    """Draw the in-game HUD with menu button and world name."""
    actions = {}
    width = surface.get_width()

    # Top bar background (semi-transparent)
    bar_surface = pygame.Surface((width, 36), pygame.SRCALPHA)
    bar_surface.fill((18, 18, 24, 200))
    surface.blit(bar_surface, (0, 0))

    # Subtle bottom border
    pygame.draw.line(surface, Theme.PANEL_BORDER, (0, 35), (width, 35), 1)

    font = pygame.font.SysFont(None, 18)
    small_font = pygame.font.SysFont(None, 16)

    # World name (left side)
    name_surf = font.render(world.name, True, Theme.TEXT_PRIMARY)
    surface.blit(name_surf, (12, 10))

    # Menu button (right side)
    menu_btn = pygame.Rect(width - 78, 6, 70, 24)
    menu_hovered = menu_btn.collidepoint(mouse_pos)
    draw_button(surface, menu_btn, "Menu", small_font, hovered=menu_hovered)
    actions["menu"] = menu_btn

    return actions


def palette_hit_test(palette_state: dict, pos: Tuple[int, int]) -> str | None:
    x, y = pos
    if not palette_state["rect"].collidepoint(x, y):
        return None
    if palette_state.get("_min_rect") and palette_state["_min_rect"].collidepoint(x, y):
        return "min"
    if palette_state.get("_grip_rect") and palette_state["_grip_rect"].collidepoint(x, y):
        return "grip"
    if palette_state.get("_title_rect") and palette_state["_title_rect"].collidepoint(x, y):
        return "title"
    if palette_state.get("_search_rect") and palette_state["_search_rect"].collidepoint(x, y):
        return "search"
    if palette_state.get("_content_rect") and palette_state["_content_rect"].collidepoint(x, y):
        return "content"
    return "panel"


def palette_click_select(registry, palette_state: dict, pos: Tuple[int, int]) -> None:
    content_rect = palette_state.get("_content_rect")
    if not content_rect or not content_rect.collidepoint(*pos):
        return
    grid_pad = 8
    q = (palette_state.get("search", "") or "").lower().strip()
    if q:
        items = [i for i in registry.all_items()
                 if q in i.key.lower()
                 or q in i.behavior.display_name.lower()
                 or q in getattr(i.behavior, 'name', '').lower()]
    else:
        items = list(registry.all_items())
    cell_w = 60
    cell_h = 72
    cols = max(1, (content_rect.w - grid_pad * 2) // cell_w)
    start_row = palette_state.get("scroll", 0)
    visible_rows = max(1, (content_rect.h - grid_pad * 2) // cell_h)
    first = start_row * cols
    last = min(len(items), first + visible_rows * cols)
    x, y = pos
    rel_x = x - (content_rect.x + grid_pad)
    rel_y = y - (content_rect.y + grid_pad)
    if rel_x < 0 or rel_y < 0:
        return
    col = rel_x // cell_w
    row = rel_y // cell_h
    idx = first + row * cols + col
    if 0 <= idx < last:
        idef = items[idx]
        palette_state["selected_id"] = idef.id


def ui_hit_world(surface: pygame.Surface, pos, ui_height: int, palette_state: dict | None = None, hud_actions: dict | None = None) -> bool:
    x, y = pos
    # Not over HUD bar at top (36 pixels)
    if y < 36:
        return False
    # Not over palette
    if palette_state and palette_state.get("visible") and palette_state.get("rect") and palette_state["rect"].collidepoint(*pos):
        return False
    return True


@dataclass
class Cell:
    item_id: int = 0
    moisture: float = 0.0
    temperature: float = 20.0
    meta: Dict[str, float] = field(default_factory=dict)


# Registry now lives in src/registry.py


class World:
    def __init__(self, width: int, height: int, registry) -> None:
        self.width = width
        self.height = height
        self.registry = registry
        self.grid = [[Cell() for _ in range(height)] for _ in range(width)]
        self._preset_to_temp = {
            "Ice Age": 0.0,
            "Cold": 10.0,
            "Mild": 20.0,
            "Hot": 35.0,
            "Volcano": 200.0,
        }
        self.ambient_preset = "Mild"
        self.ambient_temperature = self._preset_to_temp[self.ambient_preset]
        self.time_scale: float = 1.0
        self.name: str = "Untitled"

    def set_ambient_preset(self, preset: str) -> None:
        if preset in self._preset_to_temp:
            self.ambient_preset = preset
            self.ambient_temperature = self._preset_to_temp[preset]

    def set_time_scale(self, scale: float) -> None:
        self.time_scale = max(0.1, min(10.0, scale))

    def in_bounds(self, x: int, y: int) -> bool:
        return 0 <= x < self.width and 0 <= y < self.height

    def get_cell(self, x: int, y: int) -> Optional[Cell]:
        if not self.in_bounds(x, y):
            return None
        return self.grid[x][y]

    def set_item(self, x: int, y: int, item_id: int) -> None:
        if self.in_bounds(x, y):
            old = self.grid[x][y].item_id
            self.grid[x][y].item_id = item_id
            # notify registry for position tracking
            self.registry.on_set(x, y, old, item_id)

    def add_moisture(self, x: int, y: int, amount: float) -> None:
        cell = self.get_cell(x, y)
        if cell:
            cell.moisture = max(0.0, cell.moisture + amount)

    def add_temperature(self, x: int, y: int, amount: float) -> None:
        cell = self.get_cell(x, y)
        if cell:
            cell.temperature += amount

    def get_neighbors4(self, x: int, y: int):
        return tuple([(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)])

    def get_neighbors8(self, x: int, y: int):
        return tuple([
            (x - 1, y - 1), (x, y - 1), (x + 1, y - 1),
            (x - 1, y),                 (x + 1, y),
            (x - 1, y + 1), (x, y + 1), (x + 1, y + 1),
        ])

    def get_item_id(self, key: str) -> int:
        item = self.registry.get_by_key(key)
        return item.id if item else 0

    def _can_fall_into(self, from_behavior, tx: int, ty: int) -> bool:
        if not self.in_bounds(tx, ty):
            return False
        target = self.grid[tx][ty]
        if target.item_id == 0:
            return True
        target_def = self.registry.get_by_id(target.item_id)
        if not target_def:
            return False
        if not target_def.behavior.is_solid and from_behavior.density > target_def.behavior.density:
            return True
        return False

    def _can_rise_into(self, from_behavior, tx: int, ty: int) -> bool:
        if not self.in_bounds(tx, ty):
            return False
        target = self.grid[tx][ty]
        if target.item_id == 0:
            return True
        target_def = self.registry.get_by_id(target.item_id)
        if not target_def:
            return False
        if not target_def.behavior.is_solid and from_behavior.density < target_def.behavior.density:
            return True
        return False

    def _apply_gravity(self) -> None:
        moved = [[False for _ in range(self.height)] for _ in range(self.width)]
        for y in range(self.height - 2, -1, -1):
            xs = list(range(self.width))
            random.shuffle(xs)
            for x in xs:
                if moved[x][y]:
                    continue
                cell = self.grid[x][y]
                if cell.item_id == 0:
                    continue
                definition = self.registry.get_by_id(cell.item_id)
                if not definition:
                    continue
                beh = definition.behavior
                is_gas = (not beh.is_solid) and (beh.density < 0.2)
                # Solid support: per-material required solid neighbors (8-dir) to stay in place
                if beh.is_solid:
                    required = getattr(beh, "support_required_neighbors", None)
                    if required is None:
                        required = 3
                    solid_neighbors = 0
                    for nx, ny in self.get_neighbors8(x, y):
                        if not self.in_bounds(nx, ny):
                            continue
                        ncell = self.grid[nx][ny]
                        if ncell.item_id == 0:
                            continue
                        ndef = self.registry.get_by_id(ncell.item_id)
                        if ndef and ndef.behavior.is_solid:
                            solid_neighbors += 1
                            if solid_neighbors >= required:
                                break
                    if solid_neighbors >= required:
                        continue
                if is_gas:
                    candidates = [(x, y - 1), (x - 1, y - 1), (x + 1, y - 1)]
                    random.shuffle(candidates)
                elif not beh.is_solid:
                    candidates = [(x, y + 1), (x - 1, y + 1), (x + 1, y + 1)]
                    random.shuffle(candidates)
                else:
                    candidates = [(x, y + 1)]
                    diags = [(x - 1, y + 1), (x + 1, y + 1)]
                    random.shuffle(diags)
                    candidates.extend(diags)
                moved_now = False
                for tx, ty in candidates:
                    # For solid diagonal moves, require the side cell to be empty to reduce powder-like flow
                    if beh.is_solid and not is_gas and ty == y + 1 and tx != x:
                        side_x = x - 1 if tx < x else x + 1
                        if not self.in_bounds(side_x, y) or self.grid[side_x][y].item_id != 0:
                            continue
                    can_move = self._can_rise_into(beh, tx, ty) if is_gas else self._can_fall_into(beh, tx, ty)
                    if can_move:
                        a_id = self.grid[x][y].item_id
                        b_id = self.grid[tx][ty].item_id
                        self.grid[x][y], self.grid[tx][ty] = self.grid[tx][ty], self.grid[x][y]
                        moved[x][y] = True
                        moved[tx][ty] = True
                        moved_now = True
                        # notify registry of swap
                        self.registry.on_swap(x, y, a_id, tx, ty, b_id)
                        break
                if moved_now:
                    continue
                if (not is_gas) and (not beh.is_solid):
                    dirs = [-1, 1]
                    random.shuffle(dirs)
                    max_range = 4
                    did_lateral = False
                    for d in dirs:
                        nx = x + d
                        steps = 1
                        while steps <= max_range and self.in_bounds(nx, y) and self.grid[nx][y].item_id == 0:
                            if self._can_fall_into(beh, nx, y + 1):
                                self.grid[x][y], self.grid[x + d][y] = self.grid[x + d][y], self.grid[x][y]
                                moved[x][y] = True
                                moved[x + d][y] = True
                                did_lateral = True
                                break
                            nx += d
                            steps += 1
                        if did_lateral:
                            break
                    if did_lateral:
                        continue
                    lateral = [(x - 1, y), (x + 1, y)]
                    random.shuffle(lateral)
                    for lx, ly in lateral:
                        if not self.in_bounds(lx, ly):
                            continue
                        if self.grid[lx][ly].item_id != 0:
                            continue
                        if random.random() < 0.5:
                            a_id = self.grid[x][y].item_id
                            b_id = self.grid[lx][ly].item_id
                            self.grid[x][y], self.grid[lx][ly] = self.grid[lx][ly], self.grid[x][y]
                            moved[x][y] = True
                            moved[lx][ly] = True
                            self.registry.on_swap(x, y, a_id, lx, ly, b_id)
                            break
                # Solids: no lateral slip here (stability controlled by support rule and restricted diagonals)
                if is_gas and not moved[x][y]:
                    lateral = [(x - 1, y), (x + 1, y)]
                    random.shuffle(lateral)
                    for lx, ly in lateral:
                        if not self.in_bounds(lx, ly):
                            continue
                        if self._can_rise_into(beh, lx, ly):
                            self.grid[x][y], self.grid[lx][ly] = self.grid[lx][ly], self.grid[x][y]
                            moved[x][y] = True
                            moved[lx][ly] = True
                            break

    def tick(self) -> None:
        self._apply_gravity()
        for y in range(self.height - 1, -1, -1):
            for x in range(self.width):
                cell = self.grid[x][y]
                drift = 0.2 * self.time_scale
                if cell.temperature < self.ambient_temperature:
                    cell.temperature = min(self.ambient_temperature, cell.temperature + drift)
                elif cell.temperature > self.ambient_temperature:
                    cell.temperature = max(self.ambient_temperature, cell.temperature - drift)
        self.registry.apply(self)

    # --- Persistence ---
    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "width": self.width,
            "height": self.height,
            "ambient_preset": self.ambient_preset,
            "time_scale": self.time_scale,
            "cells": [
                [
                    {
                        "item_id": self.grid[x][y].item_id,
                        "moisture": self.grid[x][y].moisture,
                        "temperature": self.grid[x][y].temperature,
                    }
                    for y in range(self.height)
                ]
                for x in range(self.width)
            ],
        }

    def load_from_dict(self, data: dict) -> None:
        if data.get("width") != self.width or data.get("height") != self.height:
            return
        self.name = data.get("name", "Untitled")
        self.set_ambient_preset(data.get("ambient_preset", self.ambient_preset))
        self.set_time_scale(float(data.get("time_scale", self.time_scale)))
        cells = data.get("cells", [])
        for x in range(min(self.width, len(cells))):
            col = cells[x]
            for y in range(min(self.height, len(col))):
                c = col[y]
                self.set_item(x, y, int(c.get("item_id", 0)))
                cell = self.grid[x][y]
                cell.moisture = float(c.get("moisture", 0.0))
                cell.temperature = float(c.get("temperature", 20.0))

    def save_to_path(self, path: str) -> None:
        try:
            with open(path, "w") as f:
                json.dump(self.to_dict(), f)
        except Exception:
            pass

    def load_from_path(self, path: str) -> None:
        try:
            if not os.path.exists(path):
                return
            with open(path, "r") as f:
                data = json.load(f)
            # Reset registry position tracking first
            for x in range(self.width):
                for y in range(self.height):
                    self.set_item(x, y, 0)
            self.load_from_dict(data)
        except Exception:
            pass


def main() -> None:
    ensure_pygame()
    clock = pygame.time.Clock()
    registry = Registry()
    register_all(registry)

    world = World(120, 80, registry)

    # Ambient preset fixed for now
    world.set_ambient_preset("Mild")

    # Create surface with no reserved bottom UI
    ui_height = 0
    surface = create_surface(world, ui_height)

    # Demo world for menu background - uses its own registry to avoid interference
    demo_registry = Registry()
    register_all(demo_registry)
    demo_world = World(120, 80, demo_registry)
    demo_world.set_ambient_preset("Mild")
    demo_spawn_timer = 0
    # Materials to randomly spawn in demo (interesting visual ones)
    demo_materials = ["sand", "water", "dirt", "snow", "rock", "seed", "seed_oak", "seed_cherry"]

    # Palette UI state - positioned below the HUD bar
    palette_state = {
        "rect": pygame.Rect(20, 46, 280, 340),
        "search": "",
        "dragging": False,
        "resizing": False,
        "drag_offset": (0, 0),
        "scroll": 0,
        "input_active": False,
        "selected_id": registry.all_items()[0].id if registry.all_items() else None,
        "visible": True,
    }

    # HUD actions cache
    hud_actions = {}

    # Fixed time scale
    world.set_time_scale(1.0)

    running = True
    # Note: placement is handled via mouse state each frame
    brush_size = 1
    app_state = "menu"  # menu -> slots -> playing
    selected_slot: int | None = None
    input_text = ""
    renaming_slot: int | None = None
    slot_buttons = {}

    while running:
        # Ensure event pumping even if no input is happening
        pygame.event.pump()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # Save on quit to current slot if any
                if selected_slot:
                    paths = _slot_paths()
                    world.save_to_path(paths[selected_slot])
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                if app_state == "menu":
                    btns = draw_main_menu(surface, (mx, my))
                    if btns["start"].collidepoint(mx, my):
                        app_state = "slots"
                    continue
                if app_state == "slots":
                    # Re-scan slots to ensure UI is up-to-date
                    slot_buttons = draw_slot_menu(surface, selected_slot, (mx, my))

                    # Check buttons in priority order: back, delete, rename, then select
                    # This prevents delete/rename clicks from also triggering select
                    clicked_action = None
                    for action, rect in slot_buttons.items():
                        if rect.collidepoint(mx, my):
                            # Prioritize more specific actions over select
                            if action == "back":
                                clicked_action = action
                                break
                            elif action.startswith("delete_") or action.startswith("rename_"):
                                clicked_action = action
                                break
                            elif action.startswith("select_") and clicked_action is None:
                                clicked_action = action

                    if clicked_action:
                        if clicked_action == "back":
                            app_state = "menu"
                        elif clicked_action.startswith("select_"):
                            slot_id = int(clicked_action.split("_")[1])
                            selected_slot = slot_id
                            path = _slot_paths()[slot_id]
                            if os.path.exists(path):
                                world.load_from_path(path)
                                app_state = "playing"
                            else:
                                # New empty slot - reset world first, then prompt for name
                                world = World(120, 80, registry)
                                world.set_ambient_preset("Mild")
                                world.set_time_scale(1.0)
                                renaming_slot = slot_id
                                input_text = ""
                                app_state = "renaming"
                        elif clicked_action.startswith("delete_"):
                            slot_id = int(clicked_action.split("_")[1])
                            path = _slot_paths()[slot_id]
                            if os.path.exists(path):
                                os.remove(path)
                                if selected_slot == slot_id:
                                    selected_slot = None
                        elif clicked_action.startswith("rename_"):
                            slot_id = int(clicked_action.split("_")[1])
                            renaming_slot = slot_id
                            paths = _slot_paths()
                            try:
                                with open(paths[slot_id], "r") as f:
                                    data = json.load(f)
                                    input_text = data.get("name", "")
                            except Exception:
                                input_text = ""
                            app_state = "renaming"
                    continue

                # Game state - check HUD buttons first
                if app_state == "playing":
                    # Check HUD menu button
                    if hud_actions.get("menu") and hud_actions["menu"].collidepoint(mx, my):
                        # Save current world before going to menu
                        if selected_slot:
                            paths = _slot_paths()
                            world.save_to_path(paths[selected_slot])
                        app_state = "slots"
                        continue

                    # Check floating palette toggle button (when palette is hidden)
                    if not palette_state["visible"]:
                        toggle_rect = palette_state.get("_toggle_rect")
                        if toggle_rect and toggle_rect.collidepoint(mx, my):
                            palette_state["visible"] = True
                            continue

                if palette_state["visible"]:
                    hit = palette_hit_test(palette_state, (mx, my))
                    if hit:
                        if hit == "min":
                            palette_state["visible"] = False
                        elif hit == "title":
                            palette_state["dragging"] = True
                            dx = mx - palette_state["rect"].x
                            dy = my - palette_state["rect"].y
                            palette_state["drag_offset"] = (dx, dy)
                        elif hit == "grip":
                            palette_state["resizing"] = True
                        elif hit == "search":
                            palette_state["input_active"] = True
                        elif hit == "content":
                            palette_click_select(registry, palette_state, (mx, my))
                        continue
                # World placement
                if event.button == 2:
                    # Middle-click eyedropper
                    bx = max(0, min(world.width - 1, mx // CELL_SIZE))
                    by = max(0, min(world.height - 1, my // CELL_SIZE))
                    cell = world.get_cell(bx, by)
                    if cell and cell.item_id:
                        palette_state["selected_id"] = cell.item_id
                    continue
                # Left button handled continuously below
            elif event.type == pygame.MOUSEBUTTONUP:
                palette_state["dragging"] = False
                palette_state["resizing"] = False
            elif getattr(pygame, "MOUSEWHEEL", None) and event.type == pygame.MOUSEWHEEL:
                # Scroll content when hovering palette
                mx, my = pygame.mouse.get_pos()
                if palette_state.get("_content_rect") and palette_state["_content_rect"].collidepoint(mx, my):
                    palette_state["scroll"] = max(0, palette_state.get("scroll", 0) - int(event.y))
            elif event.type == pygame.MOUSEMOTION:
                if palette_state["visible"]:
                    if palette_state["dragging"]:
                        dx, dy = palette_state["drag_offset"]
                        palette_state["rect"].x = mx - dx
                        palette_state["rect"].y = my - dy
                    elif palette_state["resizing"]:
                        rx, ry = palette_state["rect"].x, palette_state["rect"].y
                        palette_state["rect"].w = max(180, mx - rx)
                        palette_state["rect"].h = max(180, my - ry)
            elif event.type == pygame.KEYDOWN:
                if app_state == "renaming":
                    if event.key == pygame.K_ESCAPE:
                        app_state = "slots"
                    elif event.key == pygame.K_RETURN:
                        paths = _slot_paths()
                        if renaming_slot:
                            path = paths[renaming_slot]
                            if not os.path.exists(path):
                                # Creating and starting
                                world.name = input_text or "Untitled"
                                # Create file immediately
                                world.save_to_path(path)
                                selected_slot = renaming_slot
                                app_state = "playing"
                            else:
                                # Just renaming
                                try:
                                    with open(path, "r") as f:
                                        data = json.load(f)
                                    data["name"] = input_text
                                    with open(path, "w") as f:
                                        json.dump(data, f)
                                except Exception:
                                    pass
                                app_state = "slots"
                    elif event.key == pygame.K_BACKSPACE:
                        input_text = input_text[:-1]
                    else:
                        ch = event.unicode
                        if ch and (32 <= ord(ch) <= 126):
                            input_text = (input_text + ch)[:20]
                    continue

                if palette_state.get("input_active"):
                    if event.key == pygame.K_BACKSPACE:
                        palette_state["search"] = palette_state.get("search", "")[:-1]
                    elif event.key == pygame.K_RETURN:
                        palette_state["input_active"] = False
                    else:
                        ch = event.unicode
                        if ch and (32 <= ord(ch) <= 126):
                            palette_state["search"] = (palette_state.get("search", "") + ch)[:40]

        # Advance simulation once per frame regardless of input events
        if app_state == "playing":
            world.tick()

        # Continuous placement while mouse is held down
        # Handle continuous left-click placement and right-click erasing
        mx, my = pygame.mouse.get_pos()
        if app_state == "playing" and ui_hit_world(surface, (mx, my), ui_height, palette_state):
            buttons = pygame.mouse.get_pressed()
            if buttons[0] and palette_state.get("selected_id"):
                # Left drag place with brush
                jx = random.randint(-1, 1)
                jy = random.randint(-1, 1)
                cx = max(0, min(world.width - 1, mx // CELL_SIZE + jx))
                cy = max(0, min(world.height - 1, my // CELL_SIZE + jy))
                item_id = palette_state["selected_id"]
                r = brush_size - 1
                for dx in range(-r, r + 1):
                    for dy in range(-r, r + 1):
                        bx = cx + dx
                        by = cy + dy
                        if not (0 <= bx < world.width and 0 <= by < world.height):
                            continue
                        cell = world.get_cell(bx, by)
                        if not cell:
                            continue
                        if cell.item_id != item_id:
                            world.set_item(bx, by, item_id)
                            item_def = registry.get_by_id(item_id)
                            if item_def:
                                item_def.behavior.on_place(world, bx, by, cell)
            if buttons[2]:
                # Right drag erase with brush
                cx = max(0, min(world.width - 1, mx // CELL_SIZE))
                cy = max(0, min(world.height - 1, my // CELL_SIZE))
                r = brush_size - 1
                for dx in range(-r, r + 1):
                    for dy in range(-r, r + 1):
                        bx = cx + dx
                        by = cy + dy
                        if not (0 <= bx < world.width and 0 <= by < world.height):
                            continue
                        if world.get_cell(bx, by):
                            world.set_item(bx, by, 0)

        # Get current mouse position for hover effects
        mx, my = pygame.mouse.get_pos()

        # Update demo world for menu backgrounds
        if app_state in ("menu", "slots", "renaming"):
            # Simulate demo world
            demo_world.tick()

            # Randomly spawn materials from the top
            demo_spawn_timer += 1
            if demo_spawn_timer >= 3:  # Every 3 frames
                demo_spawn_timer = 0
                # Spawn a few blocks at random x positions near top
                for _ in range(random.randint(1, 3)):
                    spawn_x = random.randint(0, demo_world.width - 1)
                    spawn_y = random.randint(0, 3)
                    mat_key = random.choice(demo_materials)
                    mat = demo_registry.get_by_key(mat_key)
                    if mat:
                        cell = demo_world.get_cell(spawn_x, spawn_y)
                        if cell and cell.item_id == 0:
                            demo_world.set_item(spawn_x, spawn_y, mat.id)

        if app_state == "menu":
            # Draw demo world as background
            draw_world(surface, demo_world, demo_registry)
            # Darken overlay for readability
            overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
            overlay.fill((18, 18, 24, 180))
            surface.blit(overlay, (0, 0))
            draw_main_menu(surface, (mx, my))
        elif app_state == "slots":
            # Draw demo world as background
            draw_world(surface, demo_world, demo_registry)
            overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
            overlay.fill((18, 18, 24, 180))
            surface.blit(overlay, (0, 0))
            draw_slot_menu(surface, selected_slot, (mx, my))
        elif app_state == "renaming":
            # Draw demo world as background
            draw_world(surface, demo_world, demo_registry)
            overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
            overlay.fill((18, 18, 24, 180))
            surface.blit(overlay, (0, 0))
            draw_slot_menu(surface, selected_slot, (mx, my))
            draw_input_dialog(surface, f"Name Slot {renaming_slot}", input_text)
        else:
            # Playing state
            draw_world(surface, world, registry)

            # Draw HUD at top
            hud_actions = draw_game_hud(surface, world, palette_state["visible"], (mx, my))

            # Draw palette if visible, otherwise show floating toggle button
            if palette_state["visible"]:
                draw_palette(surface, registry, palette_state, (mx, my))
            else:
                # Floating toggle button to show palette
                toggle_rect = pygame.Rect(12, 46, 36, 36)
                toggle_hovered = toggle_rect.collidepoint(mx, my)
                toggle_bg = Theme.BTN_HOVER if toggle_hovered else Theme.PANEL_BG
                draw_rounded_rect(surface, toggle_bg, toggle_rect, radius=8, border=2, border_color=Theme.PANEL_BORDER)
                # Draw grid dots icon (3x3)
                for row in range(3):
                    for col in range(3):
                        dot_x = toggle_rect.x + 10 + col * 8
                        dot_y = toggle_rect.y + 10 + row * 8
                        pygame.draw.circle(surface, Theme.TEXT_SECONDARY, (dot_x, dot_y), 2)
                palette_state["_toggle_rect"] = toggle_rect

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()