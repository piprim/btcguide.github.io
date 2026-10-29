# Publishing the guide as Hexo pages on blog.piprime.fr

> The "French workflow" section and the hand-written-French decisions below are superseded by FRENCH-SPEC.md (2026-10-28): French is generated from the `fr/` tree in this repository.

Design spec, 2026-10-26. Implemented by `_book/hexo.py`, which reuses helpers from `_book/build.py`.

## Intent

Publish this guide on https://blog.piprime.fr as a tree of Hexo **pages**
(not posts), in English and French, with this repository as the single
source of truth for the English text. The model is the owner's existing
Asymptote gallery: a separate builder generates Markdown into a build
directory, and an rsync step copies it into the blog's `hexo/source/`.

Why pages: the guide is 160 PDF pages with 48 screenshots. One post is
unreadable and untranslatable; posts per section fight the blog's
chronological model. Pages keep the guide's own URL tree and let the
French version be translated one page at a time.

## Goals

- `make hexo-pages` writes a complete English page tree plus media into
  `_book/out/hexo/`, deterministically, from the current checkout.
- `make hexo-sync BLOG=<path to hexo/source>` rsyncs English pages and
  media into the blog. It never touches French pages.
- Every page is readable on its own: title, breadcrumb-like prefix for
  known issues, links to its advanced page and to the next step, exactly
  as the Jekyll layout and `next_steps` include provide on the site.
- French pages are hand-written in the blog repository, one per English
  page, at the mirrored path. Tooling creates scaffolds for missing
  French pages and reports which French pages are stale.
- The generated output passes the same leak checks as the book build:
  no Liquid, no kramdown attributes, no unescaped braces, no dead
  internal links.

## Non-goals

- Machine translation. The French text is written by the owner.
- Changing the Jekyll site, the PDF/EPUB build, or upstream content.
- Comments, categories, tags, search integration, or NexT theme changes
  beyond one menu entry.
- Supporting Hexo renderers other than the blog's `hexo-renderer-markdown-it-plus`.

## Anti-goals (what would make this a failure even if it runs)

- English pages that drift from the guide because someone edited them in
  the blog repo. Generated files must say so in a comment and the sync
  must overwrite them.
- A French page silently showing stale content after the English source
  changed, with no way to notice.
- Internal links that leave the blog or land on the Jekyll site.
- Headings that collide with the page title (`h1` is the theme's).

## Facts about the target blog (verified 2026-10-26)

From https://github.com/pivaldi/blog.piprime.fr, branch `master`,
Hexo root `hexo/`:

- `url: https://blog.piprime.fr`, `root: /`.
- Posts use `permalink: :lang/:id/` and live in `source/_posts/<lang>/`.
  Pages are plain files: `source/<path>/index.md` serves at `/<path>/`.
- `i18n_dir: :lang`: a page under `source/fr/...` has `lang` `fr`;
  anything else is English. French pages exist today at
  `source/fr/about/index.md` and `source/fr/index.md`. The theme's
  language switch maps `/x/` to `/fr/x/` by path.
- Renderer: `hexo-renderer-markdown-it-plus`, `html: true`. Pandoc-style
  `{#id}` heading attributes are **not** supported; raw HTML is.
- Theme: NexT (owner's fork). Sidebar TOC enabled with numbering.
  Menu is configured in `hexo/_config.next.yml` under `menu:`; the
  Asymptote entry shows nested menus are possible.
- `default_layout: post` applies to posts only; pages need no `layout`.
- `external_link.enable: true`, so outbound links open in a new tab
  automatically.
- Media convention: `source/media/<project>/...`, referenced as
  `/media/<project>/...`.
- Nunjucks runs before Markdown, so literal `{` and `}` in content must
  be written as `&lbrace;` and `&rbrace;` (the Asymptote builder's
  `fixMDFile` does exactly this).
- The Asymptote builder emits this front matter for a page:
  `title`, `date`, `lang: en`, `description`. Its pages start at `h2`.
- The builder's sync is `rsync -auv --delete` with include/exclude
  patterns, pages to `source/asymptote/`, media to `source/media/asymptote/`.

## Output layout (build directory)

```
_book/out/hexo/
  page/btcguide/index.md                        -> /btcguide/
  page/btcguide/why-multisig/index.md           -> /btcguide/why-multisig/
  page/btcguide/why-multisig-advanced/index.md  -> /btcguide/why-multisig-advanced/
  page/btcguide/setup-wallets/index.md          -> /btcguide/setup-wallets/
  page/btcguide/setup-wallets/advanced/index.md -> /btcguide/setup-wallets/advanced/
  page/btcguide/setup-wallets/paper/index.md    -> /btcguide/setup-wallets/paper/
  page/btcguide/known-issues/hardware/coldcard/index.md
  page/btcguide/disclaimer/index.md, contributors, compensation, license
  media/btcguide/img/...                        -> /media/btcguide/img/...
```

One Hexo page per guide page, same relative URL as on the Jekyll site,
under the prefix `/btcguide/`. `index.md` pages and their `advanced.md`
siblings keep the Jekyll convention. The prefix is a constant at the top
of the generator so it can be changed once.

French pages live only in the blog repository at
`source/fr/btcguide/<same path>/index.md`.

## Page list and order

Derived from `index.html` exactly as the book build does: walk the two
`<ol>` trees ("Guide" and "Known Issues & Benefits"), emit each linked
page, and after each guide page emit its `-advanced` sibling if the file
exists. Then the root pages `disclaimer`, `contributors`, `compensation`,
and a generated `license` page holding the MIT text. The walk order is
also the prev/next order.

## Front matter (English)

```
---
title: Setup Paper Wallet
date: 2021-02-08 14:03:11        # git author date of the last commit touching the source file
lang: en
comments: false
tree_view: true                  # handled by the blog's scripts/tree-view-filter.js
description: <first sentence of the body, plain text, max 160 chars>
btcguide_source: _pages/setup-wallets/paper.md
btcguide_commit: <short sha of the last commit touching the source file>
---
<!-- Generated by _book/build.py from <repo url>; do not edit, edit the source and re-sync. -->
```

Title rules copy `_layouts/default.html`: advanced pages get the
suffix " » Advanced Considerations"; pages under `known-issues/` get the
prefix "Known Issues: ". The index page title is "10x Security Bitcoin
Guide".

`date` and `btcguide_commit` come from the last commit touching **any
source of the page**: the page file plus every include it expands
(`git log -1 -- <page> <include>...`); the index page's sources are
`index.html` and the root pages. This is the builder-check decision:
a change to a shared include such as `_includes/hosted/limited_hw.md`
re-renders several pages and must mark them changed, or `hexo-stale`
stays silent. `btcguide_source` therefore lists all sources,
space-separated, and the stale report runs `git log a..b -- <sources>`.
If the working tree has uncommitted changes to any source, the
generator warns and uses today's date with the sha suffixed `-dirty`;
it does not refuse, so previews work.

## Body transforms

Reuse `render()` from `build.py` with a Hexo output mode. Differences
from the book mode, in order of application:

1. Expand `{% include %}` as today. **Keep** `next_steps.md` semantics
   instead of dropping them: at the point of the include, emit
   - a "Advanced Considerations" box linking to the sibling advanced page,
     unless the page is advanced or sets `no_advanced_link: true`
     (same rule as the include);
   - a "Next Section: <name>" link when the include passes
     `next_url`/`next_name`, resolved through the link rule below.
   The box can be a blockquote; no theme markup needed.
2. Strip remaining Liquid tags. Replace `{{ site.github.repository_url }}`
   with the hosting repository URL and `{{ page.title }}` with the page
   title. The hosting repository for Hexo output is the fork that
   publishes the blog, `piprim/btcguide.github.io` (builder-check
   decision): that is where the `book` release with the PDF and EPUB
   exists, and where the "Source:" footer links must point. The
   Makefile passes it as `REPO`, overridable; CI keeps using
   `GITHUB_REPOSITORY`.
3. Heading levels: normalise per page as the book does (remap distinct
   levels to consecutive ones, clamp to no jumps), with the page's
   top-most heading at `h2`. `h1` is reserved for the theme's title.
4. Kramdown attributes: `{:width="85%" class="border_image"}` on an
   image becomes an HTML image tag `<img src="..." width="85%">` with
   the alt text preserved, because markdown-it ignores width syntax and
   raw HTML is enabled. Other `{:...}` are stripped.
5. Links. Internal site links (`/foo/bar`, relative `paper`,
   `../setup-computer/computer`, with optional `#fragment`) resolve to
   `/btcguide/<path>/#fragment` using the same resolver as the book
   (`posixpath.normpath`). Bare `<​/foo/bar>` autolinks are handled too.
   External links are untouched.
   **Heading ids are explicit** (builder-check decision): every heading
   in a body is preceded by `<a id="..."></a>`, with the id computed by
   the generator's own slug rule (lowercase, non-alphanumerics to
   dashes, leading non-letters dropped: the rule `resolve_link` already
   applies to fragments). Links to fragments use the same rule. This
   avoids emulating the blog renderer's slugifier, whose handling of
   apostrophes and digits is not known; `Shamir's Secret Sharing
   Scheme` is a live case. The theme's sidebar TOC uses the renderer's
   own ids for its links, which is fine: both anchors land on the same
   heading.
6. Assets: every `/assets/<sub>/<file>` link becomes
   `/media/btcguide/<sub>/<file>`, not only images. The guide links
   `/assets/guide/bip39_wordlist.pdf` from the paper wallet page, and
   the link check would otherwise fail on current content.
7. Horizontal rules `---` stay (no YAML risk in Hexo), but a page must
   not start with one.
8. Braces: after all other transforms, replace `{` with `&lbrace;` and
   `}` with `&rbrace;` outside fenced code blocks. On current content no
   literal brace survives the earlier transforms (checked by the
   builder review), so this is a guard for future content; the leak
   check must still fail on any raw brace.
9. Trailing: append a footer line "Source: <link to the source file in
   the repository> · MIT License · Last updated <date>".

## Media

Copy `assets/img/` and `assets/guide/` to
`_book/out/hexo/media/btcguide/<sub>/` as-is (no re-encoding; about
35 MB). Only files actually referenced by generated pages need
copying, but copying the folders is simpler and the sync's `--delete`
keeps the blog in step. Decision for the builder.

## Index page `/btcguide/`

Built from `index.html`: the intro paragraphs (converted from HTML as
the book does, minus the "download as PDF" paragraph), then the two
tables of contents as nested Markdown lists linking to the generated
pages, then links to the PDF and EPUB on the `book` release of the
hosting repository.

## Navigation inside pages

Each page ends with prev/next links in walk order ("← Setup Paper
Wallet · Setup Keystone →") in addition to the `next_steps` box, so
readers can traverse without the index. The theme's sidebar TOC covers
within-page navigation.

## French workflow

- French pages are written by hand in the blog repo at
  `source/fr/btcguide/<path>/index.md`. Front matter: `title` (French),
  `date`, `lang: fr`, `comments: false`, `tree_view: true`,
  `description`, and `translated_from: <sha>`, the `btcguide_commit` of
  the English page it was translated from. The scaffold emits all of
  these.
- `make hexo-fr-scaffold BLOG=<hexo/source>` creates, for every English
  page without a French counterpart, a French page containing the
  French front matter skeleton, a one-line notice in French that the
  page is not translated yet, and the English body. It never overwrites
  an existing French page.
- `make hexo-stale BLOG=<hexo/source>` prints every French page whose
  `translated_from` differs from the current `btcguide_commit` of its
  English page, with the `git log --oneline a..b -- <source>` between
  the two so the translator sees what changed. Exit code 1 if any are
  stale, so it can run in CI later.
- Internal links in French pages must point to `/fr/btcguide/...`. The
  scaffold already rewrites them; hand-written pages follow the same
  rule. `hexo-stale` also warns on `/btcguide/` links found in French
  pages.

## Sync

`make hexo-sync BLOG=<hexo/source>` runs:

```
rsync -a --delete  _book/out/hexo/page/btcguide/   $BLOG/btcguide/
rsync -a --delete  _book/out/hexo/media/btcguide/  $BLOG/media/btcguide/
```

No `-u`: a blog-side edit that kept the generated-file comment would
otherwise survive because its mtime is newer. Generated files always
win.

It refuses to run if `$BLOG/btcguide/` exists and contains a file
without the generated-file comment (someone edited in place). It never
writes under `$BLOG/fr/`.

## Blog-side one-time setup (manual, documented in README)

- Add a menu entry in `hexo/_config.next.yml`, for example
  `Bitcoin Guide: /btcguide/ || fa fa-bitcoin`, and its French label in
  the theme's language file if the fork localises menu labels.
- Nothing else: pages render with the default page layout.

## Checks the generator must perform (fail the build)

- Every internal link resolves to a generated page, and every fragment
  to a heading in that page.
- No `{%`, `{{`, `{:` left; no raw `{`/`}` outside fenced code.
- No `h1` in any body. No heading level jumps.
- Every referenced image exists in the media output.
- Page count equals the number of TOC entries plus advanced siblings
  plus the four root pages.

## Makefile targets to add

`hexo-pages`, `hexo-sync`, `hexo-fr-scaffold`, `hexo-stale`. The
existing `hexo` target (single Markdown post) can be removed once pages
work; it was a stepping stone.

## Decided during the builder check (my calls, not the owner's)

- Explicit `<a id>` anchors on every heading rather than emulating the
  renderer's slugifier.
- Staleness tracks every source a page is rendered from, includes
  included; dirty trees warn rather than refuse.
- Hosting repository for Hexo output is the publishing fork.
- All `/assets/` subfolders are mirrored under `/media/btcguide/`.
- `rsync` without `-u`.

## Decided by the owner

- Pages, not posts.
- English generated from this repository; French hand-written in the
  blog repository.
- Same approach as the Asymptote builder: build directory plus rsync.
- URL prefix is `/btcguide/`.
- The Known Issues part is published too, not only the Guide part.
- An untranslated French page shows a one-line French notice followed
  by the English body.
- Generated pages set `comments: false` and `tree_view: true` (the
  blog's tree-view filter script picks the latter up).

## Left to the builder

- Whether `render()` is refactored into shared transforms with two
  output modes or the Hexo mode is a separate function reusing helpers.
- Exact Markdown for the advanced/next boxes and the footer.
- Whether to copy all images or only referenced ones.
- How `hexo-stale` formats its report.

## Open questions

None. The builder check and the owner's answers above resolved them.
