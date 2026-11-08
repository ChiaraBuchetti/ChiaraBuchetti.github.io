/* Chiara Buchetti — carousel automatico per immagini consecutive nel prose
   Converte automaticamente ogni sequenza di 2+ immagini in successione
   nel corpo di un articolo in un carosello navigabile.
   Supporta anche i blocchi wp-block-gallery di WordPress. */
(function () {
  "use strict";

  var prose = document.querySelector(".layout-post .prose");
  if (!prose) return;

  /* ── Rileva se un elemento è un "blocco immagine" puro ── */
  function isImgBlock(el) {
    if (!el || el.nodeType !== 1) return false;
    var tag = el.tagName.toLowerCase();
    if (tag === "figure") {
      // Esclude wp-block-gallery: gestito separatamente
      if (el.classList.contains("wp-block-gallery")) return false;
      return !!el.querySelector("img");
    }
    if (tag === "p") {
      if (!el.querySelector("img")) return false;
      var clone = el.cloneNode(true);
      clone.querySelectorAll("img, a, br, span").forEach(function (n) { n.remove(); });
      return clone.textContent.trim() === "";
    }
    return false;
  }

  /* ── Estrae immagine e didascalia da un blocco ── */
  function extractSlide(el) {
    var img = el.querySelector("img");
    var cap = el.querySelector("figcaption");
    return {
      src: img ? (img.getAttribute("src") || "") : "",
      alt: img ? (img.getAttribute("alt") || "") : "",
      caption: cap ? cap.textContent.trim() : ""
    };
  }

  /* ── Costruisce il DOM del carosello ── */
  function buildCarousel(group) {
    var slides = group.map(extractSlide);
    var n = slides.length;
    var cur = 0;

    var car = document.createElement("div");
    car.className = "prose-carousel";
    car.setAttribute("role", "region");
    car.setAttribute("aria-roledescription", "carosello");
    car.setAttribute("aria-label", "Galleria di " + n + " immagini");
    car.setAttribute("tabindex", "0");

    /* Track */
    var track = document.createElement("div");
    track.className = "pcar-track";
    var strip = document.createElement("div");
    strip.className = "pcar-slides";
    track.appendChild(strip);
    car.appendChild(track);

    slides.forEach(function (data, i) {
      var slide = document.createElement("div");
      slide.className = "pcar-slide";
      slide.setAttribute("role", "group");
      slide.setAttribute("aria-roledescription", "diapositiva");
      slide.setAttribute("aria-label", (i + 1) + " di " + n);

      var img = document.createElement("img");
      img.src = data.src;
      img.alt = data.alt;
      img.loading = i === 0 ? "eager" : "lazy";
      img.className = "in-carousel";
      slide.appendChild(img);

      if (data.caption) {
        var fc = document.createElement("figcaption");
        fc.textContent = data.caption;
        slide.appendChild(fc);
      }

      strip.appendChild(slide);
    });

    /* Frecce */
    var prev = document.createElement("button");
    prev.className = "pcar-btn pcar-prev";
    prev.setAttribute("aria-label", "Immagine precedente");
    prev.innerHTML = "&#8249;";
    car.appendChild(prev);

    var next = document.createElement("button");
    next.className = "pcar-btn pcar-next";
    next.setAttribute("aria-label", "Immagine successiva");
    next.innerHTML = "&#8250;";
    car.appendChild(next);

    /* Footer: dots + contatore */
    var footer = document.createElement("div");
    footer.className = "pcar-footer";

    var dotsWrap = document.createElement("div");
    dotsWrap.className = "pcar-dots";
    var dotBtns = [];
    for (var d = 0; d < n; d++) {
      (function (idx) {
        var dot = document.createElement("button");
        dot.className = "pcar-dot" + (idx === 0 ? " is-active" : "");
        dot.setAttribute("aria-label", "Vai all'immagine " + (idx + 1));
        dot.addEventListener("click", function () { go(idx); });
        dotsWrap.appendChild(dot);
        dotBtns.push(dot);
      })(d);
    }

    var counter = document.createElement("span");
    counter.className = "pcar-counter";
    counter.setAttribute("aria-live", "polite");
    counter.setAttribute("aria-atomic", "true");
    counter.textContent = "1 / " + n;

    footer.appendChild(dotsWrap);
    footer.appendChild(counter);
    car.appendChild(footer);

    /* ── Navigazione ── */
    function go(idx) {
      cur = (idx + n) % n;
      strip.style.transform = "translateX(-" + (cur * 100) + "%)";
      dotBtns.forEach(function (b, k) { b.classList.toggle("is-active", k === cur); });
      counter.textContent = (cur + 1) + " / " + n;
    }

    prev.addEventListener("click", function () { go(cur - 1); });
    next.addEventListener("click", function () { go(cur + 1); });

    /* Tastiera (quando il carosello è in focus) */
    car.addEventListener("keydown", function (e) {
      if (e.key === "ArrowLeft")  { e.preventDefault(); go(cur - 1); }
      if (e.key === "ArrowRight") { e.preventDefault(); go(cur + 1); }
    });

    /* Touch swipe */
    var tx0 = 0, ty0 = 0, swiping = false;
    track.addEventListener("touchstart", function (e) {
      tx0 = e.touches[0].clientX;
      ty0 = e.touches[0].clientY;
      swiping = false;
    }, { passive: true });
    track.addEventListener("touchmove", function (e) {
      var dx = e.touches[0].clientX - tx0;
      var dy = e.touches[0].clientY - ty0;
      if (!swiping && Math.abs(dx) > Math.abs(dy) && Math.abs(dx) > 10) swiping = true;
      if (swiping) e.preventDefault();
    }, { passive: false });
    track.addEventListener("touchend", function (e) {
      if (!swiping) return;
      var dx = e.changedTouches[0].clientX - tx0;
      if (Math.abs(dx) > 40) go(cur + (dx < 0 ? 1 : -1));
      swiping = false;
    }, { passive: true });

    return car;
  }

  /* ── Fase 1: converti wp-block-gallery in carosello ── */
  Array.prototype.slice.call(prose.querySelectorAll("figure.wp-block-gallery")).forEach(function (gallery) {
    var inner = Array.prototype.slice.call(gallery.querySelectorAll("figure.wp-block-image"));
    if (inner.length < 2) return;
    var carousel = buildCarousel(inner);
    gallery.parentNode.insertBefore(carousel, gallery);
    gallery.parentNode.removeChild(gallery);
  });

  /* ── Fase 2: raggruppa figure/p-img consecutive nel prose ── */
  var children = Array.prototype.slice.call(prose.children);
  var groups = [], run = [];

  children.forEach(function (el) {
    if (isImgBlock(el)) {
      run.push(el);
    } else {
      if (run.length >= 2) groups.push(run.slice());
      run = [];
    }
  });
  if (run.length >= 2) groups.push(run);

  /* ── Sostituisce ogni gruppo con il carosello ── */
  groups.forEach(function (group) {
    var carousel = buildCarousel(group);
    prose.insertBefore(carousel, group[0]);
    group.forEach(function (el) { prose.removeChild(el); });
  });

})();
