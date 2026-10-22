import streamlit as st


def get_summary(tab: dict) -> str:
    # Swap this for a Delta table / LLM lookup later.
    return tab.get("summary") or "_No summary available yet._"


def render_summary(tab: dict) -> None:
    with st.expander(f"Executive summary — {tab['label']}", expanded=True):
        st.markdown(get_summary(tab))
