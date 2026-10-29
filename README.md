# btcguide.github.io

For regular users, just visit <https://btcguide.github.io/> to see GitHub Pages render this content as a static website.

---

For advanced users, you can host this locally with [jekyll](https://jekyllrb.com/) (setup instructions: [Ubuntu](https://jekyllrb.com/docs/installation/ubuntu/); [macOS](https://jekyllrb.com/docs/installation/macos/)):
```bash
$ bundle exec jekyll serve
```

Then visit: <http://127.0.0.1:4000>

To spell check (takes ~3s):
```bash
$ pyspelling -c .spellcheck.yml 
Spelling check passed :)
```

Notes:
* See `.wordlist.txt` for all the exception words.
* `$ brew install aspell && pip install pyspelling` are needed.

## PDF and EPUB

A GitHub Action builds the whole guide into `btcguide.pdf` and `btcguide.epub` on every push to master and attaches them to the `book` release.
Locally, with `pandoc` installed (and `xelatex` for a PDF identical to the published one):

```
make spellcheck   # same check as CI
make epub         # _book/out/btcguide.epub
make pdf          # _book/out/btcguide.pdf (uses calibre if xelatex is missing)
make epub-fr      # _book/out/fr/btcguide-fr.epub, from the French sources (see below)
make pdf-fr       # _book/out/fr/btcguide-fr.pdf
```

The French PDF and EPUB are attached to the same release as `btcguide-fr.pdf` and `btcguide-fr.epub`.

## Hexo pages for the blog

The guide is also published on `blog.piprime.fr` as a tree of Hexo pages, English under `/btcguide/` and French under `/fr/btcguide/`, both generated here. Design: `_book/HEXO-PAGES-SPEC.md` and `_book/FRENCH-SPEC.md`.

    make hexo-pages                          # _book/out/hexo/: page/btcguide/..., page/fr/btcguide/... and media/btcguide/...
    make hexo-sync BLOG=../blog/hexo/source  # rsync both languages into the blog; generated files always win

`REPO=https://github.com/<fork>` overrides the repository used in "Source:" footers and release links.
Dates come from `git log`, so a shallow clone needs `fetch-depth: 0`.

Blog-side setup, once: add a menu entry in `hexo/_config.next.yml`, e.g. `Bitcoin Guide: /btcguide/ || fa fa-bitcoin`
(and its French label in the theme's language file if the fork localizes menu labels). Pages render with the default page layout.

`hexo-sync` refuses to run while the blog holds a page under `btcguide/` or `fr/btcguide/` that it did not generate; delete such files (French pages hand-written in the blog before the `fr/` tree existed included) or edit the source here.

## French translation

`fr/` mirrors every source the generators read, at the same relative path: `fr/index.html` (intro and table of contents), `fr/_pages/...`, `fr/_includes/...`, `fr/disclaimer.md` and the other root pages. Structure (page set, order, advanced siblings) always comes from the English tree; a page with no French file yet becomes a stub that says it is not translated and links the English page. Media is shared, nothing under `fr/` holds images. Jekyll and the spell check never read `fr/`.

- While `fr/index.html` is missing, `make book-fr`, `make hexo-pages` and the CI French step skip French with a warning. Once it exists, its table of contents must link the same pages in the same order as the English one, or the build fails: a change to `index.html` must be mirrored in `fr/index.html` in the same commit.
- A French page whose `{% include %}` names a file missing under `fr/_includes/` fails the build (no English fallback, so pages are never half-translated).
- Headings are translated freely, but a French page must have exactly as many headings as its English original (includes counted): the generators give each translated heading the English heading's anchor as well, by position, so fragment links such as `#choosing-the-second-hardware-wallet` are kept identical and still resolve. A heading-count mismatch fails the build naming the file.
- `fr/translated_from.json` maps each English source path to the commit it was translated from. `make stale` compares it with `git log` and lists what is `MISSING`, `UNTRACKED`, `STALE` (with the commits in between) or `ORPHAN`, and fails if anything is listed. It is the translator's work list and is not run in CI.

Translating a file, by hand or by the AI translator: `index.html` first, then `_includes/`, then pages. Keep links (fragments included), image paths, include names and front-matter keys identical to the English file; translate prose, headings, `title`, `description` and the `next_name` label passed to `next_steps.md`. Then set the file's entry in `fr/translated_from.json` to the English file's current commit (`git log -1 --format=%H -- <path>`); a newer commit that contains it, such as `HEAD` at translation time, also counts as current.
