from html import escape

import streamlit as st
import streamlit.components.v1 as components


def render_dashboard(tab: dict, height: int) -> None:
    url = tab.get("embed_url")
    if not url:
        st.markdown(
            '<div class="gmf-dashboard-empty"><div>'
            f"<strong>{escape(tab['label'])}</strong><br>"
            "No dashboard configured yet &mdash; set <code>embed_url</code> in tabs.yaml."
            "</div></div>",
            unsafe_allow_html=True,
        )
        return
    components.iframe(url, height=height, scrolling=True)
