from __future__ import annotations


def update_dirt_exposure_overlay(world, registry):
    # Build per-cell pattern overrides for dirt with green bands that grow/shrink slowly
    CELL = 8  # must match CELL_SIZE
    GREEN = (60, 180, 60)
    growth_rate = 0.05 * getattr(world, "time_scale", 1.0)
    decay_rate = 0.08 * getattr(world, "time_scale", 1.0)
    for x, y in registry.iter_positions("dirt"):
        def is_air(nx: int, ny: int) -> bool:
            # Only true for in-bounds empty; edges are NOT considered air (prevents edge "growth")
            if not (0 <= nx < world.width and 0 <= ny < world.height):
                return False
            return world.grid[nx][ny].item_id == 0
        top_air = is_air(x, y - 1)
        bot_air = is_air(x, y + 1)
        left_air = is_air(x - 1, y)
        right_air = is_air(x + 1, y)
        cell = world.get_cell(x, y)
        if not cell:
            continue
        # Update growth state per side (floats 0..2)
        gt = float(cell.meta.get("grow_top", 0.0))
        gb = float(cell.meta.get("grow_bottom", 0.0))
        gl = float(cell.meta.get("grow_left", 0.0))
        gr = float(cell.meta.get("grow_right", 0.0))
        gt = min(2.0, gt + growth_rate) if top_air else max(0.0, gt - decay_rate)
        gb = min(2.0, gb + growth_rate) if bot_air else max(0.0, gb - decay_rate)
        gl = min(2.0, gl + growth_rate) if left_air else max(0.0, gl - decay_rate)
        gr = min(2.0, gr + growth_rate) if right_air else max(0.0, gr - decay_rate)
        cell.meta["grow_top"] = gt
        cell.meta["grow_bottom"] = gb
        cell.meta["grow_left"] = gl
        cell.meta["grow_right"] = gr

        # Determine integer pixel bands 0..2
        it = min(2, int(gt + 1e-6))
        ib = min(2, int(gb + 1e-6))
        il = min(2, int(gl + 1e-6))
        ir = min(2, int(gr + 1e-6))

        # Get base pattern/palette from behavior if present
        idef = registry.get_by_key("dirt")
        base_pat = getattr(idef.behavior, "pattern", None)
        base_pal = getattr(idef.behavior, "palette", None)
        if base_pat is None or base_pal is None:
            base_pat = [[0 for _ in range(CELL)] for _ in range(CELL)]
            base_pal = [getattr(idef.behavior, "color", (120, 72, 32))]
        # Ensure green is in palette
        pal = list(base_pal)
        try:
            green_idx = pal.index(GREEN)
        except ValueError:
            pal.append(GREEN)
            green_idx = len(pal) - 1
        # Start with base pattern copy
        pat = [list(row[:CELL]) + [] for row in base_pat[:CELL]]
        # Apply integer bands
        if it > 0:
            for yy in range(it):
                if yy < CELL:
                    for xx in range(CELL):
                        pat[yy][xx] = green_idx
        if ib > 0:
            for yy in range(CELL - ib, CELL):
                if 0 <= yy < CELL:
                    for xx in range(CELL):
                        pat[yy][xx] = green_idx
        if il > 0:
            for yy in range(CELL):
                for xx in range(il):
                    if xx < CELL:
                        pat[yy][xx] = green_idx
        if ir > 0:
            for yy in range(CELL):
                for xx in range(CELL - ir, CELL):
                    if 0 <= xx < CELL:
                        pat[yy][xx] = green_idx
        # Store overrides or clear when no visible band remains
        if it or ib or il or ir:
            cell.meta["pattern_override"] = pat
            cell.meta["palette_override"] = pal
        else:
            cell.meta.pop("pattern_override", None)
            cell.meta.pop("palette_override", None)
