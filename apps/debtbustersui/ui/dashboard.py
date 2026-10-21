from html import escape

import streamlit as st


def render_dashboard(tab: dict, height: int) -> None:
    url = tab.get("embed_url")
    if not url:
        st.html(
            '<div class="gmf-dashboard-empty"><div>'
            f"<strong>{escape(tab['label'])}</strong><br>"
            "No dashboard configured yet &mdash; set <code>embed_url</code> in tabs.yaml."
            "</div></div>"
        )
        return
    st.iframe(url, height=height)
