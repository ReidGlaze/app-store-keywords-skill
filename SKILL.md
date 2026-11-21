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
- Competitor names show which words the category leaders put in their titles. Subtitles and screenshot captions are not available from these endpoints; read them on the product pages if needed (an attempt to scrape subtitles from page HTML returned wrong strings).
- Add the terms already in the listing and plain descriptions of what the app does, then score everything in step 3.

### 5. Astro: difficulty and current rank

If the Astro MCP server is connected, `get_app_keywords` and `search_rankings` return popularity, difficulty and rank for keywords Astro already tracks. Limits found in practice:

- The server is read-only: it cannot add keywords or trigger a refresh. Opening the Astro app refreshed popularity values, while each keyword's difficulty and rank kept an old timestamp. Record the timestamp you see.
- Astro covers the App Store, not Google Play.
- Where Astro and Apple Ads disagree on popularity, use Apple Ads.

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

Play has no keyword field. It reads the title (30), short description (80) and full description (4,000); stuffing risks rejection, and price words such as "free" in the short description trigger a promotion-guideline notice.

Look for Play's own data first:

- Play Console → Grow users: acquisition by traffic source. A "search term" breakdown only appears once the app has enough Play search traffic.
- Play Console → Store listings → Create custom listing → target audience "Search keyword" → keyword chooser. It shows historical visitors per keyword group, or "No historical search data available".
- Google Ads Keyword Planner shows web search volume, not Play volume; treat it as a loose proxy, and only if an account already exists.

If none of these has data, say so and use the App Store terms as a proxy. Put the main term in the title, two or three in the short description, and repeat the main terms a few times in natural sentences through the full description. A custom store listing for a search-keyword cluster can be saved as a draft for the user to review.

## Output

- `keywords.csv` with the scores, sources and dates, plus the downloaded report and candidate files next to it.
- A Play sheet listing what Play data existed.
- Old-versus-new text for every field on each store, with character counts.
- A plain list of what could not be measured.
