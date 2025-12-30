from __future__ import annotations

import random

from src.materials import Solid, Liquid, Gas

# Declarative materials
MATERIALS = [
    {
        "id": "dirt", "type": "solid", "density": 1.0, "support": 4,
        "palette": [(118,70,30),(130,82,42)],
        "pattern": [
            [0,0,0,0,0,0,0,0],
            [0,0,0,1,0,0,0,0],
            [0,0,0,0,0,0,1,0],
            [0,1,0,0,0,0,0,0],
            [0,0,0,0,1,0,0,0],
            [0,0,1,0,0,0,0,0],
            [0,0,0,0,0,0,0,1],
            [0,0,0,0,0,0,0,0],
        ]
    },
    {
        "id": "water", "type": "liquid", "density": 0.5,
        "palette": [(38,108,252),(60,140,255)],
        "pattern": [[(x+y)%2 for x in range(8)] for y in range(8)],
    },
    {
        "id": "mud", "type": "solid", "density": 1.1,
        "palette": [(94,62,44),(104,70,50)],
        "pattern": [[0,0,1,0,0,0,1,0],[0,0,0,0,1,0,0,0],[1,0,0,0,0,0,0,0],[0,0,0,1,0,0,0,0],[0,1,0,0,0,0,0,0],[0,0,0,0,0,1,0,0],[0,0,0,0,0,0,0,1],[0,0,0,0,0,0,0,0]],
    },
    {
        "id": "snow", "type": "solid", "density": 0.9,
        "palette": [(240,240,255),(220,220,240)],
        "pattern": [[0 if (x+y)%4 else 1 for x in range(8)] for y in range(8)],
    },
    {
        "id": "ice", "type": "solid", "density": 0.4,
        "palette": [(170,220,255),(150,205,245)],
        "pattern": [[0,0,0,1,0,0,0,0],[0,0,0,0,0,1,0,0],[0,0,0,0,0,0,0,1],[0,1,0,0,0,0,0,0],[0,0,0,0,1,0,0,0],[1,0,0,0,0,0,0,0],[0,0,0,0,0,1,0,0],[0,0,1,0,0,0,0,0]],
    },
    {
        "id": "steam", "type": "gas", "density": 0.05,
        "palette": [(220,220,220),(200,200,200)],
        "pattern": [[0 if (x*y)%3 else 1 for x in range(8)] for y in range(8)],
    },
    {
        "id": "cloud", "type": "gas", "density": 0.08,
        # light -> dark greys
        "palette": [(220,222,230),(180,185,200),(135,140,160),(95,100,120)],
        "pattern": [[0 for x in range(8)] for y in range(8)],
    },
    {
        "id": "clay", "type": "solid", "density": 1.2,
        "palette": [(158,118,98),(170,130,110)],
        "pattern": [[0,0,0,0,1,0,0,0],[0,0,1,0,0,0,0,1],[0,0,0,0,0,1,0,0],[0,1,0,0,0,0,0,0],[0,0,0,1,0,0,0,0],[1,0,0,0,0,0,1,0],[0,0,0,0,0,0,0,0],[0,0,1,0,0,0,0,0]],
    },
    {
        "id": "grass", "type": "solid", "density": 1.0,
        "palette": [(60,180,60),(50,160,50)],
        "pattern": [[0 if (x+y)%2 else 1 for x in range(8)] for y in range(8)],
    },
    {
        "id": "sand", "type": "solid", "density": 1.1, "support": 6,
        "palette": [(222,205,150),(210,190,130)],
        "pattern": [
            [0,0,0,0,1,0,0,0],
            [0,0,1,0,0,0,0,1],
            [0,0,0,0,0,1,0,0],
            [0,1,0,0,0,0,0,0],
            [0,0,0,1,0,0,0,0],
            [1,0,0,0,0,0,1,0],
            [0,0,0,0,0,0,0,0],
            [0,0,1,0,0,0,0,0],
        ],
    },
    {
        "id": "rock", "type": "solid", "density": 1.0,
        "palette": [(100,100,100),(120,120,120)],
        "pattern": [[0,0,0,1,0,0,0,0],[0,0,0,0,0,1,0,0],[0,0,0,0,0,0,0,1],[0,1,0,0,0,0,0,0],[0,0,0,0,1,0,0,0],[1,0,0,0,0,0,1,0],[0,0,0,0,0,0,0,0],[0,0,1,0,0,0,0,0]],
    },
    {
        "id": "seed", "type": "solid", "density": 0.9,
        "palette": [(140,110,70),(160,130,90)],
        "pattern": [[1 if (x==3 and y==3) else 0 for x in range(8)] for y in range(8)],
    },
    {
        "id": "wood", "type": "solid", "density": 1.2, "support": 3,
        "palette": [(110,78,48),(130,90,60)],
        "pattern": [[0 if (x%2==0) else 1 for x in range(8)] for y in range(8)],
    },
    {
        "id": "leaves", "type": "solid", "density": 0.8, "support": 2,
        "palette": [(50,150,50),(70,170,70)],
        "pattern": [[0 if ((x+y)%2==0) else 1 for x in range(8)] for y in range(8)],
    },
    # Oak variant
    {
        "id": "seed_oak", "type": "solid", "density": 0.9,
        "palette": [(130,100,60),(150,120,80)],
        "pattern": [[1 if (x==3 and y==4) else 0 for x in range(8)] for y in range(8)],
    },
    {
        "id": "wood_oak", "type": "solid", "density": 1.2, "support": 3,
        "palette": [(120,84,54),(140,100,70)],
        "pattern": [[0 if (x%2==1) else 1 for x in range(8)] for y in range(8)],
    },
    {
        "id": "leaves_oak", "type": "solid", "density": 0.8, "support": 2,
        "palette": [(40,140,40),(60,160,60)],
        "pattern": [[0 if ((x*y)%3) else 1 for x in range(8)] for y in range(8)],
    },
    # Birch variant
    {
        "id": "seed_birch", "type": "solid", "density": 0.9,
        "palette": [(150,120,80),(170,140,100)],
        "pattern": [[1 if (x==4 and y==3) else 0 for x in range(8)] for y in range(8)],
    },
    {
        "id": "wood_birch", "type": "solid", "density": 1.2, "support": 3,
        "palette": [(210,210,190),(40,40,40)],
        "pattern": [[0 if (x%2==0) else 1 for x in range(8)] for y in range(8)],
    },
    {
        "id": "leaves_birch", "type": "solid", "density": 0.8, "support": 2,
        "palette": [(70,170,70),(90,190,90)],
        "pattern": [[0 if ((x+y)%3) else 1 for x in range(8)] for y in range(8)],
    },
    # Cherry variant
    {
        "id": "seed_cherry", "type": "solid", "density": 0.9,
        "palette": [(150,90,90),(170,110,110)],
        "pattern": [[1 if (x==3 and y==3) else 0 for x in range(8)] for y in range(8)],
    },
    {
        "id": "wood_cherry", "type": "solid", "density": 1.2, "support": 3,
        "palette": [(140,70,70),(160,90,90)],
        "pattern": [[0 if (x%2==0) else 1 for x in range(8)] for y in range(8)],
    },
    {
        "id": "leaves_cherry", "type": "solid", "density": 0.8, "support": 2,
        "palette": [(200,100,150),(220,120,170)],
        "pattern": [[0 if ((x+y)%2==0) else 1 for x in range(8)] for y in range(8)],
    },
]


def register_all(registry) -> None:
    # Register materials
    for spec in MATERIALS:
        mat_type = spec.get("type", "solid").lower()
        kwargs = {"id": spec["id"], "color": spec.get("color", (200, 200, 200)), "density": spec.get("density", 1.0)}
        if "palette" in spec:
            kwargs["palette"] = spec["palette"]
        if "pattern" in spec:
            kwargs["pattern"] = spec["pattern"]
        if "support" in spec:
            kwargs["support_required_neighbors"] = int(spec["support"])
        if mat_type == "solid":
            behavior = Solid(**kwargs)
        elif mat_type == "liquid":
            behavior = Liquid(**kwargs)
        elif mat_type == "gas":
            behavior = Gas(**kwargs)
        else:
            raise ValueError(f"Unknown material type: {mat_type}")
        registry.register(spec["id"], behavior)

    # Register rule checker functions
    registry.add_checker(water_moisturize)
    registry.add_checker(water_phase)
    registry.add_checker(mud_drying_baking)
    registry.add_checker(check_water_touch_dirt)
    # Ensure any stale overrides on non-dirt cells are removed before recomputing
    registry.add_checker(clear_non_dirt_overrides)
    registry.add_checker(update_dirt_exposure_overlay)
    registry.add_checker(plant_seeds)
    registry.add_checker(update_steam_clouds_and_rain)


# --- Rule checkers ---
def water_moisturize(world, registry):
    for x, y in registry.iter_positions("water"):
        for nx, ny in world.get_neighbors4(x, y):
            world.add_moisture(nx, ny, 0.02 * getattr(world, "time_scale", 1.0))


def water_phase(world, registry):
    ambient = getattr(world, "ambient_temperature", 20.0)
    ice = registry.get_by_key("ice")
    steam = registry.get_by_key("steam")
    for x, y in registry.iter_positions("water"):
        if ambient <= 0.0 and ice and random.random() < 0.01 * getattr(world, "time_scale", 1.0):
            world.set_item(x, y, ice.id)
        elif ambient >= 80.0 and steam and random.random() < 0.01 * getattr(world, "time_scale", 1.0):
            world.set_item(x, y, steam.id)


def mud_drying_baking(world, registry):
    dirt = registry.get_by_key("dirt")
    clay = registry.get_by_key("clay")
    for x, y in registry.iter_positions("mud"):
        cell = world.get_cell(x, y)
        if not cell:
            continue
        cell.moisture = max(0.0, cell.moisture - 0.005 * getattr(world, "time_scale", 1.0))
        if clay and cell.temperature >= 100.0 and cell.moisture <= 0.2:
            world.set_item(x, y, clay.id)
        elif dirt and cell.moisture < 0.4:
            world.set_item(x, y, dirt.id)


def check_water_touch_dirt(world, registry):
    mud = registry.get_by_key("mud")
    if not mud:
        return
    for x, y in registry.iter_positions("dirt"):
        for nx, ny in world.get_neighbors4(x, y):
            ncell = world.get_cell(nx, ny)
            if not ncell:
                continue
            wid = world.get_item_id("water")
            if ncell.item_id == wid:
                world.set_item(x, y, mud.id)
                break


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


def clear_non_dirt_overrides(world, registry):
    # Remove any lingering pattern/palette overrides from cells that are no longer dirt
    for idef in registry.all_items():
        if idef.key in ("dirt", "cloud"):
            continue
        for x, y in registry.iter_positions(idef.key):
            cell = world.get_cell(x, y)
            if not cell:
                continue
            # Only clear if previously set
            if "pattern_override" in cell.meta or "palette_override" in cell.meta:
                cell.meta.pop("pattern_override", None)
                cell.meta.pop("palette_override", None)


def _grow_tree(world, registry, x: int, y: int, trunk_id: int, leaves_id: int, height: int, layers):
    # Ensure trunk space upwards is clear (allow current seed position only)
    for k in range(0, height):
        ny = y - k
        if ny < 0:
            return False
        c = world.get_cell(x, ny)
        if c and c.item_id != 0 and k != 0:
            return False
    # Ensure leaves space is clear
    top_y = y - height
    for radius, off in layers:
        ly = top_y + off
        if ly < 0 or ly >= world.height:
            return False
        for dx in range(-radius, radius + 1):
            nx = x + dx
            if not (0 <= nx < world.width):
                return False
            c = world.get_cell(nx, ly)
            if c and c.item_id != 0:
                return False
    # Build trunk
    for k in range(0, height):
        ny = y - k
        if 0 <= ny < world.height:
            world.set_item(x, ny, trunk_id)
    # Leaves layers
    top_y = y - height
    for radius, off in layers:
        ly = top_y + off
        if ly < 0 or ly >= world.height:
            continue
        for dx in range(-radius, radius + 1):
            nx = x + dx
            if 0 <= nx < world.width:
                c = world.get_cell(nx, ly)
                if c and c.item_id == 0:
                    world.set_item(nx, ly, leaves_id)
    return True


def plant_seeds(world, registry):
    dirt_id = world.get_item_id("dirt")
    if not dirt_id:
        return
    specs = [
        {"seed": "seed", "trunk": "wood", "leaves": "leaves", "height": 7, "layers": [(1,0),(2,1),(3,2),(2,3)]},
        {"seed": "seed_oak", "trunk": "wood_oak", "leaves": "leaves_oak", "height": 6, "layers": [(2,0),(3,1),(3,2),(2,3)]},
        {"seed": "seed_birch", "trunk": "wood_birch", "leaves": "leaves_birch", "height": 8, "layers": [(1,0),(2,1),(2,2),(1,3)]},
        {"seed": "seed_cherry", "trunk": "wood_cherry", "leaves": "leaves_cherry", "height": 5, "layers": [(2,0),(2,1),(1,2)]},
    ]
    for spec in specs:
        sk = registry.get_by_key(spec["seed"])
        tk = registry.get_by_key(spec["trunk"])
        lk = registry.get_by_key(spec["leaves"])
        if not (sk and tk and lk):
            continue
        for x, y in tuple(registry.iter_positions(spec["seed"])):
            below = world.get_cell(x, y + 1)
            # If still airborne, skip this tick
            if below and below.item_id == 0:
                continue
            # If settled on non-dirt, the seed disappears
            if (not below) or below.item_id != dirt_id:
                world.set_item(x, y, 0)
                continue
            # Settled on dirt: attempt to grow, else disappear
            ok = _grow_tree(world, registry, x, y, tk.id, lk.id, spec["height"], spec["layers"])
            if ok:
                world.set_item(x, y, tk.id)
            else:
                world.set_item(x, y, 0)


def update_steam_clouds_and_rain(world, registry):
    # Bundle steam into clouds near upper half, darken with density, and rain
    steam = registry.get_by_key("steam")
    cloud = registry.get_by_key("cloud")
    water = registry.get_by_key("water")
    if not (steam and cloud and water):
        return
    # Step 1: convert dense steam to cloud (upper half bias)
    for x, y in tuple(registry.iter_positions("steam")):
        if y > world.height // 2:
            continue
        # Count adjacent steam
        count = 0
        for nx, ny in world.get_neighbors8(x, y):
            c = world.get_cell(nx, ny)
            if c and c.item_id == steam.id:
                count += 1
        if count >= 3:
            world.set_item(x, y, cloud.id)
    # Step 2: compute cloud darkness by local density and set overrides
    CELL = 8
    base_pal = getattr(cloud.behavior, "palette", [(220,222,230),(180,185,200),(135,140,160),(95,100,120)])
    for x, y in tuple(registry.iter_positions("cloud")):
        # local density within 8-neighborhood + self
        dens = 1
        for nx, ny in world.get_neighbors8(x, y):
            c = world.get_cell(nx, ny)
            if c and c.item_id == cloud.id:
                dens += 1
        # Map density [1..9] to 0..3 index
        if dens >= 8:
            idx = 3
        elif dens >= 6:
            idx = 2
        elif dens >= 4:
            idx = 1
        else:
            idx = 0
        # Compose a filled pattern of idx
        pat = [[idx for _ in range(CELL)] for _ in range(CELL)]
        cell = world.get_cell(x, y)
        if cell:
            cell.meta["pattern_override"] = pat
            cell.meta["palette_override"] = list(base_pal)
        # Step 3: rain from dark clouds
        if idx >= 3:
            import random
            if random.random() < 0.02 * getattr(world, "time_scale", 1.0):
                bx, by = x, y
                if 0 <= bx < world.width and 0 <= by < world.height:
                    below = world.get_cell(bx, by)
                    if below:
                        world.set_item(bx, by, water.id)
                        # consume part of cloud (convert cell to steam to lighten)
                        world.set_item(x, y, steam.id)
