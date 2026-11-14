"""
Backward compatibility facade for commands.
Redirects to server.application.commands.dispatcher.
"""
from server.application.commands.dispatcher import dispatcher
from server.infrastructure.persistence.save_repository import save_repository
from server.domain.engine import apply_resources


def command(USERID, data):
    commands = data.get("commands", [])
    save = save_repository.get_save(USERID)
    if save:
        for comm in commands:
            map_id = comm[0]
            cmd = comm[1]
            args = comm[2]
            resources_changed = comm[3]
            current_map = save["maps"][map_id] if map_id < len(save["maps"]) else save["maps"][0]
            apply_resources(save, current_map, resources_changed)

        dispatcher_payload = [
            {"cmd": comm[1], "args": comm[2], "townId": comm[0]}
            for comm in commands
        ]
        dispatcher.dispatch(USERID, dispatcher_payload)
