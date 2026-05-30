"""Unit tests for transcript speech analyzer."""

from app.services.speech_transcription import _merge_transcripts
from app.speech.analyzer import analyze_speech


def test_analyze_detects_fillers_and_scores():
    transcript = (
        "Um, I basically led a team and, you know, we delivered the project. "
        "I think it was successful. Like, it was um, really good actually."
    )
    result = analyze_speech(transcript, duration_seconds=30.0)

    assert result.word_count > 10
    assert result.filler_word_count >= 4
    assert result.words_per_minute > 0
    assert 0 <= result.fluency_score <= 100
    assert 0 <= result.communication_score <= 100
    assert any(s.word == "um" and s.count >= 1 for s in result.filler_word_stats)
    assert any(s.word == "like" for s in result.filler_word_stats)


def test_merge_long_transcript_chunks():
    prior = "I worked on a distributed system that handled millions of requests"
    segment = "millions of requests per day and um basically we scaled it"
    merged = _merge_transcripts(prior, segment)
    assert "millions of requests" in merged
    assert merged.count("millions of requests") == 1
    assert "um" in merged or "basically" in merged


def test_analyze_empty_duration_estimates_wpm():
    result = analyze_speech(
        "One two three four five six seven eight nine ten.", duration_seconds=None
    )
    assert result.words_per_minute > 0
