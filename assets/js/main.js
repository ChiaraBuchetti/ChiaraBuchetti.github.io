/* Chiara Buchetti — script del sito (nessuna dipendenza esterna) */
(function () {
  "use strict";

  /* Menu mobile */
  var toggle = document.querySelector(".nav-toggle");
  if (toggle) {
    toggle.addEventListener("click", function () {
      var open = document.body.classList.toggle("nav-open");
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
      toggle.setAttribute("aria-label", open ? "Chiudi il menu" : "Apri il menu");
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && document.body.classList.contains("nav-open")) toggle.click();
    });
  }

  /* Carattere del giorno */
  var card = document.getElementById("hanzi-card");
  var dataEl = document.getElementById("hanzi-data");
  if (card && dataEl) {
    var list = [];
    try { list = JSON.parse(dataEl.textContent); } catch (e) { list = []; }
    if (list.length) {
      var day = Math.floor((Date.now() - new Date().getTimezoneOffset() * 60000) / 86400000);
      var idx = day % list.length;
      var esc = function (s) {
        return String(s || "").replace(/[&<>"]/g, function (c) {
          return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c];
        });
      };
      var render = function () {
        var z = list[idx];
        card.innerHTML =
          '<div class="hanzi-grid"><span class="hanzi-char" lang="zh">' + esc(z.h) + "</span></div>" +
          '<div class="hanzi-info"><p class="hanzi-py">' + esc(z.py) + "</p>" +
          '<p class="hanzi-it">' + esc(z.it) + "</p>" +
          (z.es ? '<p class="hanzi-ex"><span lang="zh">' + esc(z.es) + "</span> <em>" + esc(z.espy) + "</em> — " + esc(z.esit) + "</p>" : "") +
          "</div>";
        card.classList.remove("is-changing");
        void card.offsetWidth;
        card.classList.add("is-changing");
      };
      render();
      var next = document.querySelector(".js-hanzi-next");
      if (next) next.addEventListener("click", function () { idx = (idx + 1 + Math.floor(Math.random() * (list.length - 1))) % list.length; render(); });
    }
  }

  /* Ricerca nell'header: l'indice viene scaricato solo alla prima apertura */
  var box = document.getElementById("site-search");
  var input = document.getElementById("search-input");
  if (box && input) {
    var header = document.querySelector(".site-header");
    var panel = document.getElementById("search-panel");
    var results = document.getElementById("search-results");
    var status = document.getElementById("search-status");
    var backdrop = document.querySelector(".search-backdrop");
    var toggleBtn = document.querySelector(".search-toggle");
    var index = null, loading = null, active = -1;
    var norm = function (s) { return String(s || "").toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g, ""); };
    var escH = function (s) { return String(s).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); };
    var escR = function (s) { return s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"); };
    var mark = function (text, q) {
      var n = norm(text), i = n.indexOf(q);
      if (i < 0) return escH(text);
      return escH(text.slice(0, i)) + "<mark>" + escH(text.slice(i, i + q.length)) + "</mark>" + escH(text.slice(i + q.length));
    };
    var snippet = function (text, q) {
      var i = norm(text).indexOf(q);
      if (i < 0) return escH(text.substr(0, 130)) + "…";
      var start = Math.max(0, i - 50);
      return (start > 0 ? "…" : "") + mark(text.substr(start, 150), q) + "…";
    };
    var load = function () {
      if (!loading) {
        loading = fetch(box.dataset.index || "/search.json")
          .then(function (r) { return r.json(); })
          .then(function (d) { index = d.filter(function (p) { return p.t; }); run(); })
          .catch(function () { status.textContent = "Impossibile caricare l'indice di ricerca."; panel.hidden = false; });
      }
      return loading;
    };
    var setActive = function (i) {
      var items = results.querySelectorAll("a");
      if (!items.length) { active = -1; return; }
      active = (i + items.length) % items.length;
      items.forEach(function (a, k) { a.classList.toggle("is-active", k === active); a.setAttribute("aria-selected", k === active); });
      items[active].scrollIntoView({ block: "nearest" });
    };
    var run = function () {
      if (!index) return;
      var raw = input.value.trim(), q = norm(raw);
      active = -1;
      if (q.length < 2) { results.innerHTML = ""; status.textContent = ""; panel.hidden = true; input.setAttribute("aria-expanded", "false"); return; }
      var words = q.split(/\s+/);
      var hits = index.map(function (p) {
        var t = norm(p.t), c = norm(p.c), score = 0;
        for (var w = 0; w < words.length; w++) {
          var inT = t.indexOf(words[w]) > -1, inC = c.indexOf(words[w]) > -1;
          if (!inT && !inC) return null;
          score += inT ? 10 : 1;
        }
        if (t.indexOf(q) === 0) score += 5;
        return { p: p, s: score };
      }).filter(Boolean).sort(function (a, b) { return b.s - a.s; });
      status.textContent = hits.length ? hits.length + " risultat" + (hits.length === 1 ? "o" : "i") : "Nessun risultato per “" + raw + "”.";
      results.innerHTML = hits.slice(0, 30).map(function (h, k) {
        var p = h.p;
        return '<li><a href="' + p.u + '" role="option" id="sr-' + k + '"><span class="sr-meta">' +
          (p.k ? '<span class="sr-kind">' + escH(p.k) + "</span>" : "") + (p.d ? "<time>" + p.d + "</time>" : "") +
          '</span><strong>' + mark(p.t, words[0]) + "</strong><p>" + snippet(p.c, words[0]) + "</p></a></li>";
      }).join("");
      panel.hidden = false;
      input.setAttribute("aria-expanded", "true");
    };
    var open = function () {
      document.body.classList.add("search-open");
      box.hidden = false; backdrop.hidden = false;
      toggleBtn.setAttribute("aria-expanded", "true");
      if (document.body.classList.contains("nav-open") && toggle) toggle.click();
      input.focus(); input.select();
      load();
    };
    var close = function () {
      document.body.classList.remove("search-open");
      box.hidden = true; panel.hidden = true; backdrop.hidden = true;
      toggleBtn.setAttribute("aria-expanded", "false");
      toggleBtn.focus();
    };
    toggleBtn.addEventListener("click", function () { document.body.classList.contains("search-open") ? close() : open(); });
    box.querySelector(".search-close").addEventListener("click", close);
    backdrop.addEventListener("click", close);
    document.querySelectorAll(".js-open-search").forEach(function (b) { b.addEventListener("click", open); });
    input.addEventListener("input", run);
    input.addEventListener("keydown", function (e) {
      if (e.key === "ArrowDown") { e.preventDefault(); setActive(active + 1); }
      else if (e.key === "ArrowUp") { e.preventDefault(); setActive(active - 1); }
      else if (e.key === "Enter") {
        var items = results.querySelectorAll("a");
        var target = items[active > -1 ? active : 0];
        if (target) { e.preventDefault(); location.href = target.href; }
      }
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && document.body.classList.contains("search-open")) { close(); return; }
      var tag = (e.target.tagName || "").toLowerCase();
      if (e.key === "/" && !document.body.classList.contains("search-open") && tag !== "input" && tag !== "textarea" && tag !== "select") {
        e.preventDefault(); open();
      }
    });
    /* vecchi link /cerca/?q=... o ?q= su qualsiasi pagina */
    var q0 = new URLSearchParams(location.search).get("q");
    if (q0) { open(); input.value = q0; }
  }

  /* Galleria e immagini ingrandibili negli articoli */
  var prose = document.querySelector(".layout-post .prose");
  if (prose) {
    var isImg = /\.(jpe?g|png|gif|webp)(\?.*)?$/i;
    var links = Array.prototype.filter.call(prose.querySelectorAll("a"), function (a) {
      return isImg.test(a.getAttribute("href") || "") && a.querySelector("img");
    });
    /* immagini che non si caricano (es. foto non ancora scaricate): nascoste */
    prose.querySelectorAll("img").forEach(function (img) {
      var hide = function () {
        var fig = img.closest(".gallery figure") || img.closest("figure") || img;
        fig.classList.add("is-broken");
        var gal = img.closest(".gallery");
        if (gal && !gal.querySelector("figure:not(.is-broken)")) gal.classList.add("is-broken");
      };
      if (img.complete && img.naturalWidth === 0) hide(); else img.addEventListener("error", hide);
    });
    /* immagini non collegate ma mostrate rimpicciolite: ingrandibili anche loro */
    var smalls = [];
    var checkSmall = function (img) {
      if (img.closest("a") || img.closest(".is-broken")) return;
      if (img.naturalWidth > img.clientWidth * 1.3 && img.naturalWidth > 500) { img.classList.add("zoomable"); smalls.push(img); }
    };
    prose.querySelectorAll("img").forEach(function (img) {
      if (img.complete) checkSmall(img); else img.addEventListener("load", function () { checkSmall(img); if (smalls.length) setupLb(); });
    });
    var lbReady = false;
    var setupLb = function () {
    if (lbReady) { smalls.forEach(bindSmall); return; }
    lbReady = true;
      var lb = document.createElement("div");
      lb.className = "lightbox"; lb.hidden = true;
      lb.setAttribute("role", "dialog"); lb.setAttribute("aria-modal", "true"); lb.setAttribute("aria-label", "Immagine ingrandita");
      lb.innerHTML = '<button class="lb-btn lb-close" aria-label="Chiudi">&times;</button>' +
        '<button class="lb-btn lb-prev" aria-label="Precedente">&#8249;</button>' +
        '<figure><img alt=""><figcaption></figcaption></figure>' +
        '<button class="lb-btn lb-next" aria-label="Successiva">&#8250;</button>';
      document.body.appendChild(lb);
      var lbImg = lb.querySelector("img"), lbCap = lb.querySelector("figcaption"), cur = 0, group = [];
      var show = function (i) {
        cur = (i + group.length) % group.length;
        var a = group[cur], im = a.tagName === "IMG" ? a : a.querySelector("img");
        lbImg.src = a.tagName === "IMG" ? (a.currentSrc || a.src) : a.href; lbImg.alt = im.alt || "";
        var fc = a.closest("figure") && a.closest("figure").querySelector("figcaption");
        lbCap.textContent = (fc ? fc.textContent : im.alt) || "";
        lb.classList.toggle("is-single", group.length < 2);
      };
      var lbClose = function () { lb.hidden = true; document.body.classList.remove("lb-open"); };
      links.forEach(function (a) {
        a.classList.add("zoomable");
        a.addEventListener("click", function (e) {
          e.preventDefault();
          var gal = a.closest(".gallery");
          group = gal ? Array.prototype.filter.call(gal.querySelectorAll("a.zoomable"), function (x) { return !x.closest(".is-broken"); }) : [a];
          show(group.indexOf(a)); lb.hidden = false; document.body.classList.add("lb-open");
          lb.querySelector(".lb-close").focus();
        });
      });
      bindSmall = function (img) {
        if (img.dataset.lb) return; img.dataset.lb = "1";
        img.addEventListener("click", function () {
          group = [img]; show(0); lb.hidden = false; document.body.classList.add("lb-open");
          lb.querySelector(".lb-close").focus();
        });
      };
      smalls.forEach(bindSmall);
      lb.querySelector(".lb-close").addEventListener("click", lbClose);
      lb.querySelector(".lb-prev").addEventListener("click", function () { show(cur - 1); });
      lb.querySelector(".lb-next").addEventListener("click", function () { show(cur + 1); });
      lb.addEventListener("click", function (e) { if (e.target === lb) lbClose(); });
      document.addEventListener("keydown", function (e) {
        if (lb.hidden) return;
        if (e.key === "Escape") lbClose();
        if (e.key === "ArrowLeft") show(cur - 1);
        if (e.key === "ArrowRight") show(cur + 1);
      });
    };
    var bindSmall = function () {};
    if (links.length || smalls.length) setupLb();
  }

  /* Modulo contatti: tipo di richiesta preselezionato da /contatti/?servizio=... */
  var sel = document.getElementById("cf-servizio");
  if (sel) {
    var sv = new URLSearchParams(location.search).get("servizio");
    if (sv && sel.querySelector('option[value="' + sv.replace(/"/g, "") + '"]')) sel.value = sv;
  }

  /* Video YouTube: l'iframe viene creato solo dopo il clic (nessun contatto con Google prima) */
  document.querySelectorAll(".video-consent").forEach(function (box) {
    var btn = box.querySelector(".video-consent-btn");
    if (!btn) return;
    btn.addEventListener("click", function () {
      var f = document.createElement("iframe");
      f.src = "https://www.youtube-nocookie.com/embed/" + encodeURIComponent(box.dataset.yt) + "?autoplay=1&rel=0";
      f.title = "Video YouTube";
      f.allow = "autoplay; encrypted-media; picture-in-picture; fullscreen";
      f.allowFullscreen = true;
      box.innerHTML = "";
      box.classList.add("is-loaded");
      box.style.aspectRatio = "16 / 9";
      box.appendChild(f);
    });
  });
})();
