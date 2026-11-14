import json
from server.application.commands.dispatcher import register_command
from server.domain.entities import CommandContext
from server.application.queries.game_config_query import config_service
from server.domain.engine import (
    map_add_item,
    map_get_item,
    map_delete_item,
    push_dead_unit,
    bought_unit_add
)


@register_command("buy")
def handle_buy(ctx: CommandContext) -> None:
    item_index = ctx.args[0]
    item_id = ctx.args[1]
    x = ctx.args[2]
    y = ctx.args[3]
    player_id = ctx.args[4]
    orientation = ctx.args[5]

    if player_id == 1:
        bought_unit_add(ctx.save, item_id)

    map_add_item(ctx.current_map, item_index, item_id, x, y, orientation=orientation, player=player_id)
    name = config_service.get_name_from_item_id(item_id)
    print(f"Add {name} at ({x},{y})")


@register_command("move")
def handle_move(ctx: CommandContext) -> None:
    item_index = ctx.args[0]
    x = ctx.args[1]
    y = ctx.args[2]

    item = map_get_item(ctx.current_map, item_index)
    if not item:
        print("[handle_move] Error: item not found.")
        return

    item[1] = x
    item[2] = y
    name = config_service.get_name_from_item_id(item[0])
    print(f"Move {name} to ({x},{y})")


@register_command("sell")
def handle_sell(ctx: CommandContext) -> None:
    item_index = ctx.args[0]
    reason = ctx.args[1] if len(ctx.args) > 1 else ""

    item = map_get_item(ctx.current_map, item_index)
    if not item:
        print("[handle_sell] Error: item not found.")
        return

    resurrectable = False
    if reason == "KILL":
        resurrectable = push_dead_unit(ctx.private_state, item)
    name = config_service.get_name_from_item_id(item[0])
    map_delete_item(ctx.current_map, item_index)

    tag = " (Resurrectable)" if resurrectable else ""
    print(f"Remove {name}{tag}. Reason: {reason}")


@register_command("kill")
def handle_kill(ctx: CommandContext) -> None:
    item_index = ctx.args[0]
    reason = ctx.args[1] if len(ctx.args) > 1 else ""

    item = map_get_item(ctx.current_map, item_index)
    if not item:
        print("[handle_kill] Error: item not found.")
        return

    name = config_service.get_name_from_item_id(item[0])
    map_delete_item(ctx.current_map, item_index)
    print(f"Kill {name}. Reason: {reason}")


@register_command("kill_iid")
def handle_kill_iid(ctx: CommandContext) -> None:
    item_id = ctx.args[0]
    name = config_service.get_name_from_item_id(item_id)
    print(f"Killed {name}")


@register_command("batch_remove")
def handle_batch_remove(ctx: CommandContext) -> None:
    index_list = json.loads(ctx.args[0])
    for idx in index_list:
        map_delete_item(ctx.current_map, idx)
    print(f"Removed {len(index_list)} items.")


@register_command("orient")
def handle_orient(ctx: CommandContext) -> None:
    item_index = ctx.args[0]
    orientation = ctx.args[1]

    item = map_get_item(ctx.current_map, item_index)
    if not item:
        print("[handle_orient] Error: item not found.")
        return

    item[4] = int(orientation)
    name = config_service.get_name_from_item_id(item[0])
    print(f"Rotate {name}")


@register_command("expand")
def handle_expand(ctx: CommandContext) -> None:
    expansion = int(ctx.args[0])
    expansions = ctx.current_map.setdefault("expansions", [])
    expansions.append(expansion)
    print(f"Unlocked Expansion {expansion}")
