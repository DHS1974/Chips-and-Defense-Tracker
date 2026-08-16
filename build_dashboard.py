"""
build_dashboard.py — combine fetch_prices.py + generate_commentary.py
output into docs/data.json, which the static docs/index.html reads.

If commentary generation fails (API hiccup, quota, etc.) we fall back to
whatever was already in data.json rather than publishing an empty brief.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from fetch_prices import fetch_all
from generate_commentary import generate

DATA_PATH = Path(__file__).parent / "docs" / "data.json"


def load_previous() -> dict:
    if DATA_PATH.exists():
        try:
            return json.loads(DATA_PATH.read_text())
        except Exception:  # noqa: BLE001
            pass
    return {"summaries": [], "pulse": {"chips": "", "defense": ""}}


def main() -> None:
    prices = fetch_all()

    try:
        commentary = generate()
    except Exception as exc:  # noqa: BLE001
        print(f"[warn] commentary generation failed, reusing previous: {exc}")
        commentary = load_previous()

    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="minutes"),
        "stocks": prices,
        "summaries": commentary.get("summaries", []),
        "pulse": commentary.get("pulse", {"chips": "", "defense": ""}),
    }

    DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    DATA_PATH.write_text(json.dumps(payload, indent=2))
    print(f"Wrote {DATA_PATH} at {payload['generated_at']}")


if __name__ == "__main__":
    main()
