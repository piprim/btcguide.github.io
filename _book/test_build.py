import re

import pytest

import build, hexo


def test_site_path():
    assert build.site_path("https://x.y/", "/a/") is None
    assert build.site_path("/setup-wallets/paper#generate-seed", "/equipment/") == ("/setup-wallets/paper", "generate-seed")
    assert build.site_path("../verify-receive-address/coldcard", "/setup-wallets/") == ("/verify-receive-address/coldcard", "")
    assert build.site_path("verify-receive-address/", "/known-issues/") == ("/known-issues/verify-receive-address", "")
    assert build.site_path("./paper#x", "/setup-wallets/") == ("/setup-wallets/paper", "x")
    assert build.site_path("/", "/a/") == ("", "")
    assert build.site_path("#frag", "/a/") == ("#", "frag")


def test_normalize_headings():
    assert build.normalize_headings("#### A\n\n## B\n\n#### C\n", 1) == "## A\n\n## B\n\n### C\n"
    assert build.normalize_headings("## A\n#### B\n", 0) == "# A\n## B\n"
    # #### lead-in before the first ## is a sibling of the ## sections, not their parent (equipment, keystone-advanced)
    assert build.normalize_headings("#### A\n#### B\n## C\n", 1) == "## A\n## B\n## C\n"
    assert build.normalize_headings("#### A\n###### B\n###### C\n#### D\n## E\n", 1) == "## A\n### B\n### C\n## D\n## E\n"


def test_walk_toc():
    html = '<h4>Guide</h4><ol><li><a href="/a">A</a><ol><li><a href="b/c">C</a></li></ol></li><li>Plain</li></ol><h4>Known Issues &amp; Benefits</h4>'
    assert list(build.walk_toc(html)) == [
        ("section", "Guide", None, 0), ("page", "A", "/a", 1), ("page", "C", "/b/c", 2),
        ("label", "Plain", None, 1), ("section", "Known Issues & Benefits", None, 0)]


def test_localized(tmp_path, monkeypatch):
    monkeypatch.setattr(build, "FR", tmp_path)
    f = build.ROOT / "_pages/equipment.md"
    assert build.localized("en", f) == f
    assert build.localized("fr", f) == tmp_path / "_pages/equipment.md"


def test_include_file(tmp_path, monkeypatch):
    monkeypatch.setattr(build, "FR", tmp_path)
    page = build.ROOT / "_pages/known-issues/hardware/coldcard.md"
    assert build.include_file("en", "hw/psbt.md", page) == build.ROOT / "_includes/hw/psbt.md"
    with pytest.raises(SystemExit, match=r"fr/_includes/hw/psbt.md missing \(included by _pages/known-issues/hardware/coldcard.md\)"):
        build.include_file("fr", "hw/psbt.md", page)
    (tmp_path / "_includes/hw").mkdir(parents=True)
    (tmp_path / "_includes/hw/psbt.md").write_text("fr")
    assert build.include_file("fr", "hw/psbt.md", page) == tmp_path / "_includes/hw/psbt.md"


def test_toc_mismatch():
    en = '<h4>Guide</h4><ol><li><a href="/a">A</a></li><li><a href="/b">B</a></li></ol>'
    assert build.toc_mismatch(en, en.replace(">A<", ">Un<").replace("Guide", "Guide (fr)")) is None
    assert build.toc_mismatch(en, '<h4>Guide</h4><ol><li><a href="/b">B</a></li><li><a href="/a">A</a></li></ol>') == "TOC mismatch at item 1: en ('page', '/a', 1) vs fr ('page', '/b', 1)"
    assert build.toc_mismatch(en, '<h4>Guide</h4><ol><li><a href="/a">A</a></li></ol>') == "TOC mismatch at item 2: en ('page', '/b', 1) vs fr None"


def test_drop_offline_paragraph():
    intro = "Purpose.\n\nPrefer to read offline? [PDF](https://x/releases/download/book/btcguide.pdf).\n\nStatus."
    assert build.drop_offline_paragraph(intro) == "Purpose.\n\nStatus."


def test_strings_same_keys():
    assert build.STRINGS["en"].keys() == build.STRINGS["fr"].keys()
    assert "{url}" in build.STRINGS["fr"]["untranslated"]


def test_render_french_page(fr_tree):
    out = build.render(build.ROOT / "_pages/why-multisig.md", "/why-multisig", 2, "why-multisig", lang="fr", label="Introduction : pourquoi le multisig ?")
    assert out.startswith("## Pourquoi le multisig ? {#why-multisig}\n\nTexte français avec un [lien](#how-it-works) et une [ancre](#when-to-rotate).")
    assert "{%" not in out and "Comment ça marche" not in out  # next_steps is dropped in the book, as in English


def test_render_stub(fr_tree):
    out = build.render(build.ROOT / "_pages/equipment.md", "/equipment", 2, "equipment", lang="fr", label="Matériel")
    assert out == "## Matériel {#equipment}\n\n*Cette page n'est pas encore traduite. [Lire la version anglaise](https://blog.piprime.fr/btcguide/equipment/).*\n\n"
    adv = build.render(build.ROOT / "_pages/equipment-advanced.md", "/equipment-advanced", 3, "equipment-advanced", " » Considérations avancées", lang="fr")
    assert adv.startswith("### Equipment » Considérations avancées {#equipment-advanced}\n\n*Cette page")  # English title: no label, no French file


def test_render_missing_include_fails(fr_tree):
    (fr_tree / "_includes/hw/python.md").unlink()
    with pytest.raises(SystemExit, match="fr/_includes/hw/python.md missing"):
        build.render(build.ROOT / "_pages/known-issues/hardware/coldcard.md", "/known-issues/hardware/coldcard", 3, "x", lang="fr")


def test_main_french_book(fr_tree):
    build.main("fr")
    book = (build.OUT / "fr/book.md").read_text()
    assert book.startswith("---\ntitle: Guide Bitcoin Sécurité 10x\nsubtitle: Comment conserver des bitcoins sans aucun point de défaillance unique\nlang: fr\n---\n\n# Introduction {#home}\n")
    assert "# Guide (fr)\n" in book and "## Pourquoi le multisig ? {#why-multisig}" in book
    assert "## Avertissement {#disclaimer}" in book and "# Annexes\n" in book and "## Licence {#license}\n\nCe guide est publié sous licence MIT." in book
    assert book.count("Cette page n'est pas encore traduite") == len(hexo.guide_pages()) - 6  # every page but home, why-multisig, coldcard, key-rotation, disclaimer, license
    assert "releases/download/book/" not in book.split("# Guide (fr)")[0]


def test_main_french_skipped_without_toc(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(build, "FR", tmp_path / "fr")
    if (build.OUT / "fr/book.md").exists():
        (build.OUT / "fr/book.md").unlink()
    build.main("fr")
    assert "fr/index.html missing, French book skipped" in capsys.readouterr().err
    assert not (build.OUT / "fr/book.md").exists()


def test_main_french_toc_mismatch_fails(fr_tree):
    idx = fr_tree / "index.html"
    idx.write_text(idx.read_text().replace('<li><a href="/how-it-works">How it Works</a></li>', "", 1))
    with pytest.raises(SystemExit, match="TOC mismatch at item"):
        build.main("fr")


def test_render_french_headings_get_english_ids(fr_tree):
    out = build.render(build.ROOT / "_pages/key-rotation.md", "/key-rotation", 2, "key-rotation", lang="fr")
    assert "### Quand renouveler {#when-to-rotate}\n" in out and "### Comment renouveler {#how-to-rotate}\n" in out
    assert "[comment](#how-to-rotate)" in out
    f = build.FR / "_pages/key-rotation.md"
    f.write_text(f.read_text().replace("#### Comment renouveler", "Comment renouveler"))
    with pytest.raises(SystemExit, match=r"key-rotation.md: 1 heading\(s\), English has 2"):
        build.render(build.ROOT / "_pages/key-rotation.md", "/key-rotation", 2, "key-rotation", lang="fr")
