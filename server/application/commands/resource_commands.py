from server.application.commands.dispatcher import register_command
from server.domain.entities import CommandContext
from server.application.queries.game_config_query import config_service
from server.domain.engine import (
    timestamp_now,
    map_get_item,
    map_add_item,
    bought_unit_add,
    add_store_item,
    finish_si
)


@register_command("collect")
def handle_collect(ctx: CommandContext) -> None:
    item_index = ctx.args[0]
    item = map_get_item(ctx.current_map, item_index)
    if not item:
        print("[handle_collect] Error: item not found.")
        return
    item[3] = timestamp_now()
    name = config_service.get_name_from_item_id(item[0])
    print(f"Collect {name}")


@register_command("trade_resource")
def handle_trade_resource(ctx: CommandContext) -> None:
    _resource_type = ctx.args[0]
    _sold = ctx.args[1]
    num_trades = ctx.current_map.get("numTradesDone", 0) + 1
    ctx.current_map["numTradesDone"] = min(20, num_trades)
    ctx.current_map["timestampLastTrade"] = timestamp_now()
    print(f"Remaining trades: {20 - num_trades}")


@register_command("win_daily_bonus")
def handle_win_daily_bonus(ctx: CommandContext) -> None:
    item = ctx.args[0]
    next_id = ctx.args[1] + 1
    if next_id > 5:
        next_id = 1

    time_now = timestamp_now()
    ctx.private_state["timestampLastBonus"] = time_now
    ctx.private_state["bonusNextId"] = next_id

    if item > 0:
        bought_unit_add(ctx.save, item)
        add_store_item(ctx.current_map, item)
        name = config_service.get_name_from_item_id(item)
        print(f"Put {name} in storage")
    else:
        print("Rewarded resources")


@register_command("weekly_reward")
def handle_weekly_reward(ctx: CommandContext) -> None:
    time_now = timestamp_now()
    if len(ctx.args) > 4:
        item_index = ctx.args[0]
        item_id = ctx.args[1]
        x = ctx.args[2]
        y = ctx.args[3]
        player_id = ctx.args[4]

        map_add_item(ctx.current_map, item_index, item_id, x, y, player=player_id)
        bought_unit_add(ctx.save, item_id)
        name = config_service.get_name_from_item_id(item_id)
        print(f"Won {name}")
    else:
        print("Won resources")

    ctx.private_state["timeStampMondayBonus"] = time_now
    reward_len = config_service.get_weekly_reward_length()
    cur_idx = ctx.private_state.get("weeklyRewardIndex", 0)
    ctx.private_state["weeklyRewardIndex"] = (cur_idx + 1) % reward_len


@register_command("set_resource_allies")
def handle_set_resource_allies(ctx: CommandContext) -> None:
    resource = ctx.args[0]
    index = ctx.args[1]

    item = map_get_item(ctx.current_map, index)
    if item:
        item[3] = timestamp_now()
        finish_si(item)

    ctx.current_map["resourceAlliesMarket"] = resource
    print("Set Allies Market resource")


@register_command("buy_premium_account")
def handle_buy_premium_account(ctx: CommandContext) -> None:
    package_index = ctx.args[0]
    days = config_service.get_premium_days(package_index)
    time_now = timestamp_now()
    ts_premium = ctx.private_state.get("timeStampEndPremium", 0)

    if time_now >= ts_premium:
        ctx.private_state["timeStampEndPremium"] = time_now + days * 86400
        print(f"Bought Premium Account for {days} day(s)")
    else:
        ctx.private_state["timeStampEndPremium"] += days * 86400
        print(f"Extended Premium Account for {days} day(s)")
