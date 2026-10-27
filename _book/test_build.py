import build


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
