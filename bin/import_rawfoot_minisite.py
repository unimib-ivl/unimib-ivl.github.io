#!/usr/bin/env python3
"""Convert the RawFooT minisite of the old IVL website (www.ivl.disco.unimib.it/minisites/rawfoot/) to static pages.

One-off migration script, kept for reference. Input: a wget mirror of the minisite without the full-size images
  wget -m -np -e robots=off --reject-regex 'RawFooT_images/.*\\.png$' http://www.ivl.disco.unimib.it/minisites/rawfoot/index.php
Output: minisites/rawfoot/ in the site:
  - x.php -> x.html; textures_detail.php?id=0001&name=... -> textures_detail_0001.html; links rewritten;
  - Google Analytics removed; script tags for files missing on the old server (support.js, underscore.js) removed;
  - <html lang="en">, charset utf-8, image metadata stripped, image descriptions from the captions;
  - texture thumbnails are no longer links to the full-size images ("click to enlarge" removed): the full-size images
    (RawFooT_images/*.png, 2.35 GB) are part of the dataset, which is distributed through the FTP download page.
Old .php addresses redirect to the new pages (see _data/redirects.yml).

Usage: python3 bin/import_rawfoot_minisite.py <mirror>/minisites/rawfoot
"""
import os
import re
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEST = os.path.join(ROOT, "minisites", "rawfoot")
PAGES = ["index", "details", "textures", "download", "contact"]


def figure(m, food):
    img, caption = m.group(2), m.group(3).strip()
    src = re.search(r'src="([^"]+)"', img).group(1)
    alt = caption if not food else "%s, %s" % (food, unescape_caption(caption))
    return '<figure>%s<img src="%s" alt="%s">%s<figcaption>%s</figcaption></figure>' % (
        m.group(1) if m.group(1) and "RawFooT_images/" not in m.group(1) else "", src, alt,
        "</a>" if m.group(1) and "RawFooT_images/" not in m.group(1) else "", m.group(3))


def unescape_caption(c):
    import html as h
    return h.unescape(c).replace('"', "'")


def convert(html):
    html = re.sub(r'="([^"]*)"', lambda m: '="%s"' % re.sub(r"[\r\n]+", "", m.group(1)), html)  # line breaks in paths
    food = re.search(r"<p><b>([^<:]+):</b> click on the <b>texture image</b> to enlarge", html)
    food = food.group(1) if food else None
    html = re.sub(r"<figure>(<a [^>]*>)?(<img [^>]*>)(?:</a>)?<figcaption>(.*?)</figcaption></figure>",
                  lambda m: figure(m, food), html, flags=re.S)
    html = re.sub(r"click on the <b>texture image</b> to enlarge or (<a [^>]*><b>here</b></a>) to go back",
                  r"click \1 to go back to all the textures", html)
    html = re.sub(r"<script>\s*\(function\(i,s,o,g,r,a,m\).*?</script>\s*", "", html, flags=re.S)  # Google Analytics
    html = re.sub(r'<script src="\./(support|underscore)\.js"></script>\s*', "", html)
    html = re.sub(r'textures_detail\.php\?id=(\d+)&(?:amp;)?name=[^"]*', r"textures_detail_\1.html", html)
    for p in PAGES:
        html = re.sub(r'(href="(?:\./)?)%s\.php"' % p, r'\g<1>%s.html"' % p, html)
    html = re.sub(r"https?://(?:www\.)?ivl\.disco\.unimib\.it/", "/", html)
    html = re.sub(r"<html>", '<html lang="en">', html, count=1)
    html = html.replace('content="text/html;charset="', 'content="text/html;charset=utf-8"')
    return html


def main():
    src = sys.argv[1]
    if os.path.exists(DEST):
        shutil.rmtree(DEST)
    os.makedirs(DEST)
    redirects = []
    for f in sorted(os.listdir(src)):
        path = os.path.join(src, f)
        if os.path.isdir(path):
            shutil.copytree(path, os.path.join(DEST, f))
            continue
        m = re.match(r"textures_detail\.php\?id=(\d+)&", f)
        if m:
            out = "textures_detail_%s.html" % m.group(1)
            redirects.append(("/minisites/rawfoot/textures_detail.php?id=%s" % m.group(1), "/minisites/rawfoot/" + out))
        elif f.endswith(".php"):
            out = f[:-4] + ".html"
            redirects.append(("/minisites/rawfoot/" + f, "/minisites/rawfoot/" + (out if out != "index.html" else "")))
        else:
            shutil.copy(path, os.path.join(DEST, f))
            continue
        html = open(path, encoding="utf-8").read()
        open(os.path.join(DEST, out), "w", encoding="utf-8").write(convert(html))
    subprocess.run(["find", DEST, "-type", "f", "(", "-name", "*.jpg", "-o", "-name", "*.gif", "-o", "-name", "*.png", ")",
                    "-exec", "mogrify", "-strip", "{}", "+"], check=True)
    for a, b in redirects:
        print("- from: %s\n  to: %s" % (a, b))


if __name__ == "__main__":
    main()
