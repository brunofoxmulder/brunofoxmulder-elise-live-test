"""Focused non-regression tests for Élise multi-API/MCP integration."""

from types import SimpleNamespace

import pytest

from elise_live_test.tools import async_load_tools, selected_api_ids


def test_selected_api_ids_defaults_to_assist():
    assert selected_api_ids({}) == ["assist"]


def test_selected_api_ids_preserves_multiple_and_deduplicates():
    assert selected_api_ids({"llm_hass_api": ["assist", "memory", "assist"]}) == [
        "assist",
        "memory",
    ]


def test_selected_api_ids_empty_is_intentional():
    assert selected_api_ids({"llm_hass_api": []}) == []


@pytest.mark.asyncio
async def test_async_load_tools_requests_all_selected_apis(monkeypatch):
    calls = []

    async def fake_get_api(*, hass, api_id, llm_context):
        calls.append(api_id)
        return SimpleNamespace(
            tools=[SimpleNamespace(name="HassTurnOn"), SimpleNamespace(name="Memory")],
        )

    monkeypatch.setattr("elise_live_test.tools.llm.async_get_api", fake_get_api)
    result = await async_load_tools(
        object(),
        {"llm_hass_api": ["assist", "agent_memory"]},
        object(),
    )

    assert result is not None
    assert calls == [["assist", "agent_memory"]]


@pytest.mark.asyncio
async def test_async_load_tools_empty_selection_does_not_fallback(monkeypatch):
    async def forbidden(*args, **kwargs):
        raise AssertionError("async_get_api must not be called")

    monkeypatch.setattr("elise_live_test.tools.llm.async_get_api", forbidden)
    assert await async_load_tools(object(), {"api_id": []}, object()) is None


@pytest.mark.asyncio
async def test_async_load_tools_rejects_reserved_tool_name(monkeypatch):
    async def fake_get_api(*, hass, api_id, llm_context):
        return SimpleNamespace(tools=[SimpleNamespace(name="end_conversation")])

    monkeypatch.setattr("elise_live_test.tools.llm.async_get_api", fake_get_api)
    with pytest.raises(Exception, match="Conflicting tool name"):
        await async_load_tools(
            object(),
            {"llm_hass_api": ["assist"]},
            object(),
        )
