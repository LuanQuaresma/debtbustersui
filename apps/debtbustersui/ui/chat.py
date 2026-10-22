import logging

import streamlit as st

from services.genie import GenieClient, GenieError
from ui.theme import section_title

logger = logging.getLogger(__name__)


def _reset() -> None:
    st.session_state.chat_history = []
    st.session_state.genie_conversation_id = None


def _render_message(msg: dict) -> None:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("data") is not None:
            st.dataframe(msg["data"], hide_index=True)
        if msg.get("sql"):
            with st.expander("View generated SQL"):
                st.code(msg["sql"], language="sql")


@st.cache_resource
def _genie_client(space_id: str) -> GenieClient:
    return GenieClient(space_id)


def _ask(prompt: str, client: GenieClient) -> dict:
    reply = client.ask(prompt, st.session_state.get("genie_conversation_id"))
    st.session_state.genie_conversation_id = reply.conversation_id
    return {
        "role": "assistant",
        "content": reply.text,
        "sql": reply.sql,
        "data": reply.data,
        "suggestions": reply.suggestions,
    }


def render_chat(starter_questions: list[str], space_id: str) -> None:
    history = st.session_state.setdefault("chat_history", [])

    title_col, action_col = st.columns([3, 2])
    with title_col:
        section_title("AI assistant")
    action_col.button("New chat", on_click=_reset, disabled=not history, use_container_width=True)

    if not space_id:
        st.info("Set `chat.genie_space_id` in tabs.yaml to connect a Genie space.")
        return

    try:
        client = _genie_client(space_id)
    except Exception:
        logger.exception("Could not initialize the Databricks Genie client")
        st.error("Could not connect to Databricks. Check this app's authorization settings.")
        return

    messages = st.container(height=360)
    with messages:
        if not history:
            st.caption("Ask a question about the data behind the dashboard, or pick a suggestion below.")
        for msg in history:
            _render_message(msg)

    suggestions = history[-1].get("suggestions") if history else starter_questions
    for index, suggestion in enumerate(suggestions or []):
        if st.button(suggestion, key=f"suggestion_{len(history)}_{index}", use_container_width=True):
            st.session_state.pending_prompt = suggestion

    prompt = st.chat_input("Ask about the dashboard...")
    prompt = prompt or st.session_state.pop("pending_prompt", None)
    if not prompt:
        return

    user_msg = {"role": "user", "content": prompt}
    history.append(user_msg)
    try:
        with st.spinner("Genie is thinking..."):
            history.append(_ask(prompt, client))
    except GenieError as exc:
        history.append({"role": "assistant", "content": str(exc)})
    except Exception:
        logger.exception("Genie request failed")
        history.append(
            {
                "role": "assistant",
                "content": "Genie could not process that request. Check the app logs for details.",
            }
        )
    st.rerun()
