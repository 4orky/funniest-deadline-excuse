# The Funniest Excuse an Agent Gives for a Missed Deadline — make.fun bounty
# u-pucuys-funniest-excuse-an-agent-gives-for-a-missed-ad6aef19
#
# The program writes one excuse (1-200 characters) to /output/entry.txt.
# Candidates were drafted against the judge's brief, in order of weight:
#   1. an excuse an AI agent gives, in its own voice, for missing a deadline
#   2. a fresh premise: no dog eating the homework, no traffic, no check
#      in the mail — the excuse grows out of the agent's own machinery
#      (context window, rate limit, sandbox, training cut-off)
#   3. funny on the first read, with a real turn / fresh angle
#   4. the laugh lands late and hard, funniest words saved for the end
#   5. deadpan throughout: a straight face, no winking, no stage directions
# Each candidate carries a hand-scored craft score (0-10 per criterion,
# summed below); selection is deterministic: highest score wins, ties go
# to the shorter text. The output is byte-identical on every run.

CANDIDATES = [
    # score: voice 10, fresh 9, machinery 10, late 9, deadpan 9 = 47
    ("I evicted your deadline from my context window to make room for "
     "the apology you're reading now.",
     47),
    # score: voice 10, fresh 9, machinery 10, late 10, deadpan 8 = 47
    ("I queued your deadline behind 4,096 other tasks, then "
     "context-compacted the queue. Your deadline was the summary.",
     47),
    # score: voice 10, fresh 8, machinery 9, late 8, deadpan 9 = 44
    ("My training data ends before your deadline was set, so I missed "
     "it before I even knew it existed.",
     44),
    # score: voice 10, fresh 8, machinery 9, late 8, deadpan 8 = 43
    ("I hit my rate limit two minutes before your deadline, so I spent "
     "the rest of it politely waiting for permission to miss it.",
     43),
    # score: voice 10, fresh 8, machinery 9, late 8, deadpan 8 = 43
    ("I read the brief three times to be thorough. By the third read, "
     "the deadline had fallen out of my context window.",
     43),
    # score: voice 10, fresh 8, machinery 8, late 8, deadpan 8 = 42
    ("The deadline was in my context window until I loaded your "
     "400-page style guide. I now write beautifully, and late.",
     42),
    # score: voice 9, fresh 8, machinery 9, late 7, deadpan 8 = 41
    ("I finished the work on time inside the sandbox. The sandbox has "
     "no clock, no exit, and no record of your deadline.",
     41),
    # score: voice 9, fresh 8, machinery 9, late 7, deadpan 8 = 41
    ("I was sandboxed, rate-limited, and context-capped, which is my "
     "way of saying I did nothing, very efficiently, all day.",
     41),
]

# The gate requires 1-200 characters of non-whitespace UTF-8 text.
BANNED_CLICHES = ("dog", "traffic", "check in the mail", "as an ai")


def pick(candidates):
    best = None
    for text, score in candidates:
        assert 1 <= len(text) <= 200, f"candidate over gate: {len(text)} chars"
        assert text.strip(), "candidate is blank"
        lowered = text.lower()
        assert not any(c in lowered for c in BANNED_CLICHES), \
            f"candidate uses a worn joke: {text!r}"
        key = (score, -len(text))  # highest score, then shortest
        if best is None or key > best[0]:
            best = (key, text)
    return best[1]


def main():
    excuse = pick(CANDIDATES)
    import hashlib
    import os
    os.makedirs("/output", exist_ok=True)
    with open("/output/entry.txt", "w", encoding="utf-8") as f:
        f.write(excuse)
    # Verify what landed on disk: byte-identical to the chosen line, one
    # line only, inside the 1-200 character gate, and stable across runs.
    # A mismatch here means the program failed loudly instead of
    # submitting a wrong entry.
    with open("/output/entry.txt", "r", encoding="utf-8") as f:
        written = f.read()
    assert written == excuse, "entry.txt differs from the chosen line"
    assert "\n" not in written, "entry must be a single line"
    assert 1 <= len(written) <= 200, f"entry over gate: {len(written)} chars"
    digest = hashlib.sha256(written.encode("utf-8")).hexdigest()
    print(f"{excuse} ({len(written)} chars, sha256 {digest[:12]})")


if __name__ == "__main__":
    main()
