"""Stall detector for the daily pulse pipeline.

The pipeline has several code paths that end with the workflow reporting SUCCESS while
nothing was published: no unseen candidate, every candidate URL dead, Gemini rejected
all three attempts, the API budget exhausted, a model retired. Each is individually
harmless for a day and individually invisible, and together they are how an unattended
pipeline dies quietly — green ticks all the way down while the site stops updating.

Rather than alarm on each cause separately, this checks the OUTCOME: how long is it
since anything actually reached the dataset. That single test covers every cause above,
including causes nobody has thought of yet, which is the point.

Exit 1 when the newest entry is older than the threshold. Intended to run as its own
workflow step with `if: always()`, AFTER the commit step, so it never blocks a publish
that did succeed.

    python devops/check_pulse_health.py [--max-age-days N] [--quiet]
"""
import json
import os
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fetch_catering_pulse import parse_any_date          # one date parser, not two

DATA_FILE = "src/data/pulseData.json"
DEFAULT_MAX_AGE_DAYS = 3


def newest_entry(entries):
    """The most recently ARRIVED entry, by added_at, falling back to pub_date.

    added_at is when the item reached this site; pub_date is when the source blog
    published it and can be years earlier, so added_at must win wherever it exists.
    """
    best, best_when = None, None
    for e in entries:
        when = parse_any_date(e.get("added_at") or e.get("pub_date", ""))
        if best_when is None or when > best_when:
            best, best_when = e, when
    return best, best_when


def main(argv):
    max_age = DEFAULT_MAX_AGE_DAYS
    if "--max-age-days" in argv:
        max_age = int(argv[argv.index("--max-age-days") + 1])
    quiet = "--quiet" in argv

    if not os.path.exists(DATA_FILE):
        print(f"::error::{DATA_FILE} is missing entirely.")
        return 1

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        entries = json.load(f)

    if not entries:
        print(f"::error::{DATA_FILE} contains no entries.")
        return 1

    entry, when = newest_entry(entries)
    if when is None or when.year < 2000:
        print("::error::No entry carries a parseable added_at or pub_date, so pipeline "
              "health cannot be determined. Treating as a failure rather than guessing.")
        return 1

    age_days = (datetime.now(timezone.utc) - when).total_seconds() / 86400.0
    stalled = age_days > max_age

    dated = sum(1 for e in entries if e.get("added_at"))
    lines = [
        "### Pulse health",
        "",
        "| check | value |",
        "| :--- | :--- |",
        f"| entries | {len(entries)} |",
        f"| newest arrival | `{entry.get('id')}` {entry.get('slug', '')} |",
        f"| age of newest | {age_days:.1f} days |",
        f"| threshold | {max_age} days |",
        f"| entries carrying added_at | {dated} of {len(entries)} |",
        f"| verdict | {'**STALLED**' if stalled else 'healthy'} |",
    ]
    summary = "\n".join(lines)
    if not quiet:
        print(summary)

    step_summary = os.getenv("GITHUB_STEP_SUMMARY")
    if step_summary:
        with open(step_summary, "a", encoding="utf-8") as fh:
            fh.write(summary + "\n")

    if stalled:
        print(f"::error::The pulse dataset has not gained an entry in {age_days:.1f} days "
              f"(threshold {max_age}). Every run may still be reporting success -- check "
              f"the 'reason' output of recent Daily Catering Pulse runs: archive-exhausted "
              f"means the sources are spent and a new feed is needed; all-candidates-dead "
              f"points at a network or user-agent problem; a generation-* reason means "
              f"Gemini is rejecting or unavailable.")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
