# UTrucking — Engineering Build Plan (Waves A / B / C)

*Technical plan — kept out of the general/exec report. Business-level roadmap lives in `PLAN.md`.*

**Last updated:** 2026-07-04

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
| **Test suite + CI** — `pytest` (40 cases) + GitHub Actions on every push | ✅ green locally and in workflow config |
| Backend wiring | ✅ all endpoints + MCP tools pushed to `main` (Round 5 `7e11720`; Round 6 pushed on top) |
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
| `GEMINI_API_KEY` | Photo-to-quote, ask-your-data copilot, any-item AI matching | **Free** at aistudio.google.com. Optional `VISION_PROVIDER=gemini` (default), `GEMINI_MODEL` (default `gemini-2.5-flash`; calls auto-fall back to `2.5-flash-lite` → `2.0-flash` on rate limits). This is the only one needed now. |
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
- **Staff-key gate is built but dormant.** The PII/ops endpoints (`/lookup_student`, `/dispatch_plan`, `/billing_audit`, `/debug_sheets`) enforce an `x-utrucking-key` header **only when `API_SECRET` is set** in Render (currently unset = open). Turning it on is a 3-step coordinated change — follow **CONNECTIONS.md → Security activation runbook** (set the env var + add the header to the Retell tool so voice keeps working; the `/ops` page already prompts staff for the key). A per-IP verification limiter (15 fails/hr) and the existing per-name lockout (5 fails/15 min) are already active regardless.
