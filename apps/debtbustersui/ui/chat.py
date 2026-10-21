import logging
import os

import streamlit as st

from services.genie import GenieClient
from ui.theme import section_title

logger = logging.getLogger(__name__)

AVATARS = {"user": ":material/person:", "assistant": ":material/smart_toy:"}


@st.cache_resource
def _genie() -> GenieClient | None:
    space_id = os.getenv("GENIE_SPACE_ID")
    return GenieClient(space_id) if space_id else None


def _queue_prompt(key: str) -> None:
    st.session_state.pending_prompt = st.session_state[key]
    st.session_state[key] = None


def _reset() -> None:
    st.session_state.chat_history = []
    st.session_state.conversation_id = None


def _render_message(msg: dict) -> None:
    with st.chat_message(msg["role"], avatar=AVATARS[msg["role"]]):
        st.markdown(msg["content"])
        if msg.get("data") is not None:
            st.dataframe(msg["data"], hide_index=True)
        if msg.get("sql"):
            with st.expander("View generated SQL", icon=":material/code:"):
                st.code(msg["sql"], language="sql")


def _ask(genie: GenieClient, prompt: str) -> dict:
    try:
        reply = genie.ask(prompt, st.session_state.get("conversation_id"))
    except Exception as exc:
        logger.exception("Genie request failed")
        return {"role": "assistant", "content": f":red[Sorry, Genie couldn't answer this one.] `{exc}`"}
    st.session_state.conversation_id = reply.conversation_id
    return {
        "role": "assistant",
        "content": reply.text or "Here's what I found:",
        "sql": reply.sql,
        "data": reply.data,
        "suggestions": reply.suggestions,
    }


def render_chat(starter_questions: list[str]) -> None:
    genie = _genie()
    history = st.session_state.setdefault("chat_history", [])

    title_col, action_col = st.columns([5, 1], vertical_alignment="center")
    with title_col:
        section_title("Ask Genie")
    action_col.button(
        "New conversation", icon=":material/refresh:", on_click=_reset, disabled=not history, width="stretch"
    )

    if genie is None:
        st.warning("Genie is not configured. Set the `GENIE_SPACE_ID` environment variable.", icon=":material/link_off:")

    messages = st.container(height=480)
    with messages:
        if not history:
            st.caption("Ask a question about the data behind the dashboard, or pick a suggestion below.")
        for msg in history:
            _render_message(msg)

    suggestions = history[-1].get("suggestions") if history else starter_questions
    if suggestions:
        key = f"suggestions_{len(history)}"
        st.pills(
            "Suggestions",
            suggestions,
            key=key,
            on_change=_queue_prompt,
            args=(key,),
            disabled=genie is None,
            label_visibility="collapsed",
        )

    prompt = st.chat_input("Ask Genie about your data...", disabled=genie is None)
    prompt = prompt or st.session_state.pop("pending_prompt", None)
    if not prompt or genie is None:
        return

    user_msg = {"role": "user", "content": prompt}
    history.append(user_msg)
    with messages:
        _render_message(user_msg)
        with st.chat_message("assistant", avatar=AVATARS["assistant"]):
            with st.spinner("Genie is thinking..."):
                history.append(_ask(genie, prompt))
    st.rerun()
