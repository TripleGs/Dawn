from __future__ import annotations


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
