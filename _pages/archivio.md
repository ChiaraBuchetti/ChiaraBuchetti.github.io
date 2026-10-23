---
title: "Archivio articoli"
zh: "档"
tone: "yellow"
permalink: /archivio/
cta: false
image:
  path: "/assets/images/social/page-archivio.png"
  width: 1200
  height: 630
---
{% include blog-tabs.html current="archivio" %}

{%- assign anni = site.posts | group_by_exp: "p", "p.date | date: '%Y'" -%}
<div class="pill-row">
{%- for a in anni -%}<a class="pill" href="#anno-{{ a.name }}">{{ a.name }} <small>{{ a.items.size }}</small></a>{%- endfor -%}
</div>

{% for a in anni %}
<section class="archive-group" id="anno-{{ a.name }}">
<h2>{{ a.name }}</h2>
<ul class="archive-list">
{%- for p in a.items %}
<li><a href="{{ p.url | relative_url }}">{{ p.title }}</a> <time>{% include date-it.html date=p.date %}</time></li>
{%- endfor %}
</ul>
</section>
{% endfor %}
