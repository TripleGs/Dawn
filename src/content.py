from __future__ import annotations

from src.materials import Gas, Liquid, Solid
from src.materials.defs import MATERIAL_SPECS
from src.rules import RULE_CHECKERS


def register_all(registry) -> None:
    for spec in MATERIAL_SPECS:
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

    registry.add_checkers(RULE_CHECKERS)
