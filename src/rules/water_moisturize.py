from __future__ import annotations


def water_moisturize(world, registry):
    for x, y in registry.iter_positions("water"):
        for nx, ny in world.get_neighbors4(x, y):
            world.add_moisture(nx, ny, 0.02 * getattr(world, "time_scale", 1.0))
