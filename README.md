# Chips & Steel — automated daily dashboard

A static dashboard tracking semiconductor and European defense stocks,
refreshed every morning by a GitHub Action and served for free on
GitHub Pages.

## How it works

- `docs/index.html` — the page itself. Static; never changes.
- `docs/data.json` — the day's data (prices, ratings, written commentary).
  Regenerated daily and committed back to the repo by the workflow below.
- `fetch_prices.py` — pulls live price/target/rating per ticker via
  `yfinance` (free, no API key).
- `generate_commentary.py` — asks Claude (with web search) to write the
  "Today's recommendations" blurbs and sector-pulse paragraphs.
- `build_dashboard.py` — combines both into `docs/data.json`. If the
  commentary step fails for any reason, it falls back to the previous
  day's text rather than publishing an empty page.
- `.github/workflows/daily-update.yml` — runs the above at 07:30
  Europe/Zurich time (two cron lines cover CET and CEST, since GitHub
  Actions cron is UTC-only and doesn't know about daylight saving).

## One-time setup

1. **Create a GitHub repo** and push this folder's contents to it
   (`main` branch).

2. **Add your Anthropic API key as a secret**:
   Repo → Settings → Secrets and variables → Actions → New repository
   secret → name it `ANTHROPIC_API_KEY`, paste your key.
   (Get one at console.anthropic.com if you don't have one — note this
   uses paid API credits, not your claude.ai subscription; each run is
   a handful of web searches plus a few thousand tokens, so cost per
   day is small, but keep an eye on it.)

3. **Enable GitHub Pages**:
   Repo → Settings → Pages → Source: "Deploy from a branch" → Branch:
   `main`, folder: `/docs` → Save.
   GitHub will give you a URL like
   `https://<your-username>.github.io/<repo-name>/` — that's your
   permanent dashboard link.

4. **Trigger the first run manually** so you don't have to wait until
   tomorrow morning: Repo → Actions → "Daily dashboard update" →
   "Run workflow". After it finishes (~1-2 min), refresh your Pages
   URL.

From then on it runs automatically every day at 07:30 Zurich time.

## Testing locally (optional)

```
pip install -r requirements.txt
export ANTHROPIC_API_KEY=sk-...
python build_dashboard.py
```
Then open `docs/index.html` directly in a browser (or run
`python -m http.server` from the repo root and visit
`http://localhost:8000/docs/`).

## Adjusting the watchlist

Edit the `WATCHLIST` list at the top of `fetch_prices.py` — add or
remove `(ticker, name, country, sector)` tuples. Tickers must be in
Yahoo Finance's format (e.g. `RHM.DE` for Rheinmetall on Xetra,
`SAAB-B.ST` for Saab on Stockholm). The `generate_commentary.py` prompt
also lists the companies by name — update that list to match if you
change the watchlist, so the written commentary stays in sync.

## Notes / limitations

- `yfinance` is unofficial and occasionally rate-limited or missing
  fields for a given ticker — the dashboard just shows "—" for
  whatever's missing rather than failing.
- The written commentary is generated fresh each day from a live web
  search, so wording will vary run to run — that's expected, not a bug.
- This is not investment advice; it's an automated aggregation of
  public analyst coverage, refreshed daily.
