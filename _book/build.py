#!/usr/bin/env python3
"""Assemble the whole guide into one Markdown file for pandoc.

Chapter order and nesting come from the table of contents in index.html, so
adding a page to the site also adds it to the book. Each page becomes a
heading whose id is the page URL with slashes replaced by dashes, and internal
links are rewritten to those ids. Liquid includes are expanded; next_steps is
dropped; kramdown attributes are stripped.

Usage: python3 _book/build.py [en|fr]  -> writes _book/out/book.md, or _book/out/fr/book.md from the fr/ tree
                                          (skipped with a warning while fr/index.html is missing; see FRENCH-SPEC.md)
       python3 _book/hexo.py           -> Hexo pages for the blog (see HEXO-PAGES-SPEC.md)
"""
import os, posixpath, re, subprocess, sys, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "_book" / "out"
INCLUDE = re.compile(r"{%\s*include\s+(\S+)[^%]*%}")
FR = ROOT / "fr"  # mirror of the English sources; read through localized() so tests can point it elsewhere
PREFIX = "/btcguide"  # URL prefix of the guide on the blog
BLOG = "https://blog.piprime.fr"

# Fixed text the generators emit, per language. Templates: {adv}, {name}, {url}.
STRINGS = {
    "en": dict(title="10x Security Bitcoin Guide", subtitle="How to store bitcoin without any single point of failure",
               introduction="Introduction", appendix="Appendix", license="License", license_lead="This guide is released under the MIT License.",
               known_issues="Known Issues: ", advanced=" » Advanced Considerations", toc="Table of Contents", offline="Offline copies",
               advanced_box=("> **Advanced Considerations**\n>\n> Comfortable with the concepts in this step? "
                             "Read the [advanced considerations]({adv}) that can potentially improve your security here.\n"),
               next_link="\n---\n\n» Next Section: [{name}]({url})\n", source="Source", mit="MIT License", updated="Last updated",
               untranslated=""),
    "fr": dict(title="Guide Bitcoin Sécurité 10x", subtitle="Comment conserver des bitcoins sans aucun point de défaillance unique",
               introduction="Introduction", appendix="Annexes", license="Licence", license_lead="Ce guide est publié sous licence MIT.",
               known_issues="Problèmes connus : ", advanced=" » Considérations avancées", toc="Table des matières", offline="Versions hors ligne",
               advanced_box=("> **Considérations avancées**\n>\n> À l'aise avec les notions de cette étape ? "
                             "Lisez les [considérations avancées]({adv}) qui peuvent encore renforcer votre sécurité.\n"),
               next_link="\n---\n\n» Section suivante : [{name}]({url})\n", source="Source", mit="Licence MIT", updated="Dernière mise à jour",
               untranslated="*Cette page n'est pas encore traduite. [Lire la version anglaise]({url}).*"),
}


def localized(lang, path):
    """The lang-tree counterpart of an English source file (may not exist)."""
    return path if lang == "en" else FR / path.relative_to(ROOT)


def include_file(lang, name, included_by):
    """Path of an include for lang; a French include that does not exist fails the build (no English fallback)."""
    f = localized(lang, ROOT / "_includes" / name)
    if lang != "en" and not f.exists():
        sys.exit(f"build.py: fr/_includes/{name} missing (included by {included_by.relative_to(ROOT)})")
    return f


def toc_mismatch(en_html, fr_html):
    """None when both TOCs link the same URLs in the same order and nesting, else a message naming the first difference."""
    key = lambda html: [(k, url, depth) for k, _, url, depth in walk_toc(html)]
    en, fr = key(en_html), key(fr_html)
    for i in range(max(len(en), len(fr))):
        a, b = (en[i] if i < len(en) else None), (fr[i] if i < len(fr) else None)
        if a != b:
            return f"TOC mismatch at item {i}: en {a} vs fr {b}"
    return None


def drop_offline_paragraph(intro):
    """The intro's 'read offline' paragraph, in any language: the book and the blog home have their own download links."""
    return "\n\n".join(p for p in intro.split("\n\n") if "releases/download/book/" not in p)


def slug(url):
    return url.strip("/").replace("/", "-")


def slugify(text):
    """kramdown's heading-id rule: keep letters, digits, spaces and dashes; spaces -> dashes; lowercase; drop leading non-letters."""
    text = re.sub(r"[^a-zA-Z0-9 -]", "", text).replace(" ", "-").lower()
    return re.sub(r"^[^a-z]+", "", text)


HEADING = re.compile(r"^(#+) (.+?)[ \t]*$", re.M)


def english_anchors(body, lf, en_body, where):
    """Give each heading of a translated body the English heading's kramdown id as well, by position, so that links
    kept identical to the English (`#choosing-the-second-hardware-wallet`) still resolve. Returns (body, [en ids])."""
    en = [slugify(h) for _, h in HEADING.findall(en_body)]
    n = len(HEADING.findall(body))
    if n != len(en):
        sys.exit(f"{where}: {lf.relative_to(ROOT)}: {n} heading(s), English has {len(en)}; headings must match one to one")
    return en


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


def front_title(f):
    m = re.match(r"---\n(.*?)\n---\n", f.read_text(), re.S)
    t = re.search(r"^title:\s*(.+)$", m.group(1), re.M) if m else None
    return t.group(1).strip() if t else None


def render(f, url, depth, anchor, title_suffix="", lang="en", label=None):
    """One page as a chapter. f is the English file; the lang counterpart is rendered, or a stub when it does not exist."""
    heading = lambda title: f"{'#' * min(depth, 6)} {title}{title_suffix} {{#{anchor}}}\n\n"
    lf = localized(lang, f)
    if not lf.exists():
        title = label or front_title(f) or slug(url)
        return heading(title) + STRINGS[lang]["untranslated"].format(url=BLOG + PREFIX + url.rstrip("/") + "/") + "\n\n"
    def source(file, lg):
        text = file.read_text()
        m = re.match(r"---\n(.*?)\n---\n", text, re.S)
        body = text[m.end():] if m else text
        return INCLUDE.sub(lambda mm: "" if mm.group(1) == "next_steps.md" else include_file(lg, mm.group(1), file).read_text(), body)
    body = source(lf, lang)
    title = front_title(lf) or slug(url)
    page_dir = url.rstrip("/") + "/" if f.name == "index.md" else url.rsplit("/", 1)[0] + "/"
    en_ids = iter(english_anchors(body, lf, source(f, "en"), "build.py")) if lang != "en" else None
    body = re.sub(r"{%.*?%}", "", body, flags=re.S)
    body = body.replace("{{ page.title }}", title)
    body = re.sub(r"{:[^}]*?width=\"(\d+%)\"[^}]*}", r"{width=\1}", body)  # kramdown width -> pandoc width
    body = re.sub(r"{:[^}]*}", "", body)
    body = re.sub(r"^-{3,}\s*$", "* * *", body, flags=re.M)  # a bare --- line would start a YAML block in pandoc
    body = normalize_headings(body, depth)  # pages skip levels (## then ####)
    if en_ids:
        body = HEADING.sub(lambda mm: f"{mm.group(1)} {mm.group(2)} {{#{next(en_ids)}}}", body)  # pandoc explicit id
    body = re.sub(r"^\[TODO\]:.*$", "", body, flags=re.M)  # maintainer notes, invisible on the site too
    body = body.replace(" (✓)", "")  # no check mark glyph in the PDF font
    body = re.sub(r"\]\(/assets/", "](assets/", body)
    body = re.sub(r"\]\(([^)\s]+)\)", lambda mm: "](" + ("assets/" + mm.group(1)[7:] if mm.group(1).startswith("assets/") else resolve_link(mm.group(1), page_dir)) + ")", body)
    body = re.sub(r"<(/[a-z][^>\s]*)>", lambda mm: f"[{mm.group(1)}](#{slug(mm.group(1))})", body)  # bare </foo> autolinks
    return heading(title) + body.strip() + "\n\n"


def main(lang="en"):
    S = STRINGS[lang]
    out_dir = OUT if lang == "en" else OUT / lang
    index = localized(lang, ROOT / "index.html")
    if not index.exists():
        print(f"build.py: {lang}/index.html missing, French book skipped", file=sys.stderr)
        return
    intro_html, toc_html = index.read_text().split("<hr>", 1)
    en_toc = (ROOT / "index.html").read_text().split("<hr>", 1)[1]
    if lang != "en" and (msg := toc_mismatch(en_toc, toc_html)):
        sys.exit("build.py: " + msg)
    out_dir.mkdir(parents=True, exist_ok=True)
    intro_html = re.sub(r"^---.*?---\n", "", intro_html, flags=re.S)
    repo = "https://github.com/" + os.environ.get("GITHUB_REPOSITORY", "btcguide/btcguide.github.io")  # set by GitHub Actions
    intro_html = intro_html.replace("{{ site.github.repository_url }}", repo)
    intro = subprocess.run(["pandoc", "-f", "html", "-t", "gfm", "--wrap=none"], input=intro_html, capture_output=True, text=True, check=True).stdout
    intro = drop_offline_paragraph(intro)  # pointless inside the book

    parts = [
        f"---\ntitle: {S['title']}\nsubtitle: {S['subtitle']}\nlang: {lang}\n---\n\n",
        f"# {S['introduction']} {{#home}}\n\n", intro.strip(), "\n\n",
    ]
    # structure from the English TOC, labels from the lang one (toc_mismatch guarantees they line up)
    for (kind, _, url, depth), (_, text, _, _) in zip(walk_toc(en_toc), walk_toc(toc_html)):
        if kind == "section":
            parts.append(f"# {text}\n\n")
        elif kind == "page":
            f = page_file(url)
            parts.append(render(f, url, depth + 1, slug(url), lang=lang, label=text))
            adv = advanced_of(f)
            if adv.exists():
                adv_url = url.rstrip("/") + ("/advanced" if url.endswith("/") else "-advanced")
                parts.append(render(adv, adv_url, depth + 2, slug(adv_url), S["advanced"], lang=lang))
        else:
            parts.append(f"{'#' * (depth + 1)} {text}\n\n")

    parts.append(f"# {S['appendix']}\n\n")
    for name in ("disclaimer", "contributors", "compensation"):
        parts.append(render(ROOT / f"{name}.md", f"/{name}", 2, name, lang=lang))
    parts.append(f"## {S['license']} {{#license}}\n\n{S['license_lead']}\n\n```\n" + (ROOT / "LICENSE").read_text().strip() + "\n```\n\n")

    book = "".join(parts).replace("{{ site.github.repository_url }}", repo)
    leak = re.search(r".{0,40}({%|{{|{:).{0,40}", book)
    assert not leak, f"liquid or kramdown syntax leaked into the book: {leak.group(0)!r}"
    (out_dir / "book.md").write_text(book)
    print(f"wrote {out_dir / 'book.md'}: {book.count(chr(10))} lines, {len(re.findall(r'^#', book, re.M))} headings")


if __name__ == "__main__":
    if sys.argv[1:] not in ([], ["en"], ["fr"]):
        sys.exit(__doc__)
    main(sys.argv[1] if sys.argv[1:] else "en")
