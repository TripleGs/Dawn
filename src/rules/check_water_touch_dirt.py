from __future__ import annotations


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
