import json
from math import ceil
from server.application.commands.dispatcher import register_command
from server.domain.entities import CommandContext
from server.application.queries.game_config_query import config_service
from server.domain.engine import (
    timestamp_now,
    map_get_item,
    map_pop_item,
    map_add_item,
    map_add_item_from_item,
    push_unit,
    pop_unit,
    push_queue_unit,
    push_queue_unit2,
    pop_queue_unit,
    resurrect_hero,
    map_lose_item
)


@register_command("push_unit")
def handle_push_unit(ctx: CommandContext) -> None:
    index_unit = ctx.args[0]
    index_building = ctx.args[1]

    unit = map_pop_item(ctx.current_map, index_unit)
    building = map_get_item(ctx.current_map, index_building)

    if not unit:
        print("[handle_push_unit] Error: unit not found.")
        return
    if not building:
        print("[handle_push_unit] Error: building not found.")
        return

    push_unit(unit, building)
    u_name = config_service.get_name_from_item_id(unit[0])
    b_name = config_service.get_name_from_item_id(building[0])
    print(f"Pushed {u_name} to {b_name}")


@register_command("pop_unit")
def handle_pop_unit(ctx: CommandContext) -> None:
    index_building = ctx.args[0]
    index_unit = ctx.args[1]
    item_id = ctx.args[2]
    x = ctx.args[3]
    y = ctx.args[4]
    player_id = ctx.args[5]

    building = map_get_item(ctx.current_map, index_building)
    if not building:
        print("[handle_pop_unit] Error: building not found.")
        return

    unit = pop_unit(building, item_id)
    if not unit:
        print("[handle_pop_unit] Error: no units in building.")
        return

    unit[0] = item_id
    unit[1] = x
    unit[2] = y
    unit[7] = player_id

    map_add_item_from_item(ctx.current_map, index_unit, unit)
    u_name = config_service.get_name_from_item_id(unit[0])
    b_name = config_service.get_name_from_item_id(building[0])
    print(f"Popped {u_name} from {b_name}")


@register_command("push_queue_unit")
def handle_push_queue_unit(ctx: CommandContext) -> None:
    index = ctx.args[0]
    item = map_get_item(ctx.current_map, index)
    if not item:
        print("[handle_push_queue_unit] Error: item not found.")
        return
    push_queue_unit(item)
    print("Pushed unit.")


@register_command("push_queue_unit2")
def handle_push_queue_unit2(ctx: CommandContext) -> None:
    atom_fusion_index = ctx.args[0]
    unit_id = ctx.args[1]

    atom_fusion = map_get_item(ctx.current_map, atom_fusion_index)
    if not atom_fusion:
        print("[handle_push_queue_unit2] Error: Atom Fusion not found.")
        return

    push_queue_unit2(atom_fusion, unit_id)
    name = config_service.get_name_from_item_id(unit_id)
    print(f"Pushed {name} to Atom Fusion.")


@register_command("pop_queue_unit")
def handle_pop_queue_unit(ctx: CommandContext) -> None:
    index = ctx.args[0]
    item = map_get_item(ctx.current_map, index)
    if not item:
        print("[handle_pop_queue_unit] Error: item not found.")
        return
    pop_queue_unit(item)
    print("Popped unit.")


@register_command("add_xp_unit")
def handle_add_xp_unit(ctx: CommandContext) -> None:
    item_index = ctx.args[0]
    xp_gain = ctx.args[1]
    level = ctx.args[2] if len(ctx.args) > 2 else None

    item = map_get_item(ctx.current_map, item_index)
    if not item:
        print("[handle_add_xp_unit] Error: item not found.")
        return

    attr = item[6]
    attr["xp"] = attr.get("xp", 0) + xp_gain
    name = config_service.get_name_from_item_id(item[0])

    if level:
        print(f"{name} +{xp_gain}xp BOUGHT LEVEL UP -> {level}")
    else:
        print(f"{name} +{xp_gain}xp")


@register_command("resurrect_hero")
def handle_resurrect_hero(ctx: CommandContext) -> None:
    index = ctx.args[0]
    item_id = ctx.args[1]
    x = ctx.args[2]
    y = ctx.args[3]

    resurrect_hero(ctx.private_state, item_id)
    map_add_item(ctx.current_map, index, item_id, x, y)
    name = config_service.get_name_from_item_id(item_id)
    print(f"Resurrected {name}")


@register_command("end_attack")
def handle_end_attack(ctx: CommandContext) -> None:
    try:
        response = json.loads(ctx.args[0])
    except Exception:
        print("[handle_end_attack] Error: Failed to parse attack response.")
        return

    attacker_units = response.get("attacker_units", [])
    for unit in attacker_units:
        lost = max(0, unit[2] - unit[3])
        if lost > 0:
            name = config_service.get_name_from_item_id(unit[0])
            print(f"Lost {lost} {name}(s)")
            map_lose_item(ctx.current_map, ctx.private_state, unit[0], lost)

    win = response.get("win", False)
    victim_name = response.get("victim", {}).get("name") if isinstance(response.get("victim"), dict) else None
    if victim_name:
        status = "Won" if win else "Lost"
        print(f"{status} battle against {victim_name}")
    else:
        status = "Won" if win else "Lost"
        print(f"{status} battle")


@register_command("soulmixer_speedup")
def handle_soulmixer_speedup(ctx: CommandContext) -> None:
    atom_fusion_index = ctx.args[0]
    atom_fusion = map_get_item(ctx.current_map, atom_fusion_index)
    if not atom_fusion:
        print("[handle_soulmixer_speedup] Error: Atom Fusion not found.")
        return

    attr = atom_fusion[6]
    start = attr.get("ts", 0)
    now = timestamp_now()
    sm_training_time = int(config_service.get_attribute_from_item_id(attr.get("ui", 0), "sm_training_time") or 0)

    remaining_time = max(0, sm_training_time - (now - start))
    cash_cost = ceil(remaining_time / 3600)
    attr["ts"] = 0

    unit_name = config_service.get_name_from_item_id(attr.get("ui", 0))
    print(f"Buy Atom Fusion Speedup for {unit_name}. Cost: {cash_cost} cash.")


@register_command("rt_open_graph_unit")
def handle_rt_open_graph_unit(ctx: CommandContext) -> None:
    item = ctx.args[0]
    published = ctx.private_state.setdefault("publishedOpenGraphUnit", [])
    if not isinstance(published, list):
        published = ctx.private_state["publishedOpenGraphUnit"] = []
    if str(item) not in published:
        published.append(str(item))

    name = config_service.get_name_from_item_id(item)
    print(f"Open Unit Graph for {name}")
