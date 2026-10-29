import json, subprocess

import pytest

import build, stale


def test_english_sources_order_and_set():
    srcs = [str(s) for s in stale.english_sources()]
    assert srcs[0] == "index.html" and srcs[1].startswith("_includes/")
    assert "_pages/why-multisig.md" in srcs and "disclaimer.md" in srcs and "LICENSE" not in srcs
    assert len(srcs) == len(set(srcs)) and srcs.index("_includes/hw/psbt.md") < srcs.index("_pages/why-multisig.md")


def test_report_without_fr(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(build, "FR", tmp_path / "fr")
    assert stale.report() == 1
    out = capsys.readouterr().out
    assert out.startswith("MISSING index.html\n") and "MISSING _pages/why-multisig.md" in out and "ORPHAN" not in out


def test_report_classes(fr_tree, capsys):
    old = subprocess.run(["git", "log", "-2", "--format=%H", "--", "_pages/why-multisig.md"], cwd=build.ROOT, capture_output=True, text=True, check=True).stdout.split()[-1]
    (fr_tree / "translated_from.json").write_text(json.dumps({
        "index.html": stale.current_sha("index.html"),
        "_pages/why-multisig.md": old,
        "_includes/hw/psbt.md": "deadbeef0000000",
    }))
    (fr_tree / "_pages/zz-orphan.md").write_text("x")
    assert stale.report() == 1
    out = capsys.readouterr().out
    assert "MISSING index.html" not in out and "UNTRACKED disclaimer.md" in out and "MISSING _pages/equipment.md" in out
    assert f"STALE _pages/why-multisig.md: {old[:7]} -> {stale.current_sha('_pages/why-multisig.md')[:7]}\n  " in out
    assert "STALE _includes/hw/psbt.md: deadbee -> " in out and "  (recorded commit unknown)" in out
    assert "ORPHAN fr/_pages/zz-orphan.md" in out and "translated_from.json" not in out


def test_report_all_current(fr_tree, capsys):
    manifest = {str(s): stale.current_sha(s) for s in stale.english_sources()}
    (fr_tree / "translated_from.json").write_text(json.dumps(manifest))
    for s in stale.english_sources():
        f = fr_tree / s
        if not f.exists():
            f.parent.mkdir(parents=True, exist_ok=True)
            f.write_text("---\ntitle: x\n---\nx\n")
    assert stale.report() == 0 and "all French files up to date" in capsys.readouterr().out


def test_report_recorded_commit_newer_than_file(fr_tree, capsys):
    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=build.ROOT, capture_output=True, text=True, check=True).stdout.strip()
    assert head != stale.current_sha("_includes/hw/psbt.md")  # the file's last change is older than HEAD
    (fr_tree / "translated_from.json").write_text(json.dumps({"_includes/hw/psbt.md": head}))
    stale.report()
    assert "psbt" not in capsys.readouterr().out  # translated at HEAD: up to date, not STALE with an empty history


def test_make_stale_exit_code():
    if (build.ROOT / "fr").exists():
        pytest.skip("make reads the real fr/ tree")
    assert subprocess.run(["make", "stale"], cwd=build.ROOT, capture_output=True).returncode != 0  # no fr/: everything MISSING; make reports a failed recipe as 2
