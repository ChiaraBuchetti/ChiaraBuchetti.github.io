#!/usr/bin/env python3
"""
Imposta l'immagine di anteprima per i social (Facebook, LinkedIn, WhatsApp, X…)
di ogni articolo e pagina, scrivendo il campo `image:` nel front matter
(letto da jekyll-seo-tag, che genera i meta og:image / twitter:image).

  * articoli: la prima immagine presente nel testo (in versione originale,
    non la miniatura "-300x200"), se esiste nel sito ed è almeno 200x200 px;
    altrimenti un'immagine generata (1200x630) con titolo e categoria;
  * pagine: un'immagine generata con titolo e carattere cinese della pagina;
  * immagine generica del sito: assets/images/social/default.png

    python3 tools/immagini_social.py              # solo ciò che manca
    python3 tools/immagini_social.py --rigenera   # ricrea anche le immagini generate

Le immagini generate finiscono in assets/images/social/. Gli articoli e le pagine
che hanno già un `image:` scelto a mano non vengono toccati.
Serve Pillow (pip install pillow) e un font con i caratteri cinesi
(su macOS PingFang/Hiragino, su Linux Noto Sans CJK): lo script li cerca da solo.
"""
import argparse
import datetime
import glob
import os
import re
import sys

import yaml
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, "assets", "images", "social")
FONTS = os.path.join(ROOT, "tools", "fonts")
W, H = 1200, 630
MIN_SIDE = 200
GEN_PREFIX = "/assets/images/social/"

# palette del sito (assets/css/main.css)
TONI = {
    "red":    {"tone": "#E8412C", "dark": "#C2301C", "tint": "#FFE9E3"},
    "yellow": {"tone": "#FFC233", "dark": "#8A6200", "tint": "#FFF5D9"},
    "jade":   {"tone": "#12A084", "dark": "#0B7A64", "tint": "#DCF5EE"},
    "sky":    {"tone": "#2F6BE0", "dark": "#1F4FB0", "tint": "#E4ECFF"},
    "ink":    {"tone": "#17182B", "dark": "#17182B", "tint": "#ECECF3"},
}
INK, INK2, MUTED, RED, YELLOW = "#17182B", "#45475E", "#74768C", "#E8412C", "#FFC233"
MESI = "gennaio febbraio marzo aprile maggio giugno luglio agosto settembre ottobre novembre dicembre".split()

CJK_CANDIDATES = [
    "/System/Library/Fonts/PingFang.ttc",
    "/System/Library/Fonts/Hiragino Sans GB.ttc",
    "/System/Library/Fonts/STHeiti Medium.ttc",
    "/Library/Fonts/Arial Unicode.ttf",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/noto-cjk/NotoSansCJK-Bold.ttc",
    "C:/Windows/Fonts/msyhbd.ttc",
    "C:/Windows/Fonts/msyh.ttc",
]


def trova_cjk():
    for p in CJK_CANDIDATES:
        if os.path.exists(p):
            return p
    for p in glob.glob("/usr/share/fonts/**/*CJK*", recursive=True):
        return p
    sys.exit("Nessun font con caratteri cinesi trovato: aggiungerne il percorso in CJK_CANDIDATES.")


class Testo:
    """Scrive testo misto latino/cinese: usa Outfit dove possibile, il font CJK per il resto."""

    def __init__(self, latin_path, cjk_path, size):
        self.lat = ImageFont.truetype(latin_path, size)
        idx = 0
        if cjk_path.endswith(".ttc") and "NotoSansCJK" in cjk_path:
            idx = 2  # Noto Sans CJK SC
        self.cjk = ImageFont.truetype(cjk_path, size, index=idx)
        from fontTools.ttLib import TTFont
        self.cmap = TTFont(latin_path).getBestCmap()
        self.size = size

    def font_per(self, ch):
        return self.lat if ord(ch) in self.cmap else self.cjk

    def runs(self, s):
        out = []
        for ch in s:
            f = self.font_per(ch)
            if out and out[-1][0] is f:
                out[-1][1] += ch
            else:
                out.append([f, ch])
        return out

    def larghezza(self, s):
        return sum(f.getlength(t) for f, t in self.runs(s))

    def scrivi(self, draw, xy, s, fill):
        x, y = xy
        base = self.lat.getmetrics()[0]
        for f, t in self.runs(s):
            dy = base - f.getmetrics()[0]
            draw.text((x, y + dy), t, font=f, fill=fill)
            x += f.getlength(t)


def a_capo(testo, font, larghezza, max_righe):
    # parole latine (con lo spazio che le segue) e singoli caratteri cinesi
    pezzi = re.findall(r"[\u3000-\u9fff\uff00-\uffef]\s*|[^\s\u3000-\u9fff\uff00-\uffef]+\s*", testo.strip())
    righe, cur = [], ""
    for p in pezzi:
        prova = cur + p
        if font.larghezza(prova.rstrip()) <= larghezza or not cur:
            cur = prova
        else:
            righe.append(cur.rstrip())
            cur = p
    if cur:
        righe.append(cur.rstrip())
    if len(righe) > max_righe:
        righe = righe[:max_righe]
        while font.larghezza(righe[-1] + "…") > larghezza and " " in righe[-1]:
            righe[-1] = righe[-1].rsplit(" ", 1)[0]
        righe[-1] = righe[-1].rstrip(" ,.;:—-") + "…"
    return righe


def disegna(titolo, kicker, zh, colore, dest, cjk_path):
    t = TONI.get(colore, TONI["red"])
    img = Image.new("RGB", (W, H), t["tint"])
    d = ImageDraw.Draw(img, "RGBA")

    # forme decorative come negli hero del sito
    def rgba(hexc, a):
        hexc = hexc.lstrip("#")
        return tuple(int(hexc[i:i + 2], 16) for i in (0, 2, 4)) + (a,)
    d.ellipse((W - 330, -170, W + 170, 330), fill=rgba(t["tone"], 34))
    d.pieslice((760, H - 90, 940, H + 90), 180, 360, fill=rgba(t["tone"], 60))
    # greca (回纹) in basso a sinistra
    for gx in range(0, 300, 36):
        for gy in range(H - 150, H, 36):
            d.line([(gx + 2, gy + 34), (gx + 2, gy + 2), (gx + 34, gy + 2), (gx + 34, gy + 34),
                    (gx + 11, gy + 34), (gx + 11, gy + 11), (gx + 25, gy + 11), (gx + 25, gy + 25), (gx + 18, gy + 25)],
                   fill=rgba(INK, 16), width=3)

    # carattere cinese grande, a destra
    if zh:
        n = len(zh)
        size = {1: 330, 2: 230, 3: 150}.get(n, 120)
        f = ImageFont.truetype(cjk_path, size, index=2 if "NotoSansCJK" in cjk_path else 0)
        layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ld = ImageDraw.Draw(layer)
        bbox = ld.textbbox((0, 0), zh, font=f)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        x = W - 80 - tw - bbox[0]
        y = (H - th) // 2 - bbox[1] - 20
        ld.text((x + 10, y + 10), zh, font=f, fill=rgba(INK, 22))
        ld.text((x, y), zh, font=f, fill=rgba(t["tone"], 255))
        layer = layer.rotate(5, resample=Image.BICUBIC, center=(x + tw / 2, y + th / 2 + bbox[1]))
        img.paste(layer, (0, 0), layer)
        d = ImageDraw.Draw(img, "RGBA")
        max_w = W - 80 - tw - 140 - 80
    else:
        max_w = W - 160
    max_w = max(max_w, 560)

    lat_bold = os.path.join(FONTS, "Outfit-Bold.ttf")
    lat_xb = os.path.join(FONTS, "Outfit-ExtraBold.ttf")
    lat_body = os.path.join(FONTS, "NunitoSans-SemiBold.ttf")

    # kicker
    k = Testo(lat_bold, cjk_path, 26)
    kx, ky = 80, 92
    kick = kicker.upper()
    x = kx
    for ch in kick:  # spaziatura lettere
        k.scrivi(d, (x, ky), ch, t["dark"])
        x += k.larghezza(ch) + 3

    # titolo (riduce il corpo finché sta in 4 righe)
    for size in (76, 68, 60, 54, 48):
        tf = Testo(lat_xb, cjk_path, size)
        righe = a_capo(titolo, tf, max_w, 4)
        if len(righe) <= 3 or size == 48:
            break
    y = ky + 58
    lh = int(size * 1.14)
    for r in righe:
        tf.scrivi(d, (80, y), r, INK)
        y += lh

    # marchio in basso
    by = H - 112
    seal = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    sd = ImageDraw.Draw(seal)
    sd.rounded_rectangle((0, 0, 63, 63), 16, fill=RED)
    sf = ImageFont.truetype(cjk_path, 22, index=2 if "NotoSansCJK" in cjk_path else 0)
    for i, ch in enumerate("中文"):
        bb = sd.textbbox((0, 0), ch, font=sf)
        sd.text(((64 - (bb[2] - bb[0])) / 2 - bb[0], 6 + i * 26 - bb[1] + 2), ch, font=sf, fill="#FFFFFF")
    shadow = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    ImageDraw.Draw(shadow).rounded_rectangle((0, 0, 63, 63), 16, fill=YELLOW)
    shadow = shadow.rotate(4, resample=Image.BICUBIC, expand=True)
    sealr = seal.rotate(4, resample=Image.BICUBIC, expand=True)
    img.paste(shadow, (84, by + 4), shadow)
    img.paste(sealr, (80, by), sealr)
    d = ImageDraw.Draw(img, "RGBA")
    name = Testo(lat_xb, cjk_path, 30)
    name.scrivi(d, (162, by + 6), "Chiara Buchetti", INK)
    tag = Testo(lat_body, cjk_path, 21)
    tag.scrivi(d, (163, by + 44), "Lingua e cultura cinese · chiarabuchetti.it", MUTED)

    # striscia rossa in fondo
    d.rectangle((0, H - 12, W, H), fill=RED)
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    img.save(dest, optimize=True)


# --- front matter -----------------------------------------------------------
def leggi(path):
    s = open(path, encoding="utf-8").read()
    m = re.match(r"^---\n(.*?)\n---\n?", s, re.S)
    if not m:
        return None, None, s
    return yaml.safe_load(m.group(1)) or {}, m, s


def scrivi_image(path, valore, m, s):
    fm = m.group(1)
    # rimuove un eventuale blocco image: generato in precedenza
    fm = re.sub(r"\nimage:\n(?:  .*\n?)+", "\n", fm + "\n").rstrip("\n")
    fm = re.sub(r"\nimage: .*", "", fm)
    blocco = f"\nimage:\n  path: \"{valore['path']}\"\n  width: {valore['width']}\n  height: {valore['height']}"
    nuovo = "---\n" + fm + blocco + "\n---\n" + s[m.end():]
    open(path, "w", encoding="utf-8").write(nuovo)


def path_image(fm):
    im = fm.get("image")
    if isinstance(im, dict):
        return im.get("path")
    return im


def prima_immagine(body):
    for src in re.findall(r'<img[^>]+src="([^"]+)"|!\[[^\]]*\]\(([^)\s]+)', body):
        src = src[0] or src[1]
        if not src.startswith("/assets/"):
            continue
        cands = []
        orig = re.sub(r"-\d+x\d+(\.\w+)$", r"\1", src)
        if orig != src:
            cands.append(orig)
        cands.append(src)
        for c in cands:
            local = os.path.join(ROOT, c.lstrip("/"))
            if not os.path.isfile(local) or not re.search(r"\.(jpe?g|png|gif|webp)$", c, re.I):
                continue
            try:
                with Image.open(local) as im:
                    w, h = im.size
            except Exception:
                continue
            if min(w, h) >= MIN_SIDE:
                return {"path": c, "width": w, "height": h}
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rigenera", action="store_true", help="ricrea anche le immagini già generate")
    args = ap.parse_args()
    cjk = trova_cjk()
    cat = yaml.safe_load(open(os.path.join(ROOT, "_data", "categorie.yml"), encoding="utf-8"))
    servizi = {s["id"]: s for s in yaml.safe_load(open(os.path.join(ROOT, "_data", "servizi.yml"), encoding="utf-8"))}
    stats = {"prima immagine": 0, "generate": 0, "con immagine già scelta": 0}

    def genera(nome, titolo, kicker, zh, colore):
        dest = os.path.join(OUT_DIR, nome + ".png")
        if args.rigenera or not os.path.exists(dest):
            disegna(titolo, kicker, zh, colore, dest, cjk)
        stats["generate"] += 1
        return {"path": GEN_PREFIX + nome + ".png", "width": W, "height": H}

    # immagine generica del sito
    genera("default", "Lingua e cultura cinese: didattica, materiali e servizi linguistici", "Chiara Buchetti", "中文", "red")

    # articoli
    for path in sorted(glob.glob(os.path.join(ROOT, "_posts", "**", "*.*"), recursive=True)):
        fm, m, s = leggi(path)
        if fm is None:
            continue
        cur = path_image(fm)
        if cur and not cur.startswith(GEN_PREFIX):
            stats["con immagine già scelta"] += 1
            continue
        body = s[m.end():]
        val = prima_immagine(body)
        if val:
            stats["prima immagine"] += 1
        else:
            ck = (fm.get("categories") or [None])[0]
            cs = cat.get(ck) or cat["default"]
            d = fm.get("date")
            if isinstance(d, str):
                d = datetime.datetime.fromisoformat(d[:10])
            data = f"{d.day} {MESI[d.month - 1]} {d.year}" if d else ""
            slug = os.path.splitext(os.path.basename(path))[0]
            slug = re.sub(r"[^A-Za-z0-9-]+", "", slug).strip("-")[:80]
            kick = " · ".join(x for x in [cs.get("nome", ck or "Blog"), data] if x)
            val = genera("post-" + slug, str(fm.get("title", "")), kick, cs.get("zh", "文"), cs.get("colore", "red"))
        if path_image(fm) != val["path"] or args.rigenera:
            scrivi_image(path, val, m, s)

    # pagine
    pagine = [os.path.join(ROOT, "index.md")] + sorted(glob.glob(os.path.join(ROOT, "_pages", "**", "*.md"), recursive=True)) \
        + sorted(glob.glob(os.path.join(ROOT, "blog", "*.html")))
    for path in pagine:
        fm, m, s = leggi(path)
        if fm is None or fm.get("redirect_to") or fm.get("sitemap") is False:
            continue
        cur = path_image(fm)
        if cur and not cur.startswith(GEN_PREFIX):
            stats["con immagine già scelta"] += 1
            continue
        rel = os.path.relpath(path, ROOT)
        nome = "page-" + re.sub(r"[^\w]+", "-", os.path.splitext(rel)[0].replace("_pages/", "")).strip("-")
        colore, zh, kicker = fm.get("tone"), fm.get("zh"), "Chiara Buchetti"
        titolo = fm.get("title", "")
        if fm.get("servizio") in servizi:
            sv = servizi[fm["servizio"]]
            colore, zh, kicker = colore or sv["colore"], zh or sv["zh"], "Servizi linguistici"
        if fm.get("categoria"):
            cs = cat.get(fm["categoria"], cat["default"])
            colore, zh, kicker, titolo = cs["colore"], cs["zh"], "Blog · categoria", cs.get("nome", fm["categoria"])
        if rel == "index.md":
            titolo, zh, colore, kicker = "Ciao, sono Chiara! Lingua e cultura cinese", "你好", "red", "Docente · autrice · traduttrice"
        if rel == os.path.join("blog", "index.html"):
            titolo, zh, colore, kicker = "Blog: notizie, guide, cultura e didattica del cinese", "博客", "red", "Chiara Buchetti"
        val = genera(nome, titolo, kicker, zh, colore or "red")
        if cur != val["path"]:
            scrivi_image(path, val, m, s)

    print(", ".join(f"{k}: {v}" for k, v in stats.items()))


if __name__ == "__main__":
    main()
