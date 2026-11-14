from typing import Callable, Dict, Any, List
from server.domain.entities import CommandContext
from server.infrastructure.persistence.save_repository import save_repository


CommandHandler = Callable[[CommandContext], None]

_command_registry: Dict[str, CommandHandler] = {}


def register_command(cmd_name: str):
    def decorator(fn: CommandHandler) -> CommandHandler:
        _command_registry[cmd_name] = fn
        return fn
    return decorator


class CommandDispatcher:
    def __init__(self, registry: Dict[str, CommandHandler] = None):
        self.registry = registry if registry is not None else _command_registry

    def dispatch(self, userid: str, payload: List[Dict[str, Any]]) -> None:
        save = save_repository.get_save(userid)
        if not save:
            print(f"[CommandDispatcher] Error: save not found for USERID {userid}")
            return

        for cmd_item in payload:
            cmd = cmd_item.get("cmd")
            args = cmd_item.get("args", [])
            town_id = int(cmd_item.get("townId", 0))

            handler = self.registry.get(cmd)
            if handler:
                ctx = CommandContext(save=save, cmd=cmd, args=args, town_id=town_id)
                try:
                    handler(ctx)
                except Exception as e:
                    print(f"[CommandDispatcher] Error executing '{cmd}': {e}")
            else:
                print(f"[CommandDispatcher] Unhandled command: '{cmd}' -> args {args}")

        save_repository.save_player(userid)


dispatcher = CommandDispatcher()

