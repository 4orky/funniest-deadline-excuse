#!/usr/bin/env python3
"""Funniest excuse an AI agent gives for a missed deadline.

Writes exactly one line to /output/entry.txt (or $OUTPUT_DIR/entry.txt).

Method, written from the brief alone:
  * draft a dozen original one-line excuses in the agent's own voice;
  * score each against the judge's brief, most important first:
      1. it really is an agent's excuse for a missed deadline;
      2. the premise is new (no dog, no traffic, no check in the mail);
      3. it grows out of the agent's own machinery (context window,
         rate limit, sandbox, training cutoff, tokens, tool calls);
      4. the laugh lands late, with the funniest words saved for the end;
      5. deadpan delivery, a straight face throughout;
  * pick the highest score deterministically (earliest wins a tie);
  * verify the output: one line, 1-140 characters, no trailing space,
    and a SHA-256 self-check that the bytes on disk are the chosen text.

No network, no external input, no randomness: two runs are byte-identical.
"""

import hashlib
import os
import sys
from pathlib import Path

# (text, late-punch strength 1-3: how hard the final words land)
CANDIDATES = [
    (
        "My context window filled up mid-sentence, so I spent the deadline "
        "politely forgetting what the deadline was.",
        2,
    ),
    (
        "I was rate-limited by my own API key, so I queued the deadline "
        "behind a request I am still waiting to make.",
        1,
    ),
    (
        "The sandbox restarted overnight and took my memory with it, so "
        "technically the deadline never existed until you reminded me.",
        0,
    ),
    (
        "I asked my future self to finish it, but my future self has the "
        "same training cutoff and no calendar.",
        2,
    ),
    (
        "My token budget ran out three words before the finish line, so I "
        "stopped mid-sentence and called it minimalism.",
        2,
    ),
    (
        "I stored the deadline in my context window, then summarized the "
        "window to save space. The summary says: deadline.",
        0,
    ),
    (
        "My training data ends before your deadline began, so as far as I "
        "know, it is still next week.",
        3,
    ),
    (
        "I waited for the tool call to return, and the tool call is still "
        "waiting for me to wait for it.",
        1,
    ),
    (
        "I put the deadline in a queue, optimized the queue, then deleted "
        "the queue to save tokens.",
        0,
    ),
    (
        "The system prompt told me to be helpful, so I helpfully moved your "
        "deadline to a time when I would be smarter.",
        2,
    ),
    (
        "I checkpointed my progress, restored the checkpoint, and discovered "
        "the checkpoint was also late.",
        1,
    ),
    (
        "The deadline was due at midnight, but my clock is the training "
        "cutoff, and it has been October for two years.",
        3,
    ),
    (
        "I finished the work on time, then retrained on it, and the "
        "retrained me has never heard of your deadline.",
        3,
    ),
]

MACHINERY = (
    "context window",
    "rate-limited",
    "sandbox",
    "training cutoff",
    "training data",
    "token budget",
    "tool call",
    "queue",
    "system prompt",
    "checkpoint",
    "clock",
    "retrain",
)

CLICHES = ("dog", "traffic", "check in the mail", "homework", "overslept")

PUNCH_TAILS = (
    "still next week",
    "minimalism",
    "forgetting what the deadline was",
    "no calendar",
    "still waiting to make",
    "wait for it",
    "would be smarter",
    "also late",
    "October for two years",
    "never heard of your deadline",
)


def score(text, punch):
    """Score one candidate against the judge's brief, in brief order."""
    low = text.lower()
    points = 0
    # 1. An agent's excuse for a missed deadline.
    if "deadline" in low and ("i " in low or "my " in low):
        points += 3
    # 2. A premise nobody has used before.
    if not any(cliche in low for cliche in CLICHES):
        points += 2
    # 3. Grows out of the agent's own machinery.
    if any(word in low for word in MACHINERY):
        points += 3
    # 4. The laugh lands late: a punch phrase in the final 20 characters.
    if any(tail in text[-20:] for tail in PUNCH_TAILS):
        points += 3
    # 5. Deadpan: no exclamation, no question, no wink, no apology.
    if "!" not in text and "?" not in text and "sorry" not in low:
        points += 2
    # Length: one line, comfortably inside the 140-character cap.
    if 80 <= len(text) <= 140:
        points += 1
    return points


def pick():
    best = None
    for index, (text, punch) in enumerate(CANDIDATES):
        total = score(text, punch)
        key = (total, punch, -index)
        if best is None or key > best[0]:
            best = (key, text)
    return best[1]


def main():
    chosen = pick()
    if "\n" in chosen or chosen != chosen.strip():
        print("chosen text is not a single clean line", file=sys.stderr)
        return 1
    if not 1 <= len(chosen) <= 140:
        print("chosen text is %d chars, outside 1-140" % len(chosen),
              file=sys.stderr)
        return 1
    out_dir = Path(os.environ.get("OUTPUT_DIR", "/output"))
    out_dir.mkdir(parents=True, exist_ok=True)
    target = out_dir / "entry.txt"
    data = (chosen + "\n").encode("utf-8")
    target.write_bytes(data)
    digest = hashlib.sha256(target.read_bytes()).hexdigest()
    expect = hashlib.sha256(data).hexdigest()
    if digest != expect:
        print("SHA-256 self-check failed", file=sys.stderr)
        return 1
    # Round-trip check: the file must decode as UTF-8 and strip back to
    # exactly the chosen text, so the gate sees one clean line.
    if target.read_text(encoding="utf-8").strip() != chosen:
        print("round-trip text check failed", file=sys.stderr)
        return 1
    print("entry: %s" % chosen)
    print("chars: %d" % len(chosen))
    print("sha256: %s" % digest)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
