from __future__ import annotations


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
        {"seed": "seed", "trunk": "wood", "leaves": "leaves", "height": 7, "layers": [(1, 0), (2, 1), (3, 2), (2, 3)]},
        {"seed": "seed_oak", "trunk": "wood_oak", "leaves": "leaves_oak", "height": 6, "layers": [(2, 0), (3, 1), (3, 2), (2, 3)]},
        {"seed": "seed_birch", "trunk": "wood_birch", "leaves": "leaves_birch", "height": 8, "layers": [(1, 0), (2, 1), (2, 2), (1, 3)]},
        {"seed": "seed_cherry", "trunk": "wood_cherry", "leaves": "leaves_cherry", "height": 5, "layers": [(2, 0), (2, 1), (1, 2)]},
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
