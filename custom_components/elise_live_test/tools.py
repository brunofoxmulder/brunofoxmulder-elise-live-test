"""Normalize the API selection; Home Assistant owns tool merging and dispatch."""

from collections.abc import Mapping
from typing import Any

from homeassistant.const import CONF_LLM_HASS_API
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import llm


def selected_api_ids(config: Mapping[str, Any]) -> list[str]:
    """Distinguish the legacy Assist default from an explicitly empty choice."""
    value = config.get(CONF_LLM_HASS_API, [llm.LLM_API_ASSIST])
    if value is None:
        return []
    if isinstance(value, str):
        value = [value] if value else []
    if not isinstance(value, list) or any(
        not isinstance(item, str) or not item for item in value
    ):
        raise HomeAssistantError("Invalid Home Assistant tool API selection")
    return list(dict.fromkeys(value))
