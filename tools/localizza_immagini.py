#!/usr/bin/env python3
"""
Copia sul sito le immagini che gli articoli caricano da siti esterni
(wp.com, Amazon, Wikimedia, Facebook, ...) e aggiorna i link.

Perché: un'immagine "esterna" fa sì che il browser del visitatore contatti
un altro server, che riceve il suo indirizzo IP (problema GDPR). Dopo lo
script tutte le immagini sono servite dal sito stesso.

    python3 tools/localizza_immagini.py              # scarica e riscrive
    python3 tools/localizza_immagini.py --prova      # mostra solo cosa farebbe
    python3 tools/localizza_immagini.py --rimuovi-mancanti
        # in più elimina dagli articoli le immagini che non si riescono a scaricare
        # (link scaduti, es. Facebook o anteprime Google)

Le immagini finiscono in assets/uploads/esterne/<sito>/. Rilanciabile.
"""
import argparse
import glob
import hashlib
import os
import re
import urllib.error
import urllib.parse
import urllib.request

IMG = re.compile(r'<img\b[^>]*>', re.I)
SRC = re.compile(r'\bsrc=(["\'])(https?://[^"\']+)\1', re.I)
SRCSET = re.compile(r'\s(?:srcset|sizes|data-[\w-]+)=(["\'])[^"\']*\1', re.I)
OWN = ("chiarabuchetti.it",)
EXT = {"image/jpeg": ".jpg", "image/png": ".png", "image/gif": ".gif", "image/webp": ".webp", "image/svg+xml": ".svg"}


def nome_locale(url, ctype):
    u = urllib.parse.urlparse(url)
    base = os.path.basename(urllib.parse.unquote(u.path)) or "immagine"
    base = re.sub(r"[^\w.-]+", "-", base)[-60:]
    stem, ext = os.path.splitext(base)
    if ext.lower() not in (".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg"):
        ext = EXT.get(ctype, ".jpg")
    h = hashlib.sha1(url.encode()).hexdigest()[:8]
    host = re.sub(r"[^\w.-]+", "-", u.netloc)
    return f"assets/uploads/esterne/{host}/{h}-{stem}{ext}"


def scarica(url, root):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (migrazione sito)"})
    with urllib.request.urlopen(req, timeout=30) as r:
        ctype = r.headers.get_content_type()
        if not ctype.startswith("image/"):
            raise ValueError(f"non è un'immagine ({ctype})")
        data = r.read()
    rel = nome_locale(url, ctype)
    dest = os.path.join(root, rel)
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    with open(dest, "wb") as f:
        f.write(data)
    return "/" + rel


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--prova", action="store_true")
    ap.add_argument("--rimuovi-mancanti", action="store_true")
    ap.add_argument("--root", default=".")
    a = ap.parse_args()
    root = os.path.abspath(a.root)
    cache, falliti = {}, {}
    files = glob.glob(os.path.join(root, "_posts", "*")) + glob.glob(os.path.join(root, "_pages", "**", "*.*"), recursive=True)
    for f in sorted(files):
        s = open(f, encoding="utf-8").read()

        def fix(m):
            tag = m.group(0)
            sm = SRC.search(tag)
            if not sm or any(o in urllib.parse.urlparse(sm.group(2)).netloc for o in OWN):
                return tag
            url = sm.group(2).replace("&amp;", "&")
            if a.prova:
                print(f"  [prova] {os.path.basename(f)}: {url}")
                return tag
            if url not in cache and url not in falliti:
                try:
                    cache[url] = scarica(url, root)
                    print(f"  ok      {url}")
                except (urllib.error.URLError, OSError, ValueError) as e:
                    falliti[url] = str(e)
                    print(f"  ERRORE  {url}: {e}")
            if url in cache:
                tag = SRCSET.sub("", tag)
                return tag.replace(sm.group(0), f'src="{cache[url]}"')
            return "" if a.rimuovi_mancanti else tag

        n = IMG.sub(fix, s)
        if n != s:
            open(f, "w", encoding="utf-8").write(n)
    print(f"\nScaricate: {len(cache)}  Non riuscite: {len(falliti)}")
    if falliti and not a.rimuovi_mancanti:
        print("Le immagini non riuscite sono ancora esterne: rilanciare con --rimuovi-mancanti per eliminarle,"
              " oppure sostituirle a mano.")


if __name__ == "__main__":
    main()
