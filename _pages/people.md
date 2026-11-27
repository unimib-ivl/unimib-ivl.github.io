---
layout: page
permalink: /people/
title: Team
nav_title: team
description: Faculty, researchers, and students of the Imaging and Vision Laboratory.
nav: true
nav_order: 3
---

<div class="lab-people-grid">
  {% assign members = site.people | sort: "order" %}
  {% for member in members %}
    <a class="lab-person-card" href="{{ member.url | relative_url }}">
      {% if member.image %}
        <div class="lab-person-portrait">
          {% include figure.liquid loading="eager" path=member.image title=member.name class="img-fluid" %}
        </div>
      {% else %}
        <div class="lab-person-placeholder" aria-hidden="true">{{ member.initials }}</div>
      {% endif %}
      <div class="lab-person-card-copy">
        <h2>{{ member.name }}</h2>
        <p>{{ member.position }}</p>
      </div>
    </a>
  {% endfor %}
</div>

{% assign past_members = site.data.past_members %}
{% if past_members and past_members.size > 0 %}

<details class="lab-former">
  <summary>
    <span class="lab-former-title">Former members</span>
    <span class="lab-former-count">{{ past_members.size }}</span>
    <span class="lab-former-icon" aria-hidden="true"></span>
  </summary>
  <div class="lab-past-members" role="list">
    {% for member in past_members %}
      <article class="lab-past-member" role="listitem">
        <h3>{{ member.name }}</h3>
        <p class="lab-past-title">{{ member.title }}</p>
        <p class="lab-past-period">{{ member.period }}</p>
      </article>
    {% endfor %}
  </div>
</details>
{% endif %}
