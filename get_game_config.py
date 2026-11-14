"""
Backward compatibility facade for game config queries.
Redirects to server.application.queries.game_config_query.
"""
from server.application.queries.game_config_query import (
    config_service,
    GameConfigService
)

get_game_config = config_service.get_config
game_config = config_service.get_config
get_item_from_id = config_service.get_item_from_id
get_attribute_from_item_id = config_service.get_attribute_from_item_id
get_name_from_item_id = config_service.get_name_from_item_id
get_item_from_subcat_functional = config_service.get_item_from_subcat_functional
get_xp_from_level = config_service.get_xp_from_level
get_level_from_xp = config_service.get_level_from_xp
get_goal_from_id = config_service.get_goal_from_id
get_attribute_from_goal_id = config_service.get_attribute_from_goal_id
get_inventory_item_name = config_service.get_inventory_item_name
get_collection_name = config_service.get_collection_name
get_collection_prize = config_service.get_collection_prize
get_premium_days = config_service.get_premium_days
get_weekly_reward_length = config_service.get_weekly_reward_length
