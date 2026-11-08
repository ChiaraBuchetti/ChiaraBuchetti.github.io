---
title: "Servizi linguistici"
zh: "服务"
subtitle: "Traduzione, mediazione, lezioni e consulenza per la lingua cinese e inglese."
permalink: /servizi-linguistici/
tone: "jade"
layout: default
image:
  path: "/assets/images/social/page-servizi-linguistici-index.png"
  width: 1200
  height: 630
---
{% include page-hero.html kicker="Lavoriamo insieme" %}

<div class="container service-page">
  {% include servizi-tabs.html %}

  <div class="service-intro">
    <p class="service-lead">Grazie agli studi svolti e alle esperienze di lavoro in ambito aziendale, universitario e come libera professionista, propongo una gamma differenziata di servizi linguistici per privati, scuole e aziende.</p>
    <div class="intro-langs">
      <p class="aside-label">Lingue di lavoro</p>
      <ul class="lang-chips lang-chips-lg">
        <li><span lang="zh">中文</span> Cinese</li>
        <li>Inglese</li>
        <li>Tedesco</li>
        <li>Italiano per stranieri</li>
      </ul>
    </div>
  </div>

  <div class="service-cards">
    {%- for sv in site.data.servizi %}
    {%- if sv.url %}<a class="svc-card tone-{{ sv.colore }}" href="{{ sv.url | relative_url }}">{% else %}<div class="svc-card tone-{{ sv.colore }} is-static">{% endif %}
      <span class="svc-zh" lang="zh" aria-hidden="true">{{ sv.zh }}<small>{{ sv.pinyin }}</small></span>
      <h2 class="svc-title">{{ sv.titolo }}</h2>
      <p class="svc-desc">{{ sv.desc }}</p>
      <ul class="lang-chips">{% for l in sv.lingue %}<li>{{ l }}</li>{% endfor %}</ul>
      {%- if sv.url %}
      <span class="svc-more">Scopri il servizio {% include icon.html name="arrow" px=18 %}</span>
    </a>
      {%- else %}
      <a class="svc-more" href="{{ '/contatti/' | relative_url }}?servizio={{ sv.form | url_encode }}">Disponibile su richiesta {% include icon.html name="arrow" px=18 %}</a>
    </div>
      {%- endif %}
    {%- endfor %}
    <a class="svc-card svc-card-cta" href="{{ '/contatti/' | relative_url }}">
      <span class="svc-zh" lang="zh" aria-hidden="true">问<small>wèn</small></span>
      <h2 class="svc-title">Hai un'altra esigenza?</h2>
      <p class="svc-desc">Raccontami di cosa hai bisogno: insieme troviamo la soluzione più adatta.</p>
      <span class="svc-more">Scrivimi {% include icon.html name="arrow" px=18 %}</span>
    </a>
  </div>

  <section class="steps-section" aria-labelledby="steps-title">
    <h2 class="section-label" id="steps-title">Come funziona</h2>
    <ol class="steps">
      <li>
        <span class="step-n">1</span>
        <h3>Scrivimi</h3>
        <p>Raccontami di cosa hai bisogno tramite il <a href="{{ '/contatti/' | relative_url }}">modulo di contatto</a>. Per una traduzione allega, se puoi, il documento.</p>
      </li>
      <li>
        <span class="step-n">2</span>
        <h3>Ricevi una proposta</h3>
        <p>Tariffe, preventivo, disponibilità e orari vengono definiti in base alla tua richiesta.</p>
      </li>
      <li>
        <span class="step-n">3</span>
        <h3>Si comincia</h3>
        <p>Lezioni, traduzioni o mediazione partono nei tempi e con le modalità concordate.</p>
      </li>
    </ol>
  </section>

</div>
