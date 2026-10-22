import base64
from html import escape
from io import BytesIO
from pathlib import Path

import streamlit as st
from PIL import Image

LOGO_PATH = Path(__file__).resolve().parent.parent / "assets" / "gmfinancial logo.png"

# GM Financial palette; --gmf-blue is sampled from the logo.
_CSS = """
<style>
:root {
  --gmf-blue: #0956FF;
  --gmf-navy: #0A2A66;
  --gmf-light: #F2F6FF;
  --gmf-border: #D6E0F5;
}
/* Keep the header (it hosts the sidebar expand button) but make it unobtrusive. */
header[data-testid="stHeader"] { background: transparent; }
[data-testid="stDecoration"], [data-testid="stMainMenu"], [data-testid="stAppDeployButton"], footer { display: none; }
[data-testid="stMainBlockContainer"] { padding: 1rem 1.5rem 1rem; max-width: 100%; }

section[data-testid="stSidebar"][data-collapsed="false"],
section[data-testid="stSidebar"][aria-expanded="true"] {
  width: 30vw !important; min-width: 30vw !important; max-width: 30vw !important;
  border-right: 1px solid var(--gmf-border);
}
[data-testid="stSidebarContent"] [data-testid="stSidebarUserContent"] { padding-top: 0; }

/* Blade toggles: a blue handle on the left edge when collapsed, an always-visible button when open. */
[data-testid="stExpandSidebarButton"] {
  position: fixed !important; left: 0; top: 50%; transform: translateY(-50%); z-index: 1000;
  flex-direction: column; gap: .5rem; height: auto !important; width: auto !important;
  padding: .9rem .4rem !important; border-radius: 0 10px 10px 0 !important;
  background: var(--gmf-blue) !important; box-shadow: 2px 2px 8px rgba(0, 59, 113, .35);
}
[data-testid="stExpandSidebarButton"]::after {
  content: "Summary & AI chat"; writing-mode: vertical-rl;
  color: #fff; font-size: .85rem; font-weight: 600; letter-spacing: .5px;
}
[data-testid="stSidebarCollapseButton"], [data-testid="stSidebarCollapseButton"] button { visibility: visible !important; }
[data-testid="stSidebarCollapseButton"] button {
  background: var(--gmf-blue) !important; border-radius: 8px !important;
  box-shadow: 0 2px 6px rgba(0, 59, 113, .35);
}
[data-testid="stSidebarCollapsedControl"] {
  position: fixed !important; left: 0; top: 50%; transform: translateY(-50%); z-index: 1000;
}
[data-testid="stSidebarCollapsedControl"] [data-testid="stLogo"] { display: none !important; }
[data-testid="stSidebarCollapsedControl"] button {
  display: flex !important; flex-direction: column; gap: .5rem; height: auto !important;
  padding: .9rem .4rem !important; border-radius: 0 10px 10px 0 !important;
  background: var(--gmf-blue) !important; box-shadow: 2px 2px 8px rgba(0, 59, 113, .35);
}
[data-testid="stSidebarCollapsedControl"] button::after {
  content: "Summary & AI chat"; writing-mode: vertical-rl;
  color: #fff; font-size: .85rem; font-weight: 600;
}
[data-testid="stSidebarCollapsedControl"] button:hover { background: var(--gmf-navy) !important; }
[data-testid="stExpandSidebarButton"]:hover, [data-testid="stSidebarCollapseButton"] button:hover {
  background: var(--gmf-navy) !important;
}
[data-testid="stExpandSidebarButton"] *, [data-testid="stSidebarCollapseButton"] button *,
[data-testid="stSidebarCollapsedControl"] button * { color: #fff !important; }
.stApp:has([data-testid="stSidebar"][data-collapsed="true"]) [data-testid="stMainBlockContainer"],
.stApp:has([data-testid="stSidebar"][aria-expanded="false"]) [data-testid="stMainBlockContainer"] { padding-left: 3rem; }

.gmf-header {
  display: flex; align-items: center; gap: 1.25rem;
  background: #fff; padding: .6rem 1.5rem; border-radius: 10px;
  border: 1px solid var(--gmf-border); border-bottom: 3px solid var(--gmf-blue);
}
.gmf-logo { height: 34px; width: auto; display: block; }
.gmf-divider { width: 1px; height: 1.8rem; background: var(--gmf-border); }
.gmf-app { font-size: 1.2rem; font-weight: 600; color: var(--gmf-navy); }

.gmf-section {
  color: var(--gmf-navy); font-weight: 600; font-size: 1.15rem;
  border-left: 4px solid var(--gmf-blue); padding-left: .6rem;
}

iframe[data-testid="stIFrame"] {
  height: calc(100vh - 150px) !important; min-height: 500px;
  border: 1px solid var(--gmf-border) !important; border-radius: 10px;
}
.gmf-dashboard-empty {
  height: calc(100vh - 150px); min-height: 500px;
  display: flex; align-items: center; justify-content: center; text-align: center;
  border: 2px dashed var(--gmf-border); border-radius: 10px;
  background: var(--gmf-light); color: var(--gmf-navy);
}

[data-testid="stChatMessage"] { border-radius: 10px; background: #fff; }
</style>
"""


def apply_theme() -> None:
  st.markdown(_CSS, unsafe_allow_html=True)


@st.cache_resource
def _logo_data_uri() -> str:
    with Image.open(LOGO_PATH) as im:
        im = im.crop(im.getchannel("A").getbbox())  # trim transparent padding
        buf = BytesIO()
        im.save(buf, format="PNG")
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()


def render_header(title: str) -> None:
  st.markdown(
        '<div class="gmf-header">'
        f'<img class="gmf-logo" src="{_logo_data_uri()}" alt="GM Financial">'
        '<span class="gmf-divider"></span>'
        f'<span class="gmf-app">{escape(title)}</span>'
        "</div>",
        unsafe_allow_html=True,
    )


def section_title(text: str) -> None:
  st.markdown(f'<div class="gmf-section">{escape(text)}</div>', unsafe_allow_html=True)
