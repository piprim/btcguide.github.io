# Local helpers. CI runs the same spellcheck and book build (see .github/workflows).
OUT := _book/out
PANDOC_FLAGS := --toc --toc-depth=4 --resource-path=.
# six heading levels need chapter..subparagraph, so build the PDF as a report
PDF_FLAGS := -N --pdf-engine=xelatex --top-level-division=chapter -V documentclass=report -V colorlinks=true -V geometry:margin=2.5cm

.PHONY: spellcheck book epub pdf hexo serve clean

spellcheck:
	pyspelling -c .spellcheck.yml

book: $(OUT)/book.md

$(OUT)/book.md: _book/build.py index.html $(wildcard _pages/* _pages/*/* _pages/*/*/* _includes/* _includes/*/*)
	python3 _book/build.py

# single Markdown post for a Hexo blog; copy assets/img to the blog's source/assets/img
hexo:
	python3 _book/build.py --hexo

epub: $(OUT)/btcguide.epub

$(OUT)/btcguide.epub: $(OUT)/book.md
	pandoc $< -o $@ $(PANDOC_FLAGS) --epub-chapter-level=2

# pandoc + xelatex as in CI; falls back to calibre when xelatex is not installed
pdf: $(OUT)/btcguide.pdf

$(OUT)/btcguide.pdf: $(OUT)/book.md
	@if command -v xelatex >/dev/null; then \
	  pandoc $< -o $@ $(PANDOC_FLAGS) $(PDF_FLAGS); \
	else \
	  echo "xelatex not found, converting via calibre instead"; \
	  pandoc $< -o $(OUT)/btcguide.epub $(PANDOC_FLAGS) --epub-chapter-level=2 && ebook-convert $(OUT)/btcguide.epub $@ >/dev/null; \
	fi

serve:
	bundle exec jekyll serve

clean:
	rm -rf $(OUT)
