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
```

## Hexo pages for the blog

The guide is also published on `blog.piprime.fr` as a tree of Hexo pages under `/btcguide/`, English generated here, French hand-written in the blog repository. Design: `_book/HEXO-PAGES-SPEC.md`.

    make hexo-pages                          # _book/out/hexo/: page/btcguide/... and media/btcguide/...
    make hexo-sync BLOG=../blog/hexo/source  # rsync into the blog; generated files always win; never touches fr/
    make hexo-fr-scaffold BLOG=...           # create fr/btcguide/<page>/index.md for every untranslated page
    make hexo-stale BLOG=...                 # list French pages whose translated_from is behind; exit 1 if any

`REPO=https://github.com/<fork>` overrides the repository used in "Source:" footers and release links.
Dates come from `git log`, so a shallow clone needs `fetch-depth: 0`.

Blog-side setup, once: add a menu entry in `hexo/_config.next.yml`, e.g. `Bitcoin Guide: /btcguide/ || fa fa-bitcoin`
(and its French label in the theme's language file if the fork localizes menu labels). Pages render with the default page layout.

Translating a page: run `make hexo-fr-scaffold`, replace the English body and the `pas encore traduite` notice, translate `title` and `description`, keep `translated_from` as the sha of the English page you translated (`make hexo-stale` compares it). Internal links in French pages point to `/fr/btcguide/...`.
