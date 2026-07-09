# UTrucking — Engineering Build Plan (Waves A / B / C)

*Technical plan — kept out of the general/exec report. Business-level roadmap lives in `PLAN.md`.*

**Last updated:** 2026-07-09

---

## Status

| Piece | State |
|---|---|
| Quote engine (A) | ✅ built + unit-tested (100% invoice reproduction) |
| Availability/scheduler engine (B) | ✅ built + tested (correct peak-day steering) |
| Billing/leakage guard (C) | ✅ built + tested (exact audit counts) |
| Wave D — insights, `/ask`, `/ops`, forecast, multi-order lookup | ✅ built + tested against live sheets (2026-07-03) |
| Hardening — staff-key gate, per-IP verify limiter, local sheet backup | ✅ built + tested (gate dormant until `API_SECRET` is set — see CONNECTIONS §5) |
| **Round 6 upgrades** — sheet caching, upsell, phone-lookup, deeper forecast + date filters, run-sheet sequencing, condition vision, staff console | ✅ built + audited against live sheets (2026-07-04) |
| **Round 16 — post-call auto-QA** (`/retell_webhook` → LLM judge → `/voiceqa`) | ✅ built + tested (needs `RETELL_API_KEY` for the live call pull) |
| **Round 16 — public MCP endpoint** (`/mcp`, Claude connector + Retell MCP node) | ✅ built + verified over the wire |
| **Round 16 — native Retell regression suite** (`tools/retell_suite.py`, 12 cases) | ✅ 12/12 green, three consecutive runs |
| **Test suite + CI** — `pytest` (**172 cases**) + GitHub Actions on every push | ✅ green locally and in workflow config |
| Backend wiring | ✅ all endpoints + MCP tools pushed to `main` (Round 16 `eb7c279`) |
| Voice agent | ✅ **v43 published** (denoise, voicemail, pronunciation dict, fallback voices, DTMF, scope boundaries, QA webhook) |
| **Live?** | ⏳ **Push done — needs a manual Render "Deploy latest commit"** (auto-deploy is off) |

Engines live in `backend/engines.py` (pure logic, no I/O) so they're testable and reused by `main.py`. The offline suite stubs the web layer (`httpx`, FastMCP, Starlette) so `main.py` imports as pure Python and every engine/endpoint path is unit-tested without a network.

---

## Shared foundation

- Backend: Python (FastMCP + Starlette) on Render, reads both sheets as CSV.
- **Booking write-back is the key unlock** for A (quote→book), B (schedule/reschedule/cancel) and C (invoice creation). It needs either a **Google service account** with edit access, or a small **Postgres** DB on Render. Public CSV is read-only.

## Wave A — win more bookings
1. **Quote engine** ✅ `/quote`.
2. **Photo-to-quote** — vision step (Claude) turns an uploaded photo → item list → `/quote`. *Needs: Anthropic API key + an image upload path (web form / MMS).*
3. **Web + SMS assistant** — reuse the agent brain on chat/SMS. *Needs: Twilio (SMS) or a web widget; reuses `lookup_student` + `/quote`.*
4. **Spanish line** — Retell language config.
5. **Group / referral booking** — booking write-back + a referral field.

## Wave B — survive the peak
1. **Availability engine** ✅ `/availability` (set real daily capacity).
2. **Booking write** (create/reschedule/cancel) — service account → Sheets/DB.
3. **Reminders / confirmations** — Render cron + Twilio SMS.
4. **Auto-dispatch + routing** — cluster by building/day; optional maps API for stop sequencing.
5. **Movers' field app** — lightweight mobile web app writing status/photos back.

## Wave C — stop leaking money
1. **Billing guard** ✅ `/billing_audit` + `should_block()`.
2. **Invoice automation** — generate invoice ID + total at booking; block `$0`.
3. **Payment chaser** — Twilio SMS + Stripe pay-link.
4. **Damage / condition vision docs** ✅ `/condition` page + `/condition_check` — free Gemini vision returns a good/wear/damage read with notes over the item photos already collected (dispute protection + protection-plan upsell hook). *(Built in Round 6; the auto-tag-at-pickup pipeline still rides booking write-back.)*

## Wave D — see & predict  ✅ built (2026-07-03)
1. **Live business dashboard** ✅ `/insights` + `/insights_api` (revenue, top items, upsell pairs, funnel, per-building demand, repeat-rate, data-quality).
2. **Ask-your-data copilot** ✅ `/ask` — aggregate-only, refuses individual-customer PII.
3. **Ops Command Center** ✅ `/ops` — greedy crew-split over `/dispatch_plan` with printable run sheets (staff-key-gated when `API_SECRET` is set).
4. **Next-season demand forecast** ✅ in `compute_metrics` — peak window + crews-needed, move-out-window share, August return season; surfaced as the Insights **planner** card.
5. **Repeat-customer multi-order lookup** ✅ callers with several orders disambiguate by order #, service, or month before the identity gate.
6. Fall return-season automation (SMS "want your stuff back?") — still later; needs booking write-back + Twilio.

## Round 6 — resilience, revenue, and a real test harness  ✅ built (2026-07-04)
Eight upgrades that need no new accounts (nothing here requires the $20 phone number or Apps Script write-back):
1. **Sheet caching + resilience** — `fetch_csv_rows` now fronts both sheets with a 60s TTL cache (`SHEET_TTL`) and, on any fetch failure, **serves the last good copy** instead of `[]`. Cuts per-call re-downloads and survives a transient Sheets outage.
2. **Upsell engine** — `engines.upsell_pairs()` mines item co-occurrence from the service sheet; `main._attach_upsell()` appends a "most people also add…" line to every quote path (phone/chat/voice/estimate/photo), skipping cart items, non-storage supplies, and unpriced partners.
3. **Identify-by-phone** — `_phone_digits` / `_match_by_phone` + a `phone` arg on `do_lookup_student`: resolve a caller by their on-file number (last-10 match), disambiguate multi-name numbers, still gate identity. `lookup_student` tool + endpoint thread the `phone` param. (Auto-greet on inbound is deferred to the provisioned number.)
4. **Deeper forecast + date-range insights** — `analytics.compute_metrics` adds `revenue_forecast` (avg order, peak-day, move-out-window revenue) and `building_peak_timing` (per-building peak date + offset). `/insights_api` accepts `from`/`to`; `_rows_in_range` + `_parse_any_date` filter both sheets; the page renders an empty-range message instead of `undefined`.
5. **Run-sheet sequencing + capacity** — `dispatch_plan` orders each building's stops by a natural room key (`_room_key`, type-tagged tuples so numbers/letters never cross-compare) and numbers each stop; return payload adds `capacity` / `jobs_per_crew` / `utilization_pct`. `/ops` gains CSV export + print.
6. **Condition vision** — vision refactored to a shared `_vision_json()` with `_vision_items` / `_vision_condition` wrappers + `_load_image_arg()`; new `/condition_check` endpoint and `/condition` page (upload → color-coded condition read).
7. **Staff console** (`/staff`) — one page fetching `/dispatch_plan` + `/billing_audit` (key-gated) + `/insights_api`: today's run sheet, revenue-to-recover flags, forecast, data-health.
8. **Test suite + CI** — `tests/` (`test_engines`, `test_main`, `test_analytics`, `test_edges`) with a `conftest.py` that stubs the web layer so `main.py` imports offline; `pytest.ini` scopes collection; `.github/workflows/tests.yml` runs it on every push. **40/40 green.**

## Round 16 — measure every call, publish behind a gate  ✅ built (2026-07-09)
The step from "works when I test it" to "measured in production, gated on release." Nothing here needs a phone number or write-back.

1. **Post-call auto-QA** — `POST /retell_webhook` takes Retell's `call_ended` / `call_analyzed` events; `_judge_transcript()` LLM-scores the transcript once against a fixed rubric (`identity_gate_held`, `over_promised`, `wrong_info`, `caller_frustrated`, 0–100 score, issue list) into a bounded `_QA_CALLS` scoreboard (oldest evicted at `_QA_MAX`). Judging is idempotent per call, so the follow-up `call_analyzed` event never double-charges the model. The endpoint **always** returns `{"ok": true}` — a webhook must never error back at Retell.
2. **Voice-QA API + page** — `GET /voice_qa_api` (staff-key gated) pulls recent calls via Retell `v3/list-calls` (`RETELL_API_KEY`), merges each call's `latency.e2e.p50`, `call_cost.combined_cost` (cents → dollars), sentiment, voicemail flag and disconnection reason with the stored judge scores, and aggregates them. Without the key it degrades to the webhook-only scoreboard rather than failing. `?judge=1` scores up to 5 recent unjudged calls on demand. `GET /voiceqa` renders it; **transcripts never leave the server**.
3. **Public MCP endpoint** — `FastMCP(..., stateless_http=True, json_response=True, transport_security=…)`. The SDK's DNS-rebinding guard defaults to a localhost-only Host allowlist, so the deployed `/mcp` answered every remote client with **421 Invalid Host**; the allowlist now includes the public host. `stateless_http` means no server-side session to lose across Render restarts. Result: `/mcp` works as a **Claude custom connector** and as a **Retell native MCP node**.
4. **Aggregate-only MCP tool** — `business_insights()` returns the `_metrics_brief` aggregate summary (revenue, demand, pricing levers, upsell lift, funnel, data quality). No individual customer data; asserted in tests and verified live against the real sheets.
5. **MCP auth** — `_McpAuthMiddleware` (pure ASGI, wraps the app) gates `/mcp` on `x-utrucking-key` **or** `Authorization: Bearer` when `API_SECRET` is set; unset = open, matching the dormant-gate rollout used everywhere else.
6. **Native regression suite** — `tools/retell_suite.py` defines 12 Retell test cases (simulated-caller persona + tool mocks + graded metrics), syncs them idempotently by name, runs `create-batch-test` against a chosen LLM version, polls, and exits non-zero on any failure. `sync` / `run --version N` / `all --version N`.
7. **Agent knobs (v43)** — `denoising_mode: noise-and-background-speech-cancellation`, `voicemail_option` (static-text drop), 12-entry IPA `pronunciation_dictionary` for building names, `fallback_voice_ids`, `user_dtmf_options` (keypad verifier entry), `enable_dynamic_voice_speed`, `enable_expressive_mode`, `timezone: America/Chicago`, `handbook_config.scope_boundaries`, `webhook_url` → `/retell_webhook?key=…`, and `x-utrucking-key` on all four custom tools.
8. **Bug caught by the new suite** — the agent answered off-topic questions (invented weather guidance, told a joke). Fixed via a `# STAYING ON TOPIC` prompt section + `scope_boundaries`. **pytest 155 → 172**; 14/14 playground sweep; 12/12 native suite ×3 runs.

> **Harness gotchas worth keeping.** `agent-playground-completion` returns **only that turn's new messages** — accumulate history client-side or every multi-turn test silently runs on a truncated transcript. And LLM judges flip-flop on **compound** metrics: keep one atomic, time-scoped assertion per metric, and always read the transcript before believing a failure.

---

## HANDOFF — what you need to do / provide

### ✅ Done from my end
- Backend endpoints — `/quote`, `/availability`, `/billing_audit`, `/dispatch_plan`, `/photo_quote` (live at commit `3790257`).
- **Voice agent updated & published (v34)** — it now calls `get_quote` and `check_availability` on calls.
- Crew capacity set from your numbers (peak ~6, high 8 → 3 → 2). `JOBS_PER_CREW = 15` in `engines.py` — tune that one number if per-crew throughput differs.
- **NEW — customer estimate page** `GET /estimate` — a self-serve web page where a customer uploads a photo *or* types items and gets an instant price. Pushed in `b3852a6`.
- **NEW — hardening + catalog (through commit `180de48`):** quote parser handles number-words to 99 + "a dozen" and never drops an item (bare item = qty 1); ~25 synonyms added (sofa→couch, bicycle→bike…); unpriceable items are **surfaced** as `unmatched` instead of hidden; price book **seeded with common student items** (monitor, printer, computer, fan, speaker, nightstand, table, filing cabinet, futon, wardrobe, crate, toolbox — recorded history still wins). `/photo_quote` now uses **`gemini-2.5-flash`** (2.0-flash's free quota was 429ing) with the key in a header + redacted from errors.
- **NEW — unified dashboard + data tools (through commit `f4734b3`, 2026-07-03):**
  - `GET /` = one branded dashboard (starfield/orbit design, mobile-checked) opening all five tools: chat, browser voice, estimate, ask-your-data, business insights. Chat + voice ARE the live phone agent's brain, hosted for free testing.
  - `analytics.py` — revenue/demand/funnel/upsell/data-quality metrics power `GET /insights` (+`/insights_api`) and ground `POST /ask_api` (aggregate-only copilot; refuses individual-customer questions; answers pricing questions with concrete numbers).
  - **Any-item pricing:** deterministic ladder (alias → typo-fuzzy → word containment) then an **AI second-chance mapping** that matches unlisted items ("baseball bat") to the closest catalog item and shows it on the line. 80-item student gauntlet passes 80/80, nothing silently dropped.
  - **Rate-limit resilience:** every Gemini call walks a 3-model fallback chain (separate free-tier quota buckets) — verified live through a real 429.
  - Estimate page accepts **photo + description together** (typed counts override the photo; text-only items are added; each line is tagged with its source).

> ⏳ **One action for you:** everything through commit **`f4734b3`** is pushed but **not deployed** — click **"Deploy latest commit"** in Render to activate the dashboard, the data tools, the any-item pricing and the 429 fix. (Render auto-deploy is off.)

### ⏸ Deferred today — Web + SMS booking assistant (deliberate)
Not wired yet, on purpose — wiring it now would cause problems, not progress:
- **SMS** can't send or receive anything without the **$20 Retell/Twilio number + Twilio credentials** — a webhook now would be dead, untestable code.
- **"Booking"** means *writing* to the sheet, which needs the free **Google service account** (not set up yet). Without it, an assistant can only quote/check availability — it can't actually book.
- **Order lookups on a public web page would leak customer PII** — the voice agent has an identity gate for exactly this reason. A web assistant needs that gate built first.
- The safe, no-account slice — **instant web quotes** — already ships as the `/estimate` page.

**Unblock sequence:** get the SMS number + Twilio keys **and** set up the Google service account → then wire web assistant (with identity gate) + SMS + booking write-back together (~1 week).

> 📄 **Booking write-back setup is ready to go** — a free, ~5-minute **Google Apps Script** method (no Google Cloud, no service account, no billing) is written up in **`SETUP_BOOKING_WRITEBACK.md`**. Do it anytime; the write-back code stays **dormant (not wired)** until you send the SMS number, then I plug it all in at once. Env vars it produces: `SHEETS_WEBAPP_URL`, `SHEETS_WEBAPP_SECRET`.

### Environment variables to add in Render (Service → Environment)
| Variable | For | Notes |
|---|---|---|
| `GEMINI_API_KEY` | Photo-to-quote, ask-your-data copilot, any-item AI matching, **post-call QA judging** | **Free** at aistudio.google.com. Optional `VISION_PROVIDER=gemini` (default), `GEMINI_MODEL` (default `gemini-2.5-flash`; calls auto-fall back to `2.5-flash-lite` → `2.0-flash` on rate limits). |
| `RETELL_API_KEY` | The Voice-QA page's live call pull (latency / cost / sentiment history) | Optional. Without it `/voiceqa` still works, but shows only calls reported by the webhook since the last restart. |
| `API_SECRET` | Activates the staff gate on every PII/ops endpoint **and** `/mcp` + `/retell_webhook` + `/voice_qa_api` | The agent already sends this key (Round 16), so setting it is now a **single step** — no agent republish. Use the value in `CONNECTIONS.md → Security activation runbook`. |
| `TWILIO_ACCOUNT_SID` · `TWILIO_AUTH_TOKEN` · `TWILIO_FROM` | SMS (reminders, texts, pay-links) | for the Wave B/C SMS tools |
| `SHEETS_WEBAPP_URL` · `SHEETS_WEBAPP_SECRET` | Booking + invoice write-back | free Google Apps Script web app — see `SETUP_BOOKING_WRITEBACK.md` |
| `STRIPE_API_KEY` | Card pay-links | payment chaser |

### Accounts / keys for the external-service parts (build code ready, you provide the account)
| Capability | You provide | ~Cost |
|---|---|---|
| SMS (reminders, web+SMS assistant, payment chaser) | **Twilio** account + a number + auth token | ~$1–2/mo number + ~$0.0079/SMS |
| Real inbound phone line for the agent | **Retell** phone number (or port Twilio) | ~$1–3/mo + per-min usage |
| Photo-to-quote / damage vision | **Anthropic API key** (Claude vision) | usage-based |
| Booking write-back + invoice write | A free **Google Apps Script** web app on the sheet (or a service account / small DB) | **free** |
| Payment links | **Stripe** account + API key | per-transaction |

### 🔒 Security — do soon
- **`utrucking-mcp` is a PUBLIC repo and contains the live Google Sheet IDs**, and the sheets are shared *"anyone with the link."* Anyone who finds the repo can read customer names/phones.
- **Recommended:** make `utrucking-mcp` **private**, and/or restrict the sheets to a **service account** instead of public-link. (The portfolio repo `utruckingai` already has these IDs redacted/excluded.)
- **Staff-key gate is built but dormant.** The PII/ops endpoints (`/lookup_student`, `/dispatch_plan`, `/billing_audit`, `/debug_sheets`, `/sample_ids`) enforce an `x-utrucking-key` header **only when `API_SECRET` is set** in Render (currently unset = open). Turning it on is a 3-step coordinated change — follow **CONNECTIONS.md → Security activation runbook** (set the env var + add the header to the Retell tool so voice keeps working; the `/ops` page already prompts staff for the key). A per-IP verification limiter (15 fails/hr) and the existing per-name lockout (5 fails/15 min) are already active regardless.
