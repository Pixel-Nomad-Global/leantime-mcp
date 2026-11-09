# SPDX-FileCopyrightText: 2026 Pixel Nomad
#
# SPDX-License-Identifier: MIT

from leantime_mcp.filters import COMPACT_FIELDS, filter_tickets, select_fields

T = [
    {"id": 1, "editorId": "1", "status": "3", "tags": "top5-2026-11-09,build", "dateToFinish": "2026-11-10 00:00:00", "headline": "a", "description": "x" * 500},
    {"id": 2, "editorId": "1", "status": "0", "tags": "build", "dateToFinish": "0000-00-00 00:00:00", "headline": "b"},
    {"id": 3, "editorId": "2", "status": "4", "tags": "", "dateToFinish": "2026-11-30 00:00:00", "headline": "c"},
    {"id": 4, "editorId": "", "status": "-1", "tags": "idea", "dateToFinish": None, "headline": "d"},
]


def ids(ts):
    return [t["id"] for t in ts]


def test_no_filters_returns_everything():
    assert ids(filter_tickets(T)) == [1, 2, 3, 4]


def test_status_open_and_done():
    assert ids(filter_tickets(T, status="open")) == [1, 3]
    assert ids(filter_tickets(T, status="done")) == [2, 4]
    assert ids(filter_tickets(T, status="4,3")) == [1, 3]


def test_assignee():
    assert ids(filter_tickets(T, assignee=1)) == [1, 2]


def test_tag_exact_and_prefix():
    assert ids(filter_tickets(T, tag="build")) == [1, 2]
    assert ids(filter_tickets(T, tag="top5-*")) == [1]
    assert ids(filter_tickets(T, tag="bui")) == []


def test_due_before_skips_missing_due_dates():
    assert ids(filter_tickets(T, due_before="2026-11-15")) == [1]


def test_filters_combine():
    assert ids(filter_tickets(T, assignee=1, status="open", tag="build")) == [1]


def test_fields_compact_and_list():
    compact = select_fields(T[:1], "compact")
    assert list(compact[0]) == COMPACT_FIELDS
    assert "description" not in compact[0]
    assert select_fields(T[:1], "id,headline") == [{"id": 1, "headline": "a"}]
    assert select_fields(T[:1], None) == T[:1]
