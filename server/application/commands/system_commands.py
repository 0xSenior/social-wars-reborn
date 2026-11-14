from server.application.commands.dispatcher import register_command
from server.domain.entities import CommandContext
from server.application.queries.game_config_query import config_service
from server.domain.engine import timestamp_now, map_get_item


@register_command("activate")
def handle_activate(ctx: CommandContext) -> None:
    item_id = ctx.args[0]
    activate = ctx.args[1]
    time_now = timestamp_now()

    item = map_get_item(ctx.current_map, item_id)
    if not item:
        print("[handle_activate] Error: item not found.")
        return

    name = config_service.get_name_from_item_id(item[0])
    if activate > 0:
        item[3] = time_now
        item[6]["cp"] = ctx.args[1]
        print(f"Activated {name} Set CP to {activate}")
    else:
        item[3] = time_now
        item[6] = {}
        print(f"Deactivated {name}")


@register_command("fast_forward")
def handle_fast_forward(ctx: CommandContext) -> None:
    seconds = ctx.args[0]
    m = ctx.current_map
    ps = ctx.private_state

    m["timestamp"] = max(0, m.get("timestamp", 0) - seconds)
    m["timestampLastChapter"] = max(0, m.get("timestampLastChapter", 0) - seconds)
    m["timestampLastTreasure"] = max(0, m.get("timestampLastTreasure", 0) - seconds)
    m["timestampLastTrade"] = max(0, m.get("timestampLastTrade", 0) - seconds)
    ps["timestampLastBonus"] = max(0, ps.get("timestampLastBonus", 0) - seconds)
    ps["timestampLastAllianceBonus"] = max(0, ps.get("timestampLastAllianceBonus", 0) - seconds)
    ps["timeStampDartsNewFree"] = max(0, ps.get("timeStampDartsNewFree", 0) - seconds)
    ps["tsAttacksReset"] = max(0, ps.get("tsAttacksReset", 0) - seconds)
    ps["tsSpyingsReset"] = max(0, ps.get("tsSpyingsReset", 0) - seconds)

    research_timers = ps.get("timeStampDoResearch", [])
    for i in range(len(research_timers)):
        research_timers[i] = max(0, research_timers[i] - seconds)

    items = m.get("items", {})
    for index in items:
        data = items[index]
        data[3] = max(0, data[3] - seconds)
        if len(data) > 6 and isinstance(data[6], dict) and "ts" in data[6]:
            data[6]["ts"] = max(0, data[6]["ts"] - seconds)

    quest_times = m.get("questTimes", {})
    for key in quest_times:
        quest_times[key] = max(0, quest_times[key] - seconds)

    print(f"Fast forwarded {seconds} seconds")


@register_command("ping")
def handle_ping(ctx: CommandContext) -> None:
    print("Pong")


@register_command("set_variables")
def handle_set_variables(ctx: CommandContext) -> None:
    print("Set player resources")


@register_command("flash_debug")
def handle_flash_debug(ctx: CommandContext) -> None:
    cash = ctx.args[0]
    _unknown = ctx.args[1]
    xp = ctx.args[2]
    gold = ctx.args[3]
    oil = ctx.args[4]
    steel = ctx.args[5]
    wood = ctx.args[6]

    ctx.player_info["cash"] = cash
    ctx.current_map["xp"] = xp
    ctx.current_map["gold"] = gold
    ctx.current_map["oil"] = oil
    ctx.current_map["steel"] = steel
    ctx.current_map["wood"] = wood

    print("Keep up with resources.")
