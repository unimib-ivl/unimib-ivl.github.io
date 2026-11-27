Self-hosted third-party files (GDPR)
====================================

Everything in this folder used to be loaded from cdn.jsdelivr.net or fonts.googleapis.com.
Loading files from those servers sends every visitor's IP address to them before any consent,
so the site serves its own copies instead (all are free/open-source licensed).

Libraries: folder names mirror the npm package paths, e.g.
    assets/vendor/masonry-layout@4.2.2/dist/masonry.pkgd.min.js
_config.yml -> third_party_libraries points at them with "/assets/vendor/<package>@{{version}}/...",
and the integrity (SRI) hashes in _config.yml still apply, because the files are byte-identical
to the CDN ones. To upgrade a library, download the new version into a new <package>@<version>
folder (same sub-paths, including the font files its CSS references), then update "version" and
"integrity" in _config.yml.

    fontawesome-free 7.2.0   css/all.min.css + webfonts/*.woff2
    academicons 1.9.5        css/academicons.min.css + fonts/*
    scholar-icons 1.0.3      css/scholar-icons.css + fonts/*
    imagesloaded 5.0.0, masonry-layout 4.2.2, vanilla-back-to-top 7.2.1
    vanilla-cookieconsent 3.1.0   dist/cookieconsent.umd.min.js (= the CDN cookieconsent.umd.js, renamed so jekyll-terser,
                                  which minifies every *.js not ending in .min.js, keeps it byte-identical); only used if enable_cookie_consent: true (Google Analytics)

Fonts: google-fonts/fonts.css + files/*.woff2 are Inter and Inter Tight (SIL Open Font License 1.1),
downloaded from the Google Fonts css2 API with a desktop Chrome user agent (woff2, all subsets;
browsers fetch only the subsets a page needs, via unicode-range).

Note: the paths start with "/" and assume baseurl is "". If the site ever moves under a sub-path
(e.g. https://<user>.github.io/ivl/), prefix them with that sub-path.
