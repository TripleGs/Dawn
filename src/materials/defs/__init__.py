from __future__ import annotations

from .dirt import SPEC as DIRT
from .water import SPEC as WATER
from .mud import SPEC as MUD
from .snow import SPEC as SNOW
from .ice import SPEC as ICE
from .steam import SPEC as STEAM
from .cloud import SPEC as CLOUD
from .clay import SPEC as CLAY
from .grass import SPEC as GRASS
from .sand import SPEC as SAND
from .rock import SPEC as ROCK
from .seed import SPEC as SEED
from .wood import SPEC as WOOD
from .leaves import SPEC as LEAVES
from .seed_oak import SPEC as SEED_OAK
from .wood_oak import SPEC as WOOD_OAK
from .leaves_oak import SPEC as LEAVES_OAK
from .seed_birch import SPEC as SEED_BIRCH
from .wood_birch import SPEC as WOOD_BIRCH
from .leaves_birch import SPEC as LEAVES_BIRCH
from .seed_cherry import SPEC as SEED_CHERRY
from .wood_cherry import SPEC as WOOD_CHERRY
from .leaves_cherry import SPEC as LEAVES_CHERRY

MATERIAL_SPECS = [
    DIRT,
    WATER,
    MUD,
    SNOW,
    ICE,
    STEAM,
    CLOUD,
    CLAY,
    GRASS,
    SAND,
    ROCK,
    SEED,
    WOOD,
    LEAVES,
    SEED_OAK,
    WOOD_OAK,
    LEAVES_OAK,
    SEED_BIRCH,
    WOOD_BIRCH,
    LEAVES_BIRCH,
    SEED_CHERRY,
    WOOD_CHERRY,
    LEAVES_CHERRY,
]

__all__ = ["MATERIAL_SPECS"]
