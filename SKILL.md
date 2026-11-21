---
name: app-store-keywords
description: Research and choose App Store and Google Play keywords for a mobile app from real data (Apple Ads search popularity, App Store autocomplete, competitor names, Astro difficulty and rank), then write the name, subtitle, keyword field, screenshot captions, custom product page and the Play title and descriptions. Use when the user asks for ASO, keyword research, a keyword field, subtitle ideas, or to optimize a store listing for search.
---

# App Store keywords

Chooses store keywords from data pulled the same day, and writes the listing text from them.
It ends at a keyword sheet plus proposed text. Changing a live listing is a separate step the user approves.

`$SKILL` below is this folder: `~/.claude/skills/app-store-keywords`.

## Rules

- **Pull, don't estimate.** Every score in the sheet comes from a tool on a stated date. If a source can't be reached, write that in the sheet instead of a number.
- **Read-only in ad accounts.** Never create, start, edit or pay for a campaign. Research panels that stage keywords must be cancelled, and you check afterwards that nothing was saved.
- **Don't create accounts** (Google Ads, Apple Ads) to get data. Say the source is unavailable.
- **Honest wording.** A keyword is only usable if the app really does that thing. Leave out competitor brand names, and, for health apps, leave out diagnosis, disease-detection, treatment and doctor-service wording. Keep a column saying why each excluded term was excluded.
- **No store changes without a yes.** Propose old-versus-new text first. An app already in review has to be pulled from review to change its metadata, so agree the text before submitting.
- **No account details in the sheet or in this skill**: no keys, tokens, account ids or spend figures.

## Method

### 1. Read how things currently work (15 minutes)

Scores and tools change. Before pulling data, check dated sources for: how Apple Ads reports search popularity this month, whether the popularity scale has had recent problems, and current indexing rules. Facts that held in November 2026:

- Apple's search uses the app name (30), subtitle (30), keyword field (100 bytes, comma-separated, no spaces) and primary category. Don't repeat a word across name, subtitle and keyword field; plurals count as repeats; skip "app" and filler words. Promotional text and the long description don't affect App Store ranking.
- Apple Ads popularity was distorted from late September 2025 (most terms reported at the minimum) and US values recovered from late October 2026. Treat any popularity history from that window with suspicion.
- Whether screenshot caption text is indexed is disputed: third parties observed it in 2025, Apple has not confirmed it. Write captions for readers first.
- Custom product pages can be assigned keywords for organic search, chosen only from the keyword field of the latest approved version.

### 2. Apple Ads: Monthly Search Term Popularity report (main demand source)

In Apple Ads (Advanced): **Insights** (top right of the Campaigns dashboard) → **Create new report** → report type menu → under "Advanced" choose **Monthly Search Term Popularity** (a weekly version sits next to it). It opens with the latest month and United States selected, without any campaign running. Download as CSV (the download icon offers XLSX or CSV). Don't save the report definition unless asked.

What it contains: for each of about 15 genres, the top 500 search terms with Rank in Genre, Search Popularity (1-100), Search Popularity (1-5) and popularity within the genre. In practice the lowest popularity in a genre is around 46 to 59, and there is no Medical genre.

```bash
python3 $SKILL/scripts/analyze_apple_ads.py report.csv 'budget|expense|invoice' [min_popularity]
```

Read the result both ways: terms that appear are high-volume head terms; a niche whose terms don't appear at all is entirely below the report's floor, and the report then can't rank those terms against each other. Say so plainly.

### 3. Apple Ads: popularity for specific terms (1 to 5)

For terms below the report's floor, the only free Apple number is the 1-5 dot scale. In an existing ad group: **Add Keywords** → paste up to about 45 comma-separated candidates in the "Add keywords" box → **Add**. The staged table shows one popularity value per keyword in the order typed (`apui-wc-popularity-dots`, attribute `value`). Read them, then **Cancel** → "I'm sure", and confirm the ad group's keyword list is unchanged.

- Wait for the table to render before reading; values read too early come back as 0.
- The left-hand "Related Keyword" list is a useful idea source but its dots are unreliable to scrape.
- This needs an ad group to exist. If the account has none, don't create a campaign; report that this source is unavailable.
- The 1-5 scale is coarse: most niche terms are 1 or 2. Use it to drop dead terms (1) and prefer 2+.

The Apple Ads Platform API has popularity endpoints (search-term-popularity query, keyword and phrase suggestions) but needs an API role and credentials set up by the account admin. Not used here.

### 4. Build a wide candidate list (aim for 100+)

```bash
python3 $SKILL/scripts/collect_candidates.py "seed one" "seed two" ...
```

Writes `candidates-autocomplete.csv` (App Store search suggestions per seed, US) and `candidates-competitors.csv` (names of apps returned for each seed, with rating counts). Both use public endpoints and send only the seed terms.

- Autocomplete carries no volume; it shows how people phrase searches and which brands dominate a seed.
- Competitor names show which words the category leaders put in their titles. Drop games, shopping and unrelated apps that share a seed word before ranking by rating count.
- **Subtitles**: fetch `https://apps.apple.com/us/app/id<id>` with a browser user agent. The app's own subtitle is the `<p class="subtitle ...">` directly after the page's `<h1>`. Do not search the page for `"subtitle":` in its embedded JSON: those belong to related apps and gave wrong strings. If no such paragraph follows the `<h1>`, the app has no subtitle; say so.
- **Screenshot captions** are only in the images. The lookup endpoint (`https://itunes.apple.com/lookup?id=<id>&country=us`) returns `screenshotUrls`; download the first six per app, join them into a contact sheet (`ffmpeg ... hstack`), and read the captions from the image. Note which competitor claims the app can't honestly make.
- Add the terms already in the listing and plain descriptions of what the app does, then score everything in step 3.

### 5. Astro: difficulty and current rank

Astro does not need to be tracking a word already. Add every candidate to the app in Astro, let it score them, then read the scores.

**Adding keywords by hand (the MCP server cannot).** Drive the Astro Mac app; it has no scripting dictionary, so use the screen:

1. Select the app in Astro's sidebar and press ⌘K (Add Keywords). The dialog first loads a "most searched" list; wait for it.
2. Put comma-separated keywords in the field and click **Add**. They appear as chips under "Keywords to be added", and Astro names any that are already tracked. Then click **Done**.
3. **At most 50 keywords per round.** Over 50, Done shows "You inserted too many keywords" and the whole staged set is lost. Work in rounds of 40: open, paste, Add, Done, wait about 30 seconds, repeat.
4. Scoring takes a few seconds per round. Each new keyword gets popularity, difficulty and the app's position with today's date.

What worked for automation on macOS, and what didn't:

- Setting the field's value through accessibility displayed the text once, then failed or timed out on later rounds. Clicking the field and pasting (⌘V) worked every time. Save and restore the user's clipboard around it.
- The dialog is a sheet whose contents accessibility mostly can't see, so click by window-relative coordinates taken from a capture of Astro's own window (`screencapture -l <window id>` captures it without bringing it forward).
- Before every click or keystroke, check that Astro is the frontmost app and stop if it isn't. A keystroke sent when another app has focus lands in that app.
- Astro's toolbar Refresh did not re-score keywords that were added in an earlier year; they keep their old difficulty date. Record it.

**Reading the scores.** Either the Astro MCP server (`get_app_keywords`, `search_rankings`; read-only, and it must be switched on in Astro's home screen), or Astro's local database opened read-only:

```bash
DB="$HOME/Library/Containers/matteospada.it.ASO/Data/Library/Application Support/Astro/Model.sqlite"
sqlite3 -header -csv "file:$DB?mode=ro" "select k.ZTEXT keyword, k.ZPOPULARITY popularity, k.ZDIFFICULTY difficulty,
  k.ZCURRENTRANKING rank, date(k.ZLASTUPDATE+978307200,'unixepoch','localtime') updated
  from ZKEYWORD k join ZAPPLICATION a on a.Z_PK=k.ZAPPLICATION where a.ZNAME='App Name' order by 2 desc;"
```

Never write to that database. A rank of 1000 means the app is outside the results Astro tracks ("not ranked"), not position 1000. Popularity 5 is Astro's minimum.

Limits:

- Astro covers the App Store, not Google Play.
- Astro's popularity is its own estimate on top of Apple's data. It separates niche terms far better than the 1-5 dots, and the two mostly disagree only at the bottom (terms Apple rates 1 that Astro puts around 20). Where they disagree, use Apple Ads and treat those terms as weaker.
- Look up every term added to Astro in the Apple Ads panel too (step 3), so both numbers exist for every row.

### 6. Score and choose

One row per keyword: Apple Ads report popularity (or "not in report"), Apple Ads 1-5, Astro popularity and difficulty, relevance 0-3, where it is used, why it was excluded.

- Target terms with relevance 2-3 and the best popularity available; where Astro has numbers, prefer popularity 20+ and difficulty under about 60.
- Strongest relevant terms go in the name, next in the subtitle, single leftover words in the keyword field.
- Fill the keyword field with single words that combine with name and subtitle words into the scored phrases ("tracker" + "expense" in the name covers "expense tracker"). Don't pad it with terms scored 1 just to reach 100 characters; list what you left out and why.

### 7. Write the App Store text

- Name: keep the brand, add the best term, 30 characters.
- Subtitle: two or three of the next terms, readable, 30 characters.
- Keyword field: 100 bytes, no spaces, no repeats of name or subtitle words.
- Promotional text and description: for readers, not ranking.
- Screenshot captions: one top keyword per caption, short enough to read at thumbnail size.
- Count every field with a script before typing it in.

### 8. Custom product page (optional)

App Store Connect → Custom Product Pages → create a page for one keyword cluster with its own promotional text and screenshots, and tick its keywords. The selectable keywords are the words in the **live** version's keyword field, so a term that moved to the name or subtitle can't be assigned. The page is added to the same review submission as the app version (choose the existing draft submission, not "Create New Submission").

### 9. Google Play is a separate method

Play has no keyword field and publishes no search volume. It reads the title (30), short description (80) and full description (4,000). Do its research separately and write its own report; do not reuse the App Store numbers as if they were Play's.

**Read the current rules first** (Google's metadata policy, store listing best practices and Health apps policy; they change). Held in November 2026:

- Title and short description: no price words ("free", "no ads"), no ranking claims ("#1", "best"), no emojis, no all caps unless it is the brand.
- Full description: no keyword lists, no repeated or unrelated keywords, don't repeat the short description.
- A health app that is not a medical device must say it "is not a medical device and does not diagnose, treat, cure, or prevent any medical condition", tell users to consult a healthcare professional, and state device compatibility if the camera is used for a health function.
- Vendors agree on weight (title, then short description, then full description) and disagree on density (roughly 2-3%, or three to five natural mentions). Treat those as observations, not rules.

**Collect, in this order:**

1. **Play Console data, for every app on the account.** Grow users: expand the Acquire card and look at the breakdown menu. If "Traffic source" shows only explore, paid and direct, and not attributed, and there is no search-term dimension, record that. Other apps on the same account show how Play traffic behaves even when the target app has none. Also check Store listings → custom listing → "Search keyword" chooser, and Policy status.
2. **Play autocomplete.** The old endpoints (`market.android.com/suggest/SuggRequest`, `suggestqueries.google.com ... ds=apps`) are dead. Type each seed into the search box on `play.google.com/store/apps` in the browser and read the five suggestions from the listbox. Type each seed twice: bare, and with a trailing space or a next letter ("skin", "skin ", "skin ch"), because the bare word is often dominated by games. Suggestions carry no volume; they show phrasing and intent.
3. **Competitor listings.**

   ```bash
   python3 $SKILL/scripts/play_listings.py "seed one" "seed two" ...
   ```

   Writes `play-search.csv` (top 12 app ids per search) and `play-listings.json` (title, short description, installs, full description) from public Play pages. The short description is the page's `itemprop="description"` meta tag. From these, tabulate: which words are in titles, installs of the first result per search (how strong the competition is), description length, and how often the main terms repeat.
4. **Google Trends**, target country, past 90 days, five terms per comparison. It is web search and has no Play filter. The page holds a hidden table with each term's average; read that rather than the chart. Tool phrases ("skin scanner") are usually too thin to trust; problem words ("rash") show what people actually call the thing.
5. **Keyword Planner** gives absolute web volumes and is the best free number available, but needs a Google Ads account. Never create one without the user's explicit yes. With a yes: at ads.google.com choose New Google Ads Account and look on the first screen for "Switch to Expert Mode", then "Create an account without a campaign" (business name, billing country, time zone, currency; no billing). In November 2026 that link was missing: the new account went straight into a "Create your first campaign" wizard and every account page, Keyword Planner included, redirected back to it. If that happens, stop and report it; do not build a campaign or add billing to get past it. When Keyword Planner does open: Tools → Keyword Planner → "Get search volume and forecasts" for the shortlist and "Discover new keywords" for ideas, target country, last 12 months, download the CSV next to the other data.

**Write the text:**

- Title: brand plus the phrase Play itself suggests and where the first result is weakest. It can differ from the App Store name.
- Short description: two or three more suggested phrases in one readable sentence.
- Full description: about as long as the competitor median, main terms in the first two sentences, each term in real sentences, sections that cover the topic (how it works, what it covers, privacy, who it is for), and the required health wording.
- Leave out any word a store has rejected before, even if it is the top suggestion; say so in the report.

**Save, don't send.** In the default store listing editor: fill the fields, Next, Save. That stores the change in Publishing overview "ready to send for review". Sending for review is a separate step the user approves.

## Output

- `keywords.csv` with the scores, sources and dates, plus the downloaded report and candidate files next to it.
- A Play report with its own data files (autocomplete, competitor listings, Trends, Play Console findings) and the title, short and full description with reasoning.
- Old-versus-new text for every field on each store, with character counts.
- A plain list of what could not be measured.
- When the user asks for a report: one Markdown file with method and sources, what each source showed and its limits, competitor findings, each recommended field with its reasoning, and the full scored table.
