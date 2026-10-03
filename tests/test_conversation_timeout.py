"""Regression tests for the live conversation response timeout."""

import asyncio

import pytest

from elise_live_test.conversation import _async_iter_with_inactivity_timeout


@pytest.mark.asyncio
async def test_slow_tool_processing_does_not_consume_model_response_timeout():
    async def responses():
        yield "tool call"
        yield "answer after tool"

    response_stream = _async_iter_with_inactivity_timeout(
        responses(),
        timeout_seconds=0.01,
    )

    assert await anext(response_stream) == "tool call"
    await asyncio.sleep(0.02)  # Simulate Home Assistant executing the tool.
    assert await anext(response_stream) == "answer after tool"


@pytest.mark.asyncio
async def test_model_response_timeout_still_applies_between_events():
    async def responses():
        yield "first event"
        await asyncio.sleep(0.02)
        yield "late event"

    response_stream = _async_iter_with_inactivity_timeout(
        responses(),
        timeout_seconds=0.01,
    )

    assert await anext(response_stream) == "first event"
    with pytest.raises(TimeoutError):
        await anext(response_stream)
