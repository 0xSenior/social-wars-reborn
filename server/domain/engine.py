import time
import json
from typing import Dict, Any, Optional, List


def _get_item_attr(item_id: int, attr: str) -> Any:
    from server.application.queries.game_config_query import config_service
    return config_service.get_attribute_from_item_id(item_id, attr)


def timestamp_now() -> int:
    return int(time.time())



def map_add_item(
    game_map: dict,
    index: int,
    item: int,
    x: int,
    y: int,
    orientation: int = 0,
    timestamp: Optional[int] = None,
    attr: Optional[dict] = None,
    store: Optional[list] = None,
    player: int = 1
) -> None:
    if attr is None:
        attr = {}
    if store is None:
        store = []
    if timestamp is None:
        timestamp = timestamp_now()

    if player == 1:
        properties = _get_item_attr(item, "properties")
        if properties:
            try:
                props = json.loads(properties)
                if "friend_assistable" in props and int(props["friend_assistable"]) > 0:
                    attr["si"] = []
            except Exception:
                pass
        click_to_build = _get_item_attr(item, "clicks_to_build")
        if click_to_build and int(click_to_build) > 0:
            attr["nc"] = 0

    game_map["items"][str(index)] = [item, x, y, timestamp, orientation, store, attr, player]


def map_add_item_from_item(game_map: dict, index: int, item: list) -> None:
    game_map["items"][str(index)] = item


def map_get_item(game_map: dict, index: int) -> Optional[list]:
    return game_map["items"].get(str(index))


def map_pop_item(game_map: dict, index: int) -> Optional[list]:
    return game_map["items"].pop(str(index), None)


def map_delete_item(game_map: dict, index: int) -> None:
    game_map["items"].pop(str(index), None)


def push_unit(unit: Any, building: list) -> None:
    building[5].append(unit)
    building[3] = timestamp_now()


def pop_unit(building: list, item_id: int) -> Optional[Any]:
    for idx, item in enumerate(building[5]):
        if item[0] == item_id:
            return building[5].pop(idx)
    return None


def add_store_item(game_map: dict, item: int, quantity: int = 1) -> None:
    item_str = str(item)
    game_map["store"][item_str] = game_map["store"].get(item_str, 0) + quantity


def remove_store_item(game_map: dict, item: int, quantity: int = 1) -> None:
    item_str = str(item)
    if item_str in game_map["store"]:
        new_quantity = game_map["store"][item_str] - quantity
        if new_quantity <= 0:
            game_map["store"].pop(item_str, None)
        else:
            game_map["store"][item_str] = new_quantity


def bought_unit_add(save: dict, item: int) -> None:
    bought_units = save["privateState"].setdefault("boughtUnits", [])
    if item not in bought_units:
        bought_units.append(item)


def unit_collection_complete(save: dict, collection: int) -> None:
    completed = save["privateState"].setdefault("unitCollectionsCompleted", [])
    if collection not in completed:
        completed.append(collection)


def set_goals(private_state: dict, goal: int, progress: list) -> None:
    goals = private_state.setdefault("goals", [])
    while goal >= len(goals):
        goals.append(None)
    goals[goal] = progress


def complete_goal(private_state: dict, goal: int) -> None:
    goals = private_state.setdefault("goals", [])
    while goal >= len(goals):
        goals.append(None)
    goals[goal] = -1


def inventory_set(private_state: dict, item: int, quantity: int) -> None:
    item_str = str(item)
    inv = private_state.setdefault("inventoryItems", {})
    if quantity > 0:
        inv[item_str] = quantity
    else:
        inv.pop(item_str, None)


def inventory_add(private_state: dict, item: int, quantity: int) -> None:
    item_str = str(item)
    inv = private_state.setdefault("inventoryItems", {})
    inv[item_str] = inv.get(item_str, 0) + quantity


def inventory_remove(private_state: dict, item: int, quantity: int) -> None:
    item_str = str(item)
    inv = private_state.setdefault("inventoryItems", {})
    if item_str in inv:
        new_quantity = inv[item_str] - quantity
        if new_quantity <= 0:
            inv.pop(item_str, None)
        else:
            inv[item_str] = new_quantity


def add_click(item: list) -> None:
    attr = item[6]
    attr["nc"] = attr.get("nc", 0) + 1


def activate_item_click(item: list) -> None:
    item[6].pop("nc", None)


def buy_si_help(item: list) -> None:
    attr = item[6]
    if "si" not in attr or not isinstance(attr["si"], list):
        attr["si"] = [0]
    else:
        attr["si"].append(0)


def finish_si(item: list) -> None:
    item[6].pop("si", None)


def push_dead_unit(private_state: dict, item: list) -> bool:
    if item[7] != 1:
        return False
    properties = _get_item_attr(item[0], "properties")
    if not properties:
        return False
    try:
        props = json.loads(properties)
        if int(props.get("resurrectable", 0)) > 0:
            dead_heroes = private_state.setdefault("deadHeroes", {})
            item_str = str(item[0])
            dead_heroes[item_str] = dead_heroes.get(item_str, 0) + 1
            return True
    except Exception:
        pass
    return False


def resurrect_hero(private_state: dict, item: int) -> None:
    dead_heroes = private_state.setdefault("deadHeroes", {})
    item_str = str(item)
    if item_str in dead_heroes:
        remaining = dead_heroes[item_str] - 1
        if remaining <= 0:
            dead_heroes.pop(item_str, None)
        else:
            dead_heroes[item_str] = remaining


def push_queue_unit(item: list) -> None:
    attr = item[6]
    attr["nu"] = attr.get("nu", 0) + 1
    attr["ts"] = timestamp_now()


def push_queue_unit2(item: list, unit_id: int) -> None:
    attr = item[6]
    attr["nu"] = attr.get("nu", 0) + 1
    attr["ts"] = timestamp_now()
    attr["ui"] = unit_id


def pop_queue_unit(item: list) -> None:
    attr = item[6]
    if "nu" not in attr:
        return
    nu = attr["nu"] - 1
    if nu > 0:
        attr["nu"] = nu
        attr["ts"] = timestamp_now()
    else:
        attr.pop("nu", None)
        attr.pop("ts", None)
        attr.pop("ui", None)


def map_lose_item(game_map: dict, private_state: dict, item: int, quantity: int) -> None:
    qty = quantity
    map_items = game_map["items"]
    while qty > 0:
        deleted = False
        for idx in list(map_items.keys()):
            if map_items[idx][0] == item and map_items[idx][7]:
                lost_item = map_pop_item(game_map, idx)
                if lost_item:
                    push_dead_unit(private_state, lost_item)
                deleted = True
                break
        if not deleted:
            return
        qty -= 1


def reset_stuff(save: dict) -> None:
    now = timestamp_now()
    for m in save.get("maps", []):
        last_trade = m.get("timestampLastTrade", 0)
        if now // 86400 != last_trade // 86400:
            m["numTradesDone"] = 0

    private_state = save.get("privateState", {})
    if "timeStampDartsReset" in private_state:
        last_darts_reset = private_state["timeStampDartsReset"] + 259200
        temp = now + 259200
        if temp // 604800 != last_darts_reset // 604800:
            private_state["timeStampDartsReset"] = 0


def apply_resources(save: dict, game_map: dict, resource: list) -> None:
    _unknown = resource[0]
    xp = resource[1]
    gold = resource[2]
    wood = resource[3]
    oil = resource[4]
    steel = resource[5]
    cash = resource[6]
    mana = resource[7]

    game_map["xp"] = max(game_map.get("xp", 0) + xp, 0)
    game_map["gold"] = max(game_map.get("gold", 0) + gold, 0)
    game_map["wood"] = max(game_map.get("wood", 0) + wood, 0)
    game_map["oil"] = max(game_map.get("oil", 0) + oil, 0)
    game_map["steel"] = max(game_map.get("steel", 0) + steel, 0)
    save["playerInfo"]["cash"] = max(save["playerInfo"].get("cash", 0) + cash, 0)
    save["privateState"]["mana"] = max(save["privateState"].get("mana", 0) + mana, 0)
