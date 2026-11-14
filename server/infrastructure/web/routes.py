import os
import json
from flask import Blueprint, request, session, redirect, render_template, send_from_directory, jsonify

from server.infrastructure.config import (
    ASSETS_DIR,
    STUB_DIR,
    TEMPLATES_DIR,
    ServerConfig
)
from server.infrastructure.persistence.save_repository import save_repository
from server.application.queries.game_config_query import config_service
from server.application.queries.player_info_query import player_info_service
from server.application.commands.dispatcher import dispatcher
from server.domain.engine import timestamp_now, apply_resources
from server.domain.constants import Quests
from version import version_name

api_blueprint = Blueprint("game_api", __name__)

STATIC_ROOT = "/static/socialwars"
DYNAMIC_ROOT = "/dynamic/menvswomen/srvsexwars"


def register_routes(bp: Blueprint, server_config: ServerConfig):
    @bp.route("/", methods=["GET", "POST"])
    def login():
        session.pop("USERID", default=None)
        session.pop("GAMEVERSION", default=None)
        save_repository.load_saves()

        if request.method == "POST":
            userid = request.form.get("USERID")
            game_version = request.form.get("GAMEVERSION", "Basesec_1.5.4.swf")
            session["USERID"] = userid
            session["GAMEVERSION"] = game_version
            print(f"[LOGIN] USERID: {userid} (Version: {game_version})")
            return redirect("/play.html")

        saves_info = save_repository.get_all_saves_info()
        return render_template("login.html", saves_info=saves_info, version=version_name)

    @bp.route("/play.html")
    def play():
        userid = session.get("USERID")
        game_version = session.get("GAMEVERSION")
        if not userid or not game_version:
            return redirect("/")

        if userid not in save_repository.get_all_save_ids():
            return redirect("/")

        save_info = save_repository.get_save_info(userid)
        friends_info = save_repository.get_fb_friends(userid)

        return render_template(
            "play.html",
            save_info=save_info,
            serverTime=timestamp_now(),
            friendsInfo=friends_info,
            version=version_name,
            GAMEVERSION=game_version,
            public_url=server_config.resolved_public_url,
            SERVERIP=server_config.host,
            SERVERPORT=server_config.port
        )

    @bp.route("/health")
    def health():
        return jsonify({"status": "ok", "version": version_name})

    @bp.route("/new.html")
    def new_empire():
        new_uid = save_repository.create_new_village()
        session["USERID"] = new_uid
        session["GAMEVERSION"] = "Basesec_1.5.4.swf"
        print(f"[NEW] Created Empire USERID: {new_uid}")
        return redirect("/play.html")

    @bp.route("/crossdomain.xml")
    def crossdomain():
        return send_from_directory(STUB_DIR, "crossdomain.xml")

    @bp.route("/img/<path:path>")
    def images(path):
        return send_from_directory(os.path.join(TEMPLATES_DIR, "img"), path)

    @bp.route("/avatars/<path:path>")
    def avatars(path):
        return send_from_directory(os.path.join(TEMPLATES_DIR, "avatars"), path)

    @bp.route("/css/<path:path>")
    def css(path):
        return send_from_directory(os.path.join(TEMPLATES_DIR, "css"), path)

    @bp.route(f"{STATIC_ROOT}/<path:path>")
    def static_assets(path):
        return send_from_directory(ASSETS_DIR, path)

    @bp.route(f"{DYNAMIC_ROOT}/track_game_status.php", methods=["POST"])
    def track_game_status():
        status = request.values.get("status")
        user_id = request.values.get("user_id")
        print(f"[STATUS] USERID {user_id}: {status}")
        return ("", 200)

    @bp.route(f"{DYNAMIC_ROOT}/get_game_config.php", methods=["GET", "POST"])
    def get_game_config_endpoint():
        userid = request.values.get("USERID")
        print(f"[CONFIG] USERID {userid}")
        return jsonify(config_service.get_config())

    @bp.route(f"{DYNAMIC_ROOT}/get_player_info.php", methods=["POST"])
    def get_player_info_endpoint():
        userid = request.values.get("USERID")
        user = request.values.get("user")
        map_num = int(request.values.get("map", 0)) if "map" in request.values else None

        if user is None:
            print(f"[PLAYER INFO] USERID {userid}")
            info = player_info_service.get_player_info(userid)
            return (jsonify(info), 200) if info else ("Player not found", 404)
        elif user in ["100000030", "100000031"]:
            print(f"[VISIT] USERID {userid} visiting General Mike ({user}).")
            return jsonify(player_info_service.get_neighbor_info("100000030", map_num)), 200
        elif user.startswith("100000"):
            quest_name = Quests.QUEST.get(user, "?")
            print(f"[QUEST] USERID {userid} loading {quest_name} ({user}).")
            return jsonify(player_info_service.get_neighbor_info(user, map_num)), 200
        else:
            print(f"[VISIT] USERID {userid} visiting user: {user}.")
            return jsonify(player_info_service.get_neighbor_info(user, map_num)), 200

    @bp.route(f"{DYNAMIC_ROOT}/sync_error_track.php", methods=["POST"])
    def sync_error_track():
        return ("", 200)

    @bp.route("/null")
    def flash_sync_error():
        return redirect("/play.html")

    @bp.route(f"{DYNAMIC_ROOT}/command.php", methods=["POST"])
    def command_endpoint():
        userid = request.values.get("USERID")
        data_str = request.values.get("data", "")
        if len(data_str) <= 65:
            return (jsonify({"result": "error", "message": "invalid data format"}), 400)

        data_payload = data_str[65:]
        data = json.loads(data_payload)
        commands = data.get("commands", [])

        # Execute commands through Clean Architecture dispatcher
        save = save_repository.get_save(userid)
        if save:
            for comm in commands:
                map_id = comm[0]
                cmd = comm[1]
                args = comm[2]
                resources_changed = comm[3]
                current_map = save["maps"][map_id] if map_id < len(save["maps"]) else save["maps"][0]
                apply_resources(save, current_map, resources_changed)

            # Map to standard command format for dispatcher
            dispatcher_payload = [
                {"cmd": comm[1], "args": comm[2], "townId": comm[0]}
                for comm in commands
            ]
            dispatcher.dispatch(userid, dispatcher_payload)

        return (jsonify({"result": "success"}), 200)

    @bp.route(f"{DYNAMIC_ROOT}/alliance/", methods=["POST"])
    def alliance():
        return (jsonify({}), 200)
