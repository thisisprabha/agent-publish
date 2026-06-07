"""Smart Tag Suggestion -- extract / suggest tags from markdown content.

When `--tags` is passed, this module:
  1. Attempts keyword extraction from headings, bold text, and capitalized phrases.
  2. Falls back to LLM-based tagging if an API key is available.
  3. Returns a deduplicated, ranked list of 3-8 tags.
"""

import os
import re
import json
import urllib.request
from collections import Counter
from typing import List, Optional


# Common English stop words to filter out
_STOP_WORDS = frozenset({
    "the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
    "have", "has", "had", "do", "does", "did", "will", "would", "could",
    "should", "may", "might", "must", "shall", "can", "need", "dare",
    "ought", "used", "it", "this", "that", "these", "those", "i", "you",
    "he", "she", "we", "they", "me", "him", "her", "us", "them",
    "my", "your", "his", "her", "its", "our", "their", "mine", "yours",
    "of", "in", "to", "for", "with", "on", "at", "by", "from", "as",
    "into", "through", "during", "before", "after", "above", "below",
    "between", "under", "and", "but", "or", "yet", "so", "if", "because",
    "although", "though", "while", "where", "when", "that", "which", "who",
    "what", "how", "why", "all", "each", "every", "both", "few", "more",
    "most", "other", "some", "such", "no", "not", "only", "own", "same",
    "than", "too", "very", "just", "now", "then", "here", "there",
    "up", "down", "out", "off", "over", "again", "further", "once",
})

# Patterns that look like file extensions or paths (not tags)
_PATH_PATTERNS = re.compile(r"\.(py|js|ts|tsx|java|go|rs|md|html|css|json|yaml|toml|sh|bash|zsh)", re.I)


def _get_api_config():
    key = os.environ.get("AGENT_PUBLISH_API_KEY", "")
    base = os.environ.get("AGENT_PUBLISH_API_BASE", "https://api.openai.com/v1")
    model = os.environ.get("AGENT_PUBLISH_MODEL", "gpt-4o-mini")
    return key, base, model


def _simple_stem(word: str) -> str:
    """Very light stem: strip trailing 's' (e.g. agents/agent)."""
    if word.endswith("ies"):
        return word[:-3] + "y"
    if word.endswith("s") and not word.endswith("ss") and len(word) > 3:
        return word[:-1]
    return word


def _clean_tag(raw: str) -> Optional[str]:
    """Normalize a raw candidate into a kebab-case tag or None if invalid."""
    raw = raw.strip()
    if not raw or len(raw) < 2:
        return None
    if re.match(r"^\d+(\.\d+)?$", raw):  # pure number
        return None
    if _PATH_PATTERNS.search(raw):  # looks like a file extension
        return None
    # Remove markdown formatting
    raw = re.sub(r"`+[^`]*`+", "", raw)  # inline code
    raw = re.sub(r"\*\*([^*]+)\*\*", r"\1", raw)  # bold
    raw = re.sub(r"\*([^*]+)\*", r"\1", raw)  # italic
    raw = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", raw)  # links
    raw = re.sub(r"<[^>]+>", "", raw)  # html
    raw = raw.strip()
    if not raw or len(raw) < 2:
        return None
    # Lowercase and kebab-ize
    tag = re.sub(r"[^\w\s-]", "", raw)
    tag = re.sub(r"[\s_]+", "-", tag)
    tag = tag.strip("-").lower()
    if len(tag) < 2 or tag in _STOP_WORDS:
        return None
    return tag


def _extract_from_headings(text: str) -> Counter:
    """Pull words from # Headings."""
    counts = Counter()
    for line in text.splitlines():
        m = re.match(r"^(#{1,6})\s+(.*)", line)
        if m:
            words = re.findall(r"[A-Za-z0-9]+(?:[-_][A-Za-z0-9]+)*", m.group(2))
            for w in words:
                tag = _clean_tag(w)
                if tag:
                    counts[tag] += 3  # headings weight = 3
    return counts


def _extract_from_bold(text: str) -> Counter:
    """Pull words from **bold** / __bold__ text."""
    counts = Counter()
    for match in re.finditer(r"\*\*([^*]+)\*\*", text):
        for w in re.findall(r"[A-Za-z0-9]+(?:[-_][A-Za-z0-9]+)*", match.group(1)):
            tag = _clean_tag(w)
            if tag:
                counts[tag] += 2  # bold weight = 2
    return counts


def _extract_from_capitalized_phrases(text: str) -> Counter:
    """Multi-word capitalized phrases look like proper nouns / topics."""
    counts = Counter()
    # Match sequences of 2-4 capitalized words
    pattern = r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3})\b"
    for match in re.finditer(pattern, text):
        phrase = match.group(1)
        tag = _clean_tag(phrase.replace(" ", "-"))
        if tag and len(tag) > 3:
            counts[tag] += 2
    return counts


def _extract_from_lists(text: str) -> Counter:
    """Pull candidate words from bullet-point lists."""
    counts = Counter()
    for line in text.splitlines():
        stripped = re.sub(r"^[ ]*[-*•][ ]+", "", line)
        stripped = re.sub(r"^\d+\.[ ]+", "", stripped)
        for w in re.findall(r"[A-Za-z0-9]+(?:[-_][A-Za-z0-9]+)*", stripped):
            tag = _clean_tag(w)
            if tag:
                counts[tag] += 1
    return counts


def suggest_tags_zero_token(md_content: str, count: int = 5) -> List[str]:
    """Extract tags purely from markdown text, no LLM needed.

    Args:
        md_content: Markdown text to analyze.
        count: Number of tags to return (default 5).

    Returns:
        List of kebab-case tag strings, ranked by relevance.
    """
    text = re.sub(r"```[\s\S]*?```", "", md_content)  # strip code blocks

    total = Counter()
    total.update(_extract_from_headings(text))
    total.update(_extract_from_bold(text))
    total.update(_extract_from_capitalized_phrases(text))
    total.update(_extract_from_lists(text))

    if not total:
        return []

    # Deduplicate by simple stem
    seen_stems = {}  # stem -> best tag
    for tag, score in total.most_common():
        stem = _simple_stem(tag)
        # Keep the highest-scoring tag for each stem
        if stem not in seen_stems or score > total[seen_stems[stem]]:
            if stem in seen_stems:
                total[seen_stems[stem]] = 0
            seen_stems[stem] = tag
    for t in total:
        if t not in seen_stems.values():
            total[t] = 0

    # Second pass: also blacklist sub-tags (e.g. if "artificial-intelligence" and "intelligence" both exist, drop "intelligence")
    ranked = [t for t, s in total.most_common() if s > 0]
    filtered = []
    for t in ranked:
        is_redundant = any(
            t != other and (t in other or (other.endswith("-" + t) if t != "" else False))
            for other in ranked if other != t
        )
        if not is_redundant:
            filtered.append(t)

    return filtered[:count]


def _llm_tags(md_content: str, api_key: str, api_base: str, model: str) -> List[str]:
    """Ask an LLM for tags; return empty list on any error."""
    prompt = f"""Given the following article, suggest 5-8 relevant topic tags.
Output ONLY a JSON array of strings, e.g. ["tag-one", "tag-two"].
No markdown fences, no extra text.

{md_content[:6000]}
"""
    payload = json.dumps({
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.2,
        "max_tokens": 256,
    }).encode("utf-8")

    req = urllib.request.Request(
        f"{api_base}/chat/completions",
        data=payload,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            raw = data["choices"][0]["message"]["content"]
            raw = re.sub(r"^```json\s*|```$", "", raw.strip())
            tags = json.loads(raw)
            if isinstance(tags, list):
                cleaned = [_clean_tag(str(t)) for t in tags]
                return [t for t in cleaned if t]
    except Exception:
        pass
    return []


def suggest_tags(
    md_content: str,
    count: int = 5,
    api_key: Optional[str] = None,
    api_base: Optional[str] = None,
    model: Optional[str] = None,
) -> List[str]:
    """Suggest tags with best-effort LLM enhancement; zero-token fallback.

    Priority:
      1. LLM tags (if API key configured).
      2. Zero-token extraction from markdown structure.
    """
    _key, _base, _model = _get_api_config()
    key = api_key or _key

    if key:
        llm_result = _llm_tags(md_content, key, api_base or _base, model or _model)
        if llm_result:
            seen = {}
            deduped = []
            for t in llm_result:
                s = _simple_stem(t)
                if s not in seen:
                    seen[s] = t
                    deduped.append(t)
            return deduped[:count]

    return suggest_tags_zero_token(md_content, count=count)
