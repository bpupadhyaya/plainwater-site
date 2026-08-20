#!/usr/bin/env python3
"""Static-renders the module/feature browser from .content-src/*.json
(populated by sync-content.sh) into modules/index.html and modules/<id>/index.html.

Free features render in full (entries, citations). Premium features render
title + summary only, plus an "unlock in the app" note — full premium
content is never published on the public web site. The raw source JSON
itself is never copied into a served path (see .gitignore's .content-src/
entry) specifically to prevent premium content leaking via view-source.

Re-run after scripts/sync-content.sh whenever the mobile repo's content
changes. Output (modules/**/*.html) is committed — this is the site's own
"build step," not a client-side one; the deployed pages need no JavaScript.
"""
import html
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / ".content-src"
OUT = ROOT / "modules"

NAV = [
    ("Home", "root", ""),
    ("Modules", "root", "modules/"),
    ("About", "root", "about/"),
    ("Privacy Policy", "root", "privacy/"),
    ("Support", "root", "support/"),
]

MODULE_FILES = {
    "a": "module-a-visual-sensory.json",
    "b": "module-b-test-kit.json",
    "c": "module-c-purification.json",
    "d": "module-d-illness.json",
    "e": "module-e-storage.json",
    "f": "module-f-region.json",
    "g": "module-g-scenario.json",
    "h": "module-h-reference.json",
}


def esc(s):
    return html.escape(s, quote=False) if s else ""


def nav_html(root_prefix):
    links = "\n".join(
        f'            <li><a href="{root_prefix}{path}">{esc(label)}</a></li>' for label, _, path in NAV
    )
    return f"""<nav>
    <div class="nav-inner">
        <a href="{root_prefix}" class="nav-logo">
            <img src="{root_prefix}assets/img/favicon.svg" alt="" width="34" height="34">
            PlainWater
        </a>
        <ul class="nav-links">
{links}
        </ul>
        <button class="mobile-menu-btn" onclick="document.querySelector('.nav-links').classList.toggle('show')" aria-label="Menu">&#9776;</button>
    </div>
</nav>"""


def footer_html(root_prefix):
    return f"""<footer>
    <div class="footer-inner">
        <ul class="footer-links">
            <li><a href="{root_prefix}modules/">Modules</a></li>
            <li><a href="{root_prefix}about/">About</a></li>
            <li><a href="{root_prefix}privacy/">Privacy Policy</a></li>
            <li><a href="{root_prefix}disclaimer/">Disclaimer</a></li>
            <li><a href="{root_prefix}support/">Support</a></li>
            <li><a href="https://equalinformation.com" target="_blank" rel="noopener">EqualInformation</a></li>
        </ul>
        <p class="footer-copy">
            &copy; 2026 EqualInformation, LLC. All rights reserved.<br>
            PlainWater provides general educational information, not medical advice or water-test certification. <a href="{root_prefix}disclaimer/">Read the disclaimer</a>.
        </p>
    </div>
</footer>"""


def page(title, description, body, canonical_path, depth=1):
    """depth = number of directory levels below the site root this page lives at
    (modules/index.html -> 1, modules/a/index.html -> 2)."""
    root_prefix = "../" * depth
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{esc(title)}</title>
    <meta name="description" content="{esc(description)}">
    <link rel="canonical" href="https://bpupadhyaya.github.io/plainwater-site/{canonical_path}">
    <link rel="icon" type="image/svg+xml" href="{root_prefix}assets/img/favicon.svg">
    <meta name="theme-color" content="#0b3d2e">
    <link rel="stylesheet" href="{root_prefix}assets/fonts/inter.css">
    <link rel="stylesheet" href="{root_prefix}assets/css/style.css">
    <link rel="stylesheet" href="{root_prefix}assets/css/modules.css">
</head>
<body>
{nav_html(root_prefix)}
{body}
{footer_html(root_prefix)}
</body>
</html>
"""


def module_nav(current=None):
    items = []
    for key in MODULE_FILES:
        cls = ' class="current"' if key == current else ""
        items.append(f'<a href="../{key}/"{cls}>{key.upper()}</a>')
    return '<div class="module-nav">' + "".join(items) + "</div>"


def render_entry(entry):
    urgency = entry.get("urgency") or "info"
    heading = esc(entry["heading"])
    body = esc(entry["body"])
    key_points = entry.get("keyPoints") or []
    kp_html = ""
    if key_points:
        items = "".join(f"<li>{esc(k)}</li>" for k in key_points)
        kp_html = f'<ul class="key-points">{items}</ul>'
    cites = entry.get("citations") or []
    cite_html = ""
    if cites:
        return None, urgency, heading, body, kp_html, cites
    return "", urgency, heading, body, kp_html, cites


def build_module_page(key, data):
    citations_map = data.get("citations", {})
    features_html = []
    free_count = sum(1 for f in data["features"] if f["tier"] == "free")
    premium_count = len(data["features"]) - free_count

    for feat in data["features"]:
        tier = feat["tier"]
        title = esc(feat["title"])
        summary = esc(feat["summary"])
        tier_label = "Free" if tier == "free" else "Premium — PlainWater Pro or a pack"

        if tier == "free":
            entries_html = []
            for entry in feat.get("entries", []):
                urgency = entry.get("urgency") or "info"
                kp = entry.get("keyPoints") or []
                kp_html = ("<ul class=\"key-points\">" + "".join(f"<li>{esc(k)}</li>" for k in kp) + "</ul>") if kp else ""
                cites = entry.get("citations") or []
                cite_links = []
                for ckey in cites:
                    c = citations_map.get(ckey)
                    if c:
                        cite_links.append(
                            f'<a href="{esc(c["url"])}" target="_blank" rel="noopener">{esc(c["authority"])} — {esc(c["title"])}</a>'
                        )
                cite_html = f'<div class="citations">Source{"s" if len(cite_links) != 1 else ""}: ' + "; ".join(cite_links) + "</div>" if cite_links else ""
                entries_html.append(f"""
                <div class="feature-entry">
                    <h4><span class="urgency-bar {esc(urgency)}"></span>{esc(entry["heading"])}</h4>
                    <p>{esc(entry["body"])}</p>
                    {kp_html}
                    {cite_html}
                </div>""")
            body_html = f'<div class="feature-entries">{"".join(entries_html)}</div>'
        else:
            body_html = '<div class="premium-note">This feature\'s full guidance unlocks with PlainWater Pro or the relevant pack in the app. Summary shown here; full reference content is available on-device.</div>'

        features_html.append(f"""
        <div class="feature-card">
            <span class="feature-tier {tier}">{esc(tier_label)}</span>
            <h3>{title}</h3>
            <p class="f-summary">{summary}</p>
            {body_html}
        </div>""")

    body = f"""
<div class="hero hero-sub">
    <div class="wrap">
        <h1>Module {key.upper()} <span class="accent">&mdash; {esc(data['title'])}</span></h1>
        <p class="tagline">{esc(data['subtitle'])}</p>
        <p class="lede">{esc(data['overview'])}</p>
        <div class="stats">
            <div class="stat"><div class="num">{len(data['features'])}</div><div class="label">Features</div></div>
            <div class="stat"><div class="num">{free_count}</div><div class="label">Free</div></div>
            <div class="stat"><div class="num">{premium_count}</div><div class="label">Premium</div></div>
        </div>
    </div>
</div>
<div class="crumbs" role="navigation" aria-label="Breadcrumb"><div class="wrap"><a href="../../">Home</a><span class="sep">&rsaquo;</span><a href="../">Modules</a><span class="sep">&rsaquo;</span><span class="current">{esc(data['title'])}</span></div></div>
<div class="content wrap">
    {module_nav(key)}
    <div class="feature-list">
        {"".join(features_html)}
    </div>
</div>"""

    return page(
        f"{data['title']} — PlainWater",
        f"PlainWater module {key.upper()}: {data['subtitle']}. {len(data['features'])} features, browsable offline reference.",
        body,
        f"modules/{key}/",
        depth=2,
    )


def build_index_page(modules):
    cards = []
    for key, data in modules.items():
        free_count = sum(1 for f in data["features"] if f["tier"] == "free")
        cards.append(f"""
        <a class="module-card" href="{key}/">
            <span class="m-letter">{key.upper()}</span>
            <h3>{esc(data['title'])}</h3>
            <p class="m-tagline">{esc(data['subtitle'])}</p>
            <p>{esc(data['overview'])}</p>
            <div class="m-counts">{len(data['features'])} features &middot; {free_count} free</div>
        </a>""")

    total_features = sum(len(d["features"]) for d in modules.values())
    total_free = sum(sum(1 for f in d["features"] if f["tier"] == "free") for d in modules.values())

    body = f"""
<div class="hero hero-sub">
    <div class="wrap">
        <h1>Browse all <span class="accent">{total_features} features</span></h1>
        <p class="tagline">Eight modules, offline water-safety guidance</p>
        <p class="lede">The same knowledge base that ships on-device in the PlainWater app, laid out for a bigger screen. Free features are shown in full below, including their citations; premium features show a summary — full guidance unlocks in the app.</p>
        <div class="stats">
            <div class="stat"><div class="num">{total_features}</div><div class="label">Total features</div></div>
            <div class="stat"><div class="num">{total_free}</div><div class="label">Free forever</div></div>
            <div class="stat"><div class="num">8</div><div class="label">Modules</div></div>
        </div>
    </div>
</div>
<div class="crumbs" role="navigation" aria-label="Breadcrumb"><div class="wrap"><a href="../">Home</a><span class="sep">&rsaquo;</span><span class="current">Modules</span></div></div>
<div class="content wrap">
    <div class="module-grid">
        {"".join(cards)}
    </div>
</div>"""
    return page(
        "Browse All Features — PlainWater",
        "Browse all 78 PlainWater water-safety features across 8 modules, with full free-tier content and citations.",
        body,
        "modules/",
    )


def main():
    if not SRC.exists():
        print(f"error: {SRC} not found — run scripts/sync-content.sh first", file=sys.stderr)
        return 1

    modules = {}
    for key, filename in MODULE_FILES.items():
        fp = SRC / filename
        if not fp.exists():
            print(f"error: missing {fp}", file=sys.stderr)
            return 1
        modules[key] = json.loads(fp.read_text())

    OUT.mkdir(exist_ok=True)
    (OUT / "index.html").write_text(build_index_page(modules))
    for key, data in modules.items():
        module_dir = OUT / key
        module_dir.mkdir(exist_ok=True)
        (module_dir / "index.html").write_text(build_module_page(key, data))

    print(f"Built modules/index.html + {len(modules)} module pages ({sum(len(d['features']) for d in modules.values())} features total).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
