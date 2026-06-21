from pathlib import Path

import scripts.design_system_gate as dsg


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_analyze_warns_on_page_literals_controls_and_size(tmp_path):
    _write(tmp_path / "web/src/app/globals.css", ":root { --brand: #3182F6; }")
    _write(tmp_path / "web/src/lib/design-tokens.ts", 'export const brand = "#3182F6";')
    _write(
        tmp_path / "web/src/app/home/page.tsx",
        '<button className="flex items-center justify-between rounded-lg border border-border px-3 py-2">Run</button>\n'
        '<input style={{ color: "#123456" }} />\n',
    )

    findings, warnings = dsg.analyze(tmp_path, page_limit_bytes=20)
    categories = {warning.category for warning in warnings}

    assert findings == []
    assert "raw-color-literal" in categories
    assert "bare-control-in-page" in categories
    assert "oversized-page" in categories
    assert not any(w.path == "web/src/app/globals.css" for w in warnings)
    assert not any(w.path == "web/src/lib/design-tokens.ts" for w in warnings)


def test_default_check_allows_warning_first(tmp_path, capsys):
    _write(tmp_path / "web/src/app/home/page.tsx", '<button style={{ color: "#123456" }}>Run</button>')

    assert dsg.main(["--root", str(tmp_path), "--check"]) == 0
    assert dsg.main(["--root", str(tmp_path), "--check", "--strict"]) == 1

    out = capsys.readouterr().out
    assert "design-system-gate: watch" in out


def test_repeated_class_cluster_warning(tmp_path):
    repeated = "flex items-center justify-between rounded-lg border border-border px-3 py-2 text-sm"
    for name in ("home", "trade", "settings"):
        _write(tmp_path / f"web/src/app/{name}/page.tsx", f'<div className="{repeated}">x</div>')

    _, warnings = dsg.analyze(tmp_path)

    assert any(w.category == "repeated-class-cluster" for w in warnings)
