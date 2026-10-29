import json, os, pathlib, re, shutil, subprocess

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
    git = lambda *a: subprocess.run(["git", *a], cwd=hexo.ROOT, capture_output=True, text=True).stdout
    dirty = git("status", "--porcelain")
    f = next(hexo.ROOT / n for n in git("ls-files").split() if n not in dirty)  # a committed, unmodified file
    date, sha = hexo.git_stamp([f])
    assert re.fullmatch(r"\d{4}-\d\d-\d\d \d\d:\d\d:\d\d", date) and re.fullmatch(r"[0-9a-f]{7,}", sha)
    both = hexo.git_stamp([f, hexo.ROOT / "_includes/hosted/limited_hw.md"])
    assert both[0] >= date  # include touched later moves the stamp
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
    assert len(list(built.glob("page/btcguide/**/index.md"))) == len(hexo.guide_pages())
    for f in built.glob("page/btcguide/**/index.md"):
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
    blog.mkdir()
    r = subprocess.run(["make", "hexo-sync", f"BLOG={blog}"], cwd=hexo.ROOT, capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    assert (blog / "btcguide/setup-wallets/paper/index.md").exists()
    assert (blog / "media/btcguide/guide/bip39_wordlist.pdf").exists()
    assert not (blog / "fr/btcguide").exists() and "no French pages to sync" in r.stdout
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


def test_hexo_sync_french(fr_tree, tmp_path):
    if (hexo.ROOT / "fr").exists():
        pytest.skip("make reads the real fr/ tree")
    shutil.copytree(fr_tree, hexo.ROOT / "fr")  # make runs in a subprocess, which cannot see the monkeypatched build.FR
    try:
        _sync_french(tmp_path)
    finally:
        shutil.rmtree(hexo.ROOT / "fr")


def _sync_french(tmp_path):
    blog = tmp_path / "source"
    (blog / "fr/btcguide/quorum").mkdir(parents=True)
    (blog / "fr/btcguide/quorum/index.md").write_text("hand-written")
    r = subprocess.run(["make", "hexo-sync", f"BLOG={blog}"], cwd=hexo.ROOT, capture_output=True, text=True)  # fr_tree is on disk, so make builds French too
    assert r.returncode != 0 and "fr/btcguide/quorum/index.md" in r.stdout + r.stderr and "delete" in (r.stdout + r.stderr).lower()
    (blog / "fr/btcguide/quorum/index.md").unlink()
    r = subprocess.run(["make", "hexo-sync", f"BLOG={blog}"], cwd=hexo.ROOT, capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    assert "lang: fr" in (blog / "fr/btcguide/why-multisig/index.md").read_text()
    assert len(list((blog / "fr/btcguide").glob("**/index.md"))) == len(hexo.guide_pages())




def test_git_stamp_untracked_page():  # a brand-new page must preview, not crash
    f = hexo.ROOT / "_pages/zz-untracked-test-page.md"
    f.write_text("---\ntitle: T\n---\nx\n")
    try:
        date, sha = hexo.git_stamp([f])
    finally:
        f.unlink()
    assert sha.endswith("-dirty") and re.fullmatch(r"\d{4}-\d\d-\d\d \d\d:\d\d:\d\d", date)



def test_description_from_front_matter():
    pages = hexo.guide_pages()
    by = {p.url: p for p in pages}
    for url in ("/equipment", "/known-issues/software/specter", ""):
        p = by[url]
        desc = hexo.read_page(p)[0]["description"]  # every page carries a hand-written one
        assert 20 < len(desc) <= 160 and ": " not in desc and desc[0].isalpha()
        assert f"description: {json.dumps(desc, ensure_ascii=False)}" in hexo.render_page(p, pages)


def test_prefix_and_hexo_url_fr():
    assert hexo.prefix("fr") == "/fr/btcguide" and hexo.hexo_url("/equipment", "x", "fr") == "/fr/btcguide/equipment/#x"


def test_guide_pages_fr_titles_and_stubs(fr_tree):
    en, fr = hexo.guide_pages(), hexo.guide_pages("fr")
    assert [p.url for p in fr] == [p.url for p in en] and all(p.lang == "fr" for p in fr)
    by = {p.url: p for p in fr}
    assert by[""].title == "Guide Bitcoin Sécurité 10x" and not hexo.is_stub(by[""])
    assert by["/why-multisig"].title == "Pourquoi le multisig ?" and not hexo.is_stub(by["/why-multisig"])
    assert by["/equipment"].title == "Matériel" and hexo.is_stub(by["/equipment"])  # stub of a TOC page: the French label
    assert by["/equipment-advanced"].title == "Equipment" and hexo.is_stub(by["/equipment-advanced"])  # no label, no file: English title
    assert hexo.display_title(by["/equipment-advanced"]) == "Equipment » Considérations avancées"
    assert hexo.display_title(by["/known-issues/hardware/coldcard"]) == "Problèmes connus : Coldcard"
    assert by["/license"].title == "Licence" and by["/disclaimer"].title == "Avertissement"


def test_render_french_page_and_stub(fr_tree):
    pages = hexo.guide_pages("fr")
    by = {p.url: p for p in pages}
    out = hexo.render_page(by["/why-multisig"], pages)
    fr = hexo.book.FR.relative_to(hexo.ROOT)
    assert "lang: fr\n" in out and f'btcguide_source: "{fr}/_pages/why-multisig.md"' in out
    assert "[lien](/fr/btcguide/how-it-works/)" in out and "» Section suivante : [Comment ça marche](/fr/btcguide/how-it-works/)" in out
    assert "![](/media/btcguide/img/setup-paper-seedpicker-example-output.png)" in out  # shared media
    assert "[considérations avancées](/fr/btcguide/why-multisig-advanced/)" in out
    assert f"(https://github.com/piprim/btcguide.github.io/blob/master/{fr}/_pages/why-multisig.md)" in out and "[Licence MIT](/fr/btcguide/license/)" in out and "Dernière mise à jour" in out
    stub = hexo.render_page(by["/equipment"], pages)
    assert "*Cette page n'est pas encore traduite. [Lire la version anglaise](/btcguide/equipment/).*" in stub
    assert 'btcguide_source: "_pages/equipment.md"' in stub and "blob/master/_pages/equipment.md" in stub
    assert 'title: "Matériel"' in stub
    assert "← [Pick Quorum » Considérations avancées](/fr/btcguide/quorum-advanced/) · [Equipment » Considérations avancées](/fr/btcguide/equipment-advanced/) →" in stub
    assert "Ubuntu" not in stub  # blank: no English body
    coldcard = hexo.render_page(by["/known-issues/hardware/coldcard"], pages)
    assert "Python en français." in coldcard and 'title: "Problèmes connus : Coldcard"' in coldcard
    assert '<a id="bug-de-gnration-de-graine-2021--2026"></a>\n\n<a id="weak-seed-generation-bug-2021-to-2026"></a>' in coldcard


def test_render_french_missing_include_fails(fr_tree):
    (fr_tree / "_includes/hw/python.md").unlink()
    pages = hexo.guide_pages("fr")
    with pytest.raises(SystemExit, match="fr/_includes/hw/python.md missing"):
        hexo.render_page({p.url: p for p in pages}["/known-issues/hardware/coldcard"], pages)


def test_french_home(fr_tree):
    pages = hexo.guide_pages("fr")
    home = hexo.render_page(pages[0], pages)
    assert "## Table des matières" in home and "### Guide (fr)" in home
    assert "- [Introduction : pourquoi le multisig ?](/fr/btcguide/why-multisig/)" in home
    assert "releases/download/book/btcguide-fr.pdf" in home and "releases/download/book/btcguide.pdf" not in home


def test_check_accepts_stub_links_only_to_real_pages(built, fr_tree):
    pages = hexo.guide_pages("fr")
    good = {p.url: hexo.render_page(p, pages) for p in pages}
    media = hexo.HEXO_OUT / "media/btcguide"
    assert hexo.check(good, media, len(good)) == []
    bad = dict(good)
    bad["/equipment"] = good["/equipment"].replace("(/btcguide/equipment/)", "(/btcguide/nope/)")
    assert hexo.check(bad, media, len(good))


def test_build_both_languages(fr_tree):
    hexo.build()
    out = hexo.HEXO_OUT
    assert (out / "page/btcguide/equipment/index.md").exists() and (out / "page/fr/btcguide/equipment/index.md").exists()
    assert len(list(out.glob("page/fr/btcguide/**/index.md"))) == len(hexo.guide_pages())
    assert not (out / "media/fr").exists() and not (out / "page/fr/media").exists()  # media once
    assert "lang: fr" in (out / "page/fr/btcguide/why-multisig/index.md").read_text()


def test_build_skips_french_without_toc(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(hexo.book, "FR", tmp_path / "fr")
    hexo.build()
    assert "fr/index.html missing, French pages skipped" in capsys.readouterr().err
    assert not (hexo.HEXO_OUT / "page/fr").exists()


def test_build_fails_on_french_toc_mismatch(fr_tree):
    idx = fr_tree / "index.html"
    idx.write_text(idx.read_text().replace('<li><a href="/how-it-works">How it Works</a></li>', "", 1))
    with pytest.raises(SystemExit, match="TOC mismatch"):
        hexo.build()


def test_french_headings_keep_english_anchors(fr_tree):
    pages = hexo.guide_pages("fr")
    by = {p.url: p for p in pages}
    out = hexo.render_page(by["/key-rotation"], pages)
    assert '<a id="quand-renouveler"></a>\n\n<a id="when-to-rotate"></a>\n\n## Quand renouveler' in out
    assert "[comment](#how-to-rotate)" in out
    assert "[ancre](/fr/btcguide/key-rotation/#when-to-rotate)" in hexo.render_page(by["/why-multisig"], pages)
    assert hexo.check({p.url: hexo.render_page(p, pages) for p in pages}, hexo.HEXO_OUT / "media/btcguide", len(pages)) == []


def test_french_heading_count_must_match_english(fr_tree):
    f = fr_tree / "_pages/key-rotation.md"
    f.write_text(f.read_text().replace("#### Comment renouveler", "Comment renouveler"))
    pages = hexo.guide_pages("fr")
    with pytest.raises(SystemExit, match=r"key-rotation.md: 1 heading\(s\), English has 2"):
        hexo.render_page({p.url: p for p in pages}["/key-rotation"], pages)
