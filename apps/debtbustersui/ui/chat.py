import streamlit as st

from ui.theme import section_title

AVATARS = {"user": ":material/person:", "assistant": ":material/smart_toy:"}


def _queue_prompt(key: str) -> None:
    st.session_state.pending_prompt = st.session_state[key]
    st.session_state[key] = None


def _reset() -> None:
    st.session_state.chat_history = []


def _render_message(msg: dict) -> None:
    with st.chat_message(msg["role"], avatar=AVATARS[msg["role"]]):
        st.markdown(msg["content"])
        if msg.get("data") is not None:
            st.dataframe(msg["data"], hide_index=True)
        if msg.get("sql"):
            with st.expander("View generated SQL", icon=":material/code:"):
                st.code(msg["sql"], language="sql")


def _ask(prompt: str) -> dict:
    # Placeholder until the AI agent integration is added.
    return {"role": "assistant", "content": f"_(AI assistant not connected yet)_ You asked: **{prompt}**"}


def render_chat(starter_questions: list[str]) -> None:
    history = st.session_state.setdefault("chat_history", [])

    title_col, action_col = st.columns([5, 1], vertical_alignment="center")
    with title_col:
        section_title("AI assistant")
    action_col.button(
        "New conversation", icon=":material/refresh:", on_click=_reset, disabled=not history, width="stretch"
    )

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
            label_visibility="collapsed",
        )

    prompt = st.chat_input("Ask about the dashboard...")
    prompt = prompt or st.session_state.pop("pending_prompt", None)
    if not prompt:
        return

    user_msg = {"role": "user", "content": prompt}
    history.append(user_msg)
    with messages:
        _render_message(user_msg)
        with st.chat_message("assistant", avatar=AVATARS["assistant"]):
            with st.spinner("Thinking..."):
                history.append(_ask(prompt))
    st.rerun()
