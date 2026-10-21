from html import escape

import streamlit as st

# GM Financial palette — adjust to the official brand hex codes if needed.
_CSS = """
<style>
:root {
  --gmf-blue: #0072CE;
  --gmf-navy: #003B71;
  --gmf-light: #F2F7FC;
  --gmf-border: #D6E2F0;
}
header[data-testid="stHeader"], footer, #MainMenu { display: none; }
[data-testid="stMainBlockContainer"] { padding: 1rem 2rem 2rem; max-width: 100%; }

.gmf-header {
  display: flex; align-items: center; gap: 1rem;
  background: linear-gradient(90deg, var(--gmf-navy), var(--gmf-blue));
  color: #fff; padding: .8rem 1.5rem; border-radius: 10px;
}
.gmf-logo { font-size: 1.35rem; font-weight: 700; letter-spacing: .3px; }
.gmf-divider { width: 1px; height: 1.6rem; background: rgba(255,255,255,.5); }
.gmf-app { font-size: 1.1rem; font-weight: 400; opacity: .95; }

.gmf-section {
  color: var(--gmf-navy); font-weight: 600; font-size: 1.15rem;
  border-left: 4px solid var(--gmf-blue); padding-left: .6rem;
}

iframe[data-testid="stIFrame"] {
  height: calc(100vh - 170px) !important; min-height: 600px;
  border: 1px solid var(--gmf-border) !important; border-radius: 10px;
}
.gmf-dashboard-empty {
  height: calc(100vh - 170px); min-height: 600px;
  display: flex; align-items: center; justify-content: center; text-align: center;
  border: 2px dashed var(--gmf-border); border-radius: 10px;
  background: var(--gmf-light); color: var(--gmf-navy);
}

[data-testid="stChatMessage"] { border-radius: 10px; }
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) { background: var(--gmf-light); }
</style>
"""


def apply_theme() -> None:
    st.html(_CSS)


def render_header(title: str) -> None:
    st.html(
        '<div class="gmf-header">'
        '<span class="gmf-logo">GM Financial</span>'
        '<span class="gmf-divider"></span>'
        f'<span class="gmf-app">{escape(title)}</span>'
        "</div>"
    )


def section_title(text: str) -> None:
    st.html(f'<div class="gmf-section">{escape(text)}</div>')
