# SPDX-FileCopyrightText: 2026 Pixel Nomad
#
# SPDX-License-Identifier: MIT

"""Filters for list_tickets results.

Leantime's getAll returns every field of every ticket (about 4 MB for the whole
instance). These filters run on that result so the agent only sees what it asked
for. No filters and no fields: the full result, as before.
"""

from typing import Any, Iterable, Optional

COMPACT_FIELDS = [
    "id", "headline", "status", "priority", "editorId", "editorFirstname",
    "dateToFinish", "tags", "projectId", "projectName", "type",
]
DONE_STATUSES = {"0", "-1"}


def _tags(ticket: dict) -> list[str]:
    return [t.strip() for t in str(ticket.get("tags") or "").split(",") if t.strip()]


def _due(ticket: dict) -> str:
    value = str(ticket.get("dateToFinish") or "")[:10]
    return "" if not value or value.startswith("0000") else value


def _status_match(ticket: dict, status: str) -> bool:
    current = str(ticket.get("status"))
    if status == "open":
        return current not in DONE_STATUSES
    if status == "done":
        return current in DONE_STATUSES
    wanted = {s.strip() for s in status.split(",") if s.strip()}
    return current in wanted


def filter_tickets(
    tickets: Iterable[dict],
    assignee: Optional[int] = None,
    status: Optional[str] = None,
    tag: Optional[str] = None,
    due_before: Optional[str] = None,
) -> list[dict]:
    """Keep tickets that match every filter given.

    assignee: user id (editorId). status: "open", "done" or codes like "1,4".
    tag: exact tag, or a prefix ending in "*" (e.g. "top5-*").
    due_before: YYYY-MM-DD; tickets with a due date before it (no due date: excluded).
    """
    out = []
    for t in tickets:
        if assignee is not None and str(t.get("editorId")) != str(assignee):
            continue
        if status and not _status_match(t, status):
            continue
        if tag:
            tags = _tags(t)
            if tag.endswith("*"):
                if not any(x.startswith(tag[:-1]) for x in tags):
                    continue
            elif tag not in tags:
                continue
        if due_before:
            due = _due(t)
            if not due or due >= due_before:
                continue
        out.append(t)
    return out


def select_fields(tickets: Iterable[dict], fields: Optional[str]) -> list[dict]:
    """fields: None (all), "compact", or a comma-separated list of field names."""
    tickets = list(tickets)
    if not fields:
        return tickets
    names = COMPACT_FIELDS if fields == "compact" else [f.strip() for f in fields.split(",") if f.strip()]
    return [{k: t.get(k) for k in names} for t in tickets]
