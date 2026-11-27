---
layout: page
permalink: /how-to-reach/
title: Get in touch
nav_title: get in touch
description: Visit or contact the Imaging and Vision Laboratory.
nav: true
nav_order: 6
nav_button: true
---

<div class="ivl-contact-grid">
  <aside class="ivl-contact-card">
    <p class="ivl-eyebrow">Where we are</p>
    <h2>Milano-Bicocca</h2>
    <address>
      Imaging and Vision Laboratory<br>
      Department of Informatics, Systems and Communication<br>
      University of Milano-Bicocca<br><br>
      Viale Sarca 336, Building U14<br>
      20126 Milano, Italy
    </address>
    <p><a href="tel:+390264487840">+39 02 6448 7840</a></p>
    <ul class="ivl-contact-social">
      <li><a href="https://www.linkedin.com/company/ivlab" rel="noopener"><i class="fa-brands fa-linkedin" aria-hidden="true"></i> LinkedIn</a></li>
      <li><a href="https://github.com/unimib-ivl" rel="noopener"><i class="fa-brands fa-github" aria-hidden="true"></i> GitHub</a></li>
    </ul>
  </aside>
  <div class="ivl-contact-details">
    <p class="ivl-eyebrow">Work with us</p>
    <h2>Research, study, and collaboration</h2>
    <p>
      We welcome inquiries from prospective students, researchers, and organizations interested in computer vision, color imaging, multimodal machine learning, and intelligent sensing.
    </p>
    <p>
      For research inquiries, contact the faculty member whose work best matches your interests. For directions and departmental services, use the official DISCo information page.
    </p>
    <p><a class="ivl-pill" href="https://www.disco.unimib.it/it/dipartimento/come-raggiungerci">Official directions</a></p>
  </div>
</div>

<!-- Click-to-load map: the page shows a static screenshot of the map (assets/img/ivl/osm-u14.webp); clicking it replaces the
     screenshot with the OpenStreetMap iframe, so openstreetmap.org receives no request (and no IP address) on a normal page view (GDPR). -->
<figure class="lab-map-figure">
  <div class="lab-map" data-map-src="https://www.openstreetmap.org/export/embed.html?bbox=9.207801%2C45.518967%2C9.231511%2C45.528318&amp;layer=mapnik&amp;marker=45.523642%2C9.219656">
    <button type="button" class="lab-map__preview" data-map-load aria-label="Load the interactive map from OpenStreetMap">
      <img src="{{ '/assets/img/ivl/osm-u14.webp' | relative_url }}" alt="Map of the area around Building U14, Viale Sarca 336, Milano" width="1920" height="660" loading="lazy">
    </button>
  </div>
  <figcaption class="lab-map__note" data-map-note>
    Click the map to load the interactive version from OpenStreetMap, which will receive your IP address.
    Map data &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap contributors</a>,
    <a href="https://www.openstreetmap.org/?mlat=45.523642&amp;mlon=9.219656#map=17/45.523642/9.219656">open in OpenStreetMap</a>.
  </figcaption>
</figure>
<script>
  document.querySelectorAll("[data-map-load]").forEach((btn) =>
    btn.addEventListener("click", () => {
      const box = btn.closest(".lab-map");
      const frame = document.createElement("iframe");
      frame.title = "OpenStreetMap location of Building U14";
      frame.src = box.dataset.mapSrc;
      box.replaceChildren(frame);
      const note = box.closest("figure").querySelector("[data-map-note]");
      if (note) note.hidden = true;
    })
  );
</script>
