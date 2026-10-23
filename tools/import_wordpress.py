#!/usr/bin/env python3
"""
Importa i contenuti del vecchio sito WordPress nel sito Jekyll.

Uso (dalla cartella principale del repository):

    python3 tools/import_wordpress.py _wp-export/export.xml            # solo testi
    python3 tools/import_wordpress.py _wp-export/export.xml --download # testi + immagini

L'export si ottiene dal pannello WordPress: Strumenti -> Esporta -> "Tutti i contenuti".

Cosa produce:
  _posts/AAAA-MM-GG-slug.html     articoli pubblicati (stesso indirizzo del vecchio sito)
  _drafts/slug.html               bozze
  _importate/pagine/*.html        testo delle pagine (da ricopiare in _pages/ a mano)
  _importate/download-manager.txt elenco dei file del plugin Download Manager
  _importate/report.txt           riepilogo dell'import
  assets/uploads/...              immagini (solo con --download)

Usa solo la libreria standard di Python 3 (nessuna installazione richiesta).
Rilanciarlo sovrascrive i file generati in precedenza, non tocca gli altri.
"""

import argparse
import html
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime

NS = {
    "wp": "http://wordpress.org/export/1.2/",
    "content": "http://purl.org/rss/1.0/modules/content/",
    "excerpt": "http://wordpress.org/export/1.2/excerpt/",
    "dc": "http://purl.org/dc/elements/1.1/",
}

OLD_HOSTS = ("www.chiarabuchetti.it", "chiarabuchetti.it")
UPLOADS_LOCAL = "/assets/uploads/"

BLOCK_TAGS = (
    "table|thead|tfoot|caption|col|colgroup|tbody|tr|td|th|div|dl|dd|dt|ul|ol|li|pre|form|"
    "map|area|blockquote|address|math|style|p|h[1-6]|hr|fieldset|legend|section|article|"
    "aside|hgroup|header|footer|nav|figure|figcaption|details|menu|summary|iframe|script|"
    "video|audio|object|embed"
)


# --------------------------------------------------------------------------- helpers

def text(item, path):
    el = item.find(path, NS)
    return (el.text or "") if el is not None else ""


def yaml_str(s):
    """Stringa YAML sicura tra doppi apici."""
    s = html.unescape(s or "").replace("\\", "\\\\").replace('"', '\\"')
    return '"' + re.sub(r"\s+", " ", s).strip() + '"'


def old_path(link):
    """'https://www.chiarabuchetti.it/la-festa-laba-%e8%85%8a/' -> '/la-festa-laba-腊/'"""
    p = urllib.parse.unquote(urllib.parse.urlparse(link).path or "/")
    if not p.endswith("/") and "." not in os.path.basename(p):
        p += "/"
    return p


def safe_filename(slug):
    slug = urllib.parse.unquote(slug)
    slug = re.sub(r'[\\/:*?"<>|\s]+', "-", slug).strip("-")
    return slug or "senza-titolo"


def wpautop(content):
    """Versione semplificata di wpautop(): WordPress salva i testi senza <p>."""
    if not content.strip():
        return ""
    content = content.replace("\r\n", "\n").replace("\r", "\n")
    # preserva i <pre>
    pres = []

    def _keep(m):
        pres.append(m.group(0))
        return f"<!--PRE{len(pres) - 1}-->"

    content = re.sub(r"<pre[\s\S]*?</pre>", _keep, content, flags=re.I)
    content = re.sub(rf"(<(?:{BLOCK_TAGS})[\s/>])", r"\n\n\1", content, flags=re.I)
    content = re.sub(rf"(</(?:{BLOCK_TAGS})>)", r"\1\n\n", content, flags=re.I)
    out = []
    for block in re.split(r"\n\s*\n", content):
        block = block.strip()
        if not block:
            continue
        if re.match(rf"^</?(?:{BLOCK_TAGS})[\s/>]", block, flags=re.I) or block.startswith("<!--"):
            out.append(block)
        else:
            out.append("<p>" + block.replace("\n", "<br />\n") + "</p>")
    content = "\n\n".join(out)
    for i, pre in enumerate(pres):
        content = content.replace(f"<!--PRE{i}-->", pre)
    return content


YT_IFRAME = re.compile(r'<iframe[^>]*src="(?:https?:)?//(?:www\.)?youtube(?:-nocookie)?\.com/embed/([\w-]{11})[^"]*"[^>]*>\s*</iframe>', re.I)


def video_placeholder(vid):
    """Riquadro "clicca per caricare": YouTube viene contattato solo dopo il clic (GDPR)."""
    return (f'<div class="video-consent" data-yt="{vid}">'
            f'<button type="button" class="video-consent-btn" aria-label="Carica il video da YouTube">'
            f'<span class="video-play" aria-hidden="true"></span><span>Guarda il video</span></button>'
            f'<p class="video-consent-note">Il video è ospitato su YouTube: cliccando, verrà caricato da Google, '
            f'che riceverà alcuni dati di navigazione. '
            f'<a href="https://www.youtube.com/watch?v={vid}" target="_blank" rel="noopener">Apri su YouTube</a></p>'
            f'</div>')


def convert_shortcodes(content):
    # [caption ...]<img ...> Didascalia[/caption]  ->  <figure>
    def _caption(m):
        inner = m.group(1).strip()
        img = re.search(r"(<a [^>]*>\s*)?<img [^>]*>(\s*</a>)?", inner, flags=re.I)
        if not img:
            return inner
        cap = (inner[: img.start()] + inner[img.end():]).strip()
        return f'<figure class="align-center">{img.group(0)}<figcaption>{cap}</figcaption></figure>'

    content = re.sub(r"\[caption[^\]]*\]([\s\S]*?)\[/caption\]", _caption, content, flags=re.I)
    # [embed]url[/embed] e URL YouTube su riga singola
    content = re.sub(r"\[embed[^\]]*\]([\s\S]*?)\[/embed\]", lambda m: m.group(1).strip(), content)

    def _yt(m):
        url = m.group(1)
        vid = re.search(r"(?:v=|youtu\.be/|embed/)([\w-]{11})", url)
        if not vid:
            return m.group(0)
        return "\n" + video_placeholder(vid.group(1)) + "\n"

    content = YT_IFRAME.sub(lambda m: video_placeholder(m.group(1)), content)
    content = re.sub(r"^\s*(https?://(?:www\.)?(?:youtube\.com/watch\S+|youtu\.be/\S+))\s*$", _yt,
                     content, flags=re.M)
    return content


def clean_blocks(content):
    # commenti Gutenberg <!-- wp:paragraph --> ecc.
    return re.sub(r"<!--\s*/?wp:[\s\S]*?-->", "", content)


UPLOAD_RE = re.compile(
    r"https?://(?:www\.)?chiarabuchetti\.it/wp-content/uploads/([^\s\"'<>)]+)", flags=re.I
)


def rewrite_urls(content, found_uploads):
    def _up(m):
        rel = m.group(1)
        found_uploads.add(rel)
        return UPLOADS_LOCAL + rel

    content = UPLOAD_RE.sub(_up, content)
    # link interni assoluti -> relativi
    content = re.sub(r"https?://(?:www\.)?chiarabuchetti\.it(/[^\s\"'<>]*)?",
                     lambda m: urllib.parse.unquote(m.group(1) or "/"), content, flags=re.I)
    return content


def protect_liquid(content):
    """Neutralizza eventuali {{ e {% nel testo (Jekyll li interpreterebbe come Liquid)."""
    return re.sub(r"\{\{|\{%", lambda m: "{% raw %}" + m.group(0) + "{% endraw %}", content)


def convert_content(raw, found_uploads):
    c = clean_blocks(raw)
    c = convert_shortcodes(c)
    c = wpautop(c)
    c = rewrite_urls(c, found_uploads)
    return protect_liquid(c)


# --------------------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("xml", help="file di export WordPress (WXR)")
    ap.add_argument("--download", action="store_true",
                    help="scarica le immagini da wp-content/uploads in assets/uploads/")
    ap.add_argument("--root", default=".", help="cartella del sito Jekyll (default: .)")
    args = ap.parse_args()

    root = os.path.abspath(args.root)
    if not os.path.exists(os.path.join(root, "_config.yml")):
        sys.exit("Errore: lanciare lo script dalla cartella del sito (manca _config.yml).")

    tree = ET.parse(args.xml)
    channel = tree.getroot().find("channel")
    items = channel.findall("item")

    # mappa id allegato -> url (per le immagini in evidenza)
    attachments = {}
    for it in items:
        if text(it, "wp:post_type") == "attachment":
            attachments[text(it, "wp:post_id")] = text(it, "wp:attachment_url")

    dirs = {k: os.path.join(root, v) for k, v in {
        "posts": "_posts", "drafts": "_drafts",
        "pages": "_importate/pagine", "imp": "_importate",
    }.items()}
    for d in dirs.values():
        os.makedirs(d, exist_ok=True)

    uploads = set()
    stats = {"post": 0, "bozze": 0, "pagine": 0, "commenti": 0, "saltati": 0}
    wpdm = []
    tag_slugs, cat_slugs = set(), set()

    for it in items:
        ptype = text(it, "wp:post_type")
        status = text(it, "wp:status")
        title = text(it, "title")
        slug = text(it, "wp:post_name")
        link = text(it, "link")
        date_s = text(it, "wp:post_date")
        raw = text(it, "content:encoded")
        excerpt = text(it, "excerpt:encoded")
        meta = {text(m, "wp:meta_key"): text(m, "wp:meta_value") for m in it.findall("wp:postmeta", NS)}

        if ptype == "wpdmpro":
            files = re.findall(r'"([^"]+\.(?:pdf|ibooks|zip|docx?|pptx?|epub))"', meta.get("__wpdm_files", ""), re.I)
            wpdm.append(f"{title}\t{', '.join(files) or '(file non indicato)'}\t{link}")
            continue
        if ptype not in ("post", "page") or status in ("trash", "auto-draft", "inherit"):
            continue

        stats["commenti"] += sum(1 for c in it.findall("wp:comment", NS) if text(c, "wp:comment_approved") == "1")

        try:
            date = datetime.strptime(date_s, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            date = datetime.now()

        cats, tags = [], []
        for c in it.findall("category"):
            name = html.unescape(c.text or "").strip()
            if c.get("domain") == "category" and name and name.lower() not in ("uncategorized", "senza categoria"):
                cats.append(name)
                cat_slugs.add(c.get("nicename", ""))
            elif c.get("domain") == "post_tag" and name:
                tags.append(name)
                tag_slugs.add(c.get("nicename", ""))

        body = convert_content(raw, uploads)
        fm = ["---", f"title: {yaml_str(title)}", f"date: {date.strftime('%Y-%m-%d %H:%M:%S')}"]

        if ptype == "post":
            fm.append(f"permalink: {yaml_str(old_path(link))}" if link and "?p=" not in link else "")
            if cats:
                fm.append("categories: [" + ", ".join(yaml_str(c) for c in cats) + "]")
            if tags:
                fm.append("tags: [" + ", ".join(yaml_str(t) for t in tags) + "]")
            if excerpt.strip():
                fm.append(f"excerpt: {yaml_str(re.sub('<[^>]+>', '', excerpt))}")
            thumb = attachments.get(meta.get("_thumbnail_id", ""), "")
            if thumb:
                m = UPLOAD_RE.search(thumb)
                if m:
                    uploads.add(m.group(1))
                    fm += ["header:", f"  teaser: {yaml_str(UPLOADS_LOCAL + m.group(1))}"]
            fm.append(f"wordpress_id: {text(it, 'wp:post_id')}")
            fm.append("---")
            fname = safe_filename(slug or title)
            if status == "publish":
                path = os.path.join(dirs["posts"], f"{date:%Y-%m-%d}-{fname}.html")
                stats["post"] += 1
            else:
                path = os.path.join(dirs["drafts"], f"{fname}.html")
                stats["bozze"] += 1
        else:  # page
            fm.append(f"permalink: {yaml_str(old_path(link))}")
            fm.append("---")
            name = old_path(link).strip("/").replace("/", "__") or "home"
            path = os.path.join(dirs["pages"], safe_filename(name) + ".html")
            stats["pagine"] += 1

        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(l for l in fm if l) + "\n\n" + body + "\n")

    # --- download immagini
    downloaded = failed = 0
    if args.download:
        for rel in sorted(uploads):
            dest = os.path.join(root, "assets", "uploads", urllib.parse.unquote(rel))
            if os.path.exists(dest):
                continue
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            url = "https://www.chiarabuchetti.it/wp-content/uploads/" + rel
            try:
                req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (migrazione sito)"})
                with urllib.request.urlopen(req, timeout=30) as r, open(dest, "wb") as f:
                    f.write(r.read())
                downloaded += 1
                print(f"  scaricato {rel}")
            except (urllib.error.URLError, OSError) as e:
                failed += 1
                print(f"  ERRORE {rel}: {e}", file=sys.stderr)

    if wpdm:
        with open(os.path.join(dirs["imp"], "download-manager.txt"), "w", encoding="utf-8") as f:
            f.write("titolo\tfile\tvecchio indirizzo\n" + "\n".join(wpdm) + "\n")

    report = [
        f"Import del {datetime.now():%Y-%m-%d %H:%M}",
        f"Articoli pubblicati: {stats['post']}  ->  _posts/",
        f"Bozze:               {stats['bozze']}  ->  _drafts/",
        f"Pagine:              {stats['pagine']}  ->  _importate/pagine/ (da ricopiare in _pages/)",
        f"Elementi Download Manager: {len(wpdm)}  ->  _importate/download-manager.txt",
        f"Immagini referenziate: {len(uploads)}"
        + (f" (scaricate {downloaded}, errori {failed})" if args.download else " (usa --download per scaricarle)"),
        f"Commenti approvati NON importati: {stats['commenti']} (il sito statico non ha commenti)",
        "",
        "Vecchi archivi tag/categorie (redirect suggeriti):",
        *[f"  /tag/{s}/" for s in sorted(tag_slugs) if s],
        *[f"  /category/{s}/" for s in sorted(cat_slugs) if s],
    ]
    with open(os.path.join(dirs["imp"], "report.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(report) + "\n")
    print("\n".join(report[:7]))
    print(f"\nReport completo in {os.path.relpath(os.path.join(dirs['imp'], 'report.txt'), root)}")


if __name__ == "__main__":
    main()
