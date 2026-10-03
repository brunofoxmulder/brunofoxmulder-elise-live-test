"""Regression tests for tool-routing instructions in typed conversations."""

from types import SimpleNamespace

import pytest

from elise_live_test.conversation import LiveModelConversationAgent


@pytest.mark.asyncio
async def test_calendar_instruction_is_added_even_with_custom_prompt(monkeypatch):
    api = SimpleNamespace(
        api_prompt="Home Assistant Assist API tools",
        tools=[],
        custom_serializer=None,
    )

    async def fake_async_load_tools(_hass, _config, _llm_context):
        return api

    monkeypatch.setattr(
        "elise_live_test.conversation.async_load_tools",
        fake_async_load_tools,
    )
    agent = SimpleNamespace(
        hass=object(),
        entry=SimpleNamespace(
            data={"system_instruction": "Ma consigne personnalisée"},
            options={},
        ),
        integration_domain="elise_live_test",
        transcribe_config_key="transcribe_output",
        default_transcribe=False,
        default_system_instruction="Instructions par défaut",
        supports_search_grounding=False,
    )

    _api, _tools, instruction = await LiveModelConversationAgent._async_get_llm_api(
        agent,
        object(),
    )

    assert "Ma consigne personnalisée" in instruction
    assert "Home Assistant Assist API tools" in instruction
    assert "MUST call the relevant Home Assistant calendar tool" in instruction
    assert "rendez-vous" in instruction
