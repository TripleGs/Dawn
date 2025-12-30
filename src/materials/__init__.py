from __future__ import annotations

from typing import Tuple


Color = Tuple[int, int, int]


class BaseBehavior:
    def __init__(
        self,
        key: str | None = None,
        *,
        id: str | None = None,
        display_name: str | None = None,
        color: Color = (255, 255, 255),
        is_solid: bool = True,
        density: float = 1.0,
        palette: list[Color] | None = None,
        pattern: list[list[int]] | None = None,
        support_required_neighbors: int | None = None,
    ) -> None:
        k = key or id
        if not k:
            raise ValueError("A non-empty key/id is required for a material")
        self._key = k
        self._display_name = display_name or k.capitalize()
        self._color = color
        self._is_solid = is_solid
        self._density = float(density)
        self._palette = palette
        self._pattern = pattern
        self._support_required_neighbors = support_required_neighbors

    @property
    def name(self) -> str:
        return self._key

    @property
    def display_name(self) -> str:
        return self._display_name

    @property
    def color(self) -> Color:
        return self._color

    @property
    def is_solid(self) -> bool:
        return self._is_solid

    @property
    def density(self) -> float:
        return self._density

    def on_place(self, world, x: int, y: int, cell) -> None:
        return None

    def update(self, world, x: int, y: int, cell) -> None:
        return None

    @property
    def palette(self) -> list[Color] | None:
        return self._palette

    @property
    def pattern(self) -> list[list[int]] | None:
        return self._pattern

    @property
    def support_required_neighbors(self) -> int | None:
        return self._support_required_neighbors


class Solid(BaseBehavior):
    def __init__(
        self,
        key: str | None = None,
        *,
        id: str | None = None,
        display_name: str | None = None,
        color: Color = (200, 200, 200),
        density: float = 1.0,
        palette: list[Color] | None = None,
        pattern: list[list[int]] | None = None,
        support_required_neighbors: int | None = None,
    ) -> None:
        super().__init__(key, id=id, display_name=display_name, color=color, is_solid=True, density=density, palette=palette, pattern=pattern, support_required_neighbors=support_required_neighbors)


class Liquid(BaseBehavior):
    def __init__(
        self,
        key: str | None = None,
        *,
        id: str | None = None,
        display_name: str | None = None,
        color: Color = (120, 120, 255),
        density: float = 0.5,
        palette: list[Color] | None = None,
        pattern: list[list[int]] | None = None,
    ) -> None:
        super().__init__(key, id=id, display_name=display_name, color=color, is_solid=False, density=density, palette=palette, pattern=pattern)


class Gas(BaseBehavior):
    def __init__(
        self,
        key: str | None = None,
        *,
        id: str | None = None,
        display_name: str | None = None,
        color: Color = (200, 200, 255),
        density: float = 0.1,
        palette: list[Color] | None = None,
        pattern: list[list[int]] | None = None,
    ) -> None:
        super().__init__(key, id=id, display_name=display_name, color=color, is_solid=False, density=density, palette=palette, pattern=pattern)


