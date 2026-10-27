#!/usr/bin/env python3
"""Assemble the whole guide into one Markdown file for pandoc.

Chapter order and nesting come from the table of contents in index.html, so
adding a page to the site also adds it to the book. Each page becomes a
heading whose id is the page URL with slashes replaced by dashes, and internal
links are rewritten to those ids. Liquid includes are expanded; next_steps is
dropped; kramdown attributes are stripped.

Usage: python3 _book/build.py          -> writes _book/out/book.md (pandoc input)
       python3 _book/hexo.py           -> Hexo pages for the blog (see HEXO-PAGES-SPEC.md)
"""
import os, posixpath, re, subprocess, sys, pathlib

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


def site_path(link, page_dir):
    """Split an internal link into (absolute path without trailing slash, fragment).

    "" is the home page; a pure #fragment link gives ("#", frag). External links give None."""
    if re.match(r"^(https?:|mailto:)", link):
        return None
    path, _, frag = link.partition("#")
    if not path:
        return "#", frag
    if not path.startswith("/"):  # relative to the page's directory
        path = posixpath.join(page_dir, path)
    return posixpath.normpath(path).rstrip("/"), frag


def resolve_link(link, page_dir):
    """Turn a site link into a heading id. External and same-page links are returned as-is."""
    sp = site_path(link, page_dir)
    if sp is None or sp[0] == "#":
        return link
    path, frag = sp
    return "#" + (re.sub(r"^[^a-zA-Z]+", "", frag) if frag else slug(path) or "home")


def normalize_headings(body, base):
    """Remap the page's distinct heading levels to consecutive ones starting at base + 1,
    then never jump more than one level below the previous heading.
    Pages open with #### lead-ins before their first ##: those are siblings of the ## sections,
    so headings before the first shallowest one are promoted by the lead-in's depth."""
    levels = [len(h) for h in re.findall(r"^(#+) ", body, re.M)]
    if not levels:
        return body
    low, lead, shift = min(levels), levels.index(min(levels)), levels[0] - min(levels)
    levels = [max(low, lvl - shift) for lvl in levels[:lead]] + levels[lead:]
    remap = {lvl: base + 1 + i for i, lvl in enumerate(sorted(set(levels)))}
    prev, it = [base], iter(levels)

    def level(mm):
        lvl = min(remap[next(it)], prev[0] + 1, 6)
        prev[0] = lvl
        return "#" * lvl + " "
    return re.sub(r"^(#+) ", level, body, flags=re.M)


def walk_toc(toc_html):
    """Yield (kind, text, url, depth) for the TOC in index.html: 'section' for each <h4>,
    'page' for a linked <li> (url with a leading slash), 'label' for a plain <li>."""
    depth = 0
    for tok in re.finditer(r'<ol>|</ol>|<h4>(.*?)</h4>|<li>\s*(?:<a href="([^"]+)">)?\s*([^<\n]+)', toc_html):
        h4, href, label = tok.groups()
        if tok.group(0) == "<ol>":
            depth += 1
        elif tok.group(0) == "</ol>":
            depth -= 1
        elif h4:
            depth = 0
            yield "section", h4.replace("&amp;", "&"), None, 0
        elif href:
            yield "page", label.strip(), "/" + href.lstrip("/"), depth
        else:
            yield "label", label.strip(), None, depth


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
    body = normalize_headings(body, depth)  # pages skip levels (## then ####)
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
    for kind, text, url, depth in walk_toc(toc_html):
        if kind == "section":
            parts.append(f"# {text}\n\n")
        elif kind == "page":
            f = page_file(url)
            parts.append(render(f, url, depth + 1, slug(url)))
            adv = advanced_of(f)
            if adv.exists():
                adv_url = url.rstrip("/") + ("/advanced" if url.endswith("/") else "-advanced")
                parts.append(render(adv, adv_url, depth + 2, slug(adv_url), " » Advanced Considerations"))
        else:
            parts.append(f"{'#' * (depth + 1)} {text}\n\n")

    parts.append("# Appendix\n\n")
    for name in ("disclaimer", "contributors", "compensation"):
        parts.append(render(ROOT / f"{name}.md", f"/{name}", 2, name))
    parts.append("## License {#license}\n\nThis guide is released under the MIT License.\n\n```\n" + (ROOT / "LICENSE").read_text().strip() + "\n```\n\n")

    book = "".join(parts).replace("{{ site.github.repository_url }}", repo)
    leak = re.search(r".{0,40}({%|{{|{:).{0,40}", book)
    assert not leak, f"liquid or kramdown syntax leaked into the book: {leak.group(0)!r}"
    (OUT / "book.md").write_text(book)
    print(f"wrote {OUT / 'book.md'}: {book.count(chr(10))} lines, {len(re.findall(r'^#', book, re.M))} headings")


if __name__ == "__main__":
    main()
