#!/usr/bin/env python3
"""
add_logo_band.py  —  DSF Scholarship Portal

Adds the DSF logo to the header band of both HTML files and sets the
portal title. The logo is embedded directly into each file as base64,
so the files stay fully self-contained and still work offline.

USAGE:
    1. Put this script, the two HTML files, and the logo PNG in one folder.
    2. Change PORTAL_NAME below if you want a different title.
    3. Run:  python add_logo_band.py

Safe to re-run: it makes a timestamped backup each time, and running it
again just replaces the band rather than stacking a second one.
"""

import base64
import io
import os
import re
import shutil
import sys
from datetime import datetime

# ---------------------------------------------------------------
PORTAL_NAME = "DSF Scholarship Buddy"
WEBSITE      = "www.dsfindia.org"
TAGLINE_LINK = "https://www.dsfindia.org"
LOGO = "DSF_Logo_CMYK_300ppi-Slogan.png"
# ---------------------------------------------------------------

TARGETS = ["DSF_Scholarship_Portal.html", "DSF_Scholarship_Editor.html"]

CSS = """
/* --- DSF logo band --- */
.brand{display:flex;align-items:center;gap:16px;flex-wrap:wrap}
.logo-chip{display:inline-flex;align-items:center;background:#fff;border-radius:10px;
  padding:9px 14px;box-shadow:0 2px 10px rgba(18,26,58,.24);flex:0 0 auto;
  text-decoration:none;transition:transform .15s ease}
.logo-chip:hover{transform:translateY(-1px)}
.logo-chip img{height:38px;width:auto;display:block}
.logo-chip.compact{padding:6px 10px;border-radius:8px}
.logo-chip.compact img{height:26px}
.brand-txt{min-width:0}
@media(max-width:640px){
  .brand{gap:12px}
  .logo-chip{padding:7px 11px}
  .logo-chip img{height:28px}
}
/* --- footer --- */
footer .foot-brand{color:var(--navy);font-size:13.5px;font-weight:600}
footer .foot-web{margin-top:4px;font-size:13px}
footer .foot-web a{color:var(--blue);text-decoration:none;font-weight:600}
footer .foot-web a:hover{text-decoration:underline}
footer .foot-note{margin-top:9px;line-height:1.5}
"""

FOOTER = (
    '<footer>\n'
    '  <div class="foot-brand">Dream School Foundation '
    '&middot; Making the Right to Education Real</div>\n'
    f'  <div class="foot-web"><a href="{TAGLINE_LINK}" target="_blank" '
    f'rel="noopener">{WEBSITE}</a></div>\n'
    '  <div class="foot-note">Scheme data compiled 8 August 2026 for '
    'AY 2026&ndash;27 from the National Scholarship Portal, funder websites '
    'and secondary sources. This file works offline and stores nothing.</div>\n'
    '</footer>'
)


def encode_logo(path):
    """Crop transparent margins, resize for web, return a base64 data URI."""
    try:
        from PIL import Image
    except ImportError:
        print("This script needs Pillow. Install it with:")
        print("    pip install Pillow")
        sys.exit(1)

    im = Image.open(path).convert("RGBA")
    bbox = im.getbbox()
    if bbox:
        im = im.crop(bbox)
    height = 110
    width = round(im.size[0] * height / im.size[1])
    im = im.resize((width, height), Image.LANCZOS)

    buf = io.BytesIO()
    im.save(buf, format="PNG", optimize=True)
    raw = buf.getvalue()
    print(f"  logo prepared: {width}x{height}px, {len(raw) // 1024} KB")
    return "data:image/png;base64," + base64.b64encode(raw).decode("ascii")


def build_brand(data_uri, name, compact=False):
    alt = "Dream School Foundation — Making the Right to Education Real"
    chip = (f'<a class="logo-chip{" compact" if compact else ""}" href="{TAGLINE_LINK}" '
            f'target="_blank" rel="noopener" aria-label="Dream School Foundation">'
            f'<img src="{data_uri}" alt="{alt}"></a>')
    if compact:
        # Editor toolbar: logo plus the tool's own title, no subline.
        return ('<div class="brand">\n'
                f'    {chip}\n'
                f'    <div class="brand-txt"><h1>{name}</h1></div>\n'
                '  </div>')
    return (
        '<div class="brand">\n'
        f'      {chip}\n'
        '      <div class="brand-txt">\n'
        f'        <h1>{name}</h1>\n'
        '        <div class="sub" id="subline">schemes for students in Karnataka '
        '&middot; academic year 2026&ndash;27</div>\n'
        '      </div>\n'
        '    </div>'
    )


def main():
    missing = [f for f in [LOGO] + TARGETS if not os.path.exists(f)]
    if missing:
        print("Could not find these files in this folder:")
        for f in missing:
            print("   -", f)
        print(f"\nCurrent folder: {os.getcwd()}")
        return 1

    data_uri = encode_logo(LOGO)
    new_brand = build_brand(data_uri, PORTAL_NAME)
    stamp = datetime.now().strftime("%Y-%m-%d_%H%M")
    print()

    for target in TARGETS:
        html = open(target, encoding="utf-8").read()

        patched = None

        if 'class="logo-chip' in html:
            # Already has a band: swap the logo and, for the portal only,
            # the title. Leaves the editor's own toolbar title alone.
            patched = re.sub(
                r'(<a class="logo-chip[^>]*>\s*<img src=")data:image/png;base64,[^"]*(")',
                lambda mm: mm.group(1) + data_uri + mm.group(2),
                html, count=1)
            if 'id="subline"' in patched:
                patched = re.sub(
                    r'(<div class="brand-txt">\s*<h1>).*?(</h1>)',
                    lambda mm: mm.group(1) + PORTAL_NAME + mm.group(2),
                    patched, count=1, flags=re.S)
        else:
            # Portal: brand block ending in the subline div
            m = re.search(
                r'<div class="brand">.*?<div class="sub" id="subline">.*?</div>\s*</div>',
                html, re.S)
            if m:
                patched = html[: m.start()] + new_brand + html[m.end():]
            else:
                # Editor: plain wrapper holding .org and the toolbar h1
                m = re.search(
                    r'<div>\s*<div class="org">.*?</div>\s*<h1>(.*?)</h1>\s*</div>',
                    html, re.S)
                if m:
                    patched = (html[: m.start()]
                               + build_brand(data_uri, m.group(1), compact=True)
                               + html[m.end():])

        if patched is None:
            print(f"! {target}: could not find the header block — skipped")
            continue

        shutil.copy2(target, f"{target}.backup_{stamp}")
        html = patched

        # Add the CSS once, right after the .mast rule.
        if "--- DSF logo band ---" not in html:
            anchor = re.search(r'\.mast\{[^}]*\}', html)
            if anchor:
                html = html[: anchor.end()] + CSS + html[anchor.end():]
            else:
                html = html.replace("</style>", CSS + "</style>", 1)

        # Keep the browser tab title in step with the portal name.
        if 'id="subline"' in html:
            html = re.sub(r'<title>[^<]*</title>',
                          lambda mm: f'<title>{PORTAL_NAME} &mdash; Karnataka</title>',
                          html, count=1)

        # Rebuild the footer so the website link is present (portal only —
        # the editor has no footer, and its logo already links to the site).
        fm = re.search(r'<footer>.*?</footer>', html, re.S)
        if fm:
            html = html[: fm.start()] + FOOTER + html[fm.end():]

        open(target, "w", encoding="utf-8").write(html)
        size = len(html.encode()) // 1024
        print(f"  updated {target}  ({size} KB)")
        print(f"      backup: {target}.backup_{stamp}")

    print(f'\nTitle set to: "{PORTAL_NAME}"')
    print("Open the HTML file in a browser to check it, then upload to GitHub.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
