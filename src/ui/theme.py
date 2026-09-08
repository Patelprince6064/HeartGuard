"""Global CSS design system for HeartGuard (Phase 18).

Injects consistent styling across all pages: typography, spacing, colors,
buttons, forms, cards, tables, alerts, and responsive breakpoints.

Call ``inject_global_theme()`` once at the top of every page to apply.
"""

from __future__ import annotations

import streamlit as st

# HeartGuard design tokens (mirrors PALETTE in charts.py)
COLORS = {
    "primary": "#1e3a8a",
    "primary_light": "#3b82f6",
    "secondary": "#0284c7",
    "accent": "#4f46e5",
    "success": "#16a34a",
    "warning": "#d97706",
    "error": "#dc2626",
    "info": "#2563eb",
    "text": "#1e293b",
    "muted": "#64748b",
    "border": "#e2e8f0",
    "surface": "#f8fafc",
    "bg": "#ffffff",
}

# ── Global CSS ───────────────────────────────────────────────────────────────

GLOBAL_CSS = f"""
<style>
/* ── Base ─────────────────────────────────────────────────────────────── */
:root {{
    --hg-primary: {COLORS['primary']};
    --hg-primary-light: {COLORS['primary_light']};
    --hg-secondary: {COLORS['secondary']};
    --hg-accent: {COLORS['accent']};
    --hg-success: {COLORS['success']};
    --hg-warning: {COLORS['warning']};
    --hg-error: {COLORS['error']};
    --hg-info: {COLORS['info']};
    --hg-text: {COLORS['text']};
    --hg-muted: {COLORS['muted']};
    --hg-border: {COLORS['border']};
    --hg-surface: {COLORS['surface']};
    --hg-bg: {COLORS['bg']};
    --hg-radius: 8px;
    --hg-radius-sm: 4px;
    --hg-radius-lg: 12px;
    --hg-shadow: 0 1px 3px rgba(0,0,0,0.08), 0 1px 2px rgba(0,0,0,0.06);
    --hg-shadow-md: 0 4px 6px rgba(0,0,0,0.07), 0 2px 4px rgba(0,0,0,0.06);
    --hg-space-xs: 0.25rem;
    --hg-space-sm: 0.5rem;
    --hg-space-md: 1rem;
    --hg-space-lg: 1.5rem;
    --hg-space-xl: 2rem;
}}

/* ── Typography ───────────────────────────────────────────────────────── */
h1, h2, h3, h4, h5, h6 {{
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    color: var(--hg-text);
    line-height: 1.3;
}}

/* ── Sidebar ──────────────────────────────────────────────────────────── */
section[data-testid="stSidebar"] {{
    background-color: var(--hg-surface);
    border-right: 1px solid var(--hg-border);
}}

section[data-testid="stSidebar"] .stMarkdown p {{
    font-size: 0.9rem;
}}

section[data-testid="stSidebar"] [data-testid="stSidebarNav"] {{
    padding-top: 0.5rem;
}}

/* ── Cards ────────────────────────────────────────────────────────────── */
div[data-testid="stVerticalBlock"] > div[data-testid="stVerticalBlockBorderWrapper"] {{
    border-radius: var(--hg-radius);
    border-color: var(--hg-border);
    box-shadow: var(--hg-shadow);
    transition: box-shadow 0.2s ease;
}}

div[data-testid="stVerticalBlock"] > div[data-testid="stVerticalBlockBorderWrapper"]:hover {{
    box-shadow: var(--hg-shadow-md);
}}

/* ── Metrics ──────────────────────────────────────────────────────────── */
div[data-testid="stMetric"] {{
    background-color: var(--hg-surface);
    border-radius: var(--hg-radius);
    padding: 0.75rem 1rem;
    border: 1px solid var(--hg-border);
}}

div[data-testid="stMetric"] label {{
    font-size: 0.85rem !important;
    font-weight: 500 !important;
    color: var(--hg-muted) !important;
    text-transform: uppercase;
    letter-spacing: 0.025em;
}}

div[data-testid="stMetric"] [data-testid="stMetricValue"] {{
    font-size: 1.75rem !important;
    font-weight: 700 !important;
    color: var(--hg-text) !important;
}}

/* ── Buttons ──────────────────────────────────────────────────────────── */
.stButton > button {{
    border-radius: var(--hg-radius);
    font-weight: 600;
    padding: 0.5rem 1.25rem;
    transition: all 0.2s ease;
    border: 1px solid transparent;
}}

.stButton > button:hover {{
    transform: translateY(-1px);
    box-shadow: var(--hg-shadow-md);
}}

.stButton > button:active {{
    transform: translateY(0);
}}

.stButton > button:focus-visible {{
    outline: 2px solid var(--hg-primary-light);
    outline-offset: 2px;
}}

/* Primary button */
.stButton > button[kind="primary"],
.stDownloadButton > button {{
    background-color: var(--hg-primary) !important;
    color: white !important;
    border-color: var(--hg-primary) !important;
}}

.stButton > button[kind="primary"]:hover,
.stDownloadButton > button:hover {{
    background-color: #1e40af !important;
}}

/* Secondary button */
.stButton > button[kind="secondary"] {{
    background-color: transparent !important;
    color: var(--hg-primary) !important;
    border-color: var(--hg-border) !important;
}}

.stButton > button[kind="secondary"]:hover {{
    background-color: var(--hg-surface) !important;
    border-color: var(--hg-primary-light) !important;
}}

/* ── Forms ────────────────────────────────────────────────────────────── */
div[data-testid="stForm"] {{
    border: 1px solid var(--hg-border);
    border-radius: var(--hg-radius-lg);
    padding: 1.5rem;
    background-color: var(--hg-bg);
}}

div[data-testid="stForm"] label {{
    font-weight: 600;
    font-size: 0.875rem;
    color: var(--hg-text);
}}

/* ── DataFrames / Tables ──────────────────────────────────────────────── */
div[data-testid="stDataFrame"] {{
    border-radius: var(--hg-radius);
    border: 1px solid var(--hg-border);
    overflow: hidden;
}}

div[data-testid="stDataFrame"] th {{
    background-color: var(--hg-surface) !important;
    font-weight: 600 !important;
    color: var(--hg-text) !important;
    text-transform: uppercase;
    font-size: 0.8rem;
    letter-spacing: 0.025em;
}}

/* ── Alerts / Info / Warning / Error / Success ────────────────────────── */
div[data-testid="stAlert"] {{
    border-radius: var(--hg-radius);
    padding: 0.75rem 1rem;
}}

div.stAlert {{
    border-radius: var(--hg-radius);
}}

/* ── Expanders ────────────────────────────────────────────────────────── */
div[data-testid="stExpander"] {{
    border: 1px solid var(--hg-border);
    border-radius: var(--hg-radius);
}}

div[data-testid="stExpander"] summary {{
    font-weight: 600;
    color: var(--hg-text);
}}

/* ── Tabs ─────────────────────────────────────────────────────────────── */
div[data-testid="stTabs"] button[role="tab"] {{
    font-weight: 600;
    padding: 0.75rem 1.5rem;
    border-radius: var(--hg-radius-sm) var(--hg-radius-sm) 0 0;
}}

/* ── Progress Bar ─────────────────────────────────────────────────────── */
div[data-testid="stProgress"] > div > div {{
    border-radius: 999px;
}}

/* ── Dividers ─────────────────────────────────────────────────────────── */
hr {{
    border: none;
    border-top: 1px solid var(--hg-border);
    margin: 1rem 0;
}}

/* ── Spinners ─────────────────────────────────────────────────────────── */
div[data-testid="stSpinner"] {{
    border-radius: var(--hg-radius);
    padding: 1rem;
}}

/* ── Page Link Cards ──────────────────────────────────────────────────── */
a[data-testid="stPageLink"] {{
    border-radius: var(--hg-radius);
    transition: all 0.2s ease;
}}

/* ── Accessibility: Focus ─────────────────────────────────────────────── */
:focus-visible {{
    outline: 2px solid var(--hg-primary-light);
    outline-offset: 2px;
}}

/* ── Reduced Motion ───────────────────────────────────────────────────── */
@media (prefers-reduced-motion: reduce) {{
    * {{
        animation: none !important;
        transition-duration: 0.01ms !important;
    }}
}}

/* ── Print ────────────────────────────────────────────────────────────── */
@media print {{
    section[data-testid="stSidebar"] {{
        display: none !important;
    }}
    div[data-testid="stToolbar"] {{
        display: none !important;
    }}
}}

/* ── Responsive helpers ───────────────────────────────────────────────── */
@media (max-width: 768px) {{
    div[data-testid="stMetric"] [data-testid="stMetricValue"] {{
        font-size: 1.4rem !important;
    }}
    div[data-testid="stMetric"] label {{
        font-size: 0.75rem !important;
    }}
}}

@media (max-width: 480px) {{
    div[data-testid="stMetric"] [data-testid="stMetricValue"] {{
        font-size: 1.2rem !important;
    }}
}}
</style>
"""

# ── Injection guard (only inject once per page) ─────────────────────────────

_theme_injected: bool = False


def inject_global_theme() -> None:
    """Inject the global CSS design system into the current Streamlit page.

    Safe to call multiple times — CSS is only injected once per page load.
    """
    global _theme_injected
    if not _theme_injected:
        st.markdown(GLOBAL_CSS, unsafe_allow_html=True)
        _theme_injected = True


def get_colors() -> dict[str, str]:
    """Return the design token color dictionary."""
    return COLORS.copy()
