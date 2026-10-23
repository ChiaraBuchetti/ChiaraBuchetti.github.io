#!/usr/bin/env python3
"""
Sostituisce i video YouTube incorporati negli articoli con un riquadro
"clicca per caricare": YouTube viene contattato solo dopo il clic del
visitatore (consenso esplicito, conforme GDPR).

    python3 tools/video_consenso.py          # elabora _posts/ e _pages/

Si può rilanciare senza problemi: i video già convertiti vengono ignorati.
"""
import glob
import re
import sys

IFRAME = re.compile(
    r'(?:<div class="responsive-video-container">\s*)?'
    r'<iframe[^>]*src="(?:https?:)?//(?:www\.)?youtube(?:-nocookie)?\.com/embed/([\w-]{11})[^"]*"[^>]*>\s*</iframe>'
    r'(?:\s*</div>(?=\s*\n|\s*$))?', re.I)


def segnaposto(vid):
    return (f'<div class="video-consent" data-yt="{vid}">'
            f'<button type="button" class="video-consent-btn" aria-label="Carica il video da YouTube">'
            f'<span class="video-play" aria-hidden="true"></span><span>Guarda il video</span></button>'
            f'<p class="video-consent-note">Il video è ospitato su YouTube: cliccando, verrà caricato da Google, '
            f'che riceverà alcuni dati di navigazione. '
            f'<a href="https://www.youtube.com/watch?v={vid}" target="_blank" rel="noopener">Apri su YouTube</a></p>'
            f'</div>')


def main(root="."):
    tot = 0
    for f in glob.glob(f"{root}/_posts/*") + glob.glob(f"{root}/_pages/**/*.*", recursive=True):
        s = open(f, encoding="utf-8").read()
        n, cnt = IFRAME.subn(lambda m: segnaposto(m.group(1)), s)
        if cnt:
            open(f, "w", encoding="utf-8").write(n)
            tot += cnt
            print(f"{cnt} video  {f}")
    print(f"Totale: {tot} video convertiti")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else ".")
