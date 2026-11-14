import json
from server.application.commands.dispatcher import register_command
from server.domain.entities import CommandContext
from server.application.queries.game_config_query import config_service
from server.domain.engine import (
    timestamp_now,
    set_goals,
    complete_goal,
    map_lose_item
)


@register_command("complete_tutorial")
def handle_complete_tutorial(ctx: CommandContext) -> None:
    step = ctx.args[0]
    print(f"Tutorial step {step} reached.")
    if step >= 25 or step == 15:
        print("Tutorial COMPLETED!")
        ctx.player_info["completed_tutorial"] = 1


@register_command("set_goals")
def handle_set_goals(ctx: CommandContext) -> None:
    goal_id = ctx.args[0]
    progress = json.loads(ctx.args[1])
    set_goals(ctx.private_state, goal_id, progress)
    title = config_service.get_attribute_from_goal_id(goal_id, "title")
    print(f"Goal '{title}' progressed.")


@register_command("complete_goal")
def handle_complete_goal(ctx: CommandContext) -> None:
    goal_id = ctx.args[0]
    complete_goal(ctx.private_state, goal_id)
    title = config_service.get_attribute_from_goal_id(goal_id, "title")
    print(f"Goal '{title}' completed.")


@register_command("level_up")
def handle_level_up(ctx: CommandContext) -> None:
    new_level = ctx.args[0]
    ctx.current_map["level"] = new_level
    print(f"Level up! New level: {new_level}")


@register_command("set_quest_var")
def handle_set_quest_var(ctx: CommandContext) -> None:
    key = ctx.args[0]
    value = ctx.args[1]

    if key == "idSimpleChapter":
        print(f"Ignored {key}")
        return

    quest_vars = ctx.current_map.setdefault("currentQuestVars", {})
    if key == "id":
        ctx.current_map["idCurrentMission"] = value
    quest_vars[key] = value
    print(f"Set current quest {key} to '{value}'")


@register_command("collect_mission")
def handle_collect_mission(ctx: CommandContext) -> None:
    next_mission = ctx.args[0]
    if next_mission > 99:
        next_mission = 1

    ctx.current_map["idCurrentMission"] = str(next_mission)
    ctx.current_map["timestampLastChapter"] = timestamp_now()
    ctx.current_map["currentQuestVars"] = {}
    print(f"Advanced to mission {next_mission}")


@register_command("end_quest")
def handle_end_quest(ctx: CommandContext) -> None:
    try:
        response = json.loads(ctx.args[0])
    except Exception:
        print("[handle_end_quest] Error: Failed to parse quest response.")
        return

    units = response.get("units", [])
    for unit in units:
        lost = max(0, unit[2] - unit[3])
        if lost > 0:
            name = config_service.get_name_from_item_id(unit[0])
            print(f"Lost {lost} {name}(s)")
            map_lose_item(ctx.current_map, ctx.private_state, unit[0], lost)

    quest_id = response.get("quest_id")
    if not quest_id:
        print("[handle_end_quest] Error: No quest played.")
        return

    ctx.current_map.setdefault("questTimes", {})[str(quest_id)] = timestamp_now()
    outcome = "Won" if response.get("win", False) else "Failed"
    print(f"{outcome} quest {quest_id}")


@register_command("admin_set_quest_rank")
def handle_admin_set_quest_rank(ctx: CommandContext) -> None:
    quest_index = ctx.args[0]
    difficulty = ctx.args[1]
    ctx.private_state.setdefault("questsRank", {})[str(quest_index)] = difficulty
    print(f"Set quest {quest_index} rank to {difficulty}")
