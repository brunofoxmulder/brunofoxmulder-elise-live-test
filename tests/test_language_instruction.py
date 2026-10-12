"""Tests for the Gemini native-audio conversation language guard."""

from elise_live_test.stt import _add_conversation_language_instruction


def test_language_instruction_keeps_original_prompt_and_pipeline_language():
    prompt = _add_conversation_language_instruction("Original prompt", "fr")

    assert prompt.startswith("Original prompt\n\n")
    assert "conversation language is 'fr'" in prompt
    assert "reply only in that language" in prompt
    assert "instead of guessing" in prompt


def test_language_instruction_has_safe_default():
    assert "conversation language is 'en'" in _add_conversation_language_instruction(
        "Prompt", None
    )
