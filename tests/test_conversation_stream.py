"""Late transcript chunks must still reach Matt's conversation handoff."""

import asyncio
from types import SimpleNamespace
from unittest.mock import Mock

from elise_live_test.conversation import GeminiLiveConversationAgent
from elise_live_test.runtime import AudioStream, PipelineTurn, TextStream, TurnStore


async def test_voice_handoff_waits_for_late_text_and_keeps_every_delta():
    entry = SimpleNamespace(entry_id="test", data={}, options={})
    hass = SimpleNamespace(data={})
    agent = GeminiLiveConversationAgent(hass, entry)
    agent.entity_id = "conversation.test"
    agent._fire_conversation_entry = Mock()
    store = TurnStore()
    manager = SimpleNamespace(should_continue_conversation=lambda _: True)
    hass.data[agent.integration_domain] = {
        entry.entry_id: {
            agent.turn_store_key: store,
            agent.session_manager_key: manager,
        }
    }
    text = TextStream()
    audio = AudioStream()
    text.add_chunk("Oui, je vois que ")
    store.add_voice_turn(PipelineTurn(
        conversation_id="turn-1", user_text="quand ?",
        assistant_text="placeholder turn-1", audio=audio,
        assistant_text_stream=text,
    ))
    deltas = []
    first_delta = asyncio.Event()

    class ChatLog:
        async def async_add_delta_content_stream(self, _agent_id, stream):
            async for delta in stream:
                deltas.append(delta)
                if "content" in delta:
                    first_delta.set()
                yield delta

    task = asyncio.create_task(agent._async_handle_message(
        SimpleNamespace(text="quand ?", language="fr", conversation_id="turn-1"),
        ChatLog(),
    ))
    await asyncio.wait_for(first_delta.wait(), 2)
    assert not task.done()
    text.add_chunk("le scénario a été activé à 02h33.")
    text.finish()
    audio.finish()
    response = await asyncio.wait_for(task, 2)
    expected = "Oui, je vois que le scénario a été activé à 02h33."
    assert "".join(delta.get("content", "") for delta in deltas) == expected
    assert response.response.speech["plain"]["speech"] == expected
