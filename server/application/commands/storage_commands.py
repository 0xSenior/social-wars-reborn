from server.application.commands.dispatcher import register_command
from server.domain.entities import CommandContext
from server.application.queries.game_config_query import config_service
from server.domain.engine import (
    map_pop_item,
    map_add_item,
    add_store_item,
    remove_store_item,
    bought_unit_add,
    unit_collection_complete,
    inventory_add,
    inventory_remove
)


@register_command("store_item")
def handle_store_item(ctx: CommandContext) -> None:
    item_index = ctx.args[0]
    item = map_pop_item(ctx.current_map, item_index)
    if not item:
        print("[handle_store_item] Error: item not found.")
        return

    item_id = item[0]
    add_store_item(ctx.current_map, item_id)
    name = config_service.get_name_from_item_id(item_id)
    print(f"Store {name}.")


@register_command("place_stored_item")
def handle_place_stored_item(ctx: CommandContext) -> None:
    item_index = ctx.args[0]
    item_id = ctx.args[1]
    x = ctx.args[2]
    y = ctx.args[3]
    _player_id = ctx.args[4]
    orientation = ctx.args[5]

    remove_store_item(ctx.current_map, item_id)
    map_add_item(ctx.current_map, item_index, item_id, x, y, orientation=orientation)
    bought_unit_add(ctx.save, item_id)
    name = config_service.get_name_from_item_id(item_id)
    print(f"Placed stored {name}.")


@register_command("sell_stored_item")
def handle_sell_stored_item(ctx: CommandContext) -> None:
    item_id = ctx.args[0]
    remove_store_item(ctx.current_map, item_id)
    name = config_service.get_name_from_item_id(item_id)
    print(f"Sell stored {name}.")


@register_command("store_add_items")
def handle_store_add_items(ctx: CommandContext) -> None:
    item_id_list = ctx.args[0]
    names = []
    for item_id in item_id_list:
        add_store_item(ctx.current_map, item_id)
        bought_unit_add(ctx.save, item_id)
        names.append(config_service.get_name_from_item_id(item_id))
    print("Add to store", ", ".join(names))


@register_command("buy_stored_item_cash")
def handle_buy_stored_item_cash(ctx: CommandContext) -> None:
    item_id = ctx.args[0]
    bought_unit_add(ctx.save, item_id)
    add_store_item(ctx.current_map, item_id)
    name = config_service.get_name_from_item_id(item_id)
    print(f"Bought {name} from unit collection")


@register_command("unit_collections_completed")
def handle_unit_collections_completed(ctx: CommandContext) -> None:
    collection_id = ctx.args[0]
    unit_collection_complete(ctx.save, collection_id)
    print(f"Completed unit collection {collection_id}")


@register_command("add_inventory_item")
def handle_add_inventory_item(ctx: CommandContext) -> None:
    item = ctx.args[0]
    quantity = ctx.args[1]
    inventory_add(ctx.private_state, item, quantity)
    name = config_service.get_inventory_item_name(item)
    print(f"Added {quantity} {name} to inventory")


@register_command("remove_inventory_item")
def handle_remove_inventory_item(ctx: CommandContext) -> None:
    item = ctx.args[0]
    quantity = ctx.args[1]
    inventory_remove(ctx.private_state, item, quantity)
    name = config_service.get_inventory_item_name(item)
    print(f"Removed {quantity} {name} from inventory")


@register_command("complete_collection")
def handle_complete_collection(ctx: CommandContext) -> None:
    collection_id = ctx.args[0]
    bought = ctx.args[1]

    prize = config_service.get_collection_prize(collection_id)
    if prize:
        for key, qty in prize.items():
            add_store_item(ctx.current_map, int(key), qty)

    collection_name = config_service.get_collection_name(collection_id)
    collections = ctx.private_state.setdefault("collections", [])
    if collection_id not in collections:
        collections.append(collection_id)

    action = "Bought" if bought else "Completed"
    print(f"{action} {collection_name}")
