"""Markdown rendering utilities with HTML sanitization.

This module provides helpers to render untrusted Markdown text into HTML and
sanitize the result so it is safe to embed in Django Admin or other UIs.

It uses the `markdown` library for Markdown -> HTML conversion and `bleach`
for sanitization and URL linkification.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping

import bleach
import markdown as md

_DEFAULT_EXTENSIONS = ("extra", "sane_lists")

# Extend bleach's default allowed tags with common Markdown outputs
_DEFAULT_ALLOWED_TAGS = set(bleach.sanitizer.ALLOWED_TAGS).union(
    {
        "p",
        "pre",
        "code",
        "blockquote",
        "hr",
        "h1",
        "h2",
        "h3",
        "h4",
        "h5",
        "h6",
        "ul",
        "ol",
        "li",
        "table",
        "thead",
        "tbody",
        "tr",
        "th",
        "td",
    }
)

_DEFAULT_ALLOWED_ATTRS: Mapping[str, Iterable[str]] = {
    "a": ["href", "title", "rel", "target"],
    "th": ["colspan", "rowspan"],
    "td": ["colspan", "rowspan"],
}


def render_markdown_safe(
    text: str,
    *,
    extensions: Iterable[str] | None = None,
    allowed_tags: Iterable[str] | None = None,
    allowed_attrs: Mapping[str, Iterable[str]] | None = None,
) -> str:
    """Render Markdown to sanitized HTML.

    Parameters:
        text: Raw markdown text.
        extensions: Optional iterable of markdown extensions to enable. If not
            provided, a sensible default is used.
        allowed_tags: Optional iterable of allowed HTML tags for bleach. If
            not provided, a default extended set is used.
        allowed_attrs: Optional mapping of allowed attributes per tag. If not
            provided, a default safe set is used.

    Returns:
        A sanitized HTML string (not marked safe). Callers in Django should wrap
        with django.utils.safestring.mark_safe when embedding in templates/admin.
    """
    if not text:
        return ""

    html = md.markdown(text, extensions=list(extensions or _DEFAULT_EXTENSIONS))

    clean_html = bleach.clean(
        html,
        tags=list(allowed_tags or _DEFAULT_ALLOWED_TAGS),
        attributes=allowed_attrs or _DEFAULT_ALLOWED_ATTRS,
        protocols=["http", "https", "mailto"],
        strip=True,
    )
    # Auto-link plain URLs and ensure rel="nofollow noopener"
    clean_html = bleach.linkify(clean_html)
    return clean_html
