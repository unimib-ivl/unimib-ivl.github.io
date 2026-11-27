/*
 * IVL publication list: search, filters, URL state, and "show more" pagination.
 *
 * Works in two modes:
 *  - Full mode (publications page): toolbar + filter panel present.
 *  - List-only mode (member pages): only pagination over [data-pub-list].
 *
 * Filters are multi-select: values inside one filter are OR-ed, filters are AND-ed.
 * Research areas and topics share one dropdown: selecting an area selects all its topics.
 * Every entry rendered by _layouts/bib.liquid carries:
 *   data-year, data-type, data-areas, data-topics, data-authors ("last f;last f")
 */
(function () {
  "use strict";

  // The publications page's inline guard either pre-filters entries with CSS
  // (#pub-prefilter) or hides the list ("pub-js-pending") until filters and
  // pagination have been applied here; hand control back to this script.
  const ready = () => {
    document.documentElement.classList.remove("pub-js-pending");
    const prefilter = document.getElementById("pub-prefilter");
    if (prefilter) prefilter.remove();
  };

  // BibTeX blocks are rendered as plain text (see _layouts/bib.liquid); colour
  // one the first time its "BibTeX" button is used, using the Pygments token
  // classes the site's highlight theme already styles.
  const escapeHtml = (value) => value.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
  const highlightBibtex = (code) => {
    if (code.dataset.highlighted) return;
    code.dataset.highlighted = "true";
    code.innerHTML = code.textContent
      .split("\n")
      .map((line) => {
        let match = line.match(/^(@[\w-]+)(\{)([^,]*)(,?)\s*$/);
        if (match) {
          return `<span class="nc">${escapeHtml(match[1])}</span><span class="p">{</span><span class="nl">${escapeHtml(match[3])}</span><span class="p">${match[4]}</span>`;
        }
        match = line.match(/^(\s*)([\w-]+)(\s*)(=)(\s*)(.*?)(,?)\s*$/);
        if (match) {
          return `${match[1]}<span class="na">${escapeHtml(match[2])}</span>${match[3]}<span class="p">=</span>${match[5]}<span class="s">${escapeHtml(match[6])}</span><span class="p">${match[7]}</span>`;
        }
        return line.trim() === "}" ? `<span class="p">}</span>` : escapeHtml(line);
      })
      .join("\n");
  };
  document.addEventListener("click", (event) => {
    const trigger = event.target.closest("a.bibtex");
    if (!trigger) return;
    const body = trigger.closest(".pub-body");
    const code = body && body.querySelector("[data-pub-bibtex]");
    if (code) highlightBibtex(code);
  });

  const lists = Array.from(document.querySelectorAll("[data-pub-list]"));
  if (lists.length === 0) {
    ready();
    return;
  }

  const normalize = (value) => (value || "").normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase().replace(/\s+/g, " ").trim();

  const TYPE_GROUPS = {
    article: "journal",
    inproceedings: "conference",
    conference: "conference",
    proceedings: "conference",
    book: "book",
    inbook: "book",
    incollection: "book",
    patent: "patent",
    preprint: "preprint", // set by _layouts/bib.liquid for unpublished / arXiv entries
  };

  const buildEntries = (list) =>
    Array.from(list.querySelectorAll("ol.bibliography > li")).map((li) => {
      const node = li.querySelector(".pub-entry");
      const data = node ? node.dataset : {};
      const text = ["title", "author", "periodical"]
        .map((cls) => {
          const el = li.querySelector(`.pub-body > .${cls}`);
          return el ? el.textContent : "";
        })
        .join(" ");
      const moreAuthors = Array.from(li.querySelectorAll(".more-authors"))
        .map((el) => el.dataset.more || "")
        .join(" ");
      return {
        li,
        group: li.parentElement,
        heading: li.parentElement ? li.parentElement.previousElementSibling : null,
        year: Number(data.year) || null,
        type: TYPE_GROUPS[(data.type || "").toLowerCase()] || "other",
        areas: (data.areas || "").split(/\s+/).filter(Boolean),
        topics: (data.topics || "").split(/\s+/).filter(Boolean),
        authors: (data.authors || "").split(";").map(normalize).filter(Boolean),
        text: normalize(`${text} ${moreAuthors} ${data.topics || ""}`.replace(/-/g, " ")),
      };
    });

  const render = (list, entries, matches, pageSize, shown, controls) => {
    let visibleCount = 0;
    const matching = entries.filter(matches);
    entries.forEach((entry) => {
      entry.li.hidden = true;
    });
    matching.forEach((entry, index) => {
      const visible = index < shown;
      entry.li.hidden = !visible;
      if (visible) visibleCount += 1;
    });

    // Hide year headings / groups without visible entries.
    const groups = new Set(entries.map((entry) => entry.group));
    groups.forEach((group) => {
      if (!group) return;
      const hasVisible = Array.from(group.children).some((li) => !li.hidden);
      group.hidden = !hasVisible;
      const heading = group.previousElementSibling;
      if (heading && heading.matches("h2.bibliography")) heading.hidden = !hasVisible;
    });

    if (controls.more) {
      const remaining = matching.length - visibleCount;
      controls.more.hidden = remaining <= 0;
      controls.more.textContent = remaining > 0 ? `Show more (${remaining} remaining)` : "Show more";
    }
    if (controls.status) {
      controls.status.textContent =
        matching.length === entries.length
          ? `Showing ${visibleCount} of ${entries.length} publications`
          : `Showing ${visibleCount} of ${matching.length} matching publications (out of ${entries.length})`;
    }
    if (controls.empty) controls.empty.hidden = matching.length !== 0;
    return matching.length;
  };

  // ---------------------------------------------------------------------------
  // List-only mode (member pages and any secondary list)
  // ---------------------------------------------------------------------------
  const fullList = document.querySelector("[data-pub-search]") ? lists[0] : null;

  lists
    .filter((list) => list !== fullList)
    .forEach((list) => {
      const entries = buildEntries(list);
      const pageSize = Number(list.dataset.pageSize) || 10;
      if (entries.length <= pageSize) return;
      let shown = pageSize;
      const wrapper = document.createElement("div");
      wrapper.className = "pub-more";
      const more = document.createElement("button");
      more.type = "button";
      more.className = "ivl-pill ivl-pill--outline";
      wrapper.appendChild(more);
      list.after(wrapper);
      const controls = { more };
      const update = () => render(list, entries, () => true, pageSize, shown, controls);
      more.addEventListener("click", () => {
        shown += pageSize;
        update();
      });
      update();
    });

  if (!fullList) {
    ready();
    return;
  }

  // ---------------------------------------------------------------------------
  // Full mode (publications page)
  // Multi-select filters: values inside one filter are OR-ed, filters are AND-ed.
  // ---------------------------------------------------------------------------
  const $ = (selector) => document.querySelector(selector);
  const controls = {
    search: $("[data-pub-search]"),
    clear: $("[data-pub-search-clear]"),
    toggle: $("[data-pub-filter-toggle]"),
    count: $("[data-pub-filter-count]"),
    panel: $("#pub-filters"),
    minYear: $("[data-pub-year-min]"),
    maxYear: $("[data-pub-year-max]"),
    yearOutput: $("[data-pub-year-output]"),
    reset: $("[data-pub-reset]"),
    active: $("[data-pub-active]"),
    status: $("[data-pub-status]"),
    empty: $("[data-pub-empty]"),
    more: $("[data-pub-more]"),
  };

  // Multi-select dropdowns ([data-pub-ms="research|author|type"])
  const multi = {};
  document.querySelectorAll("[data-pub-ms]").forEach((root) => {
    const name = root.dataset.pubMs;
    const button = root.querySelector(".pub-ms-button");
    const menu = root.querySelector(".pub-ms-menu");
    const boxes = Array.from(menu.querySelectorAll('input[type="checkbox"]'));
    multi[name] = {
      root,
      button,
      menu,
      boxes,
      summary: root.querySelector("[data-pub-ms-summary]"),
      clearButton: menu.querySelector("[data-pub-ms-clear]"),
      values: () => boxes.filter((box) => box.checked).map((box) => box.value),
      labelOf: (value) => {
        const box = boxes.find((item) => item.value === value);
        return box ? box.nextElementSibling.textContent.trim() : value;
      },
      set: (values) => {
        boxes.forEach((box) => {
          box.checked = values.includes(box.value);
        });
      },
      remove: (value) => {
        const box = boxes.find((item) => item.value === value);
        if (box) box.checked = false;
      },
    };
  });

  // Research filter: each area checkbox owns its topic checkboxes. Checking an
  // area checks all its topics; the area box mirrors its topics (checked when all
  // are, indeterminate when some are). The active selection is reported as
  // "area:<slug>" for fully selected areas plus loose topic slugs otherwise.
  const research = multi.research;
  const areaBoxes = research.boxes.filter((box) => box.dataset.pubArea);
  const topicsOf = (areaBox) => research.boxes.filter((box) => box.dataset.pubParent === areaBox.dataset.pubArea);
  const parentOf = (topicBox) => areaBoxes.find((box) => box.dataset.pubArea === topicBox.dataset.pubParent);
  const syncAreas = () => {
    areaBoxes.forEach((areaBox) => {
      const topics = topicsOf(areaBox);
      const checked = topics.filter((box) => box.checked).length;
      if (topics.length === 0) {
        areaBox.indeterminate = false;
        return;
      }
      areaBox.checked = checked === topics.length;
      areaBox.indeterminate = checked > 0 && checked < topics.length;
    });
  };
  research.values = () =>
    research.boxes
      .filter((box) => box.checked)
      .filter((box) => !box.dataset.pubParent || !parentOf(box) || !parentOf(box).checked)
      .map((box) => box.value);
  research.set = (values) => {
    research.boxes.forEach((box) => {
      box.checked = values.includes(box.value);
    });
    areaBoxes.forEach((areaBox) => {
      if (areaBox.checked) topicsOf(areaBox).forEach((box) => (box.checked = true));
    });
    syncAreas();
  };
  research.remove = (value) => {
    const box = research.boxes.find((item) => item.value === value);
    if (!box) return;
    box.checked = false;
    if (box.dataset.pubArea) topicsOf(box).forEach((topic) => (topic.checked = false));
    syncAreas();
  };

  const closeMenus = (except) => {
    Object.values(multi).forEach((ms) => {
      if (ms === except) return;
      ms.menu.hidden = true;
      ms.button.setAttribute("aria-expanded", "false");
    });
  };

  const entries = buildEntries(fullList);
  const pageSize = Number(fullList.dataset.pageSize) || 20;
  let shown = pageSize;

  const currentMemberKeys = new Set(multi.author.boxes.filter((box) => box.hasAttribute("data-current")).map((box) => normalize(box.value)));

  const years = entries.map((entry) => entry.year).filter(Boolean);
  const minYear = Math.min(...years);
  const maxYear = Math.max(...years);
  [controls.minYear, controls.maxYear].forEach((input) => {
    input.min = String(minYear);
    input.max = String(maxYear);
  });
  controls.minYear.value = String(minYear);
  controls.maxYear.value = String(maxYear);

  const state = () => {
    const authorValues = multi.author.values();
    return {
      q: normalize(controls.search.value),
      areas: multi.research
        .values()
        .filter((value) => value.startsWith("area:"))
        .map((value) => value.slice(5)),
      topics: multi.research.values().filter((value) => !value.startsWith("area:")),
      types: multi.type.values(),
      members: authorValues.includes("members"),
      authors: authorValues.filter((value) => value !== "members").map(normalize),
      from: Number(controls.minYear.value),
      to: Number(controls.maxYear.value),
    };
  };

  const matches = (s) => (entry) => {
    if (s.q && !s.q.split(" ").every((term) => entry.text.includes(term))) return false;
    if (s.areas.length || s.topics.length) {
      const byArea = s.areas.some((area) => entry.areas.includes(area));
      const byTopic = s.topics.some((topic) => entry.topics.includes(topic));
      if (!byArea && !byTopic) return false;
    }
    if (s.types.length && !s.types.includes(entry.type)) return false;
    if (s.members || s.authors.length) {
      const byMember = s.members && entry.authors.some((key) => currentMemberKeys.has(key));
      const bySelected = s.authors.some((key) => entry.authors.includes(key));
      if (!byMember && !bySelected) return false;
    }
    if (entry.year && (entry.year < s.from || entry.year > s.to)) return false;
    return true;
  };

  const syncUrl = (s) => {
    const params = new URLSearchParams();
    if (controls.search.value.trim()) params.set("q", controls.search.value.trim());
    if (s.members) params.set("members", "current");
    if (s.areas.length) params.set("area", s.areas.join(","));
    if (s.topics.length) params.set("topic", s.topics.join(","));
    const authors = multi.author.values().filter((value) => value !== "members");
    if (authors.length) params.set("author", authors.join(","));
    if (s.types.length) params.set("type", s.types.join(","));
    if (s.from !== minYear) params.set("from", String(s.from));
    if (s.to !== maxYear) params.set("to", String(s.to));
    const query = params.toString();
    const url = `${window.location.pathname}${query ? `?${query}` : ""}${window.location.hash}`;
    window.history.replaceState(null, "", url);
  };

  const renderSummaries = () => {
    Object.values(multi).forEach((ms) => {
      const values = ms.values();
      const allLabel = ms.root.dataset.allLabel;
      ms.summary.textContent =
        values.length === 0
          ? allLabel
          : values.length === 1
            ? ms.labelOf(values[0])
            : `${values.length}${ms.root.dataset.plural ? ` ${ms.root.dataset.plural}` : ""} selected`;
      ms.button.classList.toggle("is-active", values.length > 0);
      ms.clearButton.classList.toggle("is-current", values.length === 0);
    });
  };

  const renderActive = (s) => {
    const chips = [];
    ["research", "author", "type"].forEach((name) => {
      const ms = multi[name];
      ms.values().forEach((value) => {
        chips.push({
          label: ms.labelOf(value),
          panel: true,
          clear: () => ms.remove(value),
        });
      });
    });
    if (s.from !== minYear || s.to !== maxYear) {
      chips.push({
        label: `${s.from}–${s.to}`,
        panel: true,
        clear: () => {
          controls.minYear.value = String(minYear);
          controls.maxYear.value = String(maxYear);
        },
      });
    }

    controls.active.replaceChildren(
      ...chips.map((chip) => {
        const button = document.createElement("button");
        button.type = "button";
        button.className = "pub-chip";
        button.innerHTML = `<span></span><i class="fa-solid fa-xmark" aria-hidden="true"></i>`;
        button.querySelector("span").textContent = chip.label;
        button.setAttribute("aria-label", `Remove filter: ${chip.label}`);
        button.addEventListener("click", () => {
          chip.clear();
          update({ resetPage: true });
        });
        return button;
      })
    );
    controls.active.hidden = chips.length === 0;

    controls.count.hidden = chips.length === 0;
    controls.count.textContent = String(chips.length);
  };

  const update = ({ resetPage = false } = {}) => {
    if (resetPage) shown = pageSize;
    // Keep the year range ordered.
    if (Number(controls.minYear.value) > Number(controls.maxYear.value)) {
      if (document.activeElement === controls.minYear) controls.maxYear.value = controls.minYear.value;
      else controls.minYear.value = controls.maxYear.value;
    }
    const s = state();
    controls.yearOutput.textContent = s.from === minYear && s.to === maxYear ? "all years" : `${s.from}–${s.to}`;
    controls.clear.hidden = controls.search.value.length === 0;
    render(fullList, entries, matches(s), pageSize, shown, controls);
    renderSummaries();
    renderActive(s);
    syncUrl(s);
  };

  // Restore state from the URL (?area=color,vim&topic=color-constancy&members=current ...)
  const params = new URLSearchParams(window.location.search);
  const listParam = (key) =>
    (params.get(key) || "")
      .split(",")
      .map((value) => value.trim())
      .filter(Boolean);
  if (params.get("q")) controls.search.value = params.get("q");
  multi.research.set([...listParam("area").map((slug) => `area:${slug}`), ...listParam("topic")]);
  multi.type.set(listParam("type"));
  multi.author.set([...listParam("author").map(normalize), ...(params.get("members") === "current" ? ["members"] : [])]);
  const fromParam = Number(params.get("from"));
  const toParam = Number(params.get("to"));
  if (fromParam >= minYear && fromParam <= maxYear) controls.minYear.value = String(fromParam);
  if (toParam >= minYear && toParam <= maxYear) controls.maxYear.value = String(toParam);

  // Events
  let searchTimer = null;
  controls.search.addEventListener("input", () => {
    controls.clear.hidden = controls.search.value.length === 0;
    window.clearTimeout(searchTimer);
    searchTimer = window.setTimeout(() => update({ resetPage: true }), 120);
  });
  controls.search.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && controls.search.value) {
      event.preventDefault();
      controls.search.value = "";
      update({ resetPage: true });
    }
  });
  controls.clear.addEventListener("click", () => {
    controls.search.value = "";
    controls.search.focus();
    update({ resetPage: true });
  });

  Object.values(multi).forEach((ms) => {
    ms.button.addEventListener("click", () => {
      const open = ms.menu.hidden;
      closeMenus(ms);
      ms.menu.hidden = !open;
      ms.button.setAttribute("aria-expanded", String(open));
    });
    ms.boxes.forEach((box) =>
      box.addEventListener("change", () => {
        // Area <-> topic cascade in the research filter.
        if (ms === research) {
          if (box.dataset.pubArea) topicsOf(box).forEach((topic) => (topic.checked = box.checked));
          syncAreas();
        }
        // "Current members" and individual members are mutually exclusive.
        if (ms === multi.author && box.checked) {
          const isGroup = box.value === "members";
          ms.boxes.forEach((other) => {
            if (other !== box && (isGroup || other.value === "members")) other.checked = false;
          });
        }
        update({ resetPage: true });
      })
    );
    ms.clearButton.addEventListener("click", () => {
      ms.set([]);
      update({ resetPage: true });
    });
  });
  document.addEventListener("click", (event) => {
    if (!event.target.closest("[data-pub-ms]")) closeMenus();
  });
  document.addEventListener("keydown", (event) => {
    if (event.key !== "Escape") return;
    const open = Object.values(multi).find((ms) => !ms.menu.hidden);
    if (open) {
      closeMenus();
      open.button.focus();
    }
  });

  [controls.minYear, controls.maxYear].forEach((control) => {
    control.addEventListener("input", () => update({ resetPage: true }));
  });
  controls.reset.addEventListener("click", () => {
    controls.search.value = "";
    Object.values(multi).forEach((ms) => ms.set([]));
    controls.minYear.value = String(minYear);
    controls.maxYear.value = String(maxYear);
    update({ resetPage: true });
  });
  controls.toggle.addEventListener("click", () => {
    const expanded = controls.toggle.getAttribute("aria-expanded") === "true";
    controls.toggle.setAttribute("aria-expanded", String(!expanded));
    controls.panel.hidden = expanded;
    if (expanded) closeMenus();
  });
  controls.more.addEventListener("click", () => {
    shown += pageSize;
    update();
  });

  update();
  ready();
})();
