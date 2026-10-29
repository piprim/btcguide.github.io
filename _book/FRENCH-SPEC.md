# French translation: source in this repository, every output in both languages

Design, 2026-10-28. Supersedes the "French workflow" section of
`_book/HEXO-PAGES-SPEC.md` and reverses two of its decisions: French is
no longer hand-written in the blog repository, and machine translation
is no longer a non-goal.

## Intent

The guide exists in English only. The owner wants a French version that
is published on blog.piprime.fr as Hexo pages next to the English ones,
and as a French PDF and EPUB, built by the same pipeline that already
produces the English book and Hexo pages from this repository.

The French text will be produced later by an AI translator. The
translator is not part of this design, but the layout must give it a
clean job: one French file per English file at a mirrored path, and a
record of which English commit each French file was translated from so
that only changed files need re-translating.

Why the French lives here and not in the blog: every shared paragraph,
every generated box, link, navigation line and footer is produced by the
generator from the Markdown sources. Hand-written Hexo pages freeze
copies of all of that in 75 files and can never reach the PDF/EPUB
build. Keeping the French as source lets one pipeline serve both
languages and keeps each French page one translation away from its
English original.

## Goals

- A `fr/` tree in this repository mirrors every file the generators
  read. The book build and the Hexo generator take a language and read
  from that tree.
- Hexo output for both languages from one run of `make hexo-pages`:
  English under `/btcguide/`, French under `/fr/btcguide/`, same
  relative URL for every page, so the NexT theme's language switch
  (which maps `/x/` to `/fr/x/` by path) works on every page in both
  directions.
- Media is shared. French pages reference the same `/media/btcguide/...`
  files; nothing under `fr/` holds images.
- A page that has no French source yet still exists in the French
  outputs as a stub: blank, a one-line French notice that the page is
  not yet translated, and a link to the English version.
- French PDF and EPUB, built locally and by the existing GitHub Action,
  next to the English ones.
- A staleness report run from this repository alone, listing French
  files that are missing or behind their English source, with the git
  history in between.
- `make hexo-sync` syncs both languages and keeps refusing to overwrite
  anything it did not generate.

## Non-goals

- The translator itself (the AI step that writes `fr/` files). This
  design only fixes its input and output contract, below.
- Serving French on the Jekyll site (GitHub Pages). `fr/` is excluded
  from Jekyll.
- Translating screenshots, diagrams or any other media.
- French spell checking. `fr/` is excluded from the English spell
  check; a French check can be added when the translator exists.
- Any change to the English site, book or Hexo output beyond what the
  language parameter needs.

## Anti-goals

- A French tree whose page set differs from the English one: a missing
  French page must become a stub, never a 404 or a dropped chapter.
- French text silently going stale after its English source changed,
  with no report that says so.
- Mixed-language pages produced by accident (English paragraphs leaking
  into a translated French page through a shared include).
- A second copy of the generator for French. One code path, one
  language parameter.

## Facts this design relies on

- `_book/build.py` resolves every source from `ROOT` (`index.html` for
  order and nesting, `_pages/...` for pages, `_includes/...` for shared
  paragraphs, root `*.md` pages, `LICENSE`) and writes `_book/out/book.md`.
  `_book/hexo.py` reuses it and writes `_book/out/hexo/page/btcguide/...`
  and `_book/out/hexo/media/btcguide/...`.
- Blog facts verified 2026-10-26 in `HEXO-PAGES-SPEC.md`: `i18n_dir:
  :lang`, so a page under `source/fr/...` has `lang` `fr`; the theme's
  language switch is path-based; media lives at `source/media/<project>/`.
- `.spellcheck.yml` globs `_includes/**`, `_pages/**`, `*.md`, `*.html`
  from the repository root; `fr/` is not matched today and must stay
  unmatched.
- `.github/workflows/book.yml` runs `python3 _book/build.py`, then
  pandoc for PDF and EPUB, and attaches both to the rolling `book`
  release.

## Source layout

```
fr/
  index.html                      translated copy of index.html (intro + TOC)
  disclaimer.md, contributors.md, compensation.md
  _pages/<same relative path>.md  one per English page, advanced siblings included
  _includes/hw/*.md, hosted/*.md  one per English include
  translated_from.json            manifest, see below
```

Rules:

- A French file is a translation of the English file at the same path
  relative to the repository root. Same front matter keys (`title`,
  `description`), same Liquid includes, same links and image paths as
  the English. The translator changes prose only; links, image paths,
  include names and front-matter keys stay byte-identical. The
  `next_name="..."` label passed to `next_steps.md` is prose and is
  translated; `next_url` and the include name are not.
- The structure (page set, order, nesting, which pages have an advanced
  sibling) always comes from the English `index.html` and `_pages/`
  tree. `fr/index.html` supplies the French intro and the French link
  labels, and the build fails if its TOC does not link the same URLs in
  the same order as the English TOC. This is the one French file the
  French build cannot do without, so it is the first file to translate.
  While it is missing, the French side is skipped with a clear warning:
  `make hexo-pages` still writes the English pages, `make hexo-sync`
  still syncs them, `make book-fr` and the CI French step exit 0 with
  the warning and produce nothing. A present `fr/index.html` that fails
  the TOC check is an error, not a skip.
- `LICENSE` is not translated. The French license page shows the same
  MIT text with a French one-line lead-in from the strings table.
- `fr/` is added to `exclude:` in `_config.yml`. Nothing under `fr/`
  is ever read by Jekyll or the spell check.

## The manifest `fr/translated_from.json`

A JSON object mapping each English source path (relative to the
repository root, e.g. `_pages/equipment.md`, `_includes/hw/psbt.md`,
`index.html`, `disclaimer.md`) to the short sha of the last commit that
touched that English file when the French file was written.

One mechanism for every kind of file (includes have no front matter, so
front-matter `translated_from` would need a second mechanism). The
translator writes the entry when it writes the French file; a human
translating by hand does the same. A French file with no manifest entry
is reported as untranslated, not stale, and is still used if it exists.

## Staleness: `make stale`

Replaces `hexo-stale` and needs no blog path. For every English source
file the generators read, compare `git log -1 --format=%h -- <file>`
with the manifest:

- no French file: `MISSING <path>`
- French file but no manifest entry: `UNTRACKED <path>`
- manifest sha older than the current one: `STALE <path>: a -> b`, then
  the `git log --oneline a..b -- <path>` indented beneath it
- a French file with no English counterpart: `ORPHAN <path>`

Exit 1 if anything is listed. This design does not add it to any
workflow: it is the translator's local work list, and it can only ever
join CI as a separate, allowed-to-fail check while translation is
incomplete.

## Generator changes

One language parameter, default `en`, on both `build.py` and `hexo.py`.
A `src(lang, rel)` helper returns `ROOT / rel` for English and
`ROOT / "fr" / rel` for French. Everything that reads a source file goes
through it; everything that reads structure (TOC walk, `page_file`,
`advanced_of`) keeps reading the English tree.

**Strings table.** The fixed English text the generators emit becomes a
dict keyed by language, both languages in `build.py`: book title and
subtitle, "Introduction", "Appendix", "License" and its lead-in,
"Table of Contents", "Offline copies", "Known Issues: " prefix,
" » Advanced Considerations" suffix, the advanced-considerations box,
"Next Section", the prev/next arrows, the footer ("Source", "MIT
License", "Last updated"), and the not-yet-translated notice. The
French wording of these is left to the builder.

**Display titles in French.** In this order: the French file's own
`title` when the file exists (as English does); else, for a stub, the
French TOC label when the TOC links the page; else the English title
(stubs of root pages and advanced siblings).
The "Known Issues: " prefix and the advanced suffix come from the
strings table as in English.

**Stub pages.** When `src("fr", rel)` does not exist for a page, the
page is rendered as: display title by the rule above, then only the
notice, which links to the English page:
`/btcguide/<path>/` on the blog, the absolute blog URL in the book.
Hexo stubs keep the prev/next navigation and the footer so a reader can
move on; the footer's source link points at the English source file. A
stub never appears in the stale report as anything but `MISSING`.

**Includes.** A French page whose `{% include %}` names a file missing
under `fr/_includes/` fails the build with a message naming the include.
Falling back to the English include would produce a mixed-language
page (anti-goal). The translator therefore translates includes first;
until then the French build is all stubs, which is fine.

**Links.** French sources carry the same site-relative links as English.
The Hexo generator rewrites them to `/fr/btcguide/...`, image links to
`/media/btcguide/...` as today. The existing dead-link check runs
against the French page set, which is by construction the English one.

**Anchors (added after the final review, 2026-10-29).** Fragment links
stay identical to the English (`#choosing-the-second-hardware-wallet`)
while headings are translated, so a translated heading's own anchor
would never match. Both generators therefore give every heading of a
translated page the English heading's kramdown id as well, by position:
Hexo emits a second `<a id>`, the book appends `{#english-id}` to the
heading. This requires a French page to have exactly as many headings
as its English original, includes counted; a mismatch fails the build
naming the file. The home page and stubs are exempt (the home TOC is
generated, stubs have no headings).

**Hexo front matter and output.** French pages carry `lang: fr`, the
same keys as English, `btcguide_source` listing the French sources,
`btcguide_commit` the last commit touching them. Output goes to
`_book/out/hexo/page/fr/btcguide/<path>/index.md`. Media is written
once, under `media/btcguide/`. The home page's "Offline copies" section
links the French PDF and EPUB on the French home page.

**Book.** `_book/out/fr/book.md` with `lang: fr` in its pandoc front
matter (pandoc and xelatex then use French hyphenation and typography),
rendered to `_book/out/fr/btcguide-fr.pdf` and `.epub`, the same names
the release uses. The French book
contains stubs for untranslated pages like the Hexo output does.

## Make targets

- `make book`, `make pdf`, `make epub`: English, unchanged.
- `make book-fr`, `make pdf-fr`, `make epub-fr`: French, same recipes
  with `LANG=fr` passed to `build.py` and the `fr/` output directory.
- `make hexo-pages`: both languages, one run.
- `make hexo-sync BLOG=...`: adds `rsync -a --delete` of
  `page/fr/btcguide/` to `$BLOG/fr/btcguide/`; the refusal check now
  also covers `$BLOG/fr/btcguide`. Any French pages hand-written or
  scaffolded in the blog earlier must be deleted by the owner before
  the first sync; the refusal message says so.
- `make stale`: as above.
- `hexo-fr-scaffold` and `hexo-stale` are removed, with their code and
  tests.

## CI

`book.yml` builds the French book after the English one and attaches
`btcguide-fr.pdf` and `btcguide-fr.epub` to the same `book` release.
A French build failure fails the workflow like an English one.

## Translator contract (for the later piece)

Input: `make stale` output. Order: `index.html` first (its TOC must
link the same URLs in the same order as the English one, labels
translated), then `_includes/`, then pages. For each listed English
path: read the English file, read the existing French file if any,
write the French file at `fr/<path>`, keeping links, image paths,
include names and front-matter keys identical, then set
`translated_from.json[path]` to the current English sha. Nothing else
in this design changes when the translator arrives.

## Decided by the owner (this conversation)

- French source lives in this repository and will be generated by an
  AI translator later.
- Both languages are published on the blog as Hexo pages; media is
  shared, screenshots are not translated.
- Untranslated page: blank, "not yet translated" notice, link to the
  English version.
- French PDF and EPUB are built.
- While `fr/index.html` is missing, the French build is skipped with a
  warning rather than failing or being hand-translated now.
- A present `fr/index.html` whose TOC does not match the English one
  stays a hard error, knowingly: once the French TOC exists, every
  change to the English TOC must be mirrored in `fr/index.html` in the
  same commit or the Book workflow and `make hexo-pages` fail until it
  is. Warn-and-skip was offered and declined (2026-10-29).

## My calls (not the owner's)

- `fr/` at the repository root, excluded from Jekyll and from the spell
  check, rather than `_pages/fr/` served by GitHub Pages with English
  chrome.
- Structure always from the English tree; `fr/index.html` must match
  it, checked at build time.
- One manifest file for translation provenance instead of per-file
  front matter.
- Missing French include fails the build rather than falling back to
  English.
- Stubs keep navigation and footer on the blog; the book stub is just
  title and notice.
- French display titles: the French file's title, else the TOC label,
  else English.
- `make stale` stays out of CI in this design.
- A manifest commit that contains the file's last change (for example
  `HEAD` at translation time) counts as current, not stale.
- Tests build their throwaway French tree at `.fr-test/` (git-ignored)
  with `build.FR` pointed there, so they keep running once a real `fr/`
  exists; only the two `make`-driven tests skip in that case.
- Spec location follows the repository's precedent (`_book/*-SPEC.md`)
  rather than `docs/superpowers/specs/`.

## Left to the builder

- French wording of the strings table and of the notice.
- Exact shape of the language parameter (env var like `REPO`, or a CLI
  argument) and of the Makefile pattern rules.
- Test layout; `python3 -m pytest _book` must stay green and cover the
  stub, the TOC mismatch failure, the missing-include failure and the
  stale report.
- README and CLAUDE.md updates describing `fr/`, the manifest and the
  new targets; removal of the hand-written-French paragraphs.
