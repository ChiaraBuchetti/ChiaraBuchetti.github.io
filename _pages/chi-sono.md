---
title: "Chi sono"
zh: "关于我"
subtitle: "Docente di lingua e cultura cinese, autrice, traduttrice e mediatrice linguistica."
permalink: /chi-sono/
tone: "sky"
wide: true
image:
  path: "/assets/images/social/page-chi-sono.png"
  width: 1200
  height: 630
---
<div class="about">

<div class="profile profile-card">
  {% include avatar.html big=true %}
  <div>
    <p class="profile-hello" lang="zh">大家好！</p>
    <p>Attualmente presto servizio come docente di ruolo di <strong>Lingua e Cultura Cinese</strong> (C.d.c. AI24) in un liceo linguistico della provincia di Pisa. Precedentemente ho lavorato in un istituto tecnico e in un liceo linguistico di Livorno.</p>
    <ul class="facts">
      <li>{% include icon.html name="school" %} Docente di ruolo · AI24</li>
      <li>{% include icon.html name="book" %} Autrice per Eli</li>
      <li>{% include icon.html name="globe" %} Cinese · Inglese · Tedesco</li>
    </ul>
  </div>
</div>

<div class="about-grid">
  <section class="about-card tone-sky">
    <h2 class="about-title"><span class="about-icon">{% include icon.html name="school" %}</span> Formazione</h2>
    <p>Ho conseguito il diploma di laurea triennale in <em>Mediazione linguistica e culturale</em> (in ambito turistico-imprenditoriale per le lingue inglese, cinese e tedesco) e di laurea magistrale in <em>Scienze linguistiche per la comunicazione interculturale</em>, specializzandomi in lingua e cultura cinese.</p>
    <p>Ho un Master in <em>Traduzione specializzata in ambito giuridico-amministrativo</em> conseguito presso l'Agenzia Formativa TuttoEuropa di Torino.</p>
  </section>
  <section class="about-card tone-jade">
    <h2 class="about-title"><span class="about-icon">{% include icon.html name="briefcase" %}</span> Esperienze</h2>
    <p>Dopo un periodo come traduttrice in Lavazza, sono stata impegnata per due anni come assegnista di ricerca presso l'Università per Stranieri di Siena nell'ambito del <a href="http://www.unistrasi.it/1/572/2984/LSECON.htm" target="_blank" rel="noopener">Progetto <em>LSECON</em></a> (<em>Le lingue straniere come strumento per sostenere il sistema economico e produttivo della Regione Toscana</em>), occupandomi della creazione di materiali didattici per l'insegnamento della lingua e cultura cinese ad imprenditori toscani.</p>
    <p>Mi occupo di traduzione specializzata da inglese, cinese e tedesco e di mediazione linguistico-culturale per la lingua cinese in contesto scolastico, socio-sanitario e aziendale. Ho esperienza di insegnamento del cinese a italofoni e dell'italiano a stranieri, sia in Italia sia all'estero.</p>
  </section>
</div>

<section class="about-section">
  <h2>Pubblicazioni e progetti</h2>
  <ol class="timeline">
  <li><span class="tl-year">2025</span><div>È stato pubblicato il volume <a href="/la-didattica-del-cinese-in-italia-nelle-scuole-e-nelle-universita/">«La didattica del cinese in Italia nelle scuole e nelle università»</a>, cui ho contribuito come ricercatrice.</div></li>
  <li><span class="tl-year">2024</span><div>Ho contribuito al volume <a href="https://www.utetuniversita.it/catalogo/lingue-e-letterature/tecniche-didattiche-per-la-lingua-cinese-3892" target="_blank" rel="noopener">«Tecniche didattiche per la lingua cinese – Proposte operative per la scuola secondaria di secondo grado e per l'università»</a> edito da Utet.</div></li>
  <li><span class="tl-year">2023/24</span><div>Collaboro, assieme alle colleghe Giovanna Ricchezza e Mariarosa Siani, al progetto online di supporto allo studio della lingua e cultura cinese per studenti di scuola secondaria e universitari <strong lang="zh">我们一起复习</strong> (seguici su Instagram: <a href="https://www.instagram.com/women_yiqifuxi/" target="_blank" rel="noopener">@women_yiqifuxi</a>).</div></li>
  <li><span class="tl-year">2023</span><div>Ho pubblicato, assieme alla collega Guo Man, un nuovo manuale di cultura cinese per la scuola secondaria di secondo grado: <a href="/去中国啦！destinazione-cina/"><strong lang="zh">去中国啦！</strong><strong>Destinazione Cina</strong></a> (Eli). <a href="/destinazione-cina-去中国啦！-nuova-edizione/">Nuova edizione 2026</a>.</div></li>
  <li><span class="tl-year">2020</span><div>Sono stata confermata in ruolo nel luglio 2020. Qui trovate la presentazione del mio percorso didattico e formativo, avvenuta ai tempi del Covid-19, che illustra il mio <a href="https://view.genial.ly/5ed7cb86bacf2c0da6557ab0/presentation-presentazione-anno-di-prova-buchetti" target="_blank" rel="noopener">anno di prova</a>.</div></li>
  <li><span class="tl-year">2018</span><div>Ho pubblicato il volume di cultura cinese per la scuola secondaria <a href="/cina-da-scoprire/"><strong><em>Cina da scoprire</em></strong></a> edito da Eli.</div></li>
  <li><span class="tl-year">2016</span><div>Ho partecipato al gruppo di lavoro ministeriale per l'elaborazione di un <strong>Sillabo di lingua cinese per le scuole secondarie di secondo grado</strong> (<a href="http://dida.orizzontescuola.it/news/il-sillabo-della-lingua-cinese-le-scuole-secondarie-di-secondo-grado-0" target="_blank" rel="noopener">link</a>).</div></li>
</ol>
</section>

<section class="about-section" id="rassegna-stampa">
  <h2>Rassegna stampa</h2>
  <p class="section-sub">Articoli, interviste e trasmissioni che hanno parlato dei miei progetti con le scuole.</p>
  {%- assign anni = site.data.rassegna | group_by: "anno" -%}
  <div class="press">
  {%- for a in anni %}
    {%- if forloop.index == 4 %}
  </div>
  <details class="press-more">
    {%- assign ultimo = anni | last -%}{%- assign n_extra = 0 -%}{%- for g in anni offset:3 %}{% assign n_extra = n_extra | plus: g.items.size %}{% endfor %}
    <summary>Mostra tutta la rassegna <small>({{ n_extra }} articoli, fino al {{ ultimo.name }})</small></summary>
  <div class="press">
    {%- endif %}
    <div class="press-year">
      <h3 class="press-y">{{ a.name }}</h3>
      <ul class="press-list">
        {%- for r in a.items %}
        <li class="press-item">
          <p class="press-source"><span>{{ r.testata }}</span>{% if r.nota %} · {{ r.nota }}{% endif %} <time>{{ r.data }}</time></p>
          {%- for l in r.link %}
          <a class="press-link" href="{{ l.url }}" target="_blank" rel="noopener">{{ l.titolo }} {% include icon.html name="external" px=14 %}</a>
          {%- endfor %}
        </li>
        {%- endfor %}
      </ul>
    </div>
    {%- if forloop.last and forloop.index >= 4 %}
  </div>
  </details>
    {%- endif %}
  {%- endfor %}
  {%- if anni.size < 4 %}</div>{% endif %}
</section>

</div>
