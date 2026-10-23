---
title: "Articoli per tag"
zh: "签"
tone: "jade"
permalink: /tag/
cta: false
image:
  path: "/assets/images/social/page-tag.png"
  width: 1200
  height: 630
---
{% include blog-tabs.html current="tag" %}

{%- assign tags = site.tags | sort -%}
<div class="pill-row">
{%- for t in tags -%}
<a class="pill" href="#{{ t[0] | slugify }}">{{ t[0] }} <small>{{ t[1].size }}</small></a>
{%- endfor -%}
</div>

{% for t in tags %}
<section class="archive-group" id="{{ t[0] | slugify }}">
<h2>#{{ t[0] }}</h2>
<ul class="archive-list">
{%- for p in t[1] %}
<li><a href="{{ p.url | relative_url }}">{{ p.title }}</a> <time>{% include date-it.html date=p.date %}</time></li>
{%- endfor %}
</ul>
</section>
{% endfor %}
