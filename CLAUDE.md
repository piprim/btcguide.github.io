# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

Jekyll static site for the "10x Security Bitcoin Guide" (https://btcguide.github.io), rendered by GitHub Pages. No plugins, no build step beyond Jekyll itself. Content is Markdown; the only "code" is Liquid in `_layouts/default.html` and `_includes/`.

## Commands

```bash
bundle exec jekyll serve        # local preview at http://127.0.0.1:4000
pyspelling -c .spellcheck.yml   # spell check (~3s); CI runs this on every push/PR
```

Spell check needs `aspell` and `pip install pyspelling`. It is the only CI check (`.github/workflows/spellcheck.yml`). When adding a legitimate new word (product name, acronym), append it to `.wordlist.txt`; do not reword content to dodge the checker. Text inside `code`/`pre` is skipped, so backtick-quote commands and identifiers rather than adding them to the wordlist.

## Architecture

**Routing.** `_config.yml` declares `_pages` as a collection with `permalink: /:path`, so `_pages/setup-wallets/coldcard.md` serves at `/setup-wallets/coldcard` and `_pages/foo/index.md` at `/foo/`. Every page gets `layout: default` via config defaults; front matter only needs `title`. Root-level `*.md` (contributors, disclaimer, compensation) and `index.html` are regular Jekyll pages.

**Advanced-page convention (URL-driven, not front-matter-driven).** Each guide step has an optional companion page named `<page>-advanced.md` (or `advanced.md` beside an `index.md`). The layout, breadcrumbs, and `_includes/next_steps.md` all detect this by inspecting `page.url` for `advanced`/`-advanced`:
- `default.html` appends " » Advanced Considerations" to the `<h1>` and prefixes "Known Issues:" for anything under `known-issues/`.
- `next_steps.md` auto-renders an "Advanced Considerations" call-out linking to the sibling `-advanced` page unless the current page is itself advanced or sets `no_advanced_link: true`. Pass `next_url`/`next_name` to also render the "Next Section" link.
- `breadcrumbs.html` derives crumbs purely from URL segments, with hardcoded labels for `known-issues`, `hosted`, `hardware`, `software`, `protocols`.

Consequence: renaming a page or adding one without a matching `-advanced` sibling will produce a dead link from the call-out unless you set `no_advanced_link: true`.

**Shared snippets.** `_includes/hw/*.md` and `_includes/hosted/*.md` are reusable paragraphs about common hardware-wallet / hosted-service shortcomings, included across the `known-issues/` pages. Edit the include, not each page, when the shared text changes.

**Navigation.** Top nav bar comes from `_data/navigation.yml`. The guide's table of contents is hand-maintained in `index.html`; adding a page means adding it there too.

**Styling.** Bootstrap 4 and jQuery from CDN; local overrides in `_sass/main.scss`, imported by `assets/css/styles.scss`.
