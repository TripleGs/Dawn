from __future__ import annotations

from .check_water_touch_dirt import check_water_touch_dirt
from .clear_non_dirt_overrides import clear_non_dirt_overrides
from .mud_drying_baking import mud_drying_baking
from .plant_seeds import plant_seeds
from .update_dirt_exposure_overlay import update_dirt_exposure_overlay
from .update_steam_clouds_and_rain import update_steam_clouds_and_rain
from .water_moisturize import water_moisturize
from .water_phase import water_phase

RULE_CHECKERS = [
    water_moisturize,
    water_phase,
    mud_drying_baking,
    check_water_touch_dirt,
    clear_non_dirt_overrides,
    update_dirt_exposure_overlay,
    plant_seeds,
    update_steam_clouds_and_rain,
]

__all__ = ["RULE_CHECKERS"]
