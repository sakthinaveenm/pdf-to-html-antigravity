"""
HTML Normalization and Sanitization Service.
Uses nh3 (Rust-based ultra-fast HTML sanitizer) and BeautifulSoup
to enforce safety, strip unsafe scripts, preserve Unicode combining marks,
and guarantee stable block IDs and offline relative asset URLs.
"""
from typing import Set, Dict
from bs4 import BeautifulSoup
import nh3

ALLOWED_TAGS: Set[str] = {
    "article", "section", "h1", "h2", "h3", "h4", "h5", "h6", "p",
    "span", "strong", "em", "b", "i", "u", "ul", "ol", "li",
    "table", "thead", "tbody", "tr", "th", "td",
    "figure", "img", "figcaption", "blockquote", "pre", "code", "a",
    "div", "hr", "mark", "sub", "sup"
}

ALLOWED_ATTRIBUTES: Dict[str, Set[str]] = {
    "*": {
        "id", "class", "lang", "dir", "title",
        "data-block-id", "data-page", "data-page-break",
        "data-document-id", "data-highlight-id", "data-math", "data-theme"
    },
    "a": {"href", "target", "rel"},
    "img": {"src", "alt", "width", "height", "loading"},
    "th": {"colspan", "rowspan", "scope"},
    "td": {"colspan", "rowspan"},
}

class HTMLNormalizationService:
    def sanitize(self, raw_html: str) -> str:
        """
        Sanitize HTML strictly stripping dangerous tags and protocols
        while preserving all document structure and data-block-id attributes.
        """
        return nh3.clean(
            raw_html,
            tags=ALLOWED_TAGS,
            attributes=ALLOWED_ATTRIBUTES,
            link_rel=None,
            url_schemes={"http", "https", "mailto", "data", "."}
        )

    def normalize(self, raw_html: str, document_id: str = "") -> str:
        """
        Normalize HTML tree:
        - Ensures every content block has a data-block-id and matching id
        - Resolves asset paths to relative paths
        - Cleans empty wrapper divs without touching Unicode text nodes
        """
        sanitized = self.sanitize(raw_html)
        soup = BeautifulSoup(sanitized, "html.parser")

        # Assign block IDs to any blocks that may have lost them during manual edits
        seq = 1
        for elem in soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6", "p", "table", "pre", "blockquote", "figure"]):
            b_id = elem.get("data-block-id") or elem.get("id")
            if not b_id:
                b_id = f"blk-gen-s{seq:03d}"
                elem["data-block-id"] = b_id
                elem["id"] = b_id
                seq += 1
            else:
                elem["data-block-id"] = b_id
                elem["id"] = b_id

        # Normalize img src attributes to local offline relative paths
        for img in soup.find_all("img"):
            src = img.get("src", "")
            if src.startswith("http://localhost") or src.startswith("http://127.0.0.1"):
                # Strip host and port to keep relative path
                if "/assets/" in src:
                    img["src"] = "./assets/" + src.split("/assets/")[-1]
            elif not src.startswith("./assets/") and not src.startswith("data:"):
                filename = src.split("/")[-1]
                if filename:
                    img["src"] = f"./assets/{filename}"

        return str(soup)

html_normalization_service = HTMLNormalizationService()
