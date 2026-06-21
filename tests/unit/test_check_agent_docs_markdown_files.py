from __future__ import annotations

from scripts import check_agent_docs as cad


def test_markdown_files_skips_ignored_dirs(tmp_path, monkeypatch):
    keep_dir = tmp_path / "docs"
    keep_dir.mkdir()
    keep_file = keep_dir / "keep.md"
    keep_file.write_text("# keep\n", encoding="utf-8")

    ignored_dir = tmp_path / "node_modules"
    ignored_dir.mkdir()
    (ignored_dir / "skip.md").write_text("# skip\n", encoding="utf-8")

    template_dir = tmp_path / "packages" / "agent_runtime" / "templates"
    template_dir.mkdir(parents=True)
    (template_dir / "template.md").write_text("# template\n", encoding="utf-8")

    monkeypatch.setattr(cad, "ROOT", tmp_path)

    assert cad.markdown_files() == [keep_file]


def test_markdown_files_ignores_walk_errors(tmp_path, monkeypatch):
    keep_file = tmp_path / "keep.md"
    keep_file.write_text("# keep\n", encoding="utf-8")

    def fake_walk(root, topdown=True, onerror=None):
        if onerror is not None:
            onerror(FileNotFoundError("gone"))
        yield str(root), [], ["keep.md"]

    monkeypatch.setattr(cad, "ROOT", tmp_path)
    monkeypatch.setattr(cad.os, "walk", fake_walk)

    assert cad.markdown_files() == [keep_file]
