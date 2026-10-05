"""Home Assistant local-time tool for live conversations."""

from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.util import dt as dt_util

from .live import LiveTool

CURRENT_TIME_TOOL_NAME = "GetCurrentTime"

_CURRENT_TIME_TOOL = LiveTool(
    name=CURRENT_TIME_TOOL_NAME,
    description=(
        "Return Home Assistant's current local date and time and configured time zone. "
        "Use this whenever the current local time or date is needed, including when "
        "another Home Assistant tool or script asks you to state the current time. "
        "Never infer the current time or apply a fixed UTC offset."
    ),
    parameters={
        "type": "object",
        "properties": {},
        "additionalProperties": False,
    },
)


def add_current_time_tool(tools: list[LiveTool]) -> list[LiveTool]:
    """Expose Home Assistant's local clock to the live model."""
    return [*tools, _CURRENT_TIME_TOOL]


async def async_handle_current_time_tool(
    hass: HomeAssistant, _args: dict[str, Any] | None = None
) -> dict[str, str]:
    """Return a fresh Home Assistant-local timestamp."""
    now = dt_util.as_local(dt_util.utcnow())
    return {
        "local_datetime": now.isoformat(),
        "local_time": now.strftime("%H:%M:%S"),
        "local_date": now.date().isoformat(),
        "time_zone": hass.config.time_zone,
    }
