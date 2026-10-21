from dataclasses import dataclass, field
from datetime import timedelta

import pandas as pd
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.dashboards import GenieMessage, MessageStatus

TIMEOUT = timedelta(minutes=3)


class GenieError(RuntimeError):
    pass


@dataclass
class GenieReply:
    conversation_id: str
    text: str = ""
    sql: str | None = None
    data: pd.DataFrame | None = None
    suggestions: list[str] = field(default_factory=list)


class GenieClient:
    def __init__(self, space_id: str, client: WorkspaceClient | None = None):
        self.space_id = space_id
        # In Databricks Apps this picks up the app's service principal; locally, your CLI profile.
        self.w = client or WorkspaceClient()

    def ask(self, question: str, conversation_id: str | None = None) -> GenieReply:
        if conversation_id:
            msg = self.w.genie.create_message_and_wait(
                self.space_id, conversation_id, question, timeout=TIMEOUT
            )
        else:
            msg = self.w.genie.start_conversation_and_wait(self.space_id, question, timeout=TIMEOUT)

        if msg.status != MessageStatus.COMPLETED:
            detail = msg.error.error if msg.error else msg.status
            raise GenieError(f"Genie could not answer ({detail}).")

        reply = GenieReply(conversation_id=msg.conversation_id)
        texts = []
        for att in msg.attachments or []:
            if att.text and att.text.content:
                texts.append(att.text.content)
            if att.query:
                reply.sql = att.query.query
                if att.query.description:
                    texts.append(att.query.description)
                reply.data = self._query_result(msg, att.attachment_id)
            if att.suggested_questions:
                reply.suggestions = list(att.suggested_questions.questions or [])
        reply.text = "\n\n".join(texts)
        return reply

    def _query_result(self, msg: GenieMessage, attachment_id: str) -> pd.DataFrame | None:
        resp = self.w.genie.get_message_attachment_query_result(
            self.space_id, msg.conversation_id, msg.message_id or msg.id, attachment_id
        )
        stmt = resp.statement_response
        if not stmt or not stmt.manifest or not stmt.manifest.schema:
            return None
        columns = [c.name for c in stmt.manifest.schema.columns or []]
        rows = (stmt.result.data_array if stmt.result else None) or []
        return pd.DataFrame(rows, columns=columns)
