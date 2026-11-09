# SPDX-FileCopyrightText: 2026 Pixel Nomad
#
# SPDX-License-Identifier: MIT

"""update_ticket sends only the changed fields through patchTicket. No live Leantime."""

import asyncio

import pytest

from leantime_mcp.client import LeantimeClient


class FakeClient(LeantimeClient):
    def __init__(self):
        super().__init__("https://leantime.invalid", "test-key")
        self.calls = []

    async def call(self, method, params=None):
        self.calls.append((method, params))
        return True


def test_update_uses_patch_with_only_changed_fields():
    c = FakeClient()
    asyncio.run(c.update_ticket(2591, 7, status=0))
    assert c.calls == [("leantime.rpc.Tickets.Tickets.patchTicket", {"id": 2591, "values": {"status": 0}})]


def test_update_never_sends_created_date_unless_asked():
    c = FakeClient()
    asyncio.run(c.update_ticket(2591, 7, tags="a,b", dateToFinish="2026-11-20"))
    values = c.calls[0][1]["values"]
    assert "date" not in values
    assert values == {"tags": "a,b", "dateToFinish": "2026-11-20"}


def test_update_maps_assignee_to_editor_id():
    c = FakeClient()
    asyncio.run(c.update_ticket(1, None, assignedTo=2))
    assert c.calls[0][1]["values"] == {"editorId": 2}


def test_update_restores_created_date_when_given():
    c = FakeClient()
    asyncio.run(c.update_ticket(1, None, date="2026-11-05 10:00:00"))
    assert c.calls[0][1]["values"] == {"date": "2026-11-05 10:00:00"}


def test_update_with_nothing_to_change_is_refused():
    c = FakeClient()
    with pytest.raises(ValueError):
        asyncio.run(c.update_ticket(1, 7))
    assert c.calls == []
