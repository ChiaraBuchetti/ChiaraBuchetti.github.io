---
title: "Materiale didattico"
zh: "教材"
subtitle: "Qui potete trovare il materiale utilizzato per alcuni corsi, utile per il vostro ripasso o per la creazione di lezioni ad ogni livello."
permalink: /materiale-didattico/
tone: "yellow"
wide: true
image:
  path: "/assets/images/social/page-materiale-didattico.png"
  width: 1200
  height: 630
---
{%- assign toni = "red,jade,sky,yellow,ink" | split: "," -%}
<div class="material-groups">
{%- for g in site.data.materiali %}
{%- assign tone = toni[forloop.index0] | default: "red" -%}
{%- if g.colore %}{% assign tone = g.colore %}{% endif -%}
  <section class="material-group tone-{{ tone }}">
    <h2><span class="material-num">{{ forloop.index | prepend: "0" | slice: -2, 2 }}</span>{{ g.gruppo }}</h2>
    <ul class="material-list">
    {%- for v in g.voci %}
      <li>
      {%- if v.file and v.file != "" -%}
        <a href="{{ v.file | relative_url }}" download>{% include icon.html name="download" px=18 %}<span>{{ v.titolo }}</span><small>{{ v.file | split: "." | last | upcase }}</small></a>
      {%- elsif v.url and v.url != "" -%}
        <a href="{{ v.url }}" target="_blank" rel="noopener">{% include icon.html name="external" px=18 %}<span>{{ v.titolo }}</span><small>Online</small></a>
      {%- else -%}
        <span class="is-soon">{% include icon.html name="clock" px=18 %}<span>{{ v.titolo }}</span><small>In arrivo</small></span>
      {%- endif -%}
      </li>
    {%- endfor %}
    </ul>
  </section>
{%- endfor %}
</div>
