# Cyberwave Docs

Source for [docs.cyberwave.com](https://docs.cyberwave.com), built with Mintlify. The sidebar lives in `docs.json`. Every page is an `.mdx` file whose path is its URL.

## How the docs are organized

The docs are built around one idea: **Cyberwave connects AI models to the physical world**. The navigation has four tabs:

| Tab | Reader's question | Sidebar groups |
| --- | --- | --- |
| Docs | What is this, how do I try it, and how do I put AI on a robot? | Get started (incl. the Connect AI to robots overview) · AI agents · AI models · Control (manual input · skills · workflows · VLA · RL) · Learn · Run on edge or cloud · Platform · For integrators · Help |
| Robots | Does my hardware work, and how do I connect it? | Hardware in Cyberwave (concept first) · Featured hardware by form factor · Edge computers · Add your robot |
| Tutorials | What can I build with what I have? | Grouped by the hardware you need |
| Reference | What is the exact signature or field? | SDKs & CLI · AI developer tools (MCP, Claude skill) · Driver SDK · Workflow nodes · Config files · APIs · Changelog |

URLs did not move in the 2026-09 restructure. Folder names still follow the old layout, and the tab a page appears in is set only in `docs.json`.

## Writing a page

- Frontmatter: `title` (sentence case), `description` (140 characters or fewer, states the outcome), `icon` (Font Awesome name).
- Tutorials and how-tos open with an "At a glance" line: time, level, what you need.
- End every page with `## Next steps` and a `<CardGroup>` of 2–4 cards.
- Link to the final page path, never to a path that only works through a redirect.
- Code must match the current SDK. Onboarding code uses `cw.affect("playground")`, which is free. If a page uses `"simulation"`, say that it starts a billable MuJoCo instance.
- Never publish "stub" notes. Put unfinished work in MDX comments: `{/* TODO(docs): what is missing */}`.
- Spelling: "SO-101", "catalog".

## Home-page images

The hero and the architecture diagram on the home page are PNGs rendered from HTML sources, so they look the same everywhere Mintlify serves them. Edit `images/src/home-hero.html` or `images/src/architecture.html`, then run:

```bash
pip install playwright && playwright install chromium
python3 scripts/render_images.py
```

## Checks

```bash
python3 scripts/check_docs.py        # nav, orphans, redirects, internal links, stub markers
npx mint broken-links                # Mintlify link check (needs images present)
python3 scripts/gen_cli_reference.py --check   # CLI reference is in sync with the installed cyberwave-cli
```

Both checks run in CI on every pull request (`.github/workflows/docs-checks.yml`).

## Preview

```bash
npx mint dev
```
