#!/usr/bin/env python3
"""
Sistema i contenuti importati da WordPress negli articoli (_posts/):

  * sostituisce gli shortcode [gallery ids="..."] con una galleria HTML
    (griglia di miniature, si apre a tutto schermo con un clic);
  * rimuove i paragrafi vuoti (<p>&nbsp;</p>) lasciati dall'editor;
  * con --download scarica dal vecchio sito le foto delle gallerie
    che mancano in assets/uploads/.

    python3 tools/converti_gallerie.py _wp-export/NOMEFILE.xml [--download]

Lo script si può rilanciare: gli articoli già convertiti non cambiano.
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

NS = {"wp": "http://wordpress.org/export/1.2/",
      "excerpt": "http://wordpress.org/export/1.2/excerpt/"}
SITO = "https://www.chiarabuchetti.it/wp-content/uploads/"


def allegati(xml_path):
    out = {}
    for it in ET.parse(xml_path).iter("item"):
        if it.findtext("wp:post_type", namespaces=NS) != "attachment":
            continue
        url = it.findtext("wp:attachment_url", namespaces=NS) or ""
        if "/wp-content/uploads/" not in url:
            continue
        rel = urllib.parse.unquote(url.split("/wp-content/uploads/", 1)[1])
        didascalia = (it.findtext("excerpt:encoded", namespaces=NS) or "").strip()
        out[it.findtext("wp:post_id", namespaces=NS)] = (rel, didascalia)
    return out


def galleria(ids, att, servono):
    voci = []
    for i in ids:
        a = att.get(i.strip())
        if not a:
            continue
        rel, cap = a
        servono.add(rel)
        src = "/assets/uploads/" + rel
        alt = html.escape(cap, quote=True)
        fig = (f'<figure><a href="{src}" class="gallery-item">'
               f'<img src="{src}" alt="{alt}" loading="lazy"></a>')
        if cap:
            fig += f"<figcaption>{html.escape(cap)}</figcaption>"
        voci.append(fig + "</figure>")
    if not voci:
        return ""
    return '<div class="gallery">\n' + "\n".join(voci) + "\n</div>"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("xml")
    ap.add_argument("--download", action="store_true")
    args = ap.parse_args()
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    att = allegati(args.xml)
    servono, cambiati = set(), 0

    posts = os.path.join(root, "_posts")
    for nome in sorted(os.listdir(posts)):
        p = os.path.join(posts, nome)
        testo = open(p, encoding="utf-8").read()
        nuovo = re.sub(r'(?:<p>\s*)?\[gallery([^\]]*)\](?:\s*</p>)?',
                       lambda m: galleria(re.search(r'ids="([^"]+)"', m.group(1)).group(1).split(","), att, servono)
                       if 'ids="' in m.group(1) else "", testo)
        nuovo = re.sub(r'<p[^>]*>(?:\s|&nbsp;|&#160;| |<br\s*/?>)*</p>\s*', "", nuovo)
        # le gallerie già convertite: registra comunque le foto necessarie
        for src in re.findall(r'class="gallery-item"><img src="/assets/uploads/([^"]+)"', nuovo):
            servono.add(src)
        if nuovo != testo:
            open(p, "w", encoding="utf-8").write(nuovo)
            cambiati += 1
    print(f"Articoli aggiornati: {cambiati}")

    mancanti = sorted(r for r in servono if not os.path.exists(os.path.join(root, "assets", "uploads", r)))
    print(f"Foto delle gallerie: {len(servono)}, mancanti: {len(mancanti)}")
    if not args.download:
        if mancanti:
            print("Rilanciare con --download per scaricarle dal vecchio sito.")
        return
    falliti = 0
    for rel in mancanti:
        dest = os.path.join(root, "assets", "uploads", rel)
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        url = SITO + urllib.parse.quote(rel, safe="/")
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (migrazione sito)"})
            with urllib.request.urlopen(req, timeout=30) as r:
                data = r.read()
            with open(dest, "wb") as f:
                f.write(data)
            print(f"  scaricato {rel}")
        except (urllib.error.URLError, OSError, ValueError) as e:
            falliti += 1
            print(f"  ERRORE {rel}: {e}", file=sys.stderr)
    print(f"Scaricate: {len(mancanti) - falliti}   Non riuscite: {falliti}")


if __name__ == "__main__":
    main()
