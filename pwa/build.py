#!/usr/bin/env python3
"""Build the WURA home-screen app (PWA) into app/ from the Claude Design export.

Re-run after exporting a new WURA.dc.html:  python3 pwa/build.py
"""
import hashlib
import json
import shutil
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "project"
PWA = ROOT / "pwa"
OUT = ROOT / "app"
DS = "_ds/classical-20f9543c-4b48-4898-9c80-1e2f739e756c"


def replace_once(text, old, new):
    assert text.count(old) == 1, f"expected exactly one match for: {old[:80]!r}"
    return text.replace(old, new)


HEAD = """<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>WURA</title>
<meta name="description" content="Welcome back to yourself.">
<meta name="theme-color" content="#1B2419">
<link rel="manifest" href="manifest.webmanifest">
<link rel="icon" type="image/png" sizes="192x192" href="icons/icon-192.png">
<link rel="apple-touch-icon" href="icons/apple-touch-icon.png">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-title" content="WURA">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<style>
html,body{background:#0F150E;overscroll-behavior:none}
/* On a phone (or once installed) the app fills the screen instead of sitting in a mock phone frame. */
@media (max-width:520px),(display-mode:standalone){
  [data-pwa=outer]{padding:0!important;min-height:100vh!important;min-height:100dvh!important}
  [data-pwa=frame]{width:100vw!important;height:100vh!important;height:100dvh!important;border-radius:0!important;box-shadow:none!important}
  [data-pwa=topbar]{padding-top:max(14px,calc(env(safe-area-inset-top) + 6px))!important}
  [data-pwa=nav]{bottom:max(14px,env(safe-area-inset-bottom))!important}
}
</style>
<script src="pwa-shim.js"></script>
<script src="./support.js"></script>"""


def build_html():
    html = (SRC / "WURA.dc.html").read_text()
    html = replace_once(
        html,
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n<script src="./support.js"></script>',
        HEAD,
    )
    html = replace_once(html, f'href="{DS}/styles.css"', 'href="styles.css"')
    html = replace_once(html, f'src="{DS}/_ds_bundle.js"', 'src="ds_bundle.js"')
    html = replace_once(html, '<div data-app="1" style="', '<div data-app="1" data-pwa="outer" style="')
    html = replace_once(html, '<div style="position:relative;width:390px;height:844px;', '<div data-pwa="frame" style="position:relative;width:390px;height:844px;')
    html = replace_once(html, '<div style="position:absolute;top:0;left:0;right:0;z-index:20;', '<div data-pwa="topbar" style="position:absolute;top:0;left:0;right:0;z-index:20;')
    html = replace_once(html, '<div style="position:absolute;left:14px;right:14px;bottom:20px;z-index:15;', '<div data-pwa="nav" style="position:absolute;left:14px;right:14px;bottom:20px;z-index:15;')
    return html


def icon(size, maskable=False):
    s = 4  # supersample
    W = size * s
    img = Image.new("RGB", (W, W), "#1B2419")
    # painted ground: warm light upper right, olive left
    glow = Image.new("RGB", (W, W), "#1B2419")
    g = ImageDraw.Draw(glow)
    g.ellipse([W * 0.45, -W * 0.25, W * 1.25, W * 0.55], fill="#5A4A38")
    g.ellipse([-W * 0.3, W * 0.35, W * 0.5, W * 1.05], fill="#303826")
    img = Image.blend(img, glow.filter(ImageFilter.GaussianBlur(W * 0.12)), 0.75)
    d = ImageDraw.Draw(img)
    pad = W * (0.26 if maskable else 0.2)
    left, right, bottom = pad, W - pad, W - pad * 0.85
    r = (right - left) / 2
    top = pad * 0.9
    lw = max(2, int(W * 0.012))
    gold = "#B7A17B"
    # gold hairline arch
    d.arc([left, top, right, top + 2 * r], 180, 360, fill=gold, width=lw)
    d.line([left + lw / 2, top + r, left + lw / 2, bottom], fill=gold, width=lw)
    d.line([right - lw / 2, top + r, right - lw / 2, bottom], fill=gold, width=lw)
    # soft halo orb
    cx, cy, orb = W / 2, top + r * 1.15, r * 0.42
    halo = Image.new("L", (W, W), 0)
    ImageDraw.Draw(halo).ellipse([cx - orb * 1.9, cy - orb * 1.9, cx + orb * 1.9, cy + orb * 1.9], fill=150)
    halo = halo.filter(ImageFilter.GaussianBlur(orb * 0.6))
    img.paste(Image.new("RGB", (W, W), "#EBCFD0"), (0, 0), halo)
    d = ImageDraw.Draw(img)
    d.ellipse([cx - orb, cy - orb, cx + orb, cy + orb], fill="#FFF9F2")
    ring = orb * 1.45
    d.ellipse([cx - ring, cy - ring, cx + ring, cy + ring], outline=gold, width=max(1, lw // 2))
    return img.resize((size, size), Image.LANCZOS)


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    (OUT / "vendor").mkdir(parents=True)
    (OUT / "icons").mkdir()

    (OUT / "index.html").write_text(build_html())
    for name in ("support.js", "image-slot.js"):
        shutil.copy(SRC / name, OUT / name)
    shutil.copy(SRC / DS / "styles.css", OUT / "styles.css")
    shutil.copy(SRC / DS / "_ds_bundle.js", OUT / "ds_bundle.js")
    shutil.copy(SRC / ".image-slots.state.json", OUT / "image-slots.state.json")
    for f in (PWA / "vendor").iterdir():
        shutil.copy(f, OUT / "vendor" / f.name)
    shutil.copy(PWA / "pwa-shim.js", OUT / "pwa-shim.js")
    shutil.copy(PWA / "manifest.webmanifest", OUT / "manifest.webmanifest")
    (OUT / ".nojekyll").write_text("")

    icon(192).save(OUT / "icons/icon-192.png")
    icon(512).save(OUT / "icons/icon-512.png")
    icon(512, maskable=True).save(OUT / "icons/icon-maskable-512.png")
    icon(180).save(OUT / "icons/apple-touch-icon.png")

    digest = hashlib.sha256()
    for p in sorted(OUT.rglob("*")):
        if p.is_file():
            digest.update(p.read_bytes())
    sw = (PWA / "sw.js").read_text().replace("__BUILD__", digest.hexdigest()[:10])
    (OUT / "sw.js").write_text(sw)
    print("built", OUT)


if __name__ == "__main__":
    main()
