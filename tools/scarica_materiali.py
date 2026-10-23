#!/usr/bin/env python3
"""
Scarica dal vecchio sito WordPress i file del materiale didattico
(plugin Download Manager + PDF Teen Zone) e li salva in assets/materiali/
con i nomi usati in _data/materiali.yml.

    python3 tools/scarica_materiali.py

Va lanciato da una rete che raggiunge www.chiarabuchetti.it (finché il
vecchio sito è online). I file già presenti vengono saltati.
Per ogni file prova, nell'ordine:
  1. il link di download del plugin  (/download/<slug>/?wpdmdl=<id>)
  2. il file grezzo                 (/wp-content/uploads/download-manager-files/<nome>)
Se entrambi falliscono, scaricarlo a mano dal browser (indirizzo indicato
nell'errore) o via FTP e copiarlo in assets/materiali/ col nome indicato.
"""
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

SITO = "https://www.chiarabuchetti.it"
WPDM = SITO + "/wp-content/uploads/download-manager-files/"

# (nome di destinazione, id pacchetto WPDM, slug /download/..., nome file originale)
FILE = [
    ("griglia-1.pdf", 749, "griglia-1", "1456172709wpdm_griglia01.pdf"),
    ("griglia-2.pdf", 747, "griglia-2", "1456172684wpdm_griglia02-label.pdf"),
    ("griglia-3.pdf", 744, "griglia-3", "1456172477wpdm_griglia04-label2.pdf"),
    ("linux-day-2014.pdf", 753, "linux-day-2014", "1456172868wpdm_Software_lingue_LinuxDay2014.pdf"),
    ("introduzione-alla-scrittura-cinese.ibooks", 755, "introduzione-alla-scrittura-cinese-ibooks",
     "1456173287wpdm_IntroduzioneScritturaCinese.ibooks"),
    ("introduzione-alla-scrittura-cinese.pdf", 757, "introduzione-alla-scrittura-cinese-pdf",
     "1456173466wpdm_IntroduzioneScritturaCinese.pdf"),
    ("guida-di-pechino.pdf", 992, "guida-di-pechino", "Guida di Pechino 3D-4C RIM 2015-16.pdf"),
    ("tesina-2016-diritti-umani.pdf", 1014, "tesina-maturita-cinadiritti-umani-violati",
     "Tesina. Sara Esami di stato 2016.pdf"),
    ("tesina-2016-filosofie-armonia.pdf", 1018, "tesina-maturita-2016-le-filosofie-dellarmonia",
     "tesina definitiva.pdf"),
    ("tesina-2016-uomo-natura.pdf", 1026, "tesina-maturita-2016-rapporto-uomo-natura",
     "TESINA POWERPOINT.pdf"),
]
# file caricati direttamente nella libreria media (non nel plugin)
DIRETTI = [
    ("teen-zone-2022.pdf", SITO + "/wp-content/uploads/2022/09/Teen-Zone-2022.pdf"),
]

FIRME = {".pdf": b"%PDF", ".ibooks": b"PK"}  # .ibooks è un archivio zip


def scarica(url, est):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (migrazione sito)"})
    with urllib.request.urlopen(req, timeout=60) as r:
        data = r.read()
    firma = FIRME.get(est)
    if firma and not data.startswith(firma):
        raise ValueError("la risposta non è il file atteso (forse una pagina HTML)")
    return data


def main():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    dest_dir = os.path.join(root, "assets", "materiali")
    os.makedirs(dest_dir, exist_ok=True)

    lavori = [(n, [f"{SITO}/download/{slug}/?wpdmdl={pid}",
                   WPDM + urllib.parse.quote(orig)]) for n, pid, slug, orig in FILE]
    lavori += [(n, [u]) for n, u in DIRETTI]

    ok = falliti = 0
    for nome, urls in lavori:
        dest = os.path.join(dest_dir, nome)
        if os.path.exists(dest) and os.path.getsize(dest) > 0:
            print(f"  già presente {nome}")
            continue
        est = os.path.splitext(nome)[1].lower()
        errori = []
        for url in urls:
            try:
                data = scarica(url, est)
            except (urllib.error.URLError, OSError, ValueError) as e:
                errori.append(f"{url}: {e}")
                continue
            with open(dest, "wb") as f:
                f.write(data)
            print(f"  scaricato {nome} ({len(data) // 1024} KB)")
            ok += 1
            break
        else:
            falliti += 1
            print(f"  ERRORE {nome}", file=sys.stderr)
            for e in errori:
                print(f"      {e}", file=sys.stderr)

    print(f"\nScaricati: {ok}   Non riusciti: {falliti}")
    sys.exit(1 if falliti else 0)


if __name__ == "__main__":
    main()
