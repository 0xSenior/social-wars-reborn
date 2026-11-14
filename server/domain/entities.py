from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional


@dataclass
class BuildingItem:
    index: str
    item_id: int
    x: int
    y: int
    timestamp: int
    orientation: int = 0
    store: List[Any] = field(default_factory=list)
    attr: Dict[str, Any] = field(default_factory=dict)
    player: int = 1

    @classmethod
    def from_list(cls, index: str, data: list) -> 'BuildingItem':
        return cls(
            index=str(index),
            item_id=data[0],
            x=data[1],
            y=data[2],
            timestamp=data[3],
            orientation=data[4] if len(data) > 4 else 0,
            store=data[5] if len(data) > 5 and data[5] is not None else [],
            attr=data[6] if len(data) > 6 and data[6] is not None else {},
            player=data[7] if len(data) > 7 else 1
        )

    def to_list(self) -> list:
        return [
            self.item_id,
            self.x,
            self.y,
            self.timestamp,
            self.orientation,
            self.store,
            self.attr,
            self.player
        ]


@dataclass
class MapState:
    town_id: int
    items: Dict[str, Any]
    xp: int = 0
    gold: int = 0
    wood: int = 0
    oil: int = 0
    steel: int = 0
    store: Dict[str, int] = field(default_factory=dict)
    timestamp: int = 0
    numTradesDone: int = 0
    timestampLastTrade: int = 0


@dataclass
class PlayerProfile:
    pid: str
    name: str
    level: int = 1
    cash: int = 0
    last_logged_in: int = 0


@dataclass
class GameState:
    player_info: Dict[str, Any]
    maps: List[Dict[str, Any]]
    private_state: Dict[str, Any]


@dataclass
class CommandContext:
    save: Dict[str, Any]
    cmd: str
    args: List[Any]
    town_id: int = 0

    @property
    def current_map(self) -> Dict[str, Any]:
        return self.save["maps"][self.town_id]

    @property
    def private_state(self) -> Dict[str, Any]:
        return self.save["privateState"]

    @property
    def player_info(self) -> Dict[str, Any]:
        return self.save["playerInfo"]
