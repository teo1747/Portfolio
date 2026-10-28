#!/usr/bin/env python3
"""
Static site generator for the portfolio. Standard library only (Python 3.11+).

    python3 build.py            # writes the site to ./_site
    python3 build.py --serve    # builds, then serves http://localhost:8000

All text lives in content/*.toml. Every user-visible string is either a plain
string (same in both languages) or a table {en = "...", fr = "..."}.
Edit the TOML files, rebuild, commit — the GitHub Actions workflow publishes.
"""
from __future__ import annotations

import html
import json
import re
import shutil
import sys
import tomllib
from pathlib import Path

from diagrams import DIAGRAMS

ROOT = Path(__file__).resolve().parent
CONTENT = ROOT / "content"
OUT = ROOT / "_site"
LANGS = ("en", "fr")


# --------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------
def load(name: str) -> dict:
    with open(CONTENT / f"{name}.toml", "rb") as fh:
        return tomllib.load(fh)


def t(value, lang: str) -> str:
    """Translate a bilingual value: plain str or {en, fr}."""
    if value is None:
        return ""
    if isinstance(value, dict):
        return value.get(lang) or value.get("en", "")
    return str(value)


def e(text: str) -> str:
    return html.escape(text, quote=True)


def cap(text: str) -> str:
    return text[:1].upper() + text[1:]


LINK = re.compile(r"\[([^\]]+)\]\(([^)\s]+)\)")


def inline(text: str) -> str:
    """Escape, then allow **bold**, `code` and [text](url) markup in content strings."""
    out = e(text)
    out = LINK.sub(lambda m: f'<a href="{m.group(2)}">{m.group(1)}</a>', out)
    parts = out.split("**")
    out = "".join(f"<strong>{p}</strong>" if i % 2 else p for i, p in enumerate(parts))
    parts = out.split("`")
    out = "".join(f"<code>{p}</code>" if i % 2 else p for i, p in enumerate(parts))
    return out


def paras(text: str) -> str:
    blocks = [b.strip() for b in text.strip().split("\n\n") if b.strip()]
    return "".join(f"<p>{inline(' '.join(b.split()))}</p>" for b in blocks)


# --------------------------------------------------------------------------
# UART waveform: the hero graphic. Encodes a string as 8N1 frames
# (idle high, start bit low, 8 data bits LSB first, stop bit high).
# --------------------------------------------------------------------------
def uart_svg(text: str, label: str, lang: str) -> str:
    bit_w, hi, lo, idle = 14, 18, 58, 2  # px per bit, y levels, idle bits between frames
    bits: list[int] = [1] * 3
    frames = []  # (start_index, char)
    for ch in text:
        start = len(bits)
        code = ord(ch)
        frame = [0] + [(code >> i) & 1 for i in range(8)] + [1]
        bits += frame + [1] * idle
        frames.append((start, ch, code))
    bits += [1] * 3
    width = len(bits) * bit_w

    # waveform path
    y = lambda b: hi if b else lo
    d = [f"M0 {y(bits[0])}"]
    for i, b in enumerate(bits):
        x0, x1 = i * bit_w, (i + 1) * bit_w
        if i and b != bits[i - 1]:
            d.append(f"L{x0} {y(b)}")
        d.append(f"L{x1} {y(b)}")
    path = " ".join(d)

    # decode annotations, as a protocol analyser would draw them
    ann = []
    for start, ch, code in frames:
        x0 = start * bit_w
        x_data = (start + 1) * bit_w
        x_end = (start + 10) * bit_w
        ann.append(
            f'<rect class="w-frame" x="{x0 + 1}" y="74" width="{x_end - x0 - 2}" height="22" rx="3"/>'
            f'<text class="w-dec" x="{(x_data + x_end - bit_w) / 2}" y="89" text-anchor="middle">'
            f"'{e(ch)}' 0x{code:02X}</text>"
            f'<text class="w-bit" x="{x0 + bit_w / 2}" y="89" text-anchor="middle">S</text>'
            f'<text class="w-bit" x="{x_end - bit_w / 2}" y="89" text-anchor="middle">P</text>'
        )
    # bit grid ticks
    ticks = "".join(
        f'<line class="w-tick" x1="{i * bit_w}" y1="6" x2="{i * bit_w}" y2="66"/>' for i in range(len(bits) + 1)
    )
    title = "UART TX waveform" if lang == "en" else "Forme d’onde UART TX"
    desc = (f"Logic-analyser style trace of the bytes {', '.join(repr(c) for c in text)} "
            "sent as 8N1 UART frames.") if lang == "en" else (
            f"Trace façon analyseur logique des octets {', '.join(repr(c) for c in text)} "
            "envoyés en trames UART 8N1.")
    return (
        f'<figure class="wave" aria-labelledby="wave-cap">'
        f'<div class="wave-h" aria-hidden="true"><span><b>&#9632;</b> CH1 UART TX</span><span>8N1, LSB first</span></div>'
        f'<svg viewBox="-2 0 {width + 4} 100" role="img" aria-labelledby="wave-t wave-d" preserveAspectRatio="xMinYMid meet">'
        f'<title id="wave-t">{title}</title><desc id="wave-d">{e(desc)}</desc>'
        f'<g aria-hidden="true">{ticks}'
        f'<path class="w-trace" d="{path}" pathLength="1"/>{"".join(ann)}</g></svg>'
        f'<figcaption id="wave-cap">{e(label)}</figcaption></figure>'
    )


# --------------------------------------------------------------------------
# page sections
# --------------------------------------------------------------------------
def section(id_: str, heading: str, body: str, extra_class: str = "") -> str:
    return (
        f'<section id="{id_}" class="sec {extra_class}" aria-labelledby="{id_}-h">'
        f'<h2 id="{id_}-h" class="sec-h">{e(heading)}</h2>'
        f'<div class="sec-body">{body}</div></section>'
    )


def env_list(env: list, ui: dict, lang: str) -> str:
    rows = []
    for item in env:
        label = t(ui["env"].get(item["k"], item["k"]), lang)
        rows.append(f"<dt>{e(label)}</dt><dd>{inline(t(item['v'], lang))}</dd>")
    return f'<dl class="env">{"".join(rows)}</dl>'


def render_experience(exp: list, ui: dict, lang: str) -> str:
    out = ['<ol class="timeline">']
    for job in exp:
        items = []
        for it in job.get("work", []):
            bullets = "".join(f"<li>{inline(t(b, lang))}</li>" for b in it.get("points", []))
            env = env_list(it["env"], ui, lang) if it.get("env") else ""
            items.append(
                f'<div class="work"><h4>{inline(t(it["title"], lang))}</h4>'
                f'{paras(t(it.get("text"), lang)) if it.get("text") else ""}'
                f'{"<ul>" + bullets + "</ul>" if bullets else ""}{env}</div>'
            )
        out.append(
            f'<li class="job"><div class="job-when">{e(t(job["dates"], lang))}</div>'
            f'<div class="job-what"><h3>{e(t(job["role"], lang))}</h3>'
            f'<p class="job-org">{e(job["org"])}<span class="sep" aria-hidden="true">/</span>{e(t(job["place"], lang))}</p>'
            f'{paras(t(job.get("summary"), lang))}{"".join(items)}</div></li>'
        )
    out.append("</ol>")
    return "".join(out)


def render_media(p: dict, lang: str, base: str) -> str:
    """Photo/screenshot (opens full size) or inline technical diagram."""
    img = p.get("image")
    if not img:
        return ""
    cap_text = t(p.get("image_caption"), lang)
    caption = f'<figcaption>{inline(cap_text)}</figcaption>' if cap_text else ""
    if img.startswith("diagram:"):
        name = img.split(":", 1)[1]
        svg = DIAGRAMS[name]().replace('id="ah"', f'id="ah-{name}"').replace("url(#ah)", f"url(#ah-{name})")
        return f'<figure class="proj-media is-diagram">{svg}{caption}</figure>'
    alt = t(p.get("image_alt"), lang) or t(p["title"], lang)
    fit = " is-contain" if p.get("image_fit") == "contain" else ""
    src = f"{base}assets/img/projects/{img}"
    return (f'<figure class="proj-media{fit}"><a class="zoom" href="{e(src)}" data-zoom>'
            f'<img src="{e(src)}" alt="{e(alt)}" loading="lazy" decoding="async"></a>{caption}</figure>')


def render_projects(projects: list, ui: dict, lang: str, base: str = "") -> str:
    cats = ui["categories"]
    filt = ['<div class="filters" role="group" aria-label="{}">'.format(e(t(ui["filter_label"], lang)))]
    filt.append(f'<button type="button" class="chip" aria-pressed="true" data-filter="all">{e(t(ui["all"], lang))}</button>')
    for key in ("professional", "academic", "personal"):
        filt.append(f'<button type="button" class="chip" aria-pressed="false" data-filter="{key}">{e(t(cats[key], lang))}</button>')
    filt.append("</div>")

    cards = []
    ordered = sorted(projects, key=lambda q: 0 if q.get("featured") else 1)
    for p in ordered:
        repo = ""
        if p.get("repo"):
            repo = (f'<a class="repo" href="https://github.com/{e(p["repo"])}" rel="noopener">'
                    f'{e(t(ui["source"], lang))}<span class="vh"> ({e(p["repo"])})</span></a>')
        tags = "".join(f"<li>{e(t(ui['domains'].get(d, d), lang))}</li>" for d in p.get("domains", []))
        contrib = "".join(f"<li>{inline(t(c, lang))}</li>" for c in p.get("contribution", []))
        note = f'<p class="note">{inline(t(p["note"], lang))}</p>' if p.get("note") else ""
        cards.append(
            f'<article class="proj{" featured" if p.get("featured") else ""}" data-cat="{e(p["category"])}" id="p-{e(p["id"])}">'
            f'{render_media(p, lang, base)}<div class="proj-body"><header><p class="proj-meta"><span class="cat cat-{e(p["category"])}">{e(t(cats[p["category"]], lang))}</span>'
            f'<span>{e(t(p["period"], lang))}</span></p>'
            f'<h3>{e(t(p["title"], lang))}</h3>'
            f'<p class="proj-ctx">{inline(cap(t(p["context"], lang)))}</p></header>'
            f'{paras(t(p["summary"], lang))}'
            f'<ul class="tags" aria-label="{e(t(ui["domains_label"], lang))}">{tags}</ul>'
            f'<details><summary>{e(t(ui["details"], lang))}</summary><div class="det">'
            f'<h4>{e(t(ui["problem"], lang))}</h4>{paras(t(p["problem"], lang))}'
            f'<h4>{e(t(ui["contribution"], lang))}</h4><ul>{contrib}</ul>'
            f'<h4>{e(t(ui["environment"], lang))}</h4>{env_list(p["env"], ui, lang)}'
            f'<h4>{e(t(ui["outcome"], lang))}</h4>{paras(t(p["outcome"], lang))}{note}'
            f'</div></details>{repo}</div></article>'
        )
    return "".join(filt) + f'<div class="projects" aria-live="polite">{"".join(cards)}</div>'


def render_skills(skills: list, lang: str) -> str:
    rows = []
    for g in skills:
        rows.append(f"<div class=\"skill\"><dt>{e(t(g['group'], lang))}</dt>"
                    f"<dd>{inline(t(g['items'], lang))}</dd></div>")
    return f'<dl class="skills">{"".join(rows)}</dl>'


def render_education(edu: list, lang: str) -> str:
    out = []
    for ed in edu:
        out.append(
            f'<div class="edu"><p class="job-when">{e(t(ed["dates"], lang))}</p>'
            f'<div><h3>{e(t(ed["degree"], lang))}</h3>'
            f'<p class="job-org">{e(t(ed["school"], lang))}<span class="sep" aria-hidden="true">/</span>{e(t(ed["place"], lang))}</p>'
            f'{paras(t(ed.get("text"), lang)) if ed.get("text") else ""}</div></div>'
        )
    return "".join(out)


def render_cvs(cvs: list, ui: dict, lang: str, base: str) -> str:
    # current language first
    ordered = sorted(cvs, key=lambda c: 0 if c["lang"] == lang else 1)
    items = []
    for c in ordered:
        f = ROOT / "assets" / "cv" / c["file"]
        size = f" ({f.stat().st_size // 1024} KB)" if f.exists() else ""
        items.append(
            f'<li><a class="cv" href="{base}assets/cv/{e(c["file"])}" download hreflang="{c["lang"]}">'
            f'<span class="cv-t" lang="{c["lang"]}">{e(t(c["title"], lang))}</span>'
            f'<span class="cv-m">{e(t(ui["lang_name"][c["lang"]], lang))}, PDF{size}</span></a></li>'
        )
    return f'<ul class="cvs">{"".join(items)}</ul>'


def render_page(lang: str, data: dict) -> str:
    meta, ui = data["profile"]["meta"], data["ui"]
    prof = data["profile"]
    other = "fr" if lang == "en" else "en"
    base = "" if lang == "en" else "../"
    here = "" if lang == "en" else "fr/"
    other_href = base + ("fr/" if other == "fr" else "")
    canonical = meta["url"].rstrip("/") + "/" + here

    nav_items = [("profile", ui["nav"]["profile"]), ("experience", ui["nav"]["experience"]),
                 ("projects", ui["nav"]["projects"]), ("skills", ui["nav"]["skills"]),
                 ("education", ui["nav"]["education"]), ("contact", ui["nav"]["contact"])]
    nav = "".join(f'<li><a href="#{k}">{e(t(v, lang))}</a></li>' for k, v in nav_items)

    hero = (
        f'<section class="hero" aria-labelledby="name"><div class="hero-top">'
        f'<div class="hero-text"><h1 id="name">{e(meta["name"])}</h1>'
        f'<p class="role">{e(t(prof["hero"]["role"], lang))}</p>'
        f'{paras(t(prof["hero"]["intro"], lang))}'
        f'<p class="actions"><a class="btn btn-main" href="#cv">{e(t(ui["download_cv"], lang))}</a>'
        f'<a class="btn" href="mailto:{e(meta["email"])}">{e(t(ui["email_me"], lang))}</a>'
        f'<a class="btn" href="https://github.com/{e(meta["github"])}" rel="me noopener">GitHub</a></p></div>'
        f'<figure class="portrait"><span class="refdes" aria-hidden="true">U1</span><img src="{base}assets/img/portrait.jpg" alt="{e(t(ui["portrait_alt"], lang))}" width="640" height="800"></figure></div>'
        f'{uart_svg(prof["hero"]["wave_text"], t(prof["hero"]["wave_caption"], lang), lang)}'
        f'</section>'
    )

    facts = "".join(f"<div><dt>{e(t(f['k'], lang))}</dt><dd>{inline(t(f['v'], lang))}</dd></div>"
                    for f in prof["facts"])
    profile = section("profile", t(ui["nav"]["profile"], lang),
                      f'<div class="prose">{paras(t(prof["texts"]["about"], lang))}</div><dl class="facts">{facts}</dl>')

    contact_rows = (
        f'<li><span>{e(t(ui["email"], lang))}</span><a href="mailto:{e(meta["email"])}">{e(meta["email"])}</a></li>'
        f'<li><span>LinkedIn</span><a href="https://www.linkedin.com/in/{e(meta["linkedin"])}" rel="me noopener">linkedin.com/in/{e(meta["linkedin"])}</a></li>'
        f'<li><span>GitHub</span><a href="https://github.com/{e(meta["github"])}" rel="me noopener">github.com/{e(meta["github"])}</a></li>'
    )
    if meta.get("org"):
        contact_rows += (f'<li><span>{e(t(ui["org"], lang))}</span><a href="https://github.com/{e(meta["org"])}" rel="noopener">'
                         f'github.com/{e(meta["org"])}</a></li>')
    contact = section("contact", t(ui["nav"]["contact"], lang),
                      f'{paras(t(prof["texts"]["contact_text"], lang))}<ul class="contact">{contact_rows}</ul>')

    body = "".join([
        hero,
        profile,
        section("experience", t(ui["nav"]["experience"], lang), render_experience(data["experience"]["job"], ui, lang)),
        section("projects", t(ui["nav"]["projects"], lang),
                paras(t(data["projects"]["intro"], lang)) + render_projects(data["projects"]["project"], ui, lang, base),
                "sec-wide"),
        section("skills", t(ui["nav"]["skills"], lang), render_skills(data["skills"]["group"], lang)),
        section("education", t(ui["nav"]["education"], lang), render_education(data["profile"]["education"], lang)),
        section("cv", t(ui["nav"]["cv"], lang),
                paras(t(prof["texts"]["cv_text"], lang)) + render_cvs(prof["cv"], ui, lang, base)),
        contact,
    ])

    ld = {
        "@context": "https://schema.org", "@type": "Person", "name": meta["name"],
        "jobTitle": t(prof["hero"]["role"], lang), "email": "mailto:" + meta["email"], "url": canonical,
        "sameAs": [f"https://github.com/{meta['github']}", f"https://www.linkedin.com/in/{meta['linkedin']}"],
        "alumniOf": "Polytech Dijon",
    }

    return f"""<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(meta["name"])} · {e(t(prof["hero"]["role"], lang))}</title>
<meta name="description" content="{e(t(meta["description"], lang))}">
<link rel="canonical" href="{e(canonical)}">
<link rel="alternate" hreflang="en" href="{e(meta["url"].rstrip("/") + "/")}">
<link rel="alternate" hreflang="fr" href="{e(meta["url"].rstrip("/") + "/fr/")}">
<link rel="alternate" hreflang="x-default" href="{e(meta["url"].rstrip("/") + "/")}">
<meta property="og:title" content="{e(meta["name"])}">
<meta property="og:description" content="{e(t(meta["description"], lang))}">
<meta property="og:type" content="profile">
<meta property="og:url" content="{e(canonical)}">
<meta name="theme-color" content="#f3f5f4" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#11171a" media="(prefers-color-scheme: dark)">
<link rel="icon" href="{base}assets/favicon.svg" type="image/svg+xml">
<link rel="preload" href="{base}assets/fonts/archivo-var.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="{base}assets/style.css">
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
</head>
<body>
<a class="skip" href="#main">{e(t(ui["skip"], lang))}</a>
<header class="top">
  <div class="top-in">
    <a class="brand" href="#name">{e(meta["short_name"])}</a>
    <nav aria-label="{e(t(ui["nav_label"], lang))}"><ul>{nav}</ul></nav>
    <a class="lang" href="{other_href}" hreflang="{other}" lang="{other}">
      <span class="vh">{e(t(ui["switch_to"], lang))} </span>{e(t(ui["lang_name"][other], other))}</a>
  </div>
</header>
<main id="main">
{body}
</main>
<footer class="foot">
  <p>{e(meta["name"])} · {e(t(ui["footer"], lang))}</p>
  <p><a href="https://github.com/{e(meta["github"])}/{e(meta["site_repo"])}" rel="noopener">{e(t(ui["site_source"], lang))}</a></p>
</footer>
<script src="{base}assets/site.js" defer></script>
</body>
</html>
"""


# --------------------------------------------------------------------------
def build() -> None:
    data = {n: load(n) for n in ("profile", "experience", "projects", "skills", "ui")}
    if OUT.exists():
        shutil.rmtree(OUT)
    (OUT / "fr").mkdir(parents=True)
    shutil.copytree(ROOT / "assets", OUT / "assets")
    (OUT / "index.html").write_text(render_page("en", data), encoding="utf-8")
    (OUT / "fr" / "index.html").write_text(render_page("fr", data), encoding="utf-8")
    (OUT / ".nojekyll").write_text("", encoding="utf-8")
    nf = (ROOT / "404.html")
    if nf.exists():
        shutil.copy(nf, OUT / "404.html")
    missing = [c["file"] for c in data["profile"]["cv"] if not (ROOT / "assets" / "cv" / c["file"]).exists()]
    if missing:
        print("warning: CV files missing from assets/cv/:", ", ".join(missing), file=sys.stderr)
    print(f"built {OUT}")


if __name__ == "__main__":
    build()
    if "--serve" in sys.argv:
        import functools
        import http.server
        handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(OUT))
        print("serving on http://localhost:8000  (Ctrl-C to stop)")
        http.server.ThreadingHTTPServer(("127.0.0.1", 8000), handler).serve_forever()
