"""
Backward compatibility facade for session and save persistence.
Redirects to server.infrastructure.persistence.save_repository.
"""
from server.infrastructure.persistence.save_repository import save_repository

load_saves = save_repository.load_saves
load_static_villages = save_repository.load_static_villages
load_quests = save_repository.load_quests
session = save_repository.get_save
save_session = save_repository.save_player
new_village = save_repository.create_new_village
all_saves_userid = save_repository.get_all_save_ids
all_saves_info = save_repository.get_all_saves_info
save_info = save_repository.get_save_info
neighbors = save_repository.get_neighbors
neighbor_session = save_repository.get_neighbor_village
fb_friends_str = save_repository.get_fb_friends
