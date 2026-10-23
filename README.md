# Sito di Chiara Buchetti

Sito statico [Jekyll](https://jekyllrb.com/) con un tema su misura (nessun tema esterno),
pubblicabile su GitHub Pages.
Sostituisce il vecchio sito WordPress `www.chiarabuchetti.it` mantenendo gli stessi indirizzi.

## Struttura

| Percorso | Contenuto |
|---|---|
| `_config.yml` | titolo, autrice, social, menu, impostazioni generali |
| `_data/navigation.yml` | voci del menu in alto e del menu laterale dei servizi |
| `_data/materiali.yml` | elenco del materiale didattico (file e link) |
| `index.md` | home page: tutti i testi (hero, nastro, card, libri) sono nel front matter |
| `_layouts/` | modelli di pagina: `home`, `page`, `post`, `blog`, `default` |
| `_includes/` | pezzi riutilizzabili: header, footer, card articolo, icone SVG |
| `assets/css/main.css` | tutto lo stile; i colori sono variabili in cima al file |
| `assets/js/main.js` | menu mobile, carattere del giorno, ricerca |
| `_data/hanzi.yml` | caratteri del "carattere del giorno" in home |
| `_data/categorie.yml` | colore e carattere cinese di ogni categoria del blog |
| `_pages/` | pagine fisse (Chi sono, Servizi, Contatti, …) |
| `_posts/` | articoli del blog (`AAAA-MM-GG-titolo.md`) |
| `_drafts/` | bozze e `modello-articolo.md` da copiare per un nuovo articolo |
| `assets/images/` | foto profilo, logo, immagini del sito |
| `assets/uploads/` | immagini degli articoli (stessa struttura di `wp-content/uploads`) |
| `assets/materiali/` | PDF e altri file scaricabili |
| `tools/import_wordpress.py` | import dal vecchio sito |

## Aspetto

- Ogni pagina in `_pages/` può avere nel front matter: `zh` (scritta cinese grande nell'intestazione),
  `tone` (`red`, `yellow`, `jade`, `sky`, `ink`), `subtitle`, `subnav: servizi`, `wide: true`, `cta: false`.
- Gli articoli senza immagine di anteprima (`header.teaser`) mostrano il carattere della loro categoria.
- I font sono ospitati nel sito (`assets/fonts/`: Outfit, Nunito Sans, ZCOOL KuaiLe); per il cinese
  "normale" si usano i font del dispositivo (PingFang, Microsoft YaHei, Noto CJK…).

## Privacy / GDPR

Il sito non usa cookie e, durante la navigazione, non contatta servizi esterni:

- niente Google Fonts, CDN, analytics o pulsanti social con tracciamento;
- i video YouTube sono sostituiti da un riquadro "clicca per caricare" (`tools/video_consenso.py`,
  già applicato agli articoli importati e integrato nell'import);
- le immagini caricate da altri siti vanno copiate in locale con
  `python3 tools/localizza_immagini.py` (da lanciare sul proprio computer, serve internet).
  Le immagini non più raggiungibili si eliminano con `--rimuovi-mancanti`;
- il modulo contatti contatta il servizio esterno solo al momento dell'invio.

L'informativa è in `_pages/privacy.md` (`/cookie-law/`): va riletta prima della pubblicazione.

## Lavorare in locale

Serve Ruby (su macOS consigliato tramite Homebrew: `brew install ruby`), poi:

```bash
bundle install                 # solo la prima volta
bundle exec jekyll serve       # sito su http://localhost:4000, si aggiorna da solo
bundle exec jekyll serve --drafts   # mostra anche le bozze
```

## Importare i contenuti dal vecchio WordPress

1. Nel pannello WordPress: **Strumenti → Esporta → Tutti i contenuti → Scarica il file di esportazione**.
2. Salvare il file XML in `_wp-export/` (cartella esclusa da git).
3. Lanciare:

   ```bash
   python3 tools/import_wordpress.py _wp-export/NOMEFILE.xml --download
   ```

   - articoli → `_posts/` (stessi indirizzi di prima, categorie, tag, immagine di anteprima)
   - immagini → `assets/uploads/`
   - testo delle pagine → `_importate/pagine/`: ricopiarlo nelle pagine corrispondenti in `_pages/`
     (che ora contengono bozze ricostruite, segnate con un commento `BOZZA`)
   - file del Download Manager → elenco in `_importate/download-manager.txt`: i PDF vanno
     scaricati dal vecchio sito (o dalla cartella `wp-content/uploads/download-manager-files/`
     via FTP) e copiati in `assets/materiali/` con i nomi indicati in `_data/materiali.yml`
   - riepilogo → `_importate/report.txt`
4. Eliminare l'articolo segnaposto `_posts/2026-10-23-benvenuti-nel-nuovo-sito.md`.

I commenti WordPress non vengono importati (il sito statico non li gestisce).

## Anteprime social (Facebook, LinkedIn, WhatsApp…)

Ogni articolo e pagina ha un campo `image:` nel front matter, usato come immagine di anteprima.
Dopo aver scritto nuovi articoli (o scaricato le foto delle gallerie) lanciare:

```bash
python3 tools/immagini_social.py
```

- articoli: usa la prima immagine del testo; se non ce n'è, genera un'immagine 1200×630 in `assets/images/social/`
- pagine: immagine generata con titolo e carattere cinese della pagina
- un `image:` scelto a mano non viene mai sovrascritto; `--rigenera` ricrea le immagini generate
- anche senza lanciare lo script, un articolo nuovo usa in automatico la prima immagine del testo
  (o `assets/images/social/default.png`) grazie a `_includes/head/social-image.html`

## Da completare

- [ ] Foto profilo in `assets/images/chiara-buchetti.jpg` (sul vecchio sito: `wp-content/uploads/2013/12/io.jpg`)
- [ ] Logo/favicon (vecchio sito: `wp-content/uploads/2013/12/cropped-logo.png`)
- [ ] Testi definitivi delle pagine in `_pages/` (cercare `BOZZA` / `DA COMPLETARE`)
- [ ] Link Genially in `_data/materiali.yml`
- [ ] Modulo contatti (FormSubmit, già configurato su chiara.buchetti@gmail.com): dopo la pubblicazione inviare un messaggio di prova,
      cliccare il link di attivazione arrivato via mail e sostituire l'email con l'alias ricevuto in `contact_form.endpoint` (`_config.yml`)
- [ ] Testo privacy (`_pages/privacy.md`)
- [ ] Foto delle gallerie degli articoli (118 mancanti): `python3 tools/converti_gallerie.py _wp-export/NOMEFILE.xml --download`
- [ ] Rassegna stampa: si aggiorna in `_data/rassegna.yml`

## Pubblicazione

1. Spostare il repository sull'account definitivo con nome `<account>.github.io`
   (oppure usare un dominio personalizzato) e aggiornare `url` / `repository` in `_config.yml`.
2. **Settings → Pages → Build and deployment → Deploy from a branch**, ramo `main`, cartella `/ (root)`.
3. Per mantenere `www.chiarabuchetti.it`: aggiungere il dominio in **Settings → Pages → Custom domain**
   (crea il file `CNAME`) e configurare i DNS presso il registrar
   ([istruzioni GitHub](https://docs.github.com/it/pages/configuring-a-custom-domain-for-your-github-pages-site)).
