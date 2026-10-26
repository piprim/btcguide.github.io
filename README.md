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
make hexo         # _book/out/hexo.md, one post for a Hexo blog (copy assets/img alongside)
```
