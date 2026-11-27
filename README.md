# Imaging and Vision Laboratory (IVL) website

Website of the Imaging and Vision Laboratory, University of Milano-Bicocca. Built with [Jekyll](https://jekyllrb.com/) on the
[al-folio](https://github.com/alshedivat/al-folio) v1 theme (MIT licence, see `LICENSE`).

## Where the content is

| Content                                     | Files                                                                                  |
| ------------------------------------------- | -------------------------------------------------------------------------------------- |
| Publications                                | `_bibliography/papers.bib` (PDFs in `wp-content/files/`, thumbnails in `assets/img/publication_preview/`) |
| People (current members)                    | `_people/*.md` (photos in `assets/img/ivl/people/`); former members in `_data/past_members.yml` |
| Funded projects (Projects page)             | `_projects/*.md` (images in `assets/img/ivl/projects/`)                               |
| Research project pages of the old website   | `_activities/*.html`, published at `/activities/<name>/`, linked from publications (`projects` field) |
| Minisites of the old website                | `minisites/` (DALib, CCIW 2024, RawFooT), static files published as they are           |
| Files and images of the old website         | `wp-content/` (same addresses as on the old website)                                   |
| Pages (home, privacy, accessibility, ...)   | `_pages/`                                                                              |
| Old addresses that moved                    | `_data/redirects.yml`                                                                  |

Large dataset files are not in this repository: they are shared from Google Drive, and their old addresses redirect there
(`_data/redirects.yml`).

## Preview on your computer

Requires Docker.

```bash
docker compose up -d        # then open http://127.0.0.1:8080/
docker compose logs -f      # build messages
docker compose down
```

Changes to content are picked up automatically; after editing `_config.yml` or `_plugins/`, run `docker compose restart`.

## Publishing

Every push to `main` builds the site and publishes it on GitHub Pages (`.github/workflows/deploy.yml`).
One-time repository settings: Settings → Pages → Build and deployment → Source: **GitHub Actions**; for the
custom domain, enter it under Settings → Pages → Custom domain and point the domain's DNS (CNAME) to `<owner>.github.io`.
