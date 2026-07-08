from __future__ import annotations


CUSTOM_CSS = """
<style>
  :root {
    --bg: #f5f7f8;
    --panel: rgba(255, 255, 255, 0.92);
    --panel-border: rgba(15, 23, 42, 0.08);
    --text: #0f172a;
    --muted: #667085;
    --accent: #0f766e;
    --ok: #16a34a;
    --ok-soft: rgba(22, 163, 74, 0.12);
    --bad: #dc2626;
    --bad-soft: rgba(220, 38, 38, 0.12);
  }

  html, body, [class*="css"] {
    font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text", "SF Pro Display",
      "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  }

  .stApp {
    background:
      radial-gradient(circle at top right, rgba(15, 118, 110, 0.06), transparent 28%),
      radial-gradient(circle at bottom left, rgba(59, 130, 246, 0.04), transparent 24%),
      var(--bg);
    color: var(--text);
  }

  .block-container {
    padding-top: 1.35rem;
    padding-bottom: 2rem;
    max-width: 1240px;
  }

  #MainMenu, footer {
    visibility: hidden;
  }

  [data-testid="stSidebar"] {
    background: linear-gradient(180deg, rgba(255,255,255,0.92), rgba(248,250,252,0.98));
    border-right: 1px solid var(--panel-border);
  }

  [data-testid="stSidebar"] .stButton > button,
  [data-testid="stSidebar"] [data-testid="stDownloadButton"] button {
    width: 100%;
  }

  .hero {
    padding: 1.15rem 0 1rem 0;
    margin-bottom: 1rem;
    border-bottom: 1px solid rgba(15, 23, 42, 0.08);
  }

  .eyebrow {
    font-size: 0.78rem;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--accent);
    font-weight: 700;
    margin-bottom: 0.35rem;
  }

  .hero h1 {
    font-size: 2.05rem;
    line-height: 1.1;
    margin: 0;
    color: var(--text);
    font-weight: 650;
  }

  .hero p {
    margin: 0.45rem 0 0 0;
    color: var(--muted);
    max-width: 56rem;
    font-size: 0.98rem;
  }

  .section-kicker {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 0.78rem;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--accent);
    font-weight: 700;
    margin-bottom: 0.45rem;
  }

  .section-kicker::before {
    content: "";
    width: 22px;
    height: 1px;
    background: rgba(15, 118, 110, 0.45);
    display: inline-block;
  }

  .soft-panel {
    background: var(--panel);
    border: 1px solid var(--panel-border);
    border-radius: 18px;
    padding: 1rem 1rem 0.75rem 1rem;
    box-shadow: 0 18px 44px rgba(15, 23, 42, 0.06);
    backdrop-filter: blur(12px);
  }

  .soft-panel + .soft-panel {
    margin-top: 1rem;
  }

  .mini-note {
    color: var(--muted);
    font-size: 0.92rem;
    line-height: 1.5;
  }

  .sheet-status-name {
    font-size: 0.92rem;
    color: var(--text);
    font-weight: 600;
    line-height: 1.2;
    padding-top: 0.35rem;
  }

  .sheet-status-pill {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    min-width: 4.9rem;
    padding: 0.38rem 0.75rem;
    border-radius: 999px;
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.04em;
    text-transform: uppercase;
  }

  .sheet-status-pill--ok {
    background: var(--ok-soft);
    color: var(--ok);
  }

  .sheet-status-pill--bad {
    background: var(--bad-soft);
    color: var(--bad);
  }

  [data-testid="stMetric"] {
    border: 1px solid rgba(15, 23, 42, 0.08);
    border-radius: 16px;
    padding: 14px 16px;
    background: rgba(255,255,255,0.92);
    box-shadow: 0 10px 24px rgba(15, 23, 42, 0.05);
    margin-bottom: 0.25rem;
  }

  [data-testid="stMetricLabel"] {
    color: #475467;
    font-size: 0.85rem;
  }

  [data-testid="stMetricValue"] {
    color: var(--text);
    font-size: 1.55rem;
    line-height: 1.1;
  }

  [data-testid="stMetricDelta"] {
    color: var(--accent);
  }

  .stTabs [data-baseweb="tab-list"] {
    gap: 0.35rem;
    background: rgba(255,255,255,0.58);
    border: 1px solid rgba(15, 23, 42, 0.08);
    border-radius: 14px;
    padding: 0.25rem;
  }

  .stTabs [data-baseweb="tab"] {
    border-radius: 11px;
    padding: 0.55rem 0.9rem;
    color: #475467;
    font-weight: 600;
  }

  .stTabs [aria-selected="true"] {
    background: rgba(15, 118, 110, 0.10);
    color: var(--accent) !important;
  }

  .stDataFrame, .stDataEditor {
    border-radius: 16px;
  }
</style>
"""


def render_sheet_status_pill(active: bool) -> str:
    state_class = "sheet-status-pill--ok" if active else "sheet-status-pill--bad"
    state_label = "ACTIVE" if active else "INACTIVE"
    return f'<span class="sheet-status-pill {state_class}">{state_label}</span>'
