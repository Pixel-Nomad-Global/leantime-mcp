# Plan: Leantime MCP changes for the ticket standard

**Date:** 9 Nov 2026, Mono. **Status:** plan, nothing built.
**Follows:** project-knowledge `standards/leantime-tickets.md` (draft PR #63, for the 16 Nov Mono and Seb meeting).
Build only after both agree the standard on 16 Nov. MIRSA globalisation stays Seb's top priority, so Mono's side builds this; Seb reviews.

The idea: the standard says what agents must do; the MCP makes the easy path the right one, and refuses the few things the standard forbids.

---

## Phase 0. Fix what is broken now (no standard needed)

| # | Change | Why |
|---|---|---|
| 0.1 | `update_ticket` calls `leantime.rpc.Tickets.Tickets.patchTicket` with only the changed fields, instead of `updateTicket` with the whole merged ticket | `updateTicket` sets `date` to now on every call (Leantime `Services/Tickets.php` line ~2233), so the created date is lost. `patchTicket` changes only `PATCHABLE_COLUMNS`, keeps `date`, and writes ticket history (`zp_tickethistory`) |
| 0.2 | Restore the created dates of the 24 tickets edited on 9 Nov | Backup: `~/Documents/pixel-nomad/internal/infra/leantime_original_dates_2026-11-09.tsv`. `date` is a patchable column. One-off script, dry run first |
| 0.3 | `list_tickets` filters: `assignee`, `status` (`open` = not 0 or -1), `tag`, `due_before`, and `fields` (`compact` or a list). No filters and no fields still return everything, because `leantime_digest.py` and `seb_week.py` read the full result | One unfiltered call today returns about 4 MB and always spills to a file. Every sweep, Seb page and session pays for it |
| 0.4 | Tests with a fake RPC endpoint, no live Leantime writes | The repo has no tests. Every phase below lands with tests |

## Phase 1. Tools that do one rule each

| Tool | Rule | Behaviour |
|---|---|---|
| `close_ticket(ticket_id, evidence)` | A1 | Sets status 0 and adds the comment. Refuses an empty `evidence` |
| `move_due_date(ticket_id, new_date, reason)` | A3 | Patches `dateToFinish`, comments "moved from X to Y, because Z". Refuses an empty `reason` |
| `set_status(ticket_id, status, note)` | A4 | 1 Blocked and 2 Waiting need `note` (who and what). 4 In Progress runs the WIP check (2.4) |
| `set_top5(user_id, monday, ticket_ids)` | A6 | Tags the five `top5-YYYY-MM-DD` and sets High. Refuses more than 5. Moves last week's High tickets that are not in the new five back to Medium (has a date) or Low |
| `find_tickets(project_id, text)` | B agent rule 2 | Open tickets whose headline or description matches. Used before every create |
| `my_week(user_id)` | A5, A6, A7 | This week's top 5, In Progress, Blocked, overdue, stale. The Seb page and the Monday sweep read this instead of the full dump |
| `stale_tickets(project_id?)` | A7 | In Progress over 7 days, New over 30 days, from ticket history (last change), not `date`. Flags only, never closes. **Check first** that an RPC method returns `zp_tickethistory`; if not, Phase 0.1 makes `date` a true created date and stale falls back to created date plus no comments |

## Phase 2. Guardrails inside `create_ticket` and `update_ticket`

Refusals return a plain sentence saying which rule and what to do instead, so the agent can fix and retry.

| # | Check | Refuse or warn |
|---|---|---|
| 2.1 | Priority 1 (Critical) or 2 (High) | **Refuse.** High only through `set_top5`; Critical only by a person in the Leantime UI |
| 2.2 | Assignee is a bot user (`task-loop-key`, `sales-key`, other API users) | **Refuse** |
| 2.3 | No OUTCOME or no DONE WHEN (description or `acceptanceCriteria`) | **Shape it automatically:** add tag `needs-shaping`, clear the assignee, priority Low, and say so in the reply |
| 2.4 | Status 4 for someone who already has 2 In Progress | **Refuse**, list the two |
| 2.5 | Text that looks like a credential (API key, token, password patterns) | **Refuse** |
| 2.6 | Description over about 150 words, headline over 90 characters | **Warn** in the reply, still create |
| 2.7 | `find_tickets` finds a likely twin in the project | **Warn** with the ticket IDs, still create |
| 2.8 | Tag `human-led` | Pass through; `close_ticket` on a `human-led` ticket needs a person's API key, not a bot key |

## Phase 3. Roll it out

1. Mono's skills switch to the new tools: `client-status-sweep` (and `seb_week.py`: stale flags, WIP), `seb-agent-task-writer`, `leantime-delivery-setup`, `crm-capture-workflow`, `leantime-project-map`.
2. Reconnect the MCP with `/mcp` in every open Claude session (each runs its own server process).
3. Seb's side: **open question for 16 Nov.** Do `task-loop-key` and Seb's agents call Leantime through this MCP or straight through the API? If straight, the guardrails bind only Mono's side. Options: Seb's agents switch to this MCP, or the same checks move into a small Leantime plugin later.
4. One-off clean-up, **only with Seb's yes, ticket by ticket, never in bulk**: High or Critical tickets that are not in a top 5 go to Medium or Low; bot-assigned tickets get `needs-shaping`.

## Order and size

| Phase | Size | When |
|---|---|---|
| 0.1, 0.2 | Small | Any time; fixes a live bug |
| 0.3, 0.4 | Small to medium | Before Phase 1 |
| 1 | Medium | After 16 Nov agreement |
| 2 | Medium | Same PR series as Phase 1 |
| 3 | Small per skill | Week of 23 Nov |

Review with the standard on 7 Dec.
