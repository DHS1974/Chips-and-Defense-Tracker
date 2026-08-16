"""
generate_commentary.py — ask Claude (with web search) to write the day's
"Today's recommendations" blurbs and two sector-pulse paragraphs, based
on current news, for the same watchlist fetch_prices.py covers.

Requires the ANTHROPIC_API_KEY environment variable (set as a GitHub
Actions secret — see README.md).
"""

from __future__ import annotations

import json
import os

import anthropic

MODEL = "claude-sonnet-5"

PROMPT = """\
You write a short daily markets brief for a personal dashboard covering two
watchlists: semiconductor stocks (SanDisk, Micron, Nvidia, Broadcom, Taiwan
Semiconductor, AMD) and European defense manufacturers (Rheinmetall, Saab,
Thales, Leonardo, BAE Systems, Kongsberg Gruppen).

Search the web for today's analyst ratings, price target changes, and
notable news for these companies, then respond with ONLY a single valid
JSON object (no markdown fences, no preamble) matching this shape:

{
  "summaries": [
    {
      "ticker": "SNDK",
      "sector": "chips",
      "label": "<short rating label, e.g. 'Strong Buy'>",
      "body": ["<1-2 short paragraphs, plain text, paraphrased in your own words, no direct quotes>"]
    }
  ],
  "pulse": {
    "chips": "<2 short paragraphs on the semiconductor sector today, plain text>",
    "defense": "<2 short paragraphs on the European defense sector today, plain text>"
  }
}

Rules:
- Cover every one of the 12 tickers listed above in "summaries" (you may
  group 2-3 tickers into one entry with a combined "ticker" field like
  "NVDA / AVGO / TSM" if the news is the same across them, as long as
  every company is mentioned somewhere).
- Never invent numbers you didn't find; if you're not confident of a
  specific price target or analyst count, describe the direction/rating
  qualitatively instead.
- This is NOT investment advice — keep the tone factual and descriptive
  ("analysts are...", "the stock is trading...") not prescriptive
  ("you should buy...").
- Paraphrase everything; never copy sentences from sources verbatim.
"""


def generate() -> dict:
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    response = client.messages.create(
        model=MODEL,
        max_tokens=3000,
        tools=[{"type": "web_search_20250305", "name": "web_search"}],
        messages=[{"role": "user", "content": PROMPT}],
    )

    text = "".join(block.text for block in response.content if block.type == "text")
    text = text.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    return json.loads(text)


if __name__ == "__main__":
    print(json.dumps(generate(), indent=2))
