#!/usr/bin/env python3
"""Render a one-page repo map (HTML, dark/light, no dependencies, no network) from a JSON
file the onboarding wrote. Usage: repo-map.py <map.json> <out.html>

map.json (every key optional except name):
{
  "name": "huginn", "purpose": "One inbox for everything I must answer.",
  "stack": ["Bun", "TypeScript", "SQLite", "Tauri"],
  "commands": {"install": "bun install", "test": "bun run test", "lint": "bun run code:check",
               "run": "bun run dev"},
  "baseline": "312 tests, 14 s, green on 3f2a1c0",
  "layout": [{"path": "src/domain/", "role": "rules, classification, no I/O"},
             {"path": "src/adapters/", "role": "Slack, Gmail, GitLab clients"}],
  "request_path": ["Tauri window", "IPC command", "service", "domain rule", "SQLite"],
  "layers": [{"name": "UI", "items": ["inbox", "rules editor"]},
             {"name": "Services", "items": ["triage", "learn-rule"]},
             {"name": "Domain", "items": ["conditions", "sentence rules"]},
             {"name": "Adapters", "items": ["slack", "gmail", "sqlite"]}],
  "do_not_touch": ["migrations/", "vendored/"],
  "questions": ["Where do retries for Gmail live?"],
  "where_a_feature_goes": "A new source = adapter + a triage rule + one e2e test."
}
"""
import html
import json
import sys


def esc(s):
    return html.escape(str(s))


def flow_svg(steps):
    if not steps:
        return ""
    w, h, gap = 170, 44, 34
    total = len(steps) * w + (len(steps) - 1) * gap
    parts = [f'<svg viewBox="0 0 {total} {h + 8}" class="flow" role="img" aria-label="request path">']
    for i, s in enumerate(steps):
        x = i * (w + gap)
        parts.append(f'<rect x="{x}" y="4" width="{w}" height="{h}" rx="8"/>')
        parts.append(f'<text x="{x + w / 2}" y="{h / 2 + 9}" text-anchor="middle">{esc(s)}</text>')
        if i < len(steps) - 1:
            ax = x + w
            parts.append(f'<path d="M{ax + 4} {h / 2 + 4} H{ax + gap - 6}" class="arrow"/>')
    parts.append("</svg>")
    return "".join(parts)


def layers_svg(layers):
    if not layers:
        return ""
    w, lh = 720, 64
    h = len(layers) * lh
    parts = [f'<svg viewBox="0 0 {w} {h}" class="layers" role="img" aria-label="layers">']
    for i, layer in enumerate(layers):
        y = i * lh
        parts.append(f'<rect x="0" y="{y + 4}" width="{w}" height="{lh - 8}" rx="8" class="l{i % 4}"/>')
        parts.append(f'<text x="16" y="{y + lh / 2 + 5}" class="lname">{esc(layer.get("name", ""))}</text>')
        items = layer.get("items") or []
        x = 180
        for it in items:
            bw = max(70, 9 * len(str(it)) + 24)
            if x + bw > w - 8:
                break
            parts.append(f'<rect x="{x}" y="{y + 16}" width="{bw}" height="{lh - 32}" rx="6" class="item"/>')
            parts.append(f'<text x="{x + bw / 2}" y="{y + lh / 2 + 5}" text-anchor="middle" class="iname">{esc(it)}</text>')
            x += bw + 10
    parts.append("</svg>")
    return "".join(parts)


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    with open(sys.argv[1], encoding="utf-8") as f:
        m = json.load(f)
    name = m.get("name", "repo")
    cmds = m.get("commands") or {}
    sec = []
    if m.get("purpose") or m.get("stack"):
        sec.append(f'<p class="lead">{esc(m.get("purpose", ""))}</p>'
                   + (f'<p class="stack">{" · ".join(esc(s) for s in m["stack"])}</p>' if m.get("stack") else ""))
    if cmds:
        rows = "".join(f"<tr><th>{esc(k)}</th><td><code>{esc(v)}</code></td></tr>" for k, v in cmds.items())
        base = f'<p class="note">Baseline: {esc(m["baseline"])}</p>' if m.get("baseline") else ""
        sec.append(f"<h2>Run, test, lint</h2><table>{rows}</table>{base}")
    if m.get("request_path"):
        sec.append(f"<h2>Request path</h2>{flow_svg(m['request_path'])}")
    if m.get("layers"):
        sec.append(f"<h2>Layers</h2>{layers_svg(m['layers'])}")
    if m.get("layout"):
        rows = "".join(f"<tr><td><code>{esc(e.get('path', ''))}</code></td><td>{esc(e.get('role', ''))}</td></tr>"
                       for e in m["layout"])
        sec.append(f"<h2>Layout</h2><table>{rows}</table>")
    if m.get("where_a_feature_goes"):
        sec.append(f"<h2>Where a feature goes</h2><p>{esc(m['where_a_feature_goes'])}</p>")
    if m.get("do_not_touch"):
        sec.append("<h2>Do not touch</h2><ul>" + "".join(f"<li><code>{esc(x)}</code></li>" for x in m["do_not_touch"]) + "</ul>")
    if m.get("questions"):
        sec.append("<h2>Open questions</h2><ul>" + "".join(f"<li>{esc(x)}</li>" for x in m["questions"]) + "</ul>")

    page = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(name)} map</title>
<style>
:root{{--bg:#0f1115;--fg:#e6e6e6;--muted:#9aa3ad;--line:#2a2f3a;--accent:#6fb1ff;--box:#1a1f29;
 --l0:#1d2a3a;--l1:#1f3328;--l2:#352a1d;--l3:#2f2338}}
@media (prefers-color-scheme: light){{:root{{--bg:#fff;--fg:#1a1a1a;--muted:#5a6470;--line:#ddd;--accent:#1f6fd1;--box:#f3f5f8;
 --l0:#e6f0fb;--l1:#e6f6ea;--l2:#fbf0e6;--l3:#f1e8f7}}}}
body{{margin:0;padding:24px 16px;background:var(--bg);color:var(--fg);font:15px/1.5 -apple-system,Segoe UI,sans-serif;max-width:860px;margin-inline:auto}}
h1{{font-size:26px;margin:0 0 4px}} h2{{font-size:17px;margin:28px 0 8px;color:var(--accent)}}
.lead{{font-size:17px;margin:0}} .stack,.note{{color:var(--muted);margin:4px 0}}
table{{border-collapse:collapse;width:100%}} th,td{{text-align:left;padding:6px 8px;border-bottom:1px solid var(--line);vertical-align:top}}
th{{color:var(--muted);font-weight:500;width:120px}} code{{background:var(--box);padding:1px 6px;border-radius:4px}}
svg{{width:100%;height:auto;display:block}} svg text{{fill:var(--fg);font:14px -apple-system,Segoe UI,sans-serif}}
.flow rect{{fill:var(--box);stroke:var(--accent);stroke-width:1.5}} .flow .arrow{{stroke:var(--accent);stroke-width:2;marker-end:url(#a)}}
.layers rect.l0{{fill:var(--l0)}} .layers rect.l1{{fill:var(--l1)}} .layers rect.l2{{fill:var(--l2)}} .layers rect.l3{{fill:var(--l3)}}
.layers rect.item{{fill:var(--bg);stroke:var(--line)}} .layers .lname{{font-weight:600}} .layers .iname{{font-size:13px}}
ul{{padding-left:20px}}
</style></head><body>
<svg width="0" height="0" style="position:absolute"><defs><marker id="a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0L10 5L0 10z" fill="var(--accent)"/></marker></defs></svg>
<h1>{esc(name)}</h1>
{"".join(sec)}
</body></html>
"""
    with open(sys.argv[2], "w", encoding="utf-8") as f:
        f.write(page)
    print(sys.argv[2])


if __name__ == "__main__":
    main()
