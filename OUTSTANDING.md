# Outstanding

Work on this MCP server that is planned or open. Tick here when done, with the date and the PR.
Plan: [`docs/PLAN_2026-11-09_TICKET_STANDARD.md`](docs/PLAN_2026-11-09_TICKET_STANDARD.md).
Standard it enforces: project-knowledge `standards/leantime-tickets.md` (draft PR #63, agreed or changed at the Mono and Seb meeting on 16 Nov 2026).

---

## Phase 0. Fix what is broken now

- [x] 0.1 `update_ticket` uses `patchTicket` with only the changed fields, so the created date is kept and ticket history is written. Built 9 Nov (this branch). Live check 9 Nov: tags re-sent on #846, `date` did not move.
- [x] 0.2 Restore the created dates of the 24 tickets edited on 9 Nov with `update_ticket(created_date=...)`. Backup: `~/Documents/pixel-nomad/internal/infra/leantime_original_dates_2026-11-09.tsv`. Done 9 Nov: #846 first, then the other 23. All 24 checked against the backup, all match.
- [x] 0.3 `list_tickets` filters: `assignee`, `status` (`open`, `done`, codes), `tag` (exact or `prefix*`), `due_before`, `fields` (`compact` or a list). Built 9 Nov.
- [x] 0.4 Tests with a fake RPC endpoint, no live writes: `uv run --group dev pytest`. 12 tests, 9 Nov.

## Phase 1. One tool per rule (after 16 Nov agreement)

- [ ] `close_ticket(ticket_id, evidence)`: status 0 plus the comment; refuses empty evidence (rule A1)
- [ ] `move_due_date(ticket_id, new_date, reason)`: patches the due date, comments old, new and reason (A3)
- [ ] `set_status(ticket_id, status, note)`: Blocked and Waiting need a note; In Progress runs the 2-at-a-time check (A4, A5)
- [ ] `set_top5(user_id, monday, ticket_ids)`: tag `top5-YYYY-MM-DD`, High, max 5; last week's High not in the five go to Medium or Low (A6)
- [ ] `find_tickets(project_id, text)`: open tickets that match, used before every create (B agent rule 2)
- [ ] `my_week(user_id)`: top 5, In Progress, Blocked, overdue, stale (A5 to A7)
- [ ] `stale_tickets(project_id?)`: In Progress over 7 days, New over 30 days; flags only (A7). First check an RPC method returns ticket history

## Phase 2. Checks inside create and update (after 16 Nov agreement)

- [ ] Refuse priority 1 (Critical) and 2 (High); High only through `set_top5`
- [ ] Refuse a bot user (`task-loop-key`, `sales-key`) as assignee
- [ ] No OUTCOME or DONE WHEN: tag `needs-shaping`, clear the assignee, priority Low, say so
- [ ] Refuse a third In Progress ticket for one person
- [ ] Refuse text that looks like a credential
- [ ] Warn: description over about 150 words, headline over 90 characters, likely duplicate
- [ ] `close_ticket` on a `human-led` ticket needs a person's API key

## Phase 3. Roll-out (week of 23 Nov)

- [ ] Mono's skills use the new tools: `client-status-sweep` (and `seb_week.py`: stale and WIP flags), `seb-agent-task-writer`, `leantime-delivery-setup`, `crm-capture-workflow`, `leantime-project-map`
- [ ] Reconnect `/mcp` in every open Claude session after each release
- [ ] Ask Seb on 16 Nov: do `task-loop-key` and his agents use this MCP or the API directly? If directly, decide how the checks reach them
- [ ] One-off priority clean-up, only with Seb's yes per ticket, never in bulk

## Review

- [ ] 7 Dec 2026, with the standard: what got easier, what nobody follows
