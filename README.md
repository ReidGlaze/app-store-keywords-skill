# app-store-keywords

A [Claude Code](https://claude.com/claude-code) skill for App Store and Google Play keyword research.

It pulls search-demand data the same day (Apple Ads' Monthly Search Term Popularity report and the 1 to 5 popularity scale, App Store autocomplete, competitor app names, and Astro difficulty and rank when Astro is connected), scores a wide candidate list, and writes the app name, subtitle, keyword field, screenshot captions, an optional custom product page, and the Google Play title and descriptions.

**It never starts or pays for an ad campaign, and it does not change a live store listing without your say-so.** It ends at a keyword sheet and proposed text.

## Requirements

| Need | For |
|---|---|
| Python 3 | The two scripts |
| An Apple Ads account you can sign in to | The popularity report and the 1 to 5 scale (no spend needed for the report) |
| Astro with its MCP server (optional) | Difficulty and current rank |
| Play Console access (optional) | Google Play search-term data, if the app has enough traffic |

## Install

```bash
git clone https://github.com/ReidGlaze/app-store-keywords-skill.git ~/.claude/skills/app-store-keywords
```

## Run

In Claude Code, type `/app-store-keywords`, or ask:

> Research App Store keywords for my app and propose a new subtitle and keyword field.

The scripts also run on their own:

```bash
SKILL=~/.claude/skills/app-store-keywords

# Filter a downloaded Apple Ads "Monthly Search Term Popularity" CSV
python3 $SKILL/scripts/analyze_apple_ads.py report.csv 'budget|expense|invoice' 20

# Collect App Store autocomplete suggestions and competitor app names for seed terms
python3 $SKILL/scripts/collect_candidates.py "budget planner" "expense tracker"
```

[SKILL.md](SKILL.md) has the full method, including what did not work.

## Good to know

- The monthly report lists only the top 500 terms per genre. A niche app's terms may all sit below it.
- The 1 to 5 scale is coarse, and Apple's popularity data was unreliable between late 2025 and late 2026.
- Google Play has no keyword field and usually no search-term data for small apps; the skill says so rather than guessing.
- The scripts use public Apple endpoints and send only the seed terms you give them.

## License

MIT. See [LICENSE](LICENSE).
