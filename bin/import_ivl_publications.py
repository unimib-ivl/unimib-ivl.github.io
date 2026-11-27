#!/usr/bin/env python3
"""Extract the IVL WordPress publication catalog into an al-folio BibTeX file."""

from __future__ import annotations

import argparse
import concurrent.futures
import json
import re
import sys
import tempfile
import unicodedata
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote, unquote, urljoin, urlparse
from urllib.request import Request, urlopen

try:
    import requests
except ImportError:  # The standard-library downloader remains the default.
    requests = None


SOURCE_URL = "http://www.ivl.disco.unimib.it/publications/"
DEFAULT_SOURCE = Path("_bibliography/papers.bib")
LEGACY_HOST = "www.ivl.disco.unimib.it"
LEGACY_FILE_URL = f"http://{LEGACY_HOST}/wp-content/files/"
PAPER_OVERRIDES = {
    "rota2025SegFVG": "https://boa.unimib.it/bitstream/10281/574261/2/Rota%20et%20al-2025-Sci%20Data-VoR.pdf",
    "frigerio02024convergentfood": "https://boa.unimib.it/bitstream/10281/485799/1/Frigerio-2024-Helyion-VoR.pdf",
    "ciocca2024SICBIR": "https://link.springer.com/content/pdf/10.1007/s11042-023-17646-2.pdf?pdf=button",
    "enrich2023": "https://boa.unimib.it/bitstream/10281/405277/2/Marelli-2023-ISPRS%20Journal%20of%20Photogrammetry%20and%20Remote%20Sensing-VoR.pdf",
    "marelli2022sfmflow": "https://boa.unimib.it/bitstream/10281/341970/2/Marelli-2022-SoftwareX-VoR.pdf",
    "ferrari2021trends": "https://boa.unimib.it/bitstream/10281/327257/2/10281-327257_VoR.pdf",
    "ferrari2020-on-the-personalization": "https://boa.unimib.it/bitstream/10281/265204/1/08995531.pdf",
    "ciocca2020-state-recognition": "https://boa.unimib.it/bitstream/10281/262819/2/10281-262819_VoR.pdf",
    "bianconi-cnn-based2019": "https://boa.unimib.it/bitstream/10281/255370/2/bianconi_2019_access.pdf",
}
EXPECTED_CATEGORIES = {
    "Submitted": 2,
    "Patents": 9,
    "Journal Articles": 178,
    "Books, Special Issues, and Proceedings": 21,
    "Book Chapter": 13,
    "Conference Papers": 285,
    "Other Publications": 39,
}
EXPECTED_TOTAL = sum(EXPECTED_CATEGORIES.values())
FIELD_RE = re.compile(
    r"^(\s*)(author|doi|pages|url|pdf|projectref)(\s*=\s*\{)(.*?)(\})(,?)(\}?)$",
    re.IGNORECASE,
)
ANY_FIELD_RE = re.compile(r"^\s*([A-Za-z][\w-]*)\s*=", re.IGNORECASE)
KEY_RE = re.compile(r"^@\w+\s*\{\s*([^,\s]+)\s*,", re.IGNORECASE)
YEAR_RE = re.compile(r"^\s*year\s*=", re.IGNORECASE | re.MULTILINE)
PDF_RE = re.compile(r"^\s*pdf\s*=\s*\{(.*?)\}", re.IGNORECASE | re.MULTILINE)
CATEGORY_RE = re.compile(r"^% IVL category:\s*(.+?)\s*$")


def is_legacy_url(value: str) -> bool:
    return urlparse(value).netloc.lower().removeprefix("www.") == "ivl.disco.unimib.it"


def append_field(lines: list[str], field: str, value: str) -> None:
    if lines[-1].strip() == "}":
        lines.pop()
    elif lines[-1].endswith("}}"):
        lines[-1] = lines[-1][:-1]
    else:
        raise ValueError(f"cannot append {field} to an incomplete BibTeX entry")
    if not lines[-1].endswith(","):
        lines[-1] += ","
    lines.append(f" {field} = {{{value}}}}}")


class IVLPublicationsParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.category = "Uncategorized"
        self.records: list[dict[str, str]] = []
        self._heading: list[str] | None = None
        self._article_id: str | None = None
        self._article_category: str | None = None
        self._bib_div_depth = 0
        self._in_code = False
        self._bibtex: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        classes = set((attributes.get("class") or "").split())

        if tag == "h3" and "publication-group" in classes:
            self._heading = []
        elif tag == "article" and "publication" in classes:
            self._article_id = attributes.get("id")
            self._article_category = self.category
            self._bibtex = []

        if self._bib_div_depth:
            if tag == "div":
                self._bib_div_depth += 1
        elif tag == "div" and "bibtex-code" in classes and self._article_id:
            self._bib_div_depth = 1

        if tag == "code" and self._bib_div_depth:
            self._in_code = True
        elif tag == "br" and self._in_code:
            self._bibtex.append("\n")

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.handle_starttag(tag, attrs)

    def handle_endtag(self, tag: str) -> None:
        if tag == "h3" and self._heading is not None:
            self.category = "".join(self._heading).strip()
            self._heading = None
        elif tag == "code":
            self._in_code = False
        elif tag == "div" and self._bib_div_depth:
            self._bib_div_depth -= 1
        elif tag == "article" and self._article_id:
            bibtex = "".join(self._bibtex).strip()
            if bibtex:
                self.records.append(
                    {
                        "id": self._article_id,
                        "category": self._article_category or "Uncategorized",
                        "bibtex": bibtex,
                    }
                )
            self._article_id = None
            self._article_category = None
            self._bibtex = []
            self._bib_div_depth = 0
            self._in_code = False

    def handle_data(self, data: str) -> None:
        if self._heading is not None:
            self._heading.append(data)
        if self._in_code:
            self._bibtex.append(data)


def read_source(source: str) -> str:
    parsed = urlparse(source)
    if parsed.scheme in {"http", "https"}:
        request = Request(source, headers={"User-Agent": "al-folio IVL publication importer/1.0"})
        with urlopen(request, timeout=60) as response:
            charset = response.headers.get_content_charset() or "utf-8"
            return response.read().decode(charset)
    return Path(source).read_text(encoding="utf-8")


def extract_bibliography_records(bibliography: str) -> list[dict[str, str]]:
    records: list[dict[str, str]] = []
    category = "Uncategorized"
    entry: list[str] = []
    brace_depth = 0

    for line in bibliography.splitlines():
        category_match = CATEGORY_RE.match(line)
        if category_match and not entry:
            category = category_match.group(1)
            continue
        if not entry and not line.lstrip().startswith("@"):
            continue
        entry.append(line)
        brace_depth += line.count("{") - line.count("}")
        if brace_depth > 0:
            continue

        bibtex = "\n".join(entry).strip()
        key_match = KEY_RE.match(bibtex)
        if not key_match:
            raise ValueError("local bibliography contains an entry without a valid citation key")
        records.append({"id": key_match.group(1), "category": category, "bibtex": bibtex})
        entry = []
        brace_depth = 0

    if entry:
        raise ValueError("local bibliography ends with an incomplete BibTeX entry")
    return records


def canonical_doi(value: str) -> str:
    value = value.strip().lstrip("/")
    prefixes = (
        "https://doi.org/",
        "http://doi.org/",
        "https://dx.doi.org/",
        "http://dx.doi.org/",
        "http://doi.ieeecomputersociety.org/",
        "doi:",
    )
    changed = True
    while changed:
        changed = False
        lowered = value.lower()
        for prefix in prefixes:
            if lowered.startswith(prefix):
                value = value[len(prefix) :].strip().lstrip("/")
                changed = True
                break
    return value


def normalize_entry(
    entry: str,
    stats: Counter[str],
    citation_key: str,
    local_papers: dict[tuple[str, str], str],
    unavailable_papers: set[tuple[str, str]],
) -> str:
    lines = [line.rstrip() for line in entry.replace("\u00a0", " ").splitlines() if line.strip()]
    normalized: list[str] = []
    seen_fields: set[str] = set()

    for index, line in enumerate(lines):
        if ", %" in line:
            line = line.split(", %", 1)[0]
            if index == len(lines) - 1:
                line = line.rstrip(",") + "}"
            stats["inline_comments_removed"] += 1

        field_match = ANY_FIELD_RE.match(line)
        if field_match:
            field_name = field_match.group(1).lower()
            if field_name in seen_fields:
                stats["duplicate_fields_removed"] += 1
                continue
            seen_fields.add(field_name)

        match = FIELD_RE.match(line)
        if match:
            indent, field, separator, value, close, comma, entry_close = match.groups()
            original = value
            lowered_field = field.lower()
            if lowered_field == "author" and "[...]" in value:
                value = re.sub(r"\s+and\s+\[\.\.\.\],\s+and\s+", " and ", value)
                value = value.replace("[...]", "")
                stats["author_placeholders_normalized"] += 1
            elif lowered_field == "doi":
                value = canonical_doi(value)
                if value != original:
                    stats["dois_normalized"] += 1
            elif lowered_field == "pages" and re.fullmatch(r"\d+\s*[-–—]\s*\d+", value):
                value = re.sub(r"\s*[-–—]\s*", "--", value)
                if value != original:
                    stats["page_ranges_normalized"] += 1
            elif (
                lowered_field in {"url", "pdf", "projectref"}
                and value.startswith("/")
                and not value.startswith("/wp-content/files/")
            ):
                value = urljoin(SOURCE_URL, value)
                stats["relative_links_expanded"] += 1
            if lowered_field == "pdf" and (citation_key, value) in local_papers:
                value = local_papers[(citation_key, value)]
                stats["papers_localized"] += 1
            elif lowered_field == "pdf" and (citation_key, value) in unavailable_papers:
                stats["unavailable_papers_removed"] += 1
                continue
            elif lowered_field == "pdf" and is_legacy_url(value):
                stats["unavailable_legacy_papers_removed"] += 1
                continue
            elif lowered_field == "projectref" and is_legacy_url(value):
                value = Path(urlparse(value).path.rstrip("/")).name
                stats["legacy_project_links_localized"] += 1
            elif lowered_field == "url" and is_legacy_url(value):
                local_url = local_papers.get((citation_key, value))
                if local_url:
                    value = local_url
                    stats["legacy_urls_localized"] += 1
                else:
                    stats["legacy_urls_removed"] += 1
                    continue
            line = f"{indent}{field}{separator}{value}{close}{comma}{entry_close}"

        normalized.append(line)

    brace_depth = sum(line.count("{") - line.count("}") for line in normalized)
    if brace_depth == 1:
        normalized.append("}")
    elif brace_depth != 0:
        raise ValueError(f"entry {citation_key} has unbalanced braces after normalization")

    if not any(YEAR_RE.match(line) for line in normalized):
        yearfiled = next(
            (
                match.group(1)
                for line in normalized
                if (match := re.match(r"^\s*yearfiled\s*=\s*\{((?:19|20)\d{2})\}", line, re.IGNORECASE))
            ),
            None,
        )
        key_match = KEY_RE.match(normalized[0])
        key_year = re.search(r"(?:19|20)\d{2}", key_match.group(1)) if key_match else None
        year = yearfiled or (key_year.group(0) if key_year else None)
        if year:
            append_field(normalized, "year", year)
            stats["missing_years_inferred"] += 1

    if not any(re.match(r"^\s*bibtex_show\s*=", line, re.IGNORECASE) for line in normalized):
        append_field(normalized, "bibtex_show", "true")
        stats["bibtex_show_added"] += 1

    return "\n".join(normalized)


def extract_records(html: str) -> list[dict[str, str]]:
    parser = IVLPublicationsParser()
    parser.feed(html)
    parser.close()
    return parser.records


def paper_filename(url: str, citation_key: str) -> str:
    filename = unquote(Path(urlparse(url).path).name)
    if not filename.lower().endswith(".pdf"):
        filename = f"{citation_key}.pdf"
    stem = unicodedata.normalize("NFKD", Path(filename).stem).encode("ascii", "ignore").decode()
    stem = re.sub(r"[^A-Za-z0-9._-]+", "-", stem).strip("-.") or citation_key
    return f"{stem}.pdf"


def paper_candidates(url: str, citation_key: str) -> list[str]:
    overrides = [PAPER_OVERRIDES[citation_key]] if citation_key in PAPER_OVERRIDES else []
    if is_legacy_url(url) or url.startswith("/wp-content/files/"):
        migrated_url = urljoin(LEGACY_FILE_URL, quote(unquote(Path(urlparse(url).path).name)))
        return list(dict.fromkeys((*overrides, migrated_url, url)))
    mdpi_match = re.search(
        r"mdpi\.com/(2076-3417|1424-8220|2313-433X)/(\d+)/(\d+)/(\d+)",
        url,
        re.IGNORECASE,
    )
    if mdpi_match:
        journals = {"2076-3417": "applsci", "1424-8220": "sensors", "2313-433x": "jimaging"}
        issn, volume, _, article = mdpi_match.groups()
        journal = journals[issn.lower()]
        identifier = f"{journal}-{int(volume):02d}-{int(article):05d}"
        deploy_url = f"https://mdpi-res.com/d_attachment/{journal}/{identifier}/article_deploy/"
        return [*overrides, f"{deploy_url}{identifier}.pdf", f"{deploy_url}{identifier}-v2.pdf", url]
    return [*overrides, url]


def download_paper(target: Path, candidates: list[str]) -> tuple[bool, str]:
    if target.exists():
        with target.open("rb") as paper:
            if paper.read(5) == b"%PDF-":
                return True, "cached"

    last_error = "no download candidates"
    for url in candidates:
        headers = {
            "Accept": "application/pdf,application/octet-stream;q=0.9,*/*;q=0.8",
            "User-Agent": "Mozilla/5.0 (compatible; IVL publication archive/1.0)",
        }
        if is_legacy_url(url):
            headers["Referer"] = SOURCE_URL
        elif urlparse(url).netloc == "link.springer.com":
            headers["User-Agent"] = "curl/8.5.0"
        request = Request(
            url,
            headers=headers,
        )
        temporary_path: Path | None = None
        try:
            with urlopen(request, timeout=120) as response:
                with tempfile.NamedTemporaryFile("wb", dir=target.parent, delete=False) as temporary:
                    temporary_path = Path(temporary.name)
                    first_chunk = response.read(65536)
                    if not first_chunk.lstrip().startswith(b"%PDF-"):
                        raise ValueError(f"response is not a PDF ({response.headers.get_content_type()})")
                    temporary.write(first_chunk)
                    while chunk := response.read(1024 * 1024):
                        temporary.write(chunk)
            temporary_path.replace(target)
            return True, url
        except (HTTPError, URLError, OSError, TimeoutError, ValueError) as error:
            last_error = f"{url}: {error}"
            if temporary_path:
                temporary_path.unlink(missing_ok=True)
        if requests is not None:
            temporary_path = None
            try:
                with requests.get(url, headers=headers, timeout=120, stream=True) as response:
                    response.raise_for_status()
                    chunks = response.iter_content(chunk_size=1024 * 1024)
                    first_chunk = next(chunks, b"")
                    if not first_chunk.lstrip().startswith(b"%PDF-"):
                        raise ValueError(
                            f"response is not a PDF ({response.headers.get('content-type')})"
                        )
                    with tempfile.NamedTemporaryFile("wb", dir=target.parent, delete=False) as temporary:
                        temporary_path = Path(temporary.name)
                        temporary.write(first_chunk)
                        for chunk in chunks:
                            temporary.write(chunk)
                temporary_path.replace(target)
                return True, url
            except (requests.RequestException, OSError, TimeoutError, ValueError) as error:
                last_error = f"{url}: {error}"
                if temporary_path:
                    temporary_path.unlink(missing_ok=True)
    return False, last_error


def localize_papers(
    records: list[dict[str, str]],
    paper_dir: Path,
    paper_base_url: str,
    workers: int,
) -> tuple[
    dict[tuple[str, str], str],
    list[dict[str, str]],
    set[tuple[str, str]],
]:
    paper_dir.mkdir(parents=True, exist_ok=True)
    jobs: dict[str, tuple[Path, list[str], list[tuple[str, str]]]] = {}
    filenames: dict[str, str] = {}

    for record in records:
        pdf_match = PDF_RE.search(record["bibtex"])
        if not pdf_match:
            continue
        url = pdf_match.group(1).strip()
        if url.startswith("/") and not url.startswith("/wp-content/files/"):
            url = urljoin(SOURCE_URL, url)
        filename = paper_filename(url, record["id"])
        if filename in filenames and filenames[filename] != url:
            filename = f"{record['id']}-{filename}"
        filenames[filename] = url
        if url in jobs:
            jobs[url][2].append((record["id"], url))
        else:
            jobs[url] = (
                paper_dir / filename,
                paper_candidates(url, record["id"]),
                [(record["id"], url)],
            )

    localized: dict[tuple[str, str], str] = {}
    failures: list[dict[str, str]] = []
    unavailable: set[tuple[str, str]] = set()
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {
            executor.submit(download_paper, target, candidates): (url, target, aliases)
            for url, (target, candidates, aliases) in jobs.items()
        }
        for future in concurrent.futures.as_completed(futures):
            url, target, aliases = futures[future]
            success, detail = future.result()
            if success:
                local_url = f"{paper_base_url.rstrip('/')}/{quote(target.name)}"
                for key, original_url in aliases:
                    localized[(key, original_url)] = local_url
            else:
                for key, original_url in aliases:
                    unavailable.add((key, original_url))
                    failures.append({"key": key, "url": url, "error": detail})
    return localized, sorted(failures, key=lambda failure: failure["key"]), unavailable


def validate_records(records: list[dict[str, str]], enforce_counts: bool) -> dict[str, object]:
    categories = Counter(record["category"] for record in records)
    ids = [record["id"] for record in records]
    duplicate_ids = sorted(key for key, count in Counter(ids).items() if count > 1)
    if duplicate_ids:
        raise ValueError(f"duplicate HTML publication IDs: {', '.join(duplicate_ids)}")

    keys: list[str] = []
    key_id_mismatches: list[dict[str, str]] = []
    missing_year: list[str] = []
    placeholder_authors: list[str] = []
    for record in records:
        match = KEY_RE.match(record["bibtex"])
        if not match:
            raise ValueError(f"record {record['id']} does not start with a valid BibTeX entry")
        key = match.group(1)
        keys.append(key)
        if key != record["id"]:
            key_id_mismatches.append({"id": record["id"], "key": key})
        if not YEAR_RE.search(record["bibtex"]):
            missing_year.append(record["id"])
        if "[...]" in record["bibtex"]:
            placeholder_authors.append(record["id"])

    duplicate_keys = sorted(key for key, count in Counter(keys).items() if count > 1)
    if duplicate_keys:
        raise ValueError(f"duplicate BibTeX citation keys: {', '.join(duplicate_keys)}")

    if enforce_counts:
        if len(records) != EXPECTED_TOTAL:
            raise ValueError(f"expected {EXPECTED_TOTAL} records, extracted {len(records)}")
        if dict(categories) != EXPECTED_CATEGORIES:
            raise ValueError(
                "category counts changed: "
                f"expected {EXPECTED_CATEGORIES}, extracted {dict(categories)}"
            )

    return {
        "records": len(records),
        "categories": dict(categories),
        "missing_year": missing_year,
        "placeholder_authors": placeholder_authors,
        "key_id_mismatches": key_id_mismatches,
    }


def render_bibliography(
    records: list[dict[str, str]],
    stats: Counter[str],
    local_papers: dict[tuple[str, str], str],
    unavailable_papers: set[tuple[str, str]],
) -> str:
    chunks = [
        "---\n---",
        "% Generated from the IVL publication catalog by bin/import_ivl_publications.py.",
        "% DOI-backed records still require publisher/Crossref review for canonical metadata.",
    ]
    for record in records:
        entry = normalize_entry(
            record["bibtex"], stats, record["id"], local_papers, unavailable_papers
        )
        chunks.append(f"% IVL category: {record['category']}\n{entry}")
    return "\n\n".join(chunks) + "\n"


def atomic_write(path: Path, content: str, force: bool) -> None:
    if path.exists() and not force:
        raise FileExistsError(f"{path} exists; pass --force to replace it")
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", dir=path.parent, prefix=f".{path.name}.", delete=False
    ) as temporary:
        temporary.write(content)
        temporary_path = Path(temporary.name)
    temporary_path.replace(path)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source",
        default=str(DEFAULT_SOURCE),
        help="annotated BibTeX source, publications page URL, or saved HTML file",
    )
    parser.add_argument(
        "--output",
        default="_bibliography/papers.bib",
        type=Path,
        help="destination BibTeX file",
    )
    parser.add_argument("--report", type=Path, help="optional JSON extraction report")
    parser.add_argument("--force", action="store_true", help="replace an existing output file")
    parser.add_argument(
        "--allow-count-change",
        action="store_true",
        help="accept a source whose total or category counts differ from the verified snapshot",
    )
    parser.add_argument(
        "--download-papers",
        action="store_true",
        help="download PDF fields and rewrite successful links to local files",
    )
    parser.add_argument(
        "--paper-dir",
        default=Path("wp-content/files"),
        type=Path,
        help="directory for locally archived PDFs",
    )
    parser.add_argument(
        "--paper-base-url",
        default="/wp-content/files",
        help="public URL prefix for locally archived PDFs",
    )
    parser.add_argument(
        "--workers",
        default=6,
        type=int,
        help="concurrent paper downloads",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        source_content = read_source(args.source)
        records = (
            extract_bibliography_records(source_content)
            if Path(urlparse(args.source).path).suffix.lower() == ".bib"
            else extract_records(source_content)
        )
        report = validate_records(records, enforce_counts=not args.allow_count_change)
        stats: Counter[str] = Counter()
        local_papers: dict[tuple[str, str], str] = {}
        unavailable_papers: set[tuple[str, str]] = set()
        if args.download_papers:
            local_papers, failures, unavailable_papers = localize_papers(
                records, args.paper_dir, args.paper_base_url, args.workers
            )
            report["papers"] = {
                "localized": len(local_papers),
                "failed": failures,
            }
        bibliography = render_bibliography(records, stats, local_papers, unavailable_papers)
        report["source"] = args.source
        report["normalizations"] = dict(stats)
        atomic_write(args.output, bibliography, args.force)
        if args.report:
            atomic_write(args.report, json.dumps(report, indent=2, ensure_ascii=False) + "\n", args.force)
    except (OSError, UnicodeError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1

    print(json.dumps(report, indent=2, ensure_ascii=False), file=sys.stderr)
    print(f"wrote {len(records)} records to {args.output}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
