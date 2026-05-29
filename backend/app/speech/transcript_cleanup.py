"""Remove duplicate phrases from browser speech transcripts."""


def collapse_repeated_phrases(text: str, *, min_block_words: int = 10) -> str:
    """Remove consecutive duplicate blocks (browser speech often loops the same phrase)."""
    words = text.split()
    if len(words) < min_block_words * 2:
        return text.strip()

    changed = True
    while changed and len(words) >= min_block_words * 2:
        changed = False
        max_size = min(len(words) // 2, 120)
        for size in range(max_size, min_block_words - 1, -1):
            idx = 0
            while idx + size * 2 <= len(words):
                block = words[idx : idx + size]
                nxt = words[idx + size : idx + size * 2]
                if block == nxt:
                    words = words[: idx + size] + words[idx + size * 2 :]
                    changed = True
                    break
                if size >= 8:
                    matches = sum(
                        1
                        for i, w in enumerate(block)
                        if i < len(nxt) and w.lower() == nxt[i].lower()
                    )
                    if matches >= int(size * 0.85):
                        keep = block if len(block) >= len(nxt) else nxt
                        words = words[:idx] + keep + words[idx + size * 2 :]
                        changed = True
                        break
                idx += 1
            if changed:
                break
    return " ".join(words)
