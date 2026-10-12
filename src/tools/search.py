from ddgs import DDGS
from urllib.parse import urlparse
from src.state import SearchResult
from src.config import SEARCH_RESULTS_PER_QUERY


BLOCKED_DOMAINS = {
    "merriam-webster.com", "dictionary.com", "cambridge.org",
    "vocabulary.com", "thesaurus.com", "collinsdictionary.com",
    "britannica.com", "wikipedia.org", "youtube.com", "facebook.com",
    "instagram.com", "twitter.com", "x.com", "tiktok.com",
    "pinterest.com", "vajiramandravi.com", "cogn-iq.org",
    "plato.stanford.edu", "ieeexplore.ieee.org",
}

import re

# URL patterns that are essentially never useful for research
JUNK_URL_PATTERNS = [
    r"\.well-known/",
    r"assetlinks\.json",
    r"apple-app-site-association",
    r"\.pdf$",               # often scanned/watermark noise
    r"\.(css|js|json|xml)$", # config/code files
    r"stackoverflow\.com/questions/\d+",
    r"tnurbanepay",
    r"tn\.gov\.in",
]

# Force searches inside these research-grade domains
ACADEMIC_SITES = [
    "pubmed.ncbi.nlm.nih.gov",
    "ncbi.nlm.nih.gov",
    "nature.com",
    "sciencedirect.com",
    "arxiv.org",
    "acm.org",
    "ieee.org",
    "apa.org",
    "who.int",
    "nih.gov",
]

PREFERRED_SUBSTRINGS = [
    "arxiv.org", "nature.com", "science.org", "sciencedirect.com",
    "springer.com", "wiley.com", "pubmed", "ncbi.nlm.nih.gov",
    "nih.gov", "who.int", "ieee.org", "acm.org", ".edu", ".gov",
]


def _domain_of(url: str) -> str:
    try:
        return urlparse(url).netloc.lower().replace("www.", "")
    except Exception:
        return ""

def _is_junk(url: str, title: str, snippet: str) -> bool:
    if not url or not title:
        return True
    domain = _domain_of(url)
    if any(blocked in domain for blocked in BLOCKED_DOMAINS):
        return True
    # Check URL patterns
    for pattern in JUNK_URL_PATTERNS:
        if re.search(pattern, url, re.IGNORECASE):
            return True
    path = urlparse(url).path.strip("/")
    if path == "" or path in ("index.html", "home.jsp"):
        return True
    if len(snippet.strip()) < 40:
        return True
    return False


def _score(url: str) -> int:
    domain = _domain_of(url)
    score = 0
    for preferred in PREFERRED_SUBSTRINGS:
        if preferred.startswith(".") and domain.endswith(preferred):
            score += 5
        elif preferred in domain:
            score += 5
    if len(urlparse(url).path) > 20:
        score += 2
    return score


def _raw_search(query: str, max_results: int) -> list[dict]:
    try:
        ddgs = DDGS()
        return list(ddgs.text(query, max_results=max_results))
    except Exception as e:
        print(f"Search error for '{query}': {e}")
        return []


def web_search(query: str, max_results: int = SEARCH_RESULTS_PER_QUERY) -> list[SearchResult]:
    """
    Research-tuned search:
    1. Runs general query + academic site-targeted queries
    2. Filters junk domains
    3. Ranks academic domains higher
    """
    seen = set()
    candidates: list[dict] = []

    # Build query list: raw + site-targeted academic queries
    queries = [query]
    # Pick a rotating subset of academic sites (2 per call to stay fast)
    for site in ACADEMIC_SITES[:3]:
        queries.append(f"{query} site:{site}")

    for q in queries:
        for r in _raw_search(q, max_results):
            url = r.get("href", "")
            if url and url not in seen:
                seen.add(url)
                candidates.append(r)
        # Early exit if we already have plenty
        if len(candidates) >= max_results * 5:
            break

    cleaned = [
        r for r in candidates
        if not _is_junk(r.get("href", ""), r.get("title", ""), r.get("body", ""))
    ]

    cleaned.sort(key=lambda r: _score(r.get("href", "")), reverse=True)

    return [
        SearchResult(
            title=r.get("title", ""),
            url=r.get("href", ""),
            snippet=r.get("body", ""),
        )
        for r in cleaned[:max_results]
    ]