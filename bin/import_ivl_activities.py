#!/usr/bin/env python3
"""Import the research-activity pages of the old IVL WordPress site (www.ivl.disco.unimib.it/activities/<slug>/).

One-off migration script, kept for reference and re-runs. For every old activity page it writes
_activities/<slug>.html (rendered by _layouts/ivl-project.liquid at the same URL, /activities/<slug>/), downloads the
images and files the page uses into the site at their old paths (wp-content/uploads/..., wp-content/files/...),
and tags the page's publications in _bibliography/papers.bib with  projects = {<slug>}.

Usage:  python3 bin/import_ivl_activities.py <cache-dir> [--no-download]
  <cache-dir> holds the downloaded pages as <slug>.html (fetched if missing) and the image-conversion map.

Pages that are not imported here:
  SKIP           pages that live in a minisite (handled separately) and empty pages;
  PROJECTS       funded projects, written by hand in _projects/ (their old URL redirects, see _pages/redirects/);
  BIG_FILES      downloads too large for the site: kept outside the repository, their old URLs redirect
                 (see _data/redirects.yml).
"""
import codecs
import json
import os
import re
import subprocess
import sys
import urllib.request
from html import unescape

import yaml
from bs4 import BeautifulSoup, Comment, NavigableString

OLD = "http://www.ivl.disco.unimib.it"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKIP = {"cciw-2024", "dalib", "pignoletto", "aicv4food"}  # minisites, external redirect (aicv4food), empty page
PROJECTS = {"onfoods": "onfoods", "hpc": "hpc", "progetto-e4s-energy-for-safety": "e4s"}
BIG_FILES = {  # old path -> kept outside the site (../large-files/<same path>)
    "/wp-content/files/IVL-SYNTHSFM.zip",
    "/wp-content/files/SDIVL.zip",
    "/wp-content/files/MDIVL.zip",
    "/wp-content/uploads/2016/09/LAGdataset_100.zip",
    "/wp-content/uploads/2016/09/LAGdataset_200.zip",
    "/minisites/UNIMIB2016/UNIMIB2016-images.zip",
}
KEEP_REMOTE = ()  # paths to keep linking on the old server (all minisites are now copied into the site)
DEAD = {  # links already broken on the old website: the link is removed, the text kept (with a note)
    "/quicklook": None,  # Quicklook demo server, no longer online: the sentence pointing to it is removed
    "/wp-content/uploads/2016/09/21-classes.zip": "no longer available",
    "/wp-content/uploads/2016/09/19-classes.zip": "no longer available",
}
UA = {"User-Agent": "Mozilla/5.0", "Referer": OLD + "/activities/"}


def fetch(url, dest):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=120) as r, open(dest, "wb") as f:
        f.write(r.read())


def old_path(url):
    """Return the site path of a link to the old site, or None for external links."""
    url = url.strip()
    m = re.match(r"^(?:https?:)?//(?:www\.|projects\.)?ivl\.disco\.unimib\.it(/.*)?$", url)
    if m:
        path = m.group(1) or "/"
    elif url.startswith("/") and not url.startswith("//"):
        path = url
    else:
        return None
    path = re.sub(r"\?_=\d+$", "", path)
    m = re.match(r"^/download/(?:https?://(?:www\.)?ivl\.disco\.unimib\.it)?(/.*)$", path)
    if m:  # wp-downloadmanager link to a full URL
        return m.group(1)
    m = re.match(r"^/download/([^/]+)$", path)
    if m:  # wp-downloadmanager: /download/X redirects to /wp-content/files/X
        return "/wp-content/files/" + m.group(1)
    return path


def main():
    global CACHE
    cache = CACHE = sys.argv[1]
    download = "--no-download" not in sys.argv
    imgmap = json.load(open(os.path.join(cache, "imgmap.json"))) if os.path.exists(os.path.join(cache, "imgmap.json")) else {}
    imgmap = {"/" + k: "/" + v for k, v in imgmap.items()}
    listing = []
    for page in ("", "page/2/", "page/3/"):
        try:
            html = urllib.request.urlopen(urllib.request.Request(OLD + "/activities/" + page, headers=UA)).read().decode()
        except Exception:
            continue
        listing += re.findall(OLD + r"/activities/([^/\"]+)/\"", html)
    slugs = sorted(set(s for s in listing if s not in ("filter", "page")))
    os.makedirs(os.path.join(ROOT, "_activities"), exist_ok=True)
    tags = {}  # bib key -> set(slugs)
    files_needed = set()
    youtube = []
    for slug in slugs:
        src = os.path.join(cache, slug + ".html")
        if not os.path.exists(src):
            fetch(f"{OLD}/activities/{slug}/", src)
        t = open(src, encoding="utf-8", errors="replace").read()
        pubs = re.findall(r'<article class="publication" id="([^"]+)"', t)
        if slug in PROJECTS:
            for k in pubs:
                tags.setdefault(k, set()).add(PROJECTS[slug])
            continue
        if slug in SKIP:
            continue
        for k in pubs:
            tags.setdefault(k, set()).add(slug)
        title = unescape(re.search(r"<title>(.*?)\s*\|\s*Imaging and Vision", t, re.S).group(1).strip())
        body = re.search(r'<div class="nine columns shift shrink">(.*?)(?:<div class="publications">|</div>\s*<div class="three columns">)',
                         t, re.S).group(1)
        participants = [unescape(p).strip() for p in re.findall(r'<span class="avatar-name">([^<]+)</span>', t)]
        soup = BeautifulSoup(body, "html.parser")
        clean(soup, files_needed, imgmap, youtube, slug)
        html = soup.decode(formatter="minimal").strip()
        html = re.sub(r"\n\s*\n+", "\n", html)
        desc = ""
        for p in soup.find_all("p"):
            txt = re.sub(r"\s+", " ", p.get_text(" ")).strip()
            if len(txt) > 60:
                desc = txt
                break
        if len(desc) > 160:
            desc = desc[:157].rsplit(" ", 1)[0].rstrip(",;:") + "…"
        fm = {
            "layout": "ivl-project",
            "title": title,
            "description": desc or title,
            "participants": participants,
            "publication_tag": slug,
            "render_with_liquid": False,
        }
        if not participants:
            del fm["participants"]
        header = ("---\n# Imported from " + OLD + "/activities/" + slug + "/ by bin/import_ivl_activities.py.\n"
                  "# Edit freely: re-running the import overwrites this file.\n"
                  + yaml.safe_dump(fm, allow_unicode=True, sort_keys=False, width=1000) + "---\n")
        with open(os.path.join(ROOT, "_activities", slug + ".html"), "w") as f:
            f.write(header + html + "\n")
    if download:
        for path in sorted(files_needed):
            dest = os.path.join(ROOT, path.lstrip("/"))
            if path in BIG_FILES or os.path.exists(dest) or path in imgmap.values():
                continue
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            try:
                fetch(OLD + path, dest)
                print("downloaded", path)
            except Exception as e:
                print("MISSING", path, e)
        for vid in youtube:
            dest = os.path.join(ROOT, "wp-content/uploads/youtube", vid + ".jpg")
            if not os.path.exists(dest):
                os.makedirs(os.path.dirname(dest), exist_ok=True)
                fetch(f"https://i.ytimg.com/vi/{vid}/hqdefault.jpg", dest)
        convert_big_images(cache)
    json.dump({k: sorted(v) for k, v in tags.items()}, open(os.path.join(cache, "tags.json"), "w"), indent=1)
    tag_bib(tags)


def convert_big_images(cache):
    """Re-encode PNG/JPEG images over 250 kB as WebP (max 1600 px); run the import again to update the links."""
    path = os.path.join(cache, "imgmap.json")
    mp = json.load(open(path)) if os.path.exists(path) else {}
    for d, _, files in os.walk(os.path.join(ROOT, "wp-content/uploads")):
        for f in files:
            src = os.path.join(d, f)
            ext = os.path.splitext(f)[1].lower()
            if ext not in (".png", ".jpg", ".jpeg") or os.path.getsize(src) < 250_000:
                continue
            new = os.path.splitext(src)[0] + ".webp"
            if os.path.exists(new):
                new = os.path.splitext(src)[0] + "-" + ext[1:] + ".webp"
            subprocess.run(["convert", src, "-resize", "1600x1600>", "-quality", "82", new], check=True)
            os.remove(src)
            mp[os.path.relpath(src, ROOT)] = os.path.relpath(new, ROOT)
            print("converted", os.path.relpath(src, ROOT))
    json.dump(mp, open(path, "w"), indent=1)


def clean(soup, files_needed, imgmap, youtube, slug):
    for c in soup.find_all(string=lambda s: isinstance(s, Comment)):
        c.extract()
    # WordPress video playlists: keep a plain list of the videos
    for pl in soup.select("div.wp-playlist"):
        tracks = [a.get("href") for a in pl.select("noscript a")]
        new = soup.new_tag("div")
        for href in tracks:
            v = soup.new_tag("video", controls="", preload="metadata", src=href)
            new.append(v)
        pl.replace_with(new)
    for el in soup.find_all(["script", "noscript", "meta", "style"]):
        el.decompose()
    # obfuscated e-mail addresses (rot13, "[at]")
    for a in soup.find_all("a", attrs={"data-enc-email": True}):
        email = codecs.decode(a["data-enc-email"], "rot13").replace("[ng]", "@")  # "[at]" was rot13-encoded too
        text = a.get_text(" ").strip()
        a.attrs = {"href": "mailto:" + email}
        a.clear()
        a.append(text if text and "@" not in text and "protected" not in text else email)
    # YouTube embeds: click-to-load (no request to YouTube until the visitor asks for the video)
    for fr in soup.find_all("iframe"):
        m = re.search(r"youtube(?:-nocookie)?\.com/embed/([\w-]+)", fr.get("src", ""))
        if m:
            vid = m.group(1)
            youtube.append(vid)
            div = BeautifulSoup(
                f'<div class="ivl-video" data-video-id="{vid}">'
                f'<button type="button" class="ivl-video__preview" data-video-load aria-label="Play the video (loads YouTube)">'
                f'<img src="/wp-content/uploads/youtube/{vid}.jpg" alt="" loading="lazy"><span class="ivl-video__play" aria-hidden="true"></span></button>'
                f'<p class="ivl-video__note">The video is hosted on YouTube, which receives your IP address when you play it. '
                f'<a href="https://www.youtube.com/watch?v={vid}">Watch it on YouTube</a>.</p></div>', "html.parser")
            fr.replace_with(div)
        else:
            fr.decompose()
    for el in soup.select("blockquote.wp-embedded-content"):
        el.unwrap()
    # download-manager icons and hit counters
    for img in soup.find_all("img"):
        if "wp-downloadmanager" in img.get("src", ""):
            img.decompose()
    for s in list(soup.find_all(string=True)):
        if isinstance(s, NavigableString) and re.search(r"hits\)", s):
            s.replace_with(re.sub(r"\(([\d.,]+\s*[KMG]?i?B), [\d,]+ hits\)", r"(\1)", str(s)))
    for a in soup.find_all("a", href=True):
        path = old_path(a["href"])
        if path in DEAD:
            if DEAD[path] is None:
                p = a.find_parent("p")
                for node in list(p.contents) if p else []:
                    if isinstance(node, NavigableString) and "To see the system at work" in node:
                        node.replace_with(node.split("To see the system at work")[0])
                a.decompose()
            else:
                a.replace_with(a.get_text() + " (" + DEAD[path] + ")")
    # link text that is a (mangled) address of the old site: use the title of the linked page instead
    for a in soup.find_all("a", href=True):
        if "ivl.disco.unimib.it" in a.get_text():
            m = re.match(r"^/activities/([^/]+)/", old_path(a["href"]) or "")
            target = os.path.join(CACHE, m.group(1) + ".html") if m else None
            if target and os.path.exists(target):
                t = open(target, encoding="utf-8", errors="replace").read()
                a.string = unescape(re.search(r"<title>(.*?)\s*\|", t, re.S).group(1).strip())
    # links and media; drop WordPress classes and inline styles
    for el in soup.find_all(True):
        for attr in ("href", "src"):
            if el.has_attr(attr):
                el[attr] = fix_url(el[attr], files_needed, imgmap)
        classes = el.get("class", [])
        keep_class = None
        if any(c.startswith("ivl-video") for c in classes):
            keep_class = classes
        elif el.name == "div" and "gallery" in classes:
            keep_class = ["ivl-legacy-gallery"]
        elif el.name == "figure" and "gallery-item" in classes:
            keep_class = ["ivl-legacy-gallery-item"]
        for attr in ("srcset", "sizes", "class", "style", "id", "aria-describedby", "data-wpel-link", "frameborder",
                     "align", "target", "rel", "data-mce-type", "title"):
            el.attrs.pop(attr, None)
        if keep_class:
            el["class"] = keep_class
        if el.name == "video":
            for attr in ("width", "height", "id"):
                el.attrs.pop(attr, None)
            el["controls"] = ""
            el["preload"] = "metadata"
            el.attrs.pop("class", None)
        if el.name in ("table",):
            for attr in ("width", "border", "cellpadding", "cellspacing"):
                el.attrs.pop(attr, None)
    for div in soup.find_all("div"):
        if not div.attrs:
            div.unwrap()
    for v in soup.find_all("video"):  # drop the fallback link inside <video>
        for a in v.find_all("a"):
            a.decompose()
    for tbl in soup.find_all("table"):
        wrap = soup.new_tag("div", attrs={"class": "ivl-legacy-table"})
        tbl.wrap(wrap)
    # headings: the page title is the h1, so the body starts at h2
    levels = sorted({int(h.name[1]) for h in soup.find_all(re.compile(r"^h[1-6]$"))})
    shift = {lvl: min(6, 2 + i) for i, lvl in enumerate(levels)}
    for h in soup.find_all(re.compile(r"^h[1-6]$")):
        if not h.get_text(strip=True):
            h.decompose()
            continue
        h.name = "h%d" % shift[int(h.name[1])]
    for p in soup.find_all("p"):
        if not p.get_text(strip=True) and not p.find(["img", "video", "iframe", "div", "button"]):
            p.decompose()
    for br in soup.find_all("br"):  # line breaks inside sentences (text pasted from PDFs)
        nxt = br.next_sibling
        if isinstance(nxt, NavigableString) and re.match(r"\s*[a-z(]", str(nxt)):
            br.replace_with(" ")
    # accessibility: every image gets an alt attribute; a link made only of an image needs a text alternative
    for img in soup.find_all("img"):
        if not img.get("alt", "").strip():
            fig = img.find_parent("figure")
            cap = fig.find("figcaption") if fig else None
            caption = re.sub(r"\s+", " ", cap.get_text(" ")).strip() if cap else ""
            link = img.find_parent("a")
            if link and not re.sub(r"\s+", "", link.get_text()):
                img["alt"] = ("Full-size image: " + caption) if caption else "Full-size image"
            else:
                img["alt"] = ""
    for pre in soup.find_all("pre"):  # code blocks scroll sideways: make them reachable with the keyboard
        pre["tabindex"] = "0"
    for name in ("big", "l"):
        for el in soup.find_all(name):
            el.unwrap()


def fix_url(url, files_needed, imgmap):
    url = url.strip()
    if url.startswith("javascript:"):
        return "#"
    path = old_path(url)
    if path is None:
        return url
    for keep in KEEP_REMOTE:
        if path.startswith(keep):
            return OLD + path
    m = re.match(r"^/activities/([^/]+)/([^/#]+)/?$", path)
    if m:  # WordPress attachment page of an image: link to the image file itself
        img = attachment_image(path)
        if img:
            img = imgmap.get(img, img)
            files_needed.add(img)
            return img
    m = re.match(r"^/activities/([^/]+)/?(#.*)?$", path)
    if m:
        s = m.group(1)
        if s in PROJECTS:
            return "/projects/%s/" % PROJECTS[s]
        return "/activities/%s/%s" % (s, m.group(2) or "")
    if path.startswith(("/wp-content/", "/minisites/")):
        path = imgmap.get(path, path)
        files_needed.add(path)
        return path
    if path in ("/", ""):
        return "/"
    return OLD + path


ATTACHMENTS = {}
CACHE = None


def attachment_image(path):
    if path not in ATTACHMENTS:
        try:
            req = urllib.request.Request(OLD + path, headers=UA)
            html = urllib.request.urlopen(req, timeout=60).read().decode("utf-8", "replace")
            m = re.search(r'src="https?://(?:www\.)?ivl\.disco\.unimib\.it(/wp-content/uploads/[^"]+)"', html)
            ATTACHMENTS[path] = m.group(1) if m else None
        except Exception:
            ATTACHMENTS[path] = None
    return ATTACHMENTS[path]


def tag_bib(tags):
    p = os.path.join(ROOT, "_bibliography", "papers.bib")
    blocks = re.split(r"(?=^@\w+\{)", open(p).read(), flags=re.M)
    for block in blocks:  # projectref values from the old publication catalog
        m = re.match(r"@\w+\{([^,]+),\n", block)
        r = re.search(r"projectref = \{([^}]+)\}", block)
        if m and r and "://" not in r.group(1):
            ref = r.group(1).strip().lower()
            ref = PROJECTS.get(ref, ref)
            if ref in PROJECTS.values() or (ref not in SKIP and os.path.exists(os.path.join(ROOT, "_activities", ref + ".html"))):
                tags.setdefault(m.group(1), set()).add(ref)
    out = []
    for block in blocks:
        m = re.match(r"@\w+\{([^,]+),\n", block)
        if not m or m.group(1) not in tags:
            out.append(block)
            continue
        existing = re.search(r"^projects = \{([^}]*)\},\n", block, re.M)
        cur = [x.strip() for x in existing.group(1).split(",")] if existing else []
        new = cur + [t for t in sorted(tags[m.group(1)]) if t not in cur]
        line = "projects = {%s},\n" % ", ".join(new)
        block = block.replace(existing.group(0), line, 1) if existing else block[: m.end()] + line + block[m.end():]
        out.append(block)
    open(p, "w").write("".join(out))

if __name__ == "__main__":
    main()
