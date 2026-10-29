import shutil

import pytest

import build


@pytest.fixture
def fr_tree(monkeypatch):
    """A throwaway French tree at ROOT/.fr-test (build.FR is pointed there): translated TOC, two translated pages, one include,
    one root page; everything else a stub. It must live inside the repository because git_stamp resolves paths against ROOT."""
    fr = build.ROOT / ".fr-test"
    monkeypatch.setattr(build, "FR", fr)
    if fr.exists():
        shutil.rmtree(fr)
    idx = (build.ROOT / "index.html").read_text()
    idx = (idx.replace("title: 10x Security Bitcoin Guide", "title: Guide Bitcoin Sécurité 10x")
           .replace(">Introduction: Why Multisig?<", ">Introduction : pourquoi le multisig ?<")
           .replace(">Equipment List<", ">Matériel<").replace("<h4>Guide</h4>", "<h4>Guide (fr)</h4>"))
    files = {
        "index.html": idx,
        "_pages/why-multisig.md": '---\ntitle: Pourquoi le multisig ?\ndescription: Pourquoi.\n---\n\nTexte français avec un [lien](/how-it-works) et une [ancre](/key-rotation#when-to-rotate).\n\n'
                                  '![](/assets/img/setup-paper-seedpicker-example-output.png)\n\n'
                                  '{% include next_steps.md next_url="/how-it-works" next_name="Comment ça marche" %}\n',
        # derived from the English page: same headings (one translated), same includes
        "_pages/known-issues/hardware/coldcard.md": (build.ROOT / "_pages/known-issues/hardware/coldcard.md").read_text()
                                                    .replace("#### Weak Seed Generation Bug (2021 to 2026)", "#### Bug de génération de graine (2021 à 2026)", 1),
        "_includes/hw/python.md": "Python en français.\n\n" + (build.ROOT / "_includes/hw/python.md").read_text(),  # includes keep their headings too
        "_includes/hw/encouragement.md": (build.ROOT / "_includes/hw/encouragement.md").read_text(),
        "_includes/hw/psbt.md": "PSBT en français.\n",
        # derived from the English page so front matter and includes stay identical; headings translated, one same-page link added
        "_pages/key-rotation.md": (build.ROOT / "_pages/key-rotation.md").read_text()
                                  .replace("#### When to Rotate\n", "#### Quand renouveler\n\nVoir [comment](#how-to-rotate).\n", 1)
                                  .replace("#### How to Rotate", "#### Comment renouveler"),
        "disclaimer.md": (build.ROOT / "disclaimer.md").read_text().replace("title: Disclaimer", "title: Avertissement", 1),  # headings kept
    }
    for rel, text in files.items():
        (fr / rel).parent.mkdir(parents=True, exist_ok=True)
        (fr / rel).write_text(text)
    try:
        yield fr
    finally:
        shutil.rmtree(fr)
