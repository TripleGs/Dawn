from __future__ import annotations

import random


def water_phase(world, registry):
    ambient = getattr(world, "ambient_temperature", 20.0)
    ice = registry.get_by_key("ice")
    steam = registry.get_by_key("steam")
    for x, y in registry.iter_positions("water"):
        if ambient <= 0.0 and ice and random.random() < 0.01 * getattr(world, "time_scale", 1.0):
            world.set_item(x, y, ice.id)
        elif ambient >= 80.0 and steam and random.random() < 0.01 * getattr(world, "time_scale", 1.0):
            world.set_item(x, y, steam.id)
