from __future__ import annotations


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
