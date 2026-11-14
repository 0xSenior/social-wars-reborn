"""
Backward compatibility facade for player info queries.
Redirects to server.application.queries.player_info_query.
"""
from server.application.queries.player_info_query import player_info_service

get_player_info = player_info_service.get_player_info
get_neighbor_info = player_info_service.get_neighbor_info
