---
layout: page
title: Projects
permalink: /projects/
description: Funded research projects the laboratory takes part in.
nav: true
nav_order: 2.5
published: false # hidden for now (see ivl_show_projects in _config.yml)
---

{% comment %} One card per file in _projects/ (sorted by `order`); see _projects/onfoods.md for the fields. {% endcomment %}

<div class="ivl-project-list">
  {% assign projects = site.projects | sort: 'order' %}
  {% for project in projects %}
    <a class="ivl-project-card" href="{{ project.url | relative_url }}">
      <div class="ivl-project-card-media">
        {%- if project.img -%}
          <img src="{{ project.img | relative_url }}" alt="" loading="lazy">
        {%- else -%}
          <span class="ivl-project-card-placeholder" aria-hidden="true">{{ project.title | split: ' – ' | first }}</span>
        {%- endif -%}
      </div>
      <div class="ivl-project-card-copy">
        {% if project.period %}<p class="ivl-eyebrow">{{ project.period }}</p>{% endif %}
        {%- assign title_parts = project.title | split: ' – ' -%}
        <h2>
          {%- if title_parts.size > 1 -%}
            <span class="ivl-project-acronym">{{ title_parts.first }}</span>
            <span class="ivl-project-fullname">{{ project.title | remove_first: title_parts.first | remove_first: ' – ' }}</span>
          {%- else -%}
            {{ project.title }}
          {%- endif -%}
        </h2>
        <p>{{ project.description }}</p>
        <span class="ivl-arrow-link">View project</span>
      </div>
    </a>
  {% endfor %}
</div>
