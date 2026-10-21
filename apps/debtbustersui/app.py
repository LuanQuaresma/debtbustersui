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

st.set_page_config(page_title="DebtBusters | GM Financial", layout="wide", initial_sidebar_state="expanded")


@st.cache_data
def load_config() -> dict:
    return yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8"))


config = load_config()
tab_configs = config["tabs"]

apply_theme()
render_header(config.get("title", "DebtBusters"))

active_tab = tab_configs[0]
# on_change="rerun" enables lazy tabs: only the open tab's iframe is rendered.
tab_containers = st.tabs([t["label"] for t in tab_configs], key="active_tab", on_change="rerun")
for tab, container in zip(tab_configs, tab_containers):
    if container.open:
        active_tab = tab
        with container:
            render_dashboard(tab, config["dashboard"]["height"])

with st.sidebar:
    render_summary(active_tab)
    render_chat(config.get("chat", {}).get("starter_questions", []))
