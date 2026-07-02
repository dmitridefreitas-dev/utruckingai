# UTrucking — Engineering Build Plan (Waves A / B / C)

*Technical plan — kept out of the general/exec report. Business-level roadmap lives in `PLAN.md`.*

**Last updated:** 2026-07-02

---

## Status

| Piece | State |
|---|---|
| Quote engine (A) | ✅ built + unit-tested (100% invoice reproduction) |
| Availability/scheduler engine (B) | ✅ built + tested (correct peak-day steering) |
| Billing/leakage guard (C) | ✅ built + tested (exact audit counts) |
| Backend wiring | ✅ `/quote`, `/availability`, `/billing_audit` + MCP tools `get_quote`, `check_availability` — pushed to `main` (commit `4be7802`) |
| **Live?** | ⏳ **No — needs a manual Render deploy** (auto-deploy is off) |

Engines live in `backend/engines.py` (pure logic, no I/O) so they're testable and reused by `main.py`.

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
4. **Damage / condition vision docs** — Claude vision over the item photos already collected.

## Wave D — later
Live ops dashboard · demand forecast · ask-your-data staff copilot · fall return-season automation.

---

## HANDOFF — what you need to do / provide

### ✅ Done from my end
- Backend endpoints — `/quote`, `/availability`, `/billing_audit`, `/dispatch_plan`, `/photo_quote` (live at commit `3790257`).
- **Voice agent updated & published (v34)** — it now calls `get_quote` and `check_availability` on calls.
- Crew capacity set from your numbers (peak ~6, high 8 → 3 → 2). `JOBS_PER_CREW = 15` in `engines.py` — tune that one number if per-crew throughput differs.
- **NEW — customer estimate page** `GET /estimate` — a self-serve web page where a customer uploads a photo *or* types items and gets an instant price. Pushed in `b3852a6`.
- **NEW — hardening + catalog (through commit `180de48`):** quote parser handles number-words to 99 + "a dozen" and never drops an item (bare item = qty 1); ~25 synonyms added (sofa→couch, bicycle→bike…); unpriceable items are **surfaced** as `unmatched` instead of hidden; price book **seeded with common student items** (monitor, printer, computer, fan, speaker, nightstand, table, filing cabinet, futon, wardrobe, crate, toolbox — recorded history still wins). `/photo_quote` now uses **`gemini-2.5-flash`** (2.0-flash's free quota was 429ing) with the key in a header + redacted from errors.

> ⏳ **One action for you:** everything through commit `180de48` is pushed but **not deployed** — click **"Deploy latest commit"** in Render to activate `/estimate`, the photo-quote fix (2.5-flash), the parser fixes, and the new catalog items. (Render auto-deploy is off.)

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
| `GEMINI_API_KEY` | Photo-to-quote (`/photo_quote`) | **Free** at aistudio.google.com. Optional `VISION_PROVIDER=gemini` (default). This is the only one needed now. |
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
