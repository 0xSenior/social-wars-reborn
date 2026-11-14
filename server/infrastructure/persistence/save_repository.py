import os
import json
import copy
import random
import time
from typing import Dict, Any, List, Optional

from server.infrastructure.config import SAVES_DIR, VILLAGES_DIR, QUESTS_DIR
from version import migrate_loaded_save


def timestamp_now() -> int:
    return int(time.time())



class SaveRepository:
    def __init__(self):
        self._saves: Dict[str, Dict[str, Any]] = {}
        self._static_villages: Dict[str, Dict[str, Any]] = {}
        self._quests: Dict[str, Dict[str, Any]] = {}
        self._initial_village: Optional[Dict[str, Any]] = None

    def initialize(self) -> None:
        self.load_initial_template()
        self.load_static_villages()
        self.load_quests()
        self.load_saves()

    def load_initial_template(self) -> None:
        initial_path = os.path.join(VILLAGES_DIR, "initial.json")
        if os.path.exists(initial_path):
            with open(initial_path, "r", encoding="utf-8") as f:
                self._initial_village = json.load(f)

    @staticmethod
    def is_valid_village(village: Any) -> bool:
        if not isinstance(village, dict):
            return False
        if "playerInfo" not in village or "maps" not in village or "privateState" not in village:
            return False
        if "pid" not in village["playerInfo"]:
            return False
        return True

    def load_saves(self) -> None:
        self._saves.clear()
        if not os.path.exists(SAVES_DIR):
            try:
                os.makedirs(SAVES_DIR, exist_ok=True)
            except Exception as e:
                print(f"[SaveRepo] Error creating saves directory: {e}")
                return

        for fname in os.listdir(SAVES_DIR):
            if not fname.endswith(".json"):
                continue
            fpath = os.path.join(SAVES_DIR, fname)
            try:
                with open(fpath, "r", encoding="utf-8") as f:
                    save = json.load(f)
            except Exception as e:
                print(f"[SaveRepo] Corrupted save {fname}: {e}")
                continue

            if not self.is_valid_village(save):
                print(f"[SaveRepo] Invalid save structure {fname}")
                continue

            pid = str(save["playerInfo"]["pid"])
            self._saves[pid] = save
            if migrate_loaded_save(save):
                self.save_player(pid)

    def load_static_villages(self) -> None:
        self._static_villages.clear()
        if not os.path.exists(VILLAGES_DIR):
            return

        for fname in os.listdir(VILLAGES_DIR):
            if fname == "initial.json" or not fname.endswith(".json"):
                continue
            fpath = os.path.join(VILLAGES_DIR, fname)
            try:
                with open(fpath, "r", encoding="utf-8") as f:
                    village = json.load(f)
                if self.is_valid_village(village):
                    pid = str(village["playerInfo"]["pid"])
                    self._static_villages[pid] = village
            except Exception:
                continue

    def load_quests(self) -> None:
        self._quests.clear()
        if not os.path.exists(QUESTS_DIR):
            return

        for fname in os.listdir(QUESTS_DIR):
            if not fname.endswith(".json"):
                continue
            fpath = os.path.join(QUESTS_DIR, fname)
            try:
                with open(fpath, "r", encoding="utf-8") as f:
                    quest_village = json.load(f)
                if self.is_valid_village(quest_village):
                    pid = str(quest_village["playerInfo"]["pid"])
                    self._quests[pid] = quest_village
            except Exception:
                continue

    def get_save(self, userid: str) -> Optional[Dict[str, Any]]:
        return self._saves.get(str(userid))

    def save_player(self, userid: str) -> bool:
        pid = str(userid)
        save = self._saves.get(pid)
        if not save:
            return False

        os.makedirs(SAVES_DIR, exist_ok=True)
        target_path = os.path.join(SAVES_DIR, f"{pid}.json")
        temp_path = os.path.join(SAVES_DIR, f"{pid}.json.tmp")

        try:
            with open(temp_path, "w", encoding="utf-8") as f:
                json.dump(save, f, indent=4)
            if os.path.exists(target_path):
                os.replace(temp_path, target_path)
            else:
                os.rename(temp_path, target_path)
            return True
        except Exception as e:
            print(f"[SaveRepo] Error saving {pid}: {e}")
            if os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except Exception:
                    pass
            return False

    def create_new_village(self) -> str:
        if self._initial_village is None:
            self.load_initial_template()

        new_save = copy.deepcopy(self._initial_village)
        existing_pids = set(self._saves.keys()) | set(self._static_villages.keys())

        # Generate unique 9-digit USERID
        while True:
            new_pid = str(random.randint(100000000, 999999999))
            if new_pid not in existing_pids:
                break

        now = timestamp_now()
        new_save["playerInfo"]["pid"] = new_pid
        new_save["playerInfo"]["last_logged_in"] = now
        for m in new_save.get("maps", []):
            m["timestamp"] = now

        self._saves[new_pid] = new_save
        self.save_player(new_pid)
        return new_pid

    def get_all_save_ids(self) -> List[str]:
        return list(self._saves.keys())

    def get_all_saves_info(self) -> List[Dict[str, Any]]:
        result = []
        for pid in self._saves:
            result.append(self.get_save_info(pid))
        result.sort(key=lambda x: x.get("last_logged_in", 0), reverse=True)
        return result

    def get_save_info(self, userid: str) -> Dict[str, Any]:
        save = self._saves.get(str(userid))
        if not save:
            return {
                "userid": str(userid),
                "pid": str(userid),
                "name": "Warrior",
                "level": 1,
                "cash": 0,
                "xp": 0,
                "last_logged_in": 0
            }
        info = save.get("playerInfo", {})
        default_map = info.get("default_map", 0)
        maps = save.get("maps", [])
        m = maps[default_map] if default_map < len(maps) else (maps[0] if maps else {})
        return {
            "userid": str(userid),
            "pid": str(userid),
            "name": str(info.get("name", "Warrior")),
            "level": m.get("level", info.get("level", 1)),
            "xp": m.get("xp", 0),
            "cash": info.get("cash", 0),
            "last_logged_in": info.get("last_logged_in", 0)
        }

    def get_neighbors(self, userid: str) -> List[Dict[str, Any]]:
        neighbors_list = []
        # General Mike & Static villages
        for pid, v in self._static_villages.items():
            info = v.get("playerInfo", {})
            neighbors_list.append({
                "user_id": pid,
                "name": info.get("name", "Neighbor"),
                "level": info.get("level", 1),
                "pic": info.get("pic", "")
            })

        # Other player saves
        for pid, s in self._saves.items():
            if pid == str(userid):
                continue
            info = s.get("playerInfo", {})
            neighbors_list.append({
                "user_id": pid,
                "name": info.get("name", "Warrior"),
                "level": info.get("level", 1),
                "pic": info.get("pic", "")
            })
        return neighbors_list

    def get_neighbor_village(self, userid: str) -> Optional[Dict[str, Any]]:
        pid = str(userid)
        if pid in self._static_villages:
            return self._static_villages[pid]
        if pid in self._quests:
            return self._quests[pid]
        if pid in self._saves:
            return self._saves[pid]
        return None

    def get_fb_friends(self, userid: str) -> List[Dict[str, Any]]:
        friends = []
        for n in self.get_neighbors(userid):
            friends.append({
                "uid": n.get("user_id"),
                "name": n.get("name"),
                "pic_square": n.get("pic", "")
            })
        return friends


save_repository = SaveRepository()
