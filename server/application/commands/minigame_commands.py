import json
from server.application.commands.dispatcher import register_command
from server.domain.entities import CommandContext
from server.application.queries.game_config_query import config_service
from server.domain.engine import (
    timestamp_now,
    map_get_item,
    add_store_item,
    add_click,
    activate_item_click,
    buy_si_help,
    finish_si
)


@register_command("darts_reset")
def handle_darts_reset(ctx: CommandContext) -> None:
    seed = ctx.args[0]
    time_now = timestamp_now()
    ctx.private_state["dartsRandomSeed"] = seed
    ctx.private_state["dartsBalloonsShot"] = []
    ctx.private_state["dartsHasFree"] = True
    ctx.private_state["dartsGotExtra"] = False
    ctx.private_state["timeStampDartsReset"] = time_now
    ctx.private_state["timeStampDartsNewFree"] = time_now
    print(f"Reset Targets (SEED: {seed})")


@register_command("darts_new_free")
def handle_darts_new_free(ctx: CommandContext) -> None:
    time_now = timestamp_now()
    ctx.private_state["dartsHasFree"] = True
    ctx.private_state["timeStampDartsNewFree"] = time_now
    print("Given free Targets shot")


@register_command("darts_shoot_balloon")
def handle_darts_shoot_balloon(ctx: CommandContext) -> None:
    index = ctx.args[0]
    won_extra = ctx.args[1]
    time_now = timestamp_now()

    targets = ctx.private_state.setdefault("dartsBalloonsShot", [])
    if index not in targets:
        targets.append(index)

    ctx.private_state["dartsHasFree"] = False
    ctx.private_state["timeStampDartsNewFree"] = time_now
    if won_extra:
        ctx.private_state["dartsGotExtra"] = True
        print(f"Shot Target {index} and won the game!")
    else:
        print(f"Shot Target {index}")


@register_command("buy_offer_pack")
def handle_buy_offer_pack(ctx: CommandContext) -> None:
    _package_id = ctx.args[0]
    item_list = ctx.args[1]
    items = json.loads(item_list)
    for item in items:
        add_store_item(ctx.current_map, item)
    print("Bought Offer Pack")


@register_command("buy_powerups")
def handle_buy_powerups(ctx: CommandContext) -> None:
    _powerup_index = ctx.args[0]
    print("Buy Atom Fusion PowerUP")


@register_command("add_click")
def handle_add_click(ctx: CommandContext) -> None:
    index = ctx.args[0]
    item = map_get_item(ctx.current_map, index)
    if not item:
        print("[handle_add_click] Error: item not found.")
        return
    add_click(item)
    name = config_service.get_name_from_item_id(item[0])
    print(f"Added click to {name}")


@register_command("activate_item_click")
def handle_activate_item_click(ctx: CommandContext) -> None:
    index = ctx.args[0]
    item = map_get_item(ctx.current_map, index)
    if not item:
        print("[handle_activate_item_click] Error: item not found.")
        return
    activate_item_click(item)
    name = config_service.get_name_from_item_id(item[0])
    print(f"Click to build finished for {name}")


@register_command("buy_si_help")
def handle_buy_si_help(ctx: CommandContext) -> None:
    index = ctx.args[0]
    item = map_get_item(ctx.current_map, index)
    if not item:
        print("[handle_buy_si_help] Error: item not found.")
        return
    buy_si_help(item)
    name = config_service.get_name_from_item_id(item[0])
    print(f"Bought SI help for {name}")


@register_command("finish_si")
def handle_finish_si(ctx: CommandContext) -> None:
    index = ctx.args[0]
    item = map_get_item(ctx.current_map, index)
    if not item:
        print("[handle_finish_si] Error: item not found.")
        return
    finish_si(item)
    name = config_service.get_name_from_item_id(item[0])
    print(f"Finished SI for {name}")


@register_command("first_time_marketplace")
def handle_first_time_marketplace(ctx: CommandContext) -> None:
    ctx.private_state["marketPlaceFirstTime"] = True
    print("Seen Auction House")
