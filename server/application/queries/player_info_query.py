from typing import Dict, Any, Optional

from server.infrastructure.persistence.save_repository import save_repository
from server.domain.engine import timestamp_now, reset_stuff


class PlayerInfoQueryHandler:
    def __init__(self, repo=save_repository):
        self.repo = repo

    def get_player_info(self, userid: str) -> Optional[Dict[str, Any]]:
        save = self.repo.get_save(userid)
        if not save:
            return None

        ts_now = timestamp_now()
        save["playerInfo"]["last_logged_in"] = ts_now
        reset_stuff(save)

        return {
            "result": "ok",
            "processed_errors": 0,
            "timestamp": ts_now,
            "playerInfo": save["playerInfo"],
            "map": save["maps"][0],
            "privateState": save["privateState"],
            "neighbors": self.repo.get_neighbors(userid)
        }

    def get_neighbor_info(self, userid: str, map_number: Optional[int] = None) -> Optional[Dict[str, Any]]:
        neighbor_village = self.repo.get_neighbor_village(userid)
        if not neighbor_village:
            return None

        m_idx = map_number if map_number is not None else 0
        maps = neighbor_village.get("maps", [])
        if m_idx >= len(maps):
            m_idx = 0

        return {
            "result": "ok",
            "processed_errors": 0,
            "timestamp": timestamp_now(),
            "playerInfo": neighbor_village.get("playerInfo", {}),
            "map": maps[m_idx] if maps else {},
            "privateState": neighbor_village.get("privateState", {})
        }


player_info_service = PlayerInfoQueryHandler()
