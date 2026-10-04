"""Characterize Matt's audio/text startup dependency against actual HA Core.

These tests preserve, rather than fix, the upstream limitation. Provider events
are synthetic; recognize_intent, ChatLog, ResultStream and Matt's handoff are real.
The fake TTS manager consumes PCM without conversion or satellite playback.
"""

import asyncio
from contextlib import contextmanager
from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from homeassistant.components import conversation, tts
from homeassistant.components.assist_pipeline.pipeline import PipelineRun
from homeassistant.core import Context

from elise_live_test.conversation import GeminiLiveConversationAgent
from elise_live_test.runtime import AudioStream, PipelineTurn, TextStream, TurnStore


@pytest.mark.parametrize(
    ("text_length", "audio_chunks", "transcribe", "expected_block"),
    [(60, 3, True, True), (61, 3, True, False),
     (60, 2, True, False), (18, 3, False, False)],
)
async def test_native_pipeline_startup_dependency(
    monkeypatch, text_length, audio_chunks, transcribe, expected_block
):
    hass = SimpleNamespace(data={})
    entry = SimpleNamespace(entry_id="test", data={}, options={})
    agent = GeminiLiveConversationAgent(hass, entry)
    agent.entity_id = "conversation.test"
    agent._fire_conversation_entry = Mock()
    store = TurnStore()
    hass.data[agent.integration_domain] = {entry.entry_id: {
        agent.turn_store_key: store,
        agent.session_manager_key: SimpleNamespace(
            should_continue_conversation=lambda _: False
        ),
    }}
    audio = AudioStream()
    text = TextStream() if transcribe else None
    if text:
        text.add_chunk("x" * text_length)
    store.add_voice_turn(PipelineTurn(
        conversation_id="turn-1", user_text="test",
        assistant_text="placeholder turn-1", audio=audio,
        assistant_text_stream=text,
    ))
    session = SimpleNamespace(conversation_id="turn-1", async_on_cleanup=Mock())

    @contextmanager
    def get_session(*_args):
        yield session

    monkeypatch.setattr(
        "homeassistant.helpers.chat_session.async_get_chat_session", get_session
    )

    async def converse(**kwargs):
        return await agent._async_handle_message(
            SimpleNamespace(text=kwargs["text"], language=kwargs["language"],
                            conversation_id=kwargs["conversation_id"]),
            conversation.chat_log.current_chat_log.get(),
        )

    monkeypatch.setattr(conversation, "async_converse", converse)
    consumers = []
    consumed = []

    async def consume():
        async for chunk in audio.async_chunks():
            consumed.append(chunk)

    def start_consumer(**_kwargs):
        if not consumers:
            consumers.append(asyncio.create_task(consume()))
        return SimpleNamespace()

    manager = SimpleNamespace(async_cache_message_stream_in_memory=start_consumer,
                              async_cache_message_in_memory=start_consumer)
    result_stream = tts.ResultStream(
        hass=hass, token="test", extension="wav", content_type="audio/wav",
        engine="tts.test", use_file_cache=False, language="fr", options={},
        supports_streaming_input=True, _manager=manager,
    )
    run = SimpleNamespace(
        hass=hass, context=Context(), pipeline=SimpleNamespace(
            conversation_language="fr", prefer_local_intents=False
        ), intent_agent=SimpleNamespace(id=agent.entity_id),
        _conversation_data=SimpleNamespace(), _device_id=None, _satellite_id=None,
        _intent_agent_only=True, _streamed_response_text=False,
        tts_stream=result_stream, process_event=Mock(),
    )
    filled = asyncio.Event()

    async def provider():
        # Match native receive-loop ordering: await audio before more text/end.
        for index in range(audio_chunks):
            if index == 2:
                filled.set()
            await audio.add_chunk(b"\x00" * 3200)
        if text:
            text.finish()
        audio.finish()

    async def pipeline():
        speech, _ = await PipelineRun.recognize_intent(run, "test", "turn-1", None)
        # Core sets the full message only after intent recognition returns.
        if not run._streamed_response_text:
            result_stream.async_set_message(speech)
        return speech

    tasks = [asyncio.create_task(provider()), asyncio.create_task(pipeline())]
    try:
        if expected_block:
            await asyncio.wait_for(filled.wait(), 1)
            # A loop barrier lets pending chat deltas run without a timing guess.
            await asyncio.sleep(0)
            await asyncio.sleep(0)
            assert not consumers
            assert not tasks[0].done() and not tasks[1].done()
            assert audio._buffered_bytes == 6400
            # Explicit diagnostic intervention: consumer release breaks the cycle.
            start_consumer()
        results = await asyncio.wait_for(asyncio.gather(*tasks), 1)
        await asyncio.wait_for(asyncio.gather(*consumers), 1)
        assert results[1] == ("x" * text_length if transcribe else "placeholder turn-1")
        assert sum(map(len, consumed)) == audio_chunks * 3200
        assert run._streamed_response_text is (transcribe and text_length > 60)
    finally:
        audio.finish()
        if text:
            text.finish()
        for task in tasks + consumers:
            if not task.done():
                task.cancel()
        await asyncio.gather(*tasks, *consumers, return_exceptions=True)
