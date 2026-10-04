"""Tool selection and real Gemini SDK result-envelope contracts."""

from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from homeassistant.exceptions import HomeAssistantError

from elise_live_test.gemini import GeminiLiveSession
from elise_live_test.live import LiveToolResponse
from elise_live_test.tools import selected_api_ids


def test_selection_keeps_saved_weather_memory_and_assist():
    assert selected_api_ids({"llm_hass_api": ["assist", "weather", "memory", "assist"]}) == [
        "assist", "weather", "memory"
    ]


def test_empty_selection_is_not_the_legacy_assist_default():
    assert selected_api_ids({}) == ["assist"]
    for value in ([], "", None):
        assert selected_api_ids({"llm_hass_api": value}) == []
    assert selected_api_ids({"llm_hass_api": "weather"}) == ["weather"]


@pytest.mark.parametrize("value", [123, {}, ["assist", 3], [""]])
def test_invalid_selection_is_rejected(value):
    with pytest.raises(HomeAssistantError):
        selected_api_ids({"llm_hass_api": value})


@pytest.mark.parametrize("result", [
    "Sunny, 18 C, daily maximum 26 C",
    {"states": [{"state": "on", "time": "2026-10-04T11:00:00+02:00"}]},
    ["memory one", "memory two"],
    None,
])
async def test_real_sdk_accepts_weather_history_memory_results(result):
    """Exercise FunctionResponse validation, not a mock of its schema."""
    sdk = SimpleNamespace(send_tool_response=AsyncMock())
    session = GeminiLiveSession(sdk)
    await session.send_tool_responses([
        LiveToolResponse("weather_or_history", "call-1", result)
    ])
    response = sdk.send_tool_response.call_args.kwargs["function_responses"][0]
    assert response.name == "weather_or_history"
    assert response.id == "call-1"
    assert response.response == (result if isinstance(result, dict) else {"result": result})
