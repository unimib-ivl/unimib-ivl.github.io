---
layout: page
title: News
permalink: /news/
description: Updates, awards, events, and research from IVL.
nav: true
nav_order: 4
published: false # hidden for now (changes v1)
---

{% include lab_styles.liquid %}

<div class="ivl-news-list">
  {% assign news_items = site.news | sort: 'date' | reverse %}
  {% for item in news_items %}
    <a class="ivl-news-row" href="{{ item.url | relative_url }}">
      <span class="ivl-news-row-media{% unless item.image %} ivl-news-row-media--fallback{% endunless %}" aria-hidden="true">
        {% if item.image %}
          <img src="{{ item.image | relative_url }}" alt="">
        {% else %}
          <span class="ivl-news-fallback-mark">
            <img src="{{ '/assets/img/ivl/ivl-icon.svg' | relative_url }}" alt="">
            <span>IVL update</span>
          </span>
        {% endif %}
      </span>
      <span>
        <h2>{{ item.title }}</h2>
        <time datetime="{{ item.date | date_to_xmlschema }}">{{ item.date | date: '%B %d, %Y' }}</time>
      </span>
      <span aria-hidden="true">&rarr;</span>
    </a>
  {% endfor %}
</div>
