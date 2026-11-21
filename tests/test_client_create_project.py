# SPDX-FileCopyrightText: 2026 Pixel Nomad
#
# SPDX-License-Identifier: MIT

"""create_project wraps fields in `values` and drops nulls. No live Leantime."""

import asyncio

from leantime_mcp.client import LeantimeClient


class FakeClient(LeantimeClient):
    def __init__(self):
        super().__init__("https://leantime.invalid", "test-key")
        self.calls = []

    async def call(self, method, params=None):
        self.calls.append((method, params))
        return 41


def test_create_project_wraps_values_and_drops_null_client():
    c = FakeClient()
    asyncio.run(c.create_project(name="P", details="d", clientId=None))
    assert c.calls == [("leantime.rpc.Projects.addProject", {"values": {"name": "P", "details": "d"}})]


def test_create_project_keeps_client_id():
    c = FakeClient()
    asyncio.run(c.create_project(name="P", clientId=1))
    assert c.calls[0][1] == {"values": {"name": "P", "clientId": 1}}
