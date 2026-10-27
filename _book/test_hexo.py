import os, pathlib, re, subprocess

import pytest

os.environ.pop("REPO", None)
import hexo  # noqa: E402


def test_slugify():
    assert hexo.slugify("Shamir's Secret Sharing Scheme") == "shamirs-secret-sharing-scheme"
    assert hexo.slugify("3-of-5 is Excellent") == "of-5-is-excellent"
    assert hexo.slugify("Minimum Equipment to Buy:") == "minimum-equipment-to-buy"
    assert hexo.slugify("Export Public Key Info to Computer via QR Code / Webcam") == "export-public-key-info-to-computer-via-qr-code--webcam"


def test_guide_pages_order_and_count():
    pages = hexo.guide_pages()
    urls = [p.url for p in pages]
    assert urls[:3] == ["", "/why-multisig", "/why-multisig-advanced"]
    assert urls[-4:] == ["/disclaimer", "/contributors", "/compensation", "/license"]
    assert "/setup-wallets" in urls and urls[urls.index("/setup-wallets") + 1] == "/setup-wallets/advanced"
    assert "/setup-computer/advanced" not in urls  # no such file
    assert len(urls) == len(set(urls))
    toc = sum(1 for k, *_ in hexo.book.walk_toc(hexo.toc_html()) if k == "page")
    adv = sum(1 for p in pages if hexo.is_advanced(p))
    assert len(pages) == 1 + toc + adv + 4


def test_display_title():
    by = {p.url: p for p in hexo.guide_pages()}
    assert hexo.display_title(by["/known-issues/hardware/coldcard"]) == "Known Issues: Coldcard"
    assert hexo.display_title(by["/setup-wallets/advanced"]) == "Setup Hardware Wallet Overview » Advanced Considerations"
    assert hexo.display_title(by["/why-multisig-advanced"]) == "Why Multisig? » Advanced Considerations"
    assert hexo.display_title(by[""]) == "10x Security Bitcoin Guide"


def test_page_dir_and_hexo_url():
    by = {p.url: p for p in hexo.guide_pages()}
    assert hexo.page_dir(by["/setup-wallets/paper"]) == "/setup-wallets/"
    assert hexo.page_dir(by["/setup-wallets"]) == "/setup-wallets/"
    assert hexo.page_dir(by["/equipment"]) == "/"
    assert hexo.hexo_url("") == "/btcguide/"
    assert hexo.hexo_url("/setup-wallets/paper", "generate-seed") == "/btcguide/setup-wallets/paper/#generate-seed"


def _page(url):
    return {p.url: p for p in hexo.guide_pages()}[url]


def _render(url):
    p = _page(url)
    fm, body = hexo.read_page(p)
    return hexo.transform_body(p, hexo.expand_includes(p, body))


def test_next_steps_box_and_next_link():
    out = _render("/setup-wallets/paper")
    assert "[advanced considerations](/btcguide/setup-wallets/paper-advanced/)" in out
    assert "» Next Section: [Setup Keystone](/btcguide/setup-wallets/keystone/)" in out
    idx = _render("/setup-wallets")
    assert "[advanced considerations](/btcguide/setup-wallets/advanced/)" in idx


def test_no_advanced_box_when_flagged_or_advanced():
    assert "Advanced Considerations" not in _render("/how-it-works")  # no_advanced_link: true, no sibling
    assert "[advanced considerations]" not in _render("/quorum-advanced")
    assert "» Next Section: [Equipment](/btcguide/equipment/)" in _render("/quorum-advanced")


def test_headings_start_at_h2_with_anchors_and_no_jumps():
    out = _render("/equipment")  # opens with ####, later uses ##
    levels = [len(h) for h in re.findall(r"^(#+) ", out, re.M)]
    assert levels and levels[0] == 2 and all(b - a <= 1 for a, b in zip(levels, levels[1:]))
    assert '<a id="choosing-the-second-hardware-wallet"></a>\n\n## Choosing the Second Hardware Wallet' in out  # #### lead-in siblings stay siblings
    assert '<a id="shamirs-secret-sharing-scheme"></a>' in _render("/why-multisig-advanced")
    assert not re.search(r"^# ", out, re.M)


def test_links_and_assets():
    out = _render("/equipment")
    assert "](/btcguide/setup-wallets/paper/#generate-seed)" in out  # relative link + fragment
    assert "](/btcguide/equipment/#choosing-the-second-hardware-wallet)" in _render("/setup-wallets")
    assert "](#some-thing)" in hexo.transform_body(_page("/quorum"), "[x](#Some-Thing)\n")  # same-page fragment
    assert "](/media/btcguide/guide/bip39_wordlist.pdf)" in _render("/setup-wallets/paper")
    assert "](/btcguide/verify-receive-address/coldcard/)" in _render("/setup-wallets/coordinate-multisig-advanced")  # ../ link
    assert "](/btcguide/known-issues/verify-receive-address/)" in _render("/known-issues/complexity")  # trailing slash
    assert "](/btcguide/quorum-advanced/#of-5-is-excellent)" in _render("/setup-wallets/advanced")
    assert "https://en.wikipedia.org/wiki/Checksum" in _render("/setup-wallets/paper")  # external untouched


def test_images_and_kramdown():
    out = _render("/setup-wallets/paper")
    assert '<img src="/media/btcguide/img/setup-paper-seedpicker-example-output.png" alt="" width="70%">' in out
    assert "{:" not in out and "{%" not in out and "{{" not in out


def test_liquid_and_braces():
    p = _page("/setup-wallets/paper")
    out = hexo.transform_body(p, "x {{ page.title }} y {{ site.github.repository_url }} z {% if a %}q{% endif %}\n\nfoo {bar}\n\n```\n{keep}\n```\n")
    assert "x Setup Paper Wallet y https://github.com/piprim/btcguide.github.io z q" in out
    assert "foo &lbrace;bar&rbrace;" in out and "{keep}" in out
    assert hexo.transform_body(p, "---\n\ntext\n").startswith("text")
    assert "[TODO]" not in _render("/setup-wallets")


def test_sources():
    assert hexo.sources(_page("/known-issues/hosted/casa")) == [hexo.ROOT / "_pages/known-issues/hosted/casa.md"] + [
        hexo.ROOT / "_includes/hosted" / n for n in ("limited_hw.md", "spof.md", "utxo_privacy.md", "benefits.md")]
    assert hexo.sources(_page("")) == [hexo.ROOT / "index.html", hexo.ROOT / "disclaimer.md", hexo.ROOT / "contributors.md", hexo.ROOT / "compensation.md"]


def test_git_stamp_clean_and_dirty():
    date, sha = hexo.git_stamp([hexo.ROOT / "_pages/known-issues/hosted/casa.md"])
    assert re.fullmatch(r"\d{4}-\d\d-\d\d \d\d:\d\d:\d\d", date) and re.fullmatch(r"[0-9a-f]{7,}", sha)
    both = hexo.git_stamp([hexo.ROOT / "_pages/known-issues/hosted/casa.md", hexo.ROOT / "_includes/hosted/limited_hw.md"])
    assert both[0] >= date  # include touched later moves the stamp
    f = hexo.ROOT / "_pages/known-issues/hosted/casa.md"
    orig = f.read_text()
    f.write_text(orig + "\n")
    try:
        d2, s2 = hexo.git_stamp([f])
    finally:
        f.write_text(orig)
    assert s2.endswith("-dirty") and d2 > date


def test_description():
    assert hexo.description("## H\n\n<a id=x></a>\n\nFor a video demo, check out [this example](https://x). More text.\n") == "For a video demo, check out this example."
    assert len(hexo.description("a" * 300)) == 160


def test_render_page_shape():
    pages = hexo.guide_pages()
    by = {p.url: p for p in pages}
    out = hexo.render_page(by["/setup-wallets/paper"], pages)
    lines = out.splitlines()
    assert lines[0] == "---" and lines[1] == 'title: "Setup Paper Wallet"' and lines[3] == "lang: en"
    assert lines[4] == "comments: false" and lines[5] == "tree_view: true"
    assert lines[7] == 'btcguide_source: "_pages/setup-wallets/paper.md"' and lines[8].startswith("btcguide_commit: ")
    assert lines[9] == "---" and lines[10] == hexo.GENERATED and lines[11] == ""
    assert "← [Setup Hardware Wallet Overview » Advanced Considerations](/btcguide/setup-wallets/advanced/) · [Setup Paper Wallet » Advanced Considerations](/btcguide/setup-wallets/paper-advanced/) →" in out
    assert hexo.nav(by["/setup-wallets/paper-advanced"], pages) == "← [Setup Paper Wallet](/btcguide/setup-wallets/paper/) · [Setup Keystone (Formerly Cobo Vault)](/btcguide/setup-wallets/keystone/) →"  # the spec's example, with the real title
    assert out.rstrip().endswith("· [MIT License](/btcguide/license/) · Last updated " + lines[2].split()[1])
    assert "(https://github.com/piprim/btcguide.github.io/blob/master/_pages/setup-wallets/paper.md)" in out
    casa = hexo.render_page(by["/known-issues/hosted/casa"], pages)
    assert 'btcguide_source: "_pages/known-issues/hosted/casa.md _includes/hosted/limited_hw.md' in casa
    assert 'title: "Known Issues: Casa"' in casa


def test_home_and_license_pages():
    pages = hexo.guide_pages()
    home = hexo.render_page(pages[0], pages)
    assert "Prefer to read offline" not in home
    assert "- [Introduction: Why Multisig?](/btcguide/why-multisig/)" in home
    assert "  - [Paper Wallet](/btcguide/setup-wallets/paper/)" in home
    assert "- Hosted Services" in home and "### Known Issues & Benefits" in home
    assert "(https://github.com/piprim/btcguide.github.io/releases/download/book/btcguide.epub)" in home
    assert "←" not in home and "\n[Why Multisig?](/btcguide/why-multisig/) →" in home
    lic = hexo.render_page(pages[-1], pages)
    assert 'title: "License"' in lic and "Permission is hereby granted" in lic and "→" not in lic


@pytest.fixture(scope="session")
def built():
    hexo.build()
    return hexo.HEXO_OUT


def test_build_writes_tree(built):
    assert (built / "page/btcguide/index.md").exists()
    assert (built / "page/btcguide/setup-wallets/paper/index.md").exists()
    assert (built / "page/btcguide/setup-wallets/advanced/index.md").exists()
    assert (built / "page/btcguide/known-issues/hardware/coldcard/index.md").exists()
    assert (built / "media/btcguide/guide/bip39_wordlist.pdf").exists()
    assert (built / "media/btcguide/img/setup-paper-seedpicker-example-output.png").exists()
    assert len(list(built.glob("page/**/index.md"))) == len(hexo.guide_pages())
    for f in built.glob("page/**/index.md"):
        assert f.read_text().splitlines()[10] == hexo.GENERATED


def test_check_catches_each_class(built):
    pages = hexo.guide_pages()
    good = {p.url: hexo.render_page(p, pages) for p in pages}
    media = built / "media/btcguide"
    assert hexo.check(good, media, len(good)) == []

    def bad(extra):
        d = dict(good)
        d["/quorum"] = d["/quorum"].replace("---\n\n←", extra + "\n\n---\n\n←", 1)
        return d
    assert hexo.check(bad("{% raw %}"), media, len(good))
    assert hexo.check(bad("text {x}"), media, len(good))
    assert hexo.check(bad("# Top"), media, len(good))
    assert hexo.check(bad("## A\n\n#### B"), media, len(good))
    assert hexo.check(bad("[x](/btcguide/nope/)"), media, len(good))
    assert hexo.check(bad("[x](/btcguide/equipment/#nope)"), media, len(good))
    assert hexo.check(bad("[x](#nope)"), media, len(good))  # same-page fragment
    assert hexo.check(bad("[x](/equipment)"), media, len(good))
    assert hexo.check(bad("![](/media/btcguide/img/nope.png)"), media, len(good))
    assert hexo.check(bad("[x](https://btcguide.github.io/quorum)"), media, len(good))
    assert hexo.check(good, media, len(good) + 1)


def test_hexo_sync(tmp_path):
    blog = tmp_path / "source"
    (blog / "fr/btcguide").mkdir(parents=True)
    (blog / "fr/btcguide/keep.md").write_text("fr")
    r = subprocess.run(["make", "hexo-sync", f"BLOG={blog}"], cwd=hexo.ROOT, capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    assert (blog / "btcguide/setup-wallets/paper/index.md").exists()
    assert (blog / "media/btcguide/guide/bip39_wordlist.pdf").exists()
    assert (blog / "fr/btcguide/keep.md").read_text() == "fr"
    (blog / "btcguide/stray.md").write_text("x")  # any non-generated file under btcguide/ is a blog-side edit
    r = subprocess.run(["make", "hexo-sync", f"BLOG={blog}"], cwd=hexo.ROOT, capture_output=True, text=True)
    assert r.returncode != 0 and "stray.md" in r.stdout + r.stderr
    (blog / "btcguide/stray.md").unlink()
    (blog / "btcguide/quorum/extra.png").write_bytes(b"x")  # same for a stray binary
    assert subprocess.run(["make", "hexo-sync", f"BLOG={blog}"], cwd=hexo.ROOT, capture_output=True).returncode != 0
    (blog / "btcguide/quorum/extra.png").unlink()
    subprocess.run(["make", "hexo-sync", f"BLOG={blog}"], cwd=hexo.ROOT, check=True, capture_output=True)
    edited = blog / "btcguide/quorum/index.md"
    edited.write_text(edited.read_text().replace(hexo.GENERATED, "<!-- mine -->"))
    r = subprocess.run(["make", "hexo-sync", f"BLOG={blog}"], cwd=hexo.ROOT, capture_output=True, text=True)
    assert r.returncode != 0 and "quorum/index.md" in r.stdout + r.stderr
    assert subprocess.run(["make", "hexo-sync"], cwd=hexo.ROOT, capture_output=True).returncode != 0  # BLOG required


def test_fr_scaffold(built, tmp_path):
    blog = tmp_path / "source"
    existing = blog / "fr/btcguide/quorum/index.md"
    existing.parent.mkdir(parents=True)
    existing.write_text("déjà traduit")
    created = hexo.fr_scaffold(blog)
    assert existing.read_text() == "déjà traduit" and existing not in created
    assert len(created) == len(hexo.guide_pages()) - 1
    fr = (blog / "fr/btcguide/setup-wallets/paper/index.md").read_text()
    head = fr.split("---\n")[1]
    assert "lang: fr\n" in head and "comments: false\n" in head and "tree_view: true\n" in head
    assert re.search(r"^translated_from: [0-9a-f]{7,}", head, re.M) and 'title: "Setup Paper Wallet"' in head
    assert "> *Cette page n'est pas encore traduite. Le texte anglais suit.*" in fr
    assert "](/fr/btcguide/setup-wallets/keystone/)" in fr and "](/btcguide/" not in fr
    assert "/media/btcguide/img/" in fr and hexo.GENERATED not in fr
    assert hexo.fr_scaffold(blog) == []


def test_stale(built, tmp_path, capsys):
    blog = tmp_path / "source"
    blog.mkdir()
    hexo.fr_scaffold(blog)
    assert hexo.stale(blog) == 0 and "all French pages up to date" in capsys.readouterr().out
    fr = blog / "fr/btcguide/setup-wallets/paper/index.md"
    txt = fr.read_text()
    fr.write_text(re.sub(r"^translated_from: .*$", "translated_from: 9837ce8", txt, flags=re.M).replace("](/fr/btcguide/", "](/btcguide/", 1))
    orphan = blog / "fr/btcguide/gone/index.md"
    orphan.parent.mkdir()
    orphan.write_text("---\ntranslated_from: 9837ce8\n---\nx")
    dirty = blog / "fr/btcguide/quorum/index.md"
    dirty.write_text(re.sub(r"^translated_from: .*$", "translated_from: 9837ce8-dirty", dirty.read_text(), flags=re.M))
    assert hexo.stale(blog) == 1
    out = capsys.readouterr().out
    assert "STALE fr/btcguide/setup-wallets/paper/index.md: 9837ce8 -> " in out
    assert "WARN fr/btcguide/setup-wallets/paper/index.md: 1 link(s)" in out
    assert "ORPHAN fr/btcguide/gone/index.md" in out
    assert "STALE fr/btcguide/quorum/index.md: 9837ce8-dirty -> " in out and "uncommitted" in out


def test_git_stamp_untracked_page():  # a brand-new page must preview, not crash
    f = hexo.ROOT / "_pages/zz-untracked-test-page.md"
    f.write_text("---\ntitle: T\n---\nx\n")
    try:
        date, sha = hexo.git_stamp([f])
    finally:
        f.unlink()
    assert sha.endswith("-dirty") and re.fullmatch(r"\d{4}-\d\d-\d\d \d\d:\d\d:\d\d", date)


def test_blog_required_for_fr_targets(tmp_path):
    for target in ("hexo-fr-scaffold", "hexo-stale"):
        r = subprocess.run(["make", target], cwd=hexo.ROOT, capture_output=True, text=True)
        assert r.returncode != 0 and "BLOG=" in r.stdout + r.stderr, target
    assert not (hexo.ROOT / "fr").exists()
    with pytest.raises(SystemExit):
        hexo.stale(tmp_path / "nope")
    with pytest.raises(SystemExit):
        hexo.fr_scaffold(tmp_path / "nope")
