# Import all modules to trigger decorator registrations
from server.application.commands.dispatcher import CommandDispatcher, dispatcher, register_command
import server.application.commands.building_commands
import server.application.commands.resource_commands
import server.application.commands.storage_commands
import server.application.commands.unit_commands
import server.application.commands.research_commands
import server.application.commands.progression_commands
import server.application.commands.minigame_commands
import server.application.commands.system_commands

__all__ = ["CommandDispatcher", "dispatcher", "register_command"]
