---
title: "Contatti"
zh: "联系我"
subtitle: "Per informazioni, preventivi e proposte di collaborazione potete contattarmi tramite il seguente modulo."
permalink: /contatti/
tone: "red"
cta: false
wide: true
image:
  path: "/assets/images/social/page-contatti.png"
  width: 1200
  height: 630
---
{%- assign cf = site.contact_form -%}
{%- if cf.service == "formspree" -%}
  {%- assign form_action = "https://formspree.io/f/" | append: cf.endpoint -%}
  {%- assign allegati = false -%}
{%- else -%}
  {%- assign form_action = "https://formsubmit.co/" | append: cf.endpoint -%}
  {%- assign allegati = true -%}
{%- endif %}
<div class="contact-grid">
<div class="contact-form-card">
{% if cf.endpoint and cf.endpoint != "" %}
<form class="form" id="contact-form" action="{{ form_action }}" method="POST"{% if allegati %} enctype="multipart/form-data"{% endif %}>
  <div class="form-row">
    <label>Nome e cognome *<input type="text" name="nome" autocomplete="name" required></label>
    <label>Email *<input type="email" name="email" autocomplete="email" required></label>
  </div>
  <div class="form-row">
    <label>Tipo di richiesta
      <select name="servizio" id="cf-servizio">
        <option value="Informazioni">Informazioni generali</option>
        <option value="Lezioni">Lezioni private e corsi</option>
        <option value="Traduzione">Traduzione e localizzazione</option>
        <option value="Mediazione">Mediazione linguistica e culturale</option>
        <option value="Consulenza">Consulenza per l'impresa</option>
        <option value="Collaborazione">Proposta di collaborazione</option>
      </select>
    </label>
    <label>Oggetto<input type="text" name="oggetto" id="cf-oggetto" placeholder="Es. richiesta preventivo"></label>
  </div>
  <label>Messaggio *<textarea name="messaggio" rows="7" required></textarea></label>
  {%- if allegati %}
  <label>Documento da tradurre (facoltativo)
    <input type="file" name="attachment" accept=".pdf,.doc,.docx,.odt,.rtf,.txt">
    <span class="form-hint">Word, OpenOffice, testo o PDF. Per file molto grandi scrivimi prima: ti indicherò come inviarli.</span>
  </label>
  {%- endif %}
  <label class="form-check"><input type="checkbox" name="privacy" value="accettata" required>
    <span>Ho letto l'<a href="{{ '/cookie-law/' | relative_url }}">informativa privacy</a> e acconsento all'uso dei miei dati per ricevere una risposta. *</span>
  </label>

  {%- comment -%} campi tecnici del servizio di invio {%- endcomment -%}
  <input type="hidden" name="_subject" id="cf-subject" value="[SITO] Nuovo messaggio dal sito">
  {%- if cf.service == "formspree" %}
  <input type="text" name="_gotcha" class="hp" tabindex="-1" autocomplete="off" aria-hidden="true">
  {%- else %}
  <input type="hidden" name="_next" value="{{ '/contatti/grazie/' | absolute_url }}">
  <input type="hidden" name="_captcha" value="false">
  <input type="hidden" name="_template" value="table">
  <input type="text" name="_honey" class="hp" tabindex="-1" autocomplete="off" aria-hidden="true">
  {%- endif %}

  <p class="form-note">* campi obbligatori</p>
  <button type="submit" class="btn btn-primary">Invia il messaggio {% include icon.html name="arrow" %}</button>
</form>
<script>
  // Compone l'oggetto della mail come sul vecchio sito: "[Servizio] oggetto"
  document.getElementById("contact-form").addEventListener("submit", function () {
    var s = document.getElementById("cf-servizio").value;
    var o = document.getElementById("cf-oggetto").value.trim();
    document.getElementById("cf-subject").value = "[SITO] [" + s + "] " + (o || "Nuovo messaggio dal sito");
  });
</script>
{% else %}
<div class="notice">Modulo di contatto non ancora attivo: impostare <code>contact_form.endpoint</code> in <code>_config.yml</code>.
Nel frattempo puoi scrivermi sui social.</div>
{% endif %}
</div>
<aside class="contact-side">
  <h2>Qualche consiglio</h2>
  <ul class="tips">
    <li>Scegli il <strong>tipo di richiesta</strong>: mi aiuta a risponderti più in fretta.</li>
    <li>Per un <strong>preventivo di traduzione</strong> allega il documento (Word, OpenOffice, testo o PDF) e indica la scadenza.</li>
    <li>Per <strong>lezioni e corsi</strong> scrivi il tuo livello di partenza e gli obiettivi (HSK, viaggio, lavoro…).</li>
  </ul>
  <h2>Servizi</h2>
  <ul class="tips">
    {%- for sv in site.data.servizi %}{% if sv.url %}
    <li><a href="{{ sv.url | relative_url }}">{{ sv.titolo }}</a></li>{% endif %}
    {%- endfor %}
  </ul>
  <h2>Social</h2>
  <ul class="social-list">
    {%- for s in site.social_links %}
    <li><a href="{{ s.url }}" target="_blank" rel="noopener">{% include icon.html name=s.icon %} {{ s.name }}</a></li>
    {%- endfor %}
  </ul>
</aside>
</div>
