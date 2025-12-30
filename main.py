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


def draw_palette(surface: pygame.Surface, registry, palette_state: dict) -> None:
    rect = palette_state["rect"]
    title_h = 24
    search_h = 24
    pad = 8
    # Panel background
    pygame.draw.rect(surface, (36, 36, 42), rect)
    pygame.draw.rect(surface, (80, 80, 90), rect, 2)
    # Title bar (drag handle)
    title_rect = pygame.Rect(rect.x, rect.y, rect.w, title_h)
    pygame.draw.rect(surface, (50, 50, 60), title_rect)
    title_surf = pygame.font.SysFont(None, 18).render("Palette", True, (230, 230, 240))
    surface.blit(title_surf, (rect.x + 8, rect.y + 4))
    # Minimize button on title bar
    min_rect = pygame.Rect(rect.right - 22, rect.y + 4, 16, 16)
    pygame.draw.rect(surface, (90, 90, 100), min_rect)
    minus_y = min_rect.y + min_rect.h // 2
    pygame.draw.line(surface, (230, 230, 240), (min_rect.x + 3, minus_y), (min_rect.right - 3, minus_y), 2)
    # Search box
    search_rect = pygame.Rect(rect.x + pad, rect.y + title_h + 4, rect.w - 2 * pad, search_h)
    pygame.draw.rect(surface, (26, 26, 32), search_rect)
    pygame.draw.rect(surface, (80, 80, 90), search_rect, 1)
    search_text = palette_state.get("search", "")
    font = pygame.font.SysFont(None, 18)
    txt = font.render(search_text or "search...", True, (200, 200, 210) if search_text else (110, 110, 120))
    surface.blit(txt, (search_rect.x + 6, search_rect.y + 4))
    # Resize grip (bottom-right)
    grip = pygame.Rect(rect.right - 12, rect.bottom - 12, 10, 10)
    pygame.draw.rect(surface, (90, 90, 100), grip)
    # Content grid
    content_y = search_rect.bottom + 6
    content_h = rect.bottom - content_y - 14
    content_rect = pygame.Rect(rect.x + pad, content_y, rect.w - 2 * pad, content_h)
    pygame.draw.rect(surface, (28, 28, 34), content_rect)
    # Filter items
    q = (search_text or "").lower().strip()
    items = [i for i in registry.all_items() if (q in i.behavior.display_name.lower() or q in i.key)]
    # Grid metrics
    grid_pad = 6
    cell_w = 56
    cell_h = 68
    cols = max(1, (content_rect.w - grid_pad) // cell_w)
    start_row = palette_state.get("scroll", 0)
    # Draw grid
    row = 0
    visible_rows = max(1, (content_rect.h - grid_pad) // cell_h)
    first = start_row * cols
    last = min(len(items), first + visible_rows * cols)
    for i in range(first, last):
        rel = i - first
        row = rel // cols
        col = rel % cols
        bx = content_rect.x + grid_pad + col * cell_w
        by = content_rect.y + grid_pad + row * cell_h
        # Icon (supports multi-color palette/pattern preview)
        idef = items[i]
        # Compute icon size to fit inside cell with padding
        label_h = 14
        icon_size = min(40, cell_w - 2 * grid_pad, cell_h - (label_h + 2 + grid_pad))
        ix = bx + (cell_w - icon_size) // 2
        iy = by + 2
        icon_rect = pygame.Rect(ix, iy, icon_size, icon_size)
        beh = idef.behavior
        pal = getattr(beh, "palette", None)
        pat = getattr(beh, "pattern", None)
        if pal and pat:
            rows = len(pat)
            cols_p = len(pat[0]) if rows > 0 else 0
            if rows > 0 and cols_p > 0:
                sx = max(1, icon_rect.w // cols_p)
                sy = max(1, icon_rect.h // rows)
                for py in range(rows):
                    prow = pat[py]
                    for px in range(min(cols_p, len(prow))):
                        ci = prow[px]
                        if 0 <= ci < len(pal):
                            pygame.draw.rect(
                                surface,
                                pal[ci],
                                (icon_rect.x + px * sx, icon_rect.y + py * sy, sx, sy),
                            )
            else:
                pygame.draw.rect(surface, beh.color, icon_rect)
        else:
            pygame.draw.rect(surface, beh.color, icon_rect)
        # Label centered in cell
        label_surf = pygame.font.SysFont(None, 14).render(idef.behavior.display_name, True, (220, 220, 230))
        lw = label_surf.get_width()
        surface.blit(label_surf, (bx + max(0, (cell_w - lw) // 2), iy + icon_size + 2))
        # Selection outline
        if palette_state.get("selected_id") == idef.id:
            pygame.draw.rect(surface, (250, 250, 255), icon_rect, 2)
    # Save hit regions for input
    palette_state["_search_rect"] = search_rect
    palette_state["_title_rect"] = title_rect
    palette_state["_content_rect"] = content_rect
    palette_state["_grip_rect"] = grip
    palette_state["_min_rect"] = min_rect


def draw_main_menu(surface: pygame.Surface) -> dict:
    width, height = surface.get_size()
    title_font = pygame.font.SysFont(None, 48)
    btn_font = pygame.font.SysFont(None, 28)
    title = title_font.render("Dawn", True, (230, 230, 240))
    surface.blit(title, (width // 2 - title.get_width() // 2, height // 3 - 40))
    start_rect = pygame.Rect(width // 2 - 80, height // 2, 160, 44)
    pygame.draw.rect(surface, (70, 70, 90), start_rect)
    start_txt = btn_font.render("Start", True, (230, 230, 240))
    surface.blit(start_txt, (start_rect.x + (start_rect.w - start_txt.get_width()) // 2, start_rect.y + 10))
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


def draw_slot_menu(surface: pygame.Surface, selected_slot: int | None = None) -> dict:
    width, height = surface.get_size()
    font = pygame.font.SysFont(None, 28)
    small_font = pygame.font.SysFont(None, 24)
    title = font.render("Select Save Slot", True, (230, 230, 240))
    surface.blit(title, (width // 2 - title.get_width() // 2, height // 3 - 60))

    slots_info = _scan_slots()
    actions = {}
    paths = _slot_paths()

    for i in range(1, 4):
        y = height // 2 - 60 + (i - 1) * 70  # Increased spacing

        # Main slot button
        rect = pygame.Rect(width // 2 - 160, y, 220, 50)
        color = (90, 90, 120) if selected_slot == i else (70, 70, 90)
        pygame.draw.rect(surface, color, rect)

        info = slots_info[i]
        label_text = f"Slot {i}"
        if info["exists"]:
            label_text += f": {info['name']}"
        else:
            label_text += " (Empty)"

        # Truncate if too long
        if len(label_text) > 25:
             label_text = label_text[:22] + "..."

        txt = font.render(label_text, True, (230, 230, 240))
        surface.blit(txt, (rect.x + 12, rect.y + 15))
        actions[f"select_{i}"] = rect

        if info["exists"]:
            # Rename button
            ren_rect = pygame.Rect(rect.right + 10, y, 60, 50)
            pygame.draw.rect(surface, (60, 100, 150), ren_rect)
            ren_txt = small_font.render("Name", True, (255, 255, 255))
            surface.blit(ren_txt, (ren_rect.x + (ren_rect.w - ren_txt.get_width()) // 2, ren_rect.y + 17))
            actions[f"rename_{i}"] = ren_rect

            # Delete button
            del_rect = pygame.Rect(ren_rect.right + 10, y, 40, 50)
            pygame.draw.rect(surface, (150, 60, 60), del_rect)
            del_txt = small_font.render("X", True, (255, 255, 255))
            surface.blit(del_txt, (del_rect.x + (del_rect.w - del_txt.get_width()) // 2, del_rect.y + 17))
            actions[f"delete_{i}"] = del_rect

    return actions


def draw_input_dialog(surface: pygame.Surface, prompt: str, current_text: str) -> None:
    width, height = surface.get_size()
    # Overlay
    s = pygame.Surface((width, height))
    s.set_alpha(200)
    s.fill((0, 0, 0))
    surface.blit(s, (0, 0))

    # Dialog box
    box_w, box_h = 400, 140
    box_x, box_y = (width - box_w) // 2, (height - box_h) // 2
    pygame.draw.rect(surface, (50, 50, 60), (box_x, box_y, box_w, box_h))
    pygame.draw.rect(surface, (100, 100, 120), (box_x, box_y, box_w, box_h), 2)

    font = pygame.font.SysFont(None, 24)
    # Title
    t_surf = font.render(prompt, True, (230, 230, 240))
    surface.blit(t_surf, (box_x + 10, box_y + 10))

    # Input field
    input_rect = pygame.Rect(box_x + 20, box_y + 50, box_w - 40, 40)
    pygame.draw.rect(surface, (30, 30, 35), input_rect)
    pygame.draw.rect(surface, (200, 200, 220), input_rect, 1)

    i_surf = font.render(current_text, True, (255, 255, 255))
    surface.blit(i_surf, (input_rect.x + 5, input_rect.y + 12))

    # Instruction
    inst_surf = pygame.font.SysFont(None, 18).render("Press ENTER to confirm, ESC to cancel", True, (150, 150, 160))
    surface.blit(inst_surf, (box_x + 20, box_y + 100))


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
    grid_pad = 6
    q = (palette_state.get("search", "") or "").lower().strip()
    items = [i for i in registry.all_items() if (q in i.behavior.display_name.lower() or q in i.key)]
    cell_w = 56
    cell_h = 68
    cols = max(1, (content_rect.w - grid_pad) // cell_w)
    start_row = palette_state.get("scroll", 0)
    visible_rows = max(1, (content_rect.h - grid_pad) // cell_h)
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


def ui_hit_world(surface: pygame.Surface, pos, ui_height: int, palette_state: dict | None = None) -> bool:
    # not over palette or toggle icon
    if palette_state and palette_state.get("visible") and palette_state.get("rect") and palette_state["rect"].collidepoint(*pos):
        return False
    # Toggle icon area
    togg = pygame.Rect(8, 8, 20, 20)
    if togg.collidepoint(*pos):
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
    # Palette UI state
    palette_state = {
        "rect": pygame.Rect(20, 20, 260, 300),
        "search": "",
        "dragging": False,
        "resizing": False,
        "drag_offset": (0, 0),
        "scroll": 0,
        "input_active": False,
        "selected_id": registry.all_items()[0].id if registry.all_items() else None,
        "visible": True,
    }

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
                    btns = draw_main_menu(surface)
                    if btns["start"].collidepoint(mx, my):
                        app_state = "slots"
                    continue
                if app_state == "slots":
                    slot_buttons = draw_slot_menu(surface, selected_slot)
                    for action, rect in slot_buttons.items():
                        if rect.collidepoint(mx, my):
                            if action.startswith("select_"):
                                slot_id = int(action.split("_")[1])
                                selected_slot = slot_id
                                path = _slot_paths()[slot_id]
                                if os.path.exists(path):
                                    world.load_from_path(path)
                                    app_state = "playing"
                                else:
                                    # New empty slot, prompt for name
                                    renaming_slot = slot_id
                                    input_text = ""
                                    app_state = "renaming"
                            elif action.startswith("delete_"):
                                slot_id = int(action.split("_")[1])
                                path = _slot_paths()[slot_id]
                                if os.path.exists(path):
                                    os.remove(path)
                                    if selected_slot == slot_id:
                                        selected_slot = None
                            elif action.startswith("rename_"):
                                slot_id = int(action.split("_")[1])
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
                else:
                    # Check toggle icon in corner
                    togg = pygame.Rect(8, 8, 20, 20)
                    if togg.collidepoint(mx, my):
                        palette_state["visible"] = True
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

        if app_state == "menu":
            surface.fill((20, 20, 24))
            draw_main_menu(surface)
        elif app_state == "slots":
            surface.fill((20, 20, 24))
            draw_slot_menu(surface, selected_slot)
        elif app_state == "renaming":
            surface.fill((20, 20, 24))
            # Draw slot menu in background
            draw_slot_menu(surface, selected_slot)
            draw_input_dialog(surface, f"Name Slot {renaming_slot}", input_text)
        else:
            draw_world(surface, world, registry)
            if palette_state["visible"]:
                draw_palette(surface, registry, palette_state)
            else:
                # Draw toggle icon
                togg = pygame.Rect(8, 8, 20, 20)
                pygame.draw.rect(surface, (60, 60, 72), togg)
                pygame.draw.rect(surface, (120, 120, 140), togg, 2)
                dots = [(togg.x + 6, togg.y + 6), (togg.x + 10, togg.y + 6), (togg.x + 14, togg.y + 6)]
                for (dx, dy) in dots:
                    pygame.draw.circle(surface, (220, 220, 230), (dx, dy), 1)
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()