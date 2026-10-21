# --- diagnostics bootstrap: install crash/exception logging before app code ---
import os as _diag_os
import sys as _diag_sys

_diag_dir = _diag_os.path.dirname(_diag_os.path.abspath(__file__))
if _diag_dir not in _diag_sys.path:
    _diag_sys.path.insert(0, _diag_dir)
import app_diagnostics  # noqa: E402

app_diagnostics.install_diagnostics()
# --- end diagnostics bootstrap ---

from pathlib import Path

import streamlit as st
import yaml

from ui.chat import render_chat
from ui.dashboard import render_dashboard
from ui.summary import render_summary
from ui.theme import apply_theme, render_header

CONFIG_PATH = Path(__file__).parent / "tabs.yaml"

st.set_page_config(page_title="DebtBusters | GM Financial", layout="wide")


@st.cache_data
def load_config() -> dict:
    return yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8"))


config = load_config()
tabs = {t["id"]: t for t in config["tabs"]}
default_tab = next(iter(tabs))

apply_theme()
render_header(config.get("title", "DebtBusters"))

selected = default_tab
if len(tabs) > 1:
    selected = st.segmented_control(
        "Section",
        options=list(tabs),
        format_func=lambda tab_id: tabs[tab_id]["label"],
        default=default_tab,
        key="active_tab",
        label_visibility="collapsed",
    )
# Clicking the active segment deselects it; keep showing the default instead.
tab = tabs[selected or default_tab]

render_dashboard(tab, config["dashboard"]["height"])
render_summary(tab)
render_chat(config.get("chat", {}).get("starter_questions", []))
