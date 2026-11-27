# CLAUDE.md

Website of the Imaging and Vision Laboratory (IVL), University of Milano-Bicocca: an al-folio v1 Jekyll site. `README.md`
lists where each kind of content lives. al-folio v1 is a thin starter: layouts, includes and styles come from the
`al_folio_core` gem and its sibling `al_*` gems (pinned in `Gemfile`, listed again under `plugins:` in `_config.yml`). This site
overrides some of them locally (`_layouts/`, `_includes/`, recorded in `.al-folio-overrides.yml`) and adds its own styles in
`assets/css/ivl.css`.

## Commands

```bash
docker compose up -d          # preview at http://127.0.0.1:8080/ (builds into the container's /tmp/_site)
docker compose restart        # needed after editing _plugins/ (and _config.yml, whose edits stop/restart the server)
# production build, as in .github/workflows/deploy.yml:
docker compose exec -T jekyll bash -lc 'cd /srv/jekyll && JEKYLL_ENV=production bundle exec jekyll build --destination /tmp/prod_site'
```

Deployment: GitHub Pages through GitHub Actions (`.github/workflows/deploy.yml`); `url` and `baseurl` come from the Pages
settings at build time, so the site must work both at a domain root and under a sub-path (`/<repo>/`).

## Rules for this site

- Links must work under any baseurl: use `relative_url` in Liquid; in `_activities/*.html` and `minisites/` (not processed by
  Liquid) use relative links (`../../wp-content/...`), never root-relative ones (`/wp-content/...`). Self-hosted libraries
  in `third_party_libraries` keep their `/assets/vendor/...` addresses; `_plugins/ivl_baseurl_libraries.rb` prefixes them.
- No third-party requests (GDPR): fonts, icons and libraries are self-hosted in `assets/vendor/`; YouTube videos are
  click-to-load (youtube-nocookie).
- No partner or publisher logos, except the banners of funded projects that the lab asked for (OnFoods, HPC, E4S).
- Publications: no preprints unless they will stay preprints; project links are always labelled "Project Page"; never link a
  publication to a funded project's page; no zoom on thumbnails.
- `_bibliography/papers.bib`: the `projects` field holds tags matched by `publication_tag` of `_activities/*.html`
  (query pattern `@*[projects~=(?:^|\s)TAG(?!-)\b]`; bibtex-ruby queries cannot contain lookbehinds or `<`, `=`).
- Old addresses that moved go in `_data/redirects.yml` only: `_plugins/ivl_redirects.rb` makes redirect pages (addresses
  ending in `/`) and Netlify's `_redirects`; `_pages/404.md` redirects file addresses on GitHub Pages.
- Images: WebP or compressed JPEG, at most 1600 px, metadata stripped. Files over 50 MB do not go in the repository
  (GitHub limit 100 MB per file, about 1 GB per site): upload them to Google Drive and add a redirect.
- Plans are written as .md files and implemented only when asked.
