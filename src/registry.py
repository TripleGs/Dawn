from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, List, Optional, Set, Tuple, Iterable


@dataclass
class ItemDefinition:
    id: int
    key: str
    behavior: object


class Registry:
    """Unified registry for materials (blocks) and rule/checker functions."""

    def __init__(self) -> None:
        self._items_by_key: Dict[str, ItemDefinition] = {}
        self._items: List[ItemDefinition] = []
        self._checkers: List[Callable[[object, "Registry"], None]] = []
        # Track positions of each item id for efficient rule checks
        self._positions_by_id: Dict[int, Set[Tuple[int, int]]] = {}

    # --- Materials API ---
    def register(self, key: str, behavior: object) -> int:
        if key in self._items_by_key:
            return self._items_by_key[key].id
        new_id = len(self._items) + 1  # 0 is empty
        definition = ItemDefinition(id=new_id, key=key, behavior=behavior)
        self._items.append(definition)
        self._items_by_key[key] = definition
        self._positions_by_id[new_id] = set()
        return new_id

    def get_by_id(self, item_id: int) -> Optional[ItemDefinition]:
        if item_id <= 0 or item_id > len(self._items):
            return None
        return self._items[item_id - 1]

    def get_by_key(self, key: str) -> Optional[ItemDefinition]:
        return self._items_by_key.get(key)

    def all_items(self) -> List[ItemDefinition]:
        return list(self._items)

    # --- Rules/Checkers API ---
    def add_checker(self, fn: Callable[[object, "Registry"], None]) -> None:
        self._checkers.append(fn)

    def add_checkers(self, fns: List[Callable[[object, "Registry"], None]]) -> None:
        for fn in fns:
            self.add_checker(fn)

    def apply(self, world) -> None:
        # Run all registered checker functions
        for fn in self._checkers:
            fn(world, self)

    # --- World integration: position tracking ---
    def on_set(self, x: int, y: int, old_id: int, new_id: int) -> None:
        if old_id in self._positions_by_id:
            self._positions_by_id[old_id].discard((x, y))
        if new_id in self._positions_by_id:
            self._positions_by_id[new_id].add((x, y))

    def on_swap(self, ax: int, ay: int, a_id_before: int, bx: int, by: int, b_id_before: int) -> None:
        # After swap, a_id_before is now at (bx, by); b_id_before at (ax, ay)
        if a_id_before in self._positions_by_id:
            self._positions_by_id[a_id_before].discard((ax, ay))
            self._positions_by_id[a_id_before].add((bx, by))
        if b_id_before in self._positions_by_id:
            self._positions_by_id[b_id_before].discard((bx, by))
            self._positions_by_id[b_id_before].add((ax, ay))

    # --- Query helpers for rules ---
    def iter_positions(self, key: str) -> Iterable[Tuple[int, int]]:
        idef = self.get_by_key(key)
        if not idef:
            return []
        return tuple(self._positions_by_id.get(idef.id, set()))


