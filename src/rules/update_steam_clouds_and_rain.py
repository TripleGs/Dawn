from __future__ import annotations


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
    base_pal = getattr(cloud.behavior, "palette", [(220, 222, 230), (180, 185, 200), (135, 140, 160), (95, 100, 120)])
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
