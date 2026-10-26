#!/usr/bin/env python3
"""Assemble the whole guide into one Markdown file for pandoc.

Chapter order and nesting come from the table of contents in index.html, so
adding a page to the site also adds it to the book. Each page becomes a
heading whose id is the page URL with slashes replaced by dashes, and internal
links are rewritten to those ids. Liquid includes are expanded; next_steps is
dropped; kramdown attributes are stripped.

Usage: python3 _book/build.py          -> writes _book/out/book.md (pandoc input)
       python3 _book/build.py --hexo   -> also writes _book/out/hexo.md, a single
                                          Hexo post: front-matter title is the h1,
                                          so every heading moves down one level,
                                          anchors become HTML, images are /assets/img/...
"""
import datetime, os, posixpath, re, subprocess, sys, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "_book" / "out"
INCLUDE = re.compile(r"{%\s*include\s+(\S+)[^%]*%}")


def slug(url):
    return url.strip("/").replace("/", "-")


def page_file(url):
    p = url.strip("/")
    for cand in (ROOT / "_pages" / f"{p}.md", ROOT / "_pages" / p / "index.md"):
        if cand.exists():
            return cand
    sys.exit(f"build.py: no page for {url}")


def advanced_of(f):
    return f.with_name("advanced.md") if f.name == "index.md" else f.with_name(f.stem + "-advanced.md")


def resolve_link(link, page_dir):
    """Turn a site link into a heading id. External links are returned as-is."""
    if re.match(r"^(https?:|mailto:|#)", link):
        return link
    path, _, frag = link.partition("#")
    if not path.startswith("/"):  # relative to the page's directory
        path = posixpath.normpath(posixpath.join(page_dir, path))
    return "#" + (re.sub(r"^[^a-zA-Z]+", "", frag) if frag else slug(path) or "home")


def render(f, url, depth, anchor, title_suffix=""):
    text = f.read_text()
    m = re.match(r"---\n(.*?)\n---\n", text, re.S)
    body = text[m.end():] if m else text
    title = re.search(r"^title:\s*(.+)$", m.group(1), re.M).group(1).strip() if m else slug(url)
    page_dir = url.rstrip("/") + "/" if f.name == "index.md" else url.rsplit("/", 1)[0] + "/"
    body = INCLUDE.sub(lambda mm: "" if mm.group(1) == "next_steps.md" else (ROOT / "_includes" / mm.group(1)).read_text(), body)
    body = re.sub(r"{%.*?%}", "", body, flags=re.S)
    body = body.replace("{{ page.title }}", title)
    body = re.sub(r"{:[^}]*?width=\"(\d+%)\"[^}]*}", r"{width=\1}", body)  # kramdown width -> pandoc width
    body = re.sub(r"{:[^}]*}", "", body)
    body = re.sub(r"^-{3,}\s*$", "* * *", body, flags=re.M)  # a bare --- line would start a YAML block in pandoc
    # pages skip levels (## then ####); remap their distinct levels to consecutive ones below the page title
    remap = {lvl: depth + 1 + i for i, lvl in enumerate(sorted({len(h) for h in re.findall(r"^(#+) ", body, re.M)}))}
    prev = [depth]  # then never jump more than one level below the previous heading (some pages open with an h4)

    def level(mm):
        lvl = min(remap[len(mm.group(1))], prev[0] + 1, 6)
        prev[0] = lvl
        return "#" * lvl + " "
    body = re.sub(r"^(#+) ", level, body, flags=re.M)
    body = re.sub(r"^\[TODO\]:.*$", "", body, flags=re.M)  # maintainer notes, invisible on the site too
    body = body.replace(" (✓)", "")  # no check mark glyph in the PDF font
    body = re.sub(r"\]\(/assets/", "](assets/", body)
    body = re.sub(r"\]\(([^)\s]+)\)", lambda mm: "](" + ("assets/" + mm.group(1)[7:] if mm.group(1).startswith("assets/") else resolve_link(mm.group(1), page_dir)) + ")", body)
    body = re.sub(r"<(/[a-z][^>\s]*)>", lambda mm: f"[{mm.group(1)}](#{slug(mm.group(1))})", body)  # bare </foo> autolinks
    return f"{'#' * min(depth, 6)} {title}{title_suffix} {{#{anchor}}}\n\n{body.strip()}\n\n"


def main():
    OUT.mkdir(exist_ok=True)
    idx = (ROOT / "index.html").read_text()
    intro_html, toc_html = idx.split("<hr>", 1)
    intro_html = re.sub(r"^---.*?---\n", "", intro_html, flags=re.S)
    repo = "https://github.com/" + os.environ.get("GITHUB_REPOSITORY", "btcguide/btcguide.github.io")  # set by GitHub Actions
    intro_html = intro_html.replace("{{ site.github.repository_url }}", repo)
    intro = subprocess.run(["pandoc", "-f", "html", "-t", "gfm", "--wrap=none"], input=intro_html, capture_output=True, text=True, check=True).stdout
    intro = re.sub(r"^Prefer to read offline\?.*?(\n\n|\Z)", "", intro, flags=re.S | re.M)  # pointless inside the book

    parts = [
        "---\ntitle: 10x Security Bitcoin Guide\nsubtitle: How to store bitcoin without any single point of failure\nlang: en\n---\n\n",
        "# Introduction {#home}\n\n", intro, "\n",
    ]
    depth = 0
    for tok in re.finditer(r'<ol>|</ol>|<h4>(.*?)</h4>|<li>\s*(?:<a href="([^"]+)">)?\s*([^<\n]+)', toc_html):
        h4, href, label = tok.groups()
        if tok.group(0) == "<ol>":
            depth += 1
        elif tok.group(0) == "</ol>":
            depth -= 1
        elif h4:
            depth = 0
            parts.append(f"# {h4.replace('&amp;', '&')}\n\n")
        elif href:
            url = "/" + href.lstrip("/")
            f = page_file(url)
            parts.append(render(f, url, depth + 1, slug(url)))
            adv = advanced_of(f)
            if adv.exists():
                adv_url = url.rstrip("/") + ("/advanced" if url.endswith("/") else "-advanced")
                parts.append(render(adv, adv_url, depth + 2, slug(adv_url), " » Advanced Considerations"))
        else:
            parts.append(f"{'#' * (depth + 1)} {label.strip()}\n\n")

    parts.append("# Appendix\n\n")
    for name in ("disclaimer", "contributors", "compensation"):
        parts.append(render(ROOT / f"{name}.md", f"/{name}", 2, name))
    parts.append("## License {#license}\n\nThis guide is released under the MIT License.\n\n```\n" + (ROOT / "LICENSE").read_text().strip() + "\n```\n\n")

    book = "".join(parts).replace("{{ site.github.repository_url }}", repo)
    leak = re.search(r".{0,40}({%|{{|{:).{0,40}", book)
    assert not leak, f"liquid or kramdown syntax leaked into the book: {leak.group(0)!r}"
    (OUT / "book.md").write_text(book)
    print(f"wrote {OUT / 'book.md'}: {book.count(chr(10))} lines, {len(re.findall(r'^#', book, re.M))} headings")
    if "--hexo" in sys.argv:
        (OUT / "hexo.md").write_text(to_hexo(book))
        print(f"wrote {OUT / 'hexo.md'}")


def to_hexo(book):
    body = book.split("---\n", 2)[2]  # drop the pandoc YAML block
    body = re.sub(r"^(#+) ", lambda mm: "#" * min(len(mm.group(1)) + 1, 6) + " ", body, flags=re.M)
    body = re.sub(r"^(#+ .+?) {#([^}]+)}$", r'<a id="\2"></a>\n\1', body, flags=re.M)
    body = re.sub(r"{width=\d+%}", "", body)
    body = body.replace("](assets/", "](/assets/")
    return (f"---\ntitle: 10x Security Bitcoin Guide\ndate: {datetime.date.today()}\n"
            "description: How to store bitcoin without any single point of failure\n---\n\n" + body)


if __name__ == "__main__":
    main()
