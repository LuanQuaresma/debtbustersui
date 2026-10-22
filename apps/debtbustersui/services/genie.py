import time
from dataclasses import dataclass, field
from typing import Any

import pandas as pd
from databricks.sdk import WorkspaceClient

POLL_INTERVAL_SECONDS = 1
REQUEST_TIMEOUT_SECONDS = 180


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
    def __init__(self, space_id: str, workspace_client: WorkspaceClient | None = None):
        self.space_id = space_id
        self.workspace = workspace_client or WorkspaceClient()

    def ask(self, prompt: str, conversation_id: str | None = None) -> GenieReply:
        if conversation_id:
            result = self.workspace.api_client.do(
                "POST",
                path=(
                    f"/api/2.0/genie/spaces/{self.space_id}/conversations/"
                    f"{conversation_id}/messages"
                ),
                body={"content": prompt},
            )
            conversation_id = result["conversation_id"]
            message_id = result.get("message_id") or result.get("id")
        else:
            result = self.workspace.api_client.do(
                "POST",
                path=f"/api/2.0/genie/spaces/{self.space_id}/start-conversation",
                body={"content": prompt},
            )
            conversation_id = result["conversation_id"]
            message = result.get("message") or {}
            message_id = result.get("message_id") or message.get("message_id") or message.get("id")

        if not message_id:
            raise GenieError("Genie did not return a message ID.")

        message = self._wait_for_message(conversation_id, message_id)
        if message.get("status") != "COMPLETED":
            detail = (message.get("error") or {}).get("error") or message.get("status", "unknown status")
            raise GenieError(f"Genie could not answer: {detail}")

        reply = GenieReply(conversation_id=conversation_id)
        response_text = []
        for attachment in message.get("attachments") or []:
            text = attachment.get("text") or {}
            if text.get("content"):
                response_text.append(text["content"])

            query = attachment.get("query") or {}
            reply.sql = query.get("query") or reply.sql
            if query.get("description"):
                response_text.append(query["description"])
            attachment_id = attachment.get("attachment_id")
            if attachment_id and query:
                reply.data = self._query_result(conversation_id, message_id, attachment_id)

            questions = attachment.get("suggested_questions") or {}
            reply.suggestions.extend(questions.get("questions") or [])

        reply.text = "\n\n".join(response_text) or "Genie completed the request without a text response."
        return reply

    def _wait_for_message(self, conversation_id: str, message_id: str) -> dict[str, Any]:
        path = (
            f"/api/2.0/genie/spaces/{self.space_id}/conversations/"
            f"{conversation_id}/messages/{message_id}"
        )
        deadline = time.monotonic() + REQUEST_TIMEOUT_SECONDS
        while time.monotonic() < deadline:
            message = self.workspace.api_client.do("GET", path=path)
            status = message.get("status")
            if status in {"COMPLETED", "FAILED", "CANCELLED", "QUERY_RESULT_EXPIRED"}:
                return message
            time.sleep(POLL_INTERVAL_SECONDS)
        raise GenieError("Genie took too long to respond. Please try again.")

    def _query_result(
        self, conversation_id: str, message_id: str, attachment_id: str
    ) -> pd.DataFrame | None:
        path = (
            f"/api/2.0/genie/spaces/{self.space_id}/conversations/{conversation_id}/"
            f"messages/{message_id}/attachments/{attachment_id}/query-result"
        )
        response = self.workspace.api_client.do("GET", path=path)
        statement = response.get("statement_response") or {}
        manifest = statement.get("manifest") or {}
        schema = manifest.get("schema") or {}
        columns = [column["name"] for column in schema.get("columns") or []]
        result = statement.get("result") or {}
        rows = result.get("data_array") or []
        return pd.DataFrame(rows, columns=columns) if columns else None