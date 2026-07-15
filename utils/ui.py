"""Reusable presentation components for the BrainGuard AI Streamlit UI.

These helpers intentionally contain no scoring, authentication, or database
logic.  They provide a small, consistent design layer that individual views
can compose around their existing behavior.
"""

from __future__ import annotations

from html import escape
from typing import Callable

import streamlit as st


_ICONS = {
    "brain": """<path d="M12 3.4a3.8 3.8 0 0 0-3.7 4.6A3.7 3.7 0 0 0 5 13.5a3.8 3.8 0 0 0 5.8 3.2M12 3.4a3.8 3.8 0 0 1 3.7 4.6 3.7 3.7 0 0 1 3.3 5.5 3.8 3.8 0 0 1-5.8 3.2M12 3.4v16.2M8.3 8A4.1 4.1 0 0 0 12 10.2M15.7 8A4.1 4.1 0 0 1 12 10.2"/>""",
    "family": """<circle cx="8.2" cy="7.2" r="2.2"/><circle cx="16.4" cy="8.4" r="1.8"/><path d="M3.9 19.2c.3-3 2-4.8 4.3-4.8s4 1.8 4.3 4.8M13.1 18.8c.2-2.3 1.5-3.7 3.3-3.7 1.9 0 3.1 1.4 3.4 3.7"/>""",
    "clinic": """<path d="M4 20V5.5A1.5 1.5 0 0 1 5.5 4h13A1.5 1.5 0 0 1 20 5.5V20M8 20v-4h8v4M8 8h2M14 8h2M8 12h2M14 12h2"/>""",
    "shield": """<path d="M12 3.3 19 6v5.4c0 4.3-2.8 7.7-7 9.3-4.2-1.6-7-5-7-9.3V6l7-2.7Z"/><path d="m8.7 12 2.1 2.1 4.6-4.6"/>""",
    "check": """<path d="m5 12.4 4.4 4.3L19.3 7"/>""",
    "attention": """<path d="M12 4 21 20H3L12 4Z"/><path d="M12 9v4.5M12 17h.01"/>""",
}


def icon(name: str, *, size: int = 24) -> str:
    """Return a simple, decorative line icon with a stable accessible wrapper."""
    path = _ICONS.get(name, _ICONS["shield"])
    return (
        f'<svg class="bg-icon" aria-hidden="true" width="{size}" height="{size}" '
        'viewBox="0 0 24 24" fill="none" stroke="currentColor" '
        'stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">'
        f"{path}</svg>"
    )


def render_public_header() -> None:
    """Brand header for public pages, intentionally without account controls."""
    with st.container(key="public_header"):
        left, right = st.columns([4, 2], vertical_alignment="center")
        with left:
            st.markdown(
                "<div class='bg-brand'><span>BrainGuard AI</span></div>",
                unsafe_allow_html=True,
            )
        with right:
            st.markdown(
                "<div class='bg-header-note'>Private screening support</div>",
                unsafe_allow_html=True,
            )


def render_portal_header(
    current_page: str,
    home_page: str,
    switch_role: Callable[[], None],
) -> None:
    """Persistent, keyboard-operable portal chrome for signed-in roles."""
    with st.container(key="portal_header"):
        brand_col, page_col, home_col, switch_col = st.columns(
            [3.2, 2.1, 1.15, 1.35], vertical_alignment="center"
        )
        with brand_col:
            st.markdown(
                "<div class='bg-brand'><span>BrainGuard AI</span></div>",
                unsafe_allow_html=True,
            )
        with page_col:
            st.markdown(
                f"<div class='bg-current-page'><span>Current page</span>"
                f"{escape(current_page)}</div>",
                unsafe_allow_html=True,
            )
        with home_col:
            st.page_link(home_page, label="Home", icon=":material/home:", width="stretch")
        with switch_col:
            st.button(
                "Switch role",
                icon=":material/swap_horiz:",
                on_click=switch_role,
                key="header_switch_role",
                width="stretch",
            )


def render_step_progress(current: int, total: int, label: str, *, item_label: str = "Question") -> None:
    """A text-labelled progress bar; progress is never communicated by color alone."""
    progress = max(0, min(100, round((current / max(total, 1)) * 100)))
    st.markdown(
        f"<div class='bg-step-progress' role='status' aria-live='polite'>"
        f"<div><strong>{escape(label)}</strong><span>{escape(item_label)} {current} of {total}</span></div>"
        f"<div class='bg-progress-track' role='progressbar' aria-valuemin='0' "
        f"aria-valuemax='{total}' aria-valuenow='{current}' aria-label='{escape(label)}'>"
        f"<span style='width:{progress}%'></span></div></div>",
        unsafe_allow_html=True,
    )


def render_trust_indicators() -> None:
    """Compact, textual trust indicators used below the public hero CTA."""
    indicators = [
        ("shield", "No sign-in required", "Start a lifestyle check without creating an account."),
        ("check", "Private", "Please use only your own non-sensitive information."),
        ("attention", "Not a diagnosis", "Results support a conversation with a qualified clinician."),
    ]
    cols = st.columns(3, gap="small")
    for column, (symbol, title, text) in zip(cols, indicators):
        with column:
            st.markdown(
                f"<div class='bg-trust-item'>{icon(symbol, size=20)}<div>"
                f"<strong>{title}</strong><span>{text}</span></div></div>",
                unsafe_allow_html=True,
            )


def render_status_chip(status: str, *, tone: str) -> None:
    """Status chip with an icon and visible label (not color-only)."""
    icon_name = "check" if tone == "stable" else "attention"
    st.markdown(
        f"<span class='bg-status-chip bg-status-{escape(tone)}'>{icon(icon_name, size=15)}"
        f"{escape(status)}</span>",
        unsafe_allow_html=True,
    )


def render_skeleton(*, lines: int = 3, key: str = "default") -> None:
    """Placeholder shimmer bars shown in place of blank space while content
    is loading. Built from plain divs we own (no generated Streamlit class
    names), so it stays stable across Streamlit versions. The shimmer
    animation is disabled automatically under prefers-reduced-motion by the
    global rule in utils/layout.py.
    """
    bars = "".join(
        f"<div class='bg-skeleton-line' style='width:{width}%'></div>"
        for width in ([88, 96, 72][i % 3] for i in range(lines))
    )
    st.markdown(f"<div class='bg-skeleton' aria-hidden='true' data-key='{escape(key)}'>{bars}</div>", unsafe_allow_html=True)


def render_animated_score(value: float, *, key: str) -> None:
    """Render a one-time, reduced-motion-safe score reveal.

    Streamlit has no maintained native count-up widget. This intentionally
    stays in the normal Streamlit document (instead of a deprecated custom
    HTML component) and reveals the final score with the same restrained
    entrance motion used by the rest of the interface.
    """
    token = f"_score_seen_{key}_{value:.1f}"
    animate = not st.session_state.get(token, False)
    st.session_state[token] = True
    animation = " bg-score-enter" if animate else ""
    st.markdown(
        f"<div class='bg-score{animation}' aria-label='Estimated risk score {value:.1f} percent'>"
        f"{value:.1f}%<span>Estimated score</span></div>",
        unsafe_allow_html=True,
    )
