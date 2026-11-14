import os
import json
import time
import datetime
from typing import Dict, Any, Optional, List
import jsonpatch

from server.infrastructure.config import CONFIG_DIR, CONFIG_PATCH_DIR, MODS_DIR


class GameConfigService:
    def __init__(self):
        self._config: Dict[str, Any] = {}
        self._items_by_id: Dict[int, int] = {}
        self._items_by_subcat: Dict[int, int] = {}
        self._goals_by_id: Dict[int, int] = {}
        self.reload()

    def reload(self) -> None:
        main_config_path = os.path.join(CONFIG_DIR, "main.json")
        with open(main_config_path, "r", encoding="utf-8") as f:
            self._config = json.load(f)

        self._apply_patches()
        self._apply_mods()
        self._remove_duplicates()
        self._rebuild_indices()
        self._make_dynamic()

    def _apply_patch_file(self, file_path: str) -> None:
        with open(file_path, "r", encoding="utf-8") as f:
            patch = json.load(f)
        jsonpatch.apply_patch(self._config, patch, in_place=True)

    def _apply_patches(self) -> None:
        patches_file = os.path.join(CONFIG_PATCH_DIR, "patches.txt")
        if not os.path.exists(patches_file):
            return
        with open(patches_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
        for line in lines:
            patch_name = line.strip()
            if not patch_name or patch_name.startswith("#"):
                continue
            patch_name = patch_name.replace(".json", "")
            patch_path = os.path.join(CONFIG_PATCH_DIR, f"{patch_name}.json")
            if os.path.exists(patch_path):
                self._apply_patch_file(patch_path)

    def _apply_mods(self) -> None:
        mods_file = os.path.join(MODS_DIR, "mods.txt")
        if not os.path.exists(mods_file):
            return
        with open(mods_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
        for line in lines:
            mod_name = line.strip()
            if not mod_name or mod_name.startswith("#"):
                continue
            mod_name = mod_name.replace(".json", "")
            mod_path = os.path.join(MODS_DIR, f"{mod_name}.json")
            if os.path.exists(mod_path):
                self._apply_patch_file(mod_path)

    def _remove_duplicates(self) -> None:
        indexes = {}
        items = self._config.get("items", [])
        while True:
            duplicate = False
            for idx, item in enumerate(items):
                item_id = item.get("id")
                if item_id in indexes:
                    del items[indexes[item_id]]
                    indexes.clear()
                    duplicate = True
                    break
                indexes[item_id] = idx
            if not duplicate:
                break

    def _rebuild_indices(self) -> None:
        self._items_by_id = {int(item["id"]): i for i, item in enumerate(self._config.get("items", []))}
        self._items_by_subcat = {
            int(item["subcat_functional"]): i
            for i, item in enumerate(self._config.get("items", []))
            if "subcat_functional" in item and item["subcat_functional"] is not None
        }
        self._goals_by_id = {int(item["id"]): i for i, item in enumerate(self._config.get("goals", []))}

    def _make_dynamic(self) -> None:
        if "darts_items" not in self._config:
            return
        darts_items = self._config["darts_items"]
        if not darts_items:
            return
        last_game = darts_items[-1]
        try:
            ts_last = time.mktime(datetime.datetime.strptime(last_game["start_date"], "%Y-%m-%d %H:%M:%S").timetuple())
            ts_now = int(time.time())
            last_ts = ts_last
            while ts_now >= last_ts:
                last_ts = self._update_darts(darts_items, last_ts, 0)
        except Exception:
            pass

    def _update_darts(self, darts_items: List[Dict[str, Any]], ts_first: float, seconds: int) -> float:
        week_length = 604800
        shift = seconds
        last_ts = ts_first
        for game in darts_items:
            new_date = datetime.datetime.fromtimestamp(ts_first + shift)
            if new_date.hour == 23:
                shift += 3600
                new_date = datetime.datetime.fromtimestamp(ts_first + shift)
            elif new_date.hour == 1:
                shift -= 3600
                new_date = datetime.datetime.fromtimestamp(ts_first + shift)

            weekday = new_date.isoweekday()
            if weekday == 2:
                shift -= 86400
            elif weekday == 3:
                shift -= 86400 * 2
            elif weekday == 4:
                shift -= 86400 * 3
            elif weekday == 5:
                shift += 86400 * 3
            elif weekday == 6:
                shift += 86400 * 2
            elif weekday == 7:
                shift += 86400

            new_date = datetime.datetime.fromtimestamp(ts_first + shift)
            game["start_date"] = new_date.strftime("%Y-%m-%d %H:%M:%S")
            last_ts = ts_first + shift
            shift += week_length
        return last_ts

    def get_config(self) -> Dict[str, Any]:
        self._make_dynamic()
        return self._config

    def get_item_from_id(self, item_id: int) -> Optional[Dict[str, Any]]:
        idx = self._items_by_id.get(int(item_id))
        if idx is not None and idx < len(self._config.get("items", [])):
            return self._config["items"][idx]
        return None

    def get_attribute_from_item_id(self, item_id: int, attribute_name: str) -> Any:
        item = self.get_item_from_id(item_id)
        if item and attribute_name in item:
            return item[attribute_name]
        return None

    def get_name_from_item_id(self, item_id: int) -> str:
        name = self.get_attribute_from_item_id(item_id, "name")
        return name if name is not None else f"Unknown ({item_id})"

    def get_item_from_subcat_functional(self, subcat: int) -> Optional[Dict[str, Any]]:
        idx = self._items_by_subcat.get(int(subcat))
        if idx is not None and idx < len(self._config.get("items", [])):
            return self._config["items"][idx]
        return None

    def get_xp_from_level(self, level: int) -> int:
        levels = self._config.get("levels", [])
        if int(level) < len(levels):
            return levels[int(level)].get("exp_required", 0)
        return 0

    def get_level_from_xp(self, xp: int) -> int:
        levels = self._config.get("levels", [])
        for i, lvl in enumerate(levels):
            if lvl.get("exp_required", 0) > int(xp):
                return i
        return len(levels) - 1 if levels else 0

    def get_goal_from_id(self, goal_id: int) -> Optional[Dict[str, Any]]:
        idx = self._goals_by_id.get(int(goal_id))
        if idx is not None and idx < len(self._config.get("goals", [])):
            return self._config["goals"][idx]
        return None

    def get_attribute_from_goal_id(self, goal_id: int, attribute_name: str) -> Any:
        goal = self.get_goal_from_id(goal_id)
        if goal and attribute_name in goal:
            return goal[attribute_name]
        return None

    def get_inventory_item_name(self, item_id: int) -> Optional[str]:
        items = self._config.get("inventory_items", {})
        item_str = str(item_id)
        if item_str in items:
            return items[item_str].get("name")
        return None

    def get_collection_name(self, collection_id: int) -> Optional[str]:
        idx = max(0, int(collection_id) - 1)
        collections = self._config.get("collections", [])
        if idx < len(collections):
            return collections[idx].get("name")
        return None

    def get_collection_prize(self, collection_id: int) -> Optional[Any]:
        idx = max(0, int(collection_id) - 1)
        collections = self._config.get("collections", [])
        if idx < len(collections):
            prize_str = collections[idx].get("prize")
            if prize_str:
                return json.loads(prize_str)
        return None

    def get_premium_days(self, package_index: int) -> int:
        globals_cfg = self._config.get("globals", {})
        packages = globals_cfg.get("PREMIUM_ACCOUNTS", [])
        idx = package_index if package_index < len(packages) else max(0, len(packages) - 1)
        if packages and "time" in packages[idx]:
            return packages[idx]["time"]
        return 0

    def get_weekly_reward_length(self) -> int:
        globals_cfg = self._config.get("globals", {})
        rewards = globals_cfg.get("MONDAY_BONUS_REWARDS", [])
        length = 1
        for reward in rewards:
            val = reward.get("value")
            if isinstance(val, list):
                length = max(length, len(val))
        return length


# Global singleton instance for backward compatibility and app use
config_service = GameConfigService()
