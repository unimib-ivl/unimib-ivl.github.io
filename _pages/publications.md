---
layout: page
permalink: /publications/
title: Publications
description: Research output of the Imaging and Vision Laboratory, in reverse chronological order.
nav: true
nav_order: 2
---

<!-- _pages/publications.md -->

<script>
  /*
   * Keep the unfiltered list from flashing before publication-filters.js runs, without delaying first paint:
   *  - no URL filters: show the list right away (pagination only trims entries below the fold);
   *  - only ?area= / ?topic= (homepage links): pre-filter with CSS while the page is still loading;
   *  - any other URL filter: hide the list until the script is ready (4 s fallback).
   * publication-filters.js removes both the #pub-prefilter style and the pub-js-pending class once it has rendered.
   */
  (function () {
    var params = new URLSearchParams(window.location.search);
    var keys = Array.from(params.keys());
    if (keys.length === 0) return;
    var list = function (key) {
      return (params.get(key) || "")
        .split(",")
        .map(function (value) {
          return value.trim();
        })
        .filter(Boolean);
    };
    var areas = list("area");
    var topics = list("topic");
    var researchOnly = keys.every(function (key) {
      return key === "area" || key === "topic";
    });
    var safe = areas.concat(topics).every(function (slug) {
      return /^[a-z0-9-]+$/.test(slug);
    });
    if (researchOnly && safe && areas.length + topics.length > 0 && window.CSS && CSS.supports("selector(:has(a))")) {
      var match = areas
        .map(function (slug) {
          return '.pub-entry[data-areas~="' + slug + '"]';
        })
        .concat(
          topics.map(function (slug) {
            return '.pub-entry[data-topics~="' + slug + '"]';
          })
        )
        .join(",");
      var style = document.createElement("style");
      style.id = "pub-prefilter";
      style.textContent =
        "[data-pub-list] ol.bibliography > li:not(:has(" +
        match +
        ")),[data-pub-list] h2.bibliography:has(+ ol.bibliography:not(:has(" +
        match +
        "))){display:none}";
      document.head.appendChild(style);
      return;
    }
    document.documentElement.classList.add("pub-js-pending");
    setTimeout(function () {
      document.documentElement.classList.remove("pub-js-pending");
    }, 4000);
  })();
</script>

<div class="pub-toolbar">
  <div class="pub-search">
    <i class="fa-solid fa-magnifying-glass" aria-hidden="true"></i>
    <input
      type="search"
      id="pub-search"
      data-pub-search
      placeholder="Search by title, author, or venue"
      autocomplete="off"
      spellcheck="false"
      aria-label="Search publications"
    >
    <button type="button" class="pub-search-clear" data-pub-search-clear aria-label="Clear search" hidden>
      <i class="fa-solid fa-xmark" aria-hidden="true"></i>
    </button>
  </div>

  <button class="pub-filter-toggle" type="button" aria-expanded="false" aria-controls="pub-filters" data-pub-filter-toggle>
    <i class="fa-solid fa-sliders" aria-hidden="true"></i>
    <span>Filters</span>
    <span class="pub-filter-count" data-pub-filter-count hidden></span>
  </button>
</div>

<div id="pub-filters" class="pub-filters" aria-label="Publication filters" hidden>
  <div class="pub-ms" data-pub-ms="research" data-all-label="All research areas" data-plural="">
    <span class="pub-ms-label" id="pub-ms-research-label">Research area</span>
    <button type="button" class="pub-ms-button" aria-haspopup="true" aria-expanded="false" aria-labelledby="pub-ms-research-label pub-ms-research-summary">
      <span id="pub-ms-research-summary" data-pub-ms-summary>All research areas</span>
    </button>
    <div class="pub-ms-menu pub-ms-menu--wide" role="group" aria-labelledby="pub-ms-research-label" hidden>
      <button type="button" class="pub-ms-all" data-pub-ms-clear>All research areas</button>
      {% for area in site.data.research_areas %}
        <div class="pub-ms-area" role="group" aria-label="{{ area.title }}">
          <label class="pub-ms-option pub-ms-option--strong"><input type="checkbox" value="area:{{ area.slug }}" data-pub-area="{{ area.slug }}"><span>{{ area.title }}</span></label>
          <div class="pub-ms-children">
            {% for topic in area.topics %}
              <label class="pub-ms-option"{% if topic.full %} title="{{ topic.full }}"{% endif %}><input type="checkbox" value="{{ topic.slug }}" data-pub-parent="{{ area.slug }}"><span>{{ topic.name }}</span></label>
            {% endfor %}
          </div>
        </div>
      {% endfor %}
    </div>
  </div>

  <div class="pub-ms" data-pub-ms="author" data-all-label="All authors" data-plural="authors">
    <span class="pub-ms-label" id="pub-ms-author-label">Author</span>
    <button type="button" class="pub-ms-button" aria-haspopup="true" aria-expanded="false" aria-labelledby="pub-ms-author-label pub-ms-author-summary">
      <span id="pub-ms-author-summary" data-pub-ms-summary>All authors</span>
    </button>
    <div class="pub-ms-menu" role="group" aria-labelledby="pub-ms-author-label" hidden>
      <button type="button" class="pub-ms-all" data-pub-ms-clear>All authors</button>
      <label class="pub-ms-option pub-ms-option--strong"><input type="checkbox" value="members" data-pub-ms-members><span>Current members</span></label>
      <p class="pub-ms-group">Select members</p>
      {% assign lab_members = site.people | sort: 'name' %}
      {% for member in lab_members %}
        {% assign m_parts = member.name | remove_accents | downcase | split: ' ' %}
        <label class="pub-ms-option"><input type="checkbox" value="{{ m_parts.last }} {{ m_parts.first | slice: 0 }}" data-current><span>{{ member.name }}</span></label>
      {% endfor %}
    </div>
  </div>

  <div class="pub-ms" data-pub-ms="type" data-all-label="All types" data-plural="types">
    <span class="pub-ms-label" id="pub-ms-type-label">Type</span>
    <button type="button" class="pub-ms-button" aria-haspopup="true" aria-expanded="false" aria-labelledby="pub-ms-type-label pub-ms-type-summary">
      <span id="pub-ms-type-summary" data-pub-ms-summary>All types</span>
    </button>
    <div class="pub-ms-menu" role="group" aria-labelledby="pub-ms-type-label" hidden>
      <button type="button" class="pub-ms-all" data-pub-ms-clear>All types</button>
      <label class="pub-ms-option"><input type="checkbox" value="journal"><span>Journal articles</span></label>
      <label class="pub-ms-option"><input type="checkbox" value="conference"><span>Conference papers</span></label>
      <label class="pub-ms-option"><input type="checkbox" value="book"><span>Books and chapters</span></label>
      <label class="pub-ms-option"><input type="checkbox" value="patent"><span>Patents</span></label>
      <label class="pub-ms-option"><input type="checkbox" value="preprint"><span>Preprints</span></label>
      <label class="pub-ms-option"><input type="checkbox" value="other"><span>Other</span></label>
    </div>
  </div>

  <div class="pub-year-range" data-pub-year-range>
    <span>Year <output data-pub-year-output>all years</output></span>
    <div class="pub-range-slider">
      <input type="range" data-pub-year-min min="1900" max="2100" value="1900" aria-label="From year">
      <input type="range" data-pub-year-max min="1900" max="2100" value="2100" aria-label="To year">
    </div>
  </div>

<button type="button" class="pub-reset" data-pub-reset>Reset filters</button>

</div>

<div class="pub-active" data-pub-active aria-label="Active filters"></div>
<p class="pub-status" data-pub-status aria-live="polite"></p>

{% include pub-fallback-sprite.svg %}
<div class="publications" data-pub-list data-page-size="20">

{% bibliography %}

</div>

<p class="pub-empty" data-pub-empty hidden>No publications match the current filters.</p>

<div class="pub-more">
  <button type="button" class="ivl-pill ivl-pill--outline" data-pub-more hidden>Show more</button>
</div>

<script defer src="{{ '/assets/js/publication-filters.js' | relative_url | bust_file_cache }}"></script>
