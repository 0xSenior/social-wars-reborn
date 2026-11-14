from server.application.commands.dispatcher import register_command
from server.domain.entities import CommandContext
from server.domain.engine import timestamp_now

_LAB_TYPES = ["Area 51", "Robotic Center"]


@register_command("next_research_step")
def handle_next_research_step(ctx: CommandContext) -> None:
    lab_type = ctx.args[0]
    ctx.private_state["researchStepNumber"][lab_type] += 1
    ctx.private_state["timeStampDoResearch"][lab_type] = timestamp_now()
    label = _LAB_TYPES[lab_type] if lab_type < len(_LAB_TYPES) else f"Lab {lab_type}"
    print(f"Research step for {label}")


@register_command("research_buy_step_cash")
def handle_research_buy_step_cash(ctx: CommandContext) -> None:
    _cash = ctx.args[0]
    lab_type = ctx.args[1]
    ctx.private_state["timeStampDoResearch"][lab_type] = 0
    label = _LAB_TYPES[lab_type] if lab_type < len(_LAB_TYPES) else f"Lab {lab_type}"
    print(f"Buy research step for {label}")


@register_command("next_research_item")
def handle_next_research_item(ctx: CommandContext) -> None:
    lab_type = ctx.args[0]
    ctx.private_state["researchItemNumber"][lab_type] += 1
    ctx.private_state["researchStepNumber"][lab_type] = 0
    ctx.private_state["timeStampDoResearch"][lab_type] = 0
    label = _LAB_TYPES[lab_type] if lab_type < len(_LAB_TYPES) else f"Lab {lab_type}"
    print(f"Finished research for {label}")


@register_command("reset_research_item")
def handle_reset_research_item(ctx: CommandContext) -> None:
    lab_type = ctx.args[0]
    ctx.private_state["researchItemNumber"][lab_type] = 0
    ctx.private_state["researchStepNumber"][lab_type] = 0
    ctx.private_state["timeStampDoResearch"][lab_type] = 0
    label = _LAB_TYPES[lab_type] if lab_type < len(_LAB_TYPES) else f"Lab {lab_type}"
    print(f"Reset research for {label}")


@register_command("buy_mana_new")
def handle_buy_mana_new(ctx: CommandContext) -> None:
    print("Bought mana")


@register_command("buy_magic")
def handle_buy_magic(ctx: CommandContext) -> None:
    magic_id = ctx.args[0]
    magics = ctx.private_state.setdefault("magics", {})
    mid_str = str(magic_id)
    magics[mid_str] = min(50, magics.get(mid_str, 0) + 1)
    print("Bought magic spell")


@register_command("use_magic")
def handle_use_magic(ctx: CommandContext) -> None:
    magic_id = ctx.args[0]
    magics = ctx.private_state.setdefault("magics", {})
    mid_str = str(magic_id)
    magics[mid_str] = max(0, magics.get(mid_str, 0) - 1)
    print("Used magic spell")
