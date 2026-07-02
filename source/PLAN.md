# UTrucking AI Phone Assistant — Build Plan, Progress & Roadmap

**Last updated:** 2026-07-02 · **Live agent:** v33 · **Backend:** commit `282d7b0` (deployed)

---

## Where we are today

The assistant is **live and fully tested**. It answers calls in a warm, natural voice, looks up any student's order across **both** data sheets, verifies the caller's identity before sharing anything, answers questions one at a time, handles general questions from a knowledge base, and transfers to the team on request. As of 2026-07-02 the backend is fixed and redeployed: the item/invoice sheet now loads (654 records) and the name-match cutoff was tightened to reduce false matches.

---

## Delivered so far

| Capability | Status |
|---|---|
| Order lookup by name (handles mispronounced / misspelled names) | ✅ Live |
| Natural, one-answer-at-a-time conversation (no rambling) | ✅ Live |
| Identity verification — name **plus** a second detail | ✅ Live |
| Privacy protection — never reveals another student's data | ✅ Live |
| Two-sheet join (dispatch logistics + invoice/item detail) | ✅ Live |
| Pricing / service questions from the knowledge base | ✅ Live |
| Transfer to the office at (314) 266-8878 | ✅ Live |
| Safety guardrails (stays on-task, resists misuse) | ✅ Live |
| Post-call logging (found, order ID, resolution, sentiment) | ✅ Live |
| Hard-name + impostor stress testing | ✅ Done |
| Documentation: flow maps, connections, QA log, exec deck, data audit | ✅ Done |

---

## Roadmap — from *answering* to *doing*

Each future item below lists **what it entails**, a **build-time estimate**, **what it requires (with real costs)**, and how it **future-proofs** the operation. Estimates assume one developer and the current Render + Google Sheets stack.

### Phase 1 — Information assistant · ✅ DONE (live)
Answers questions, verifies identity, transfers to a human. Deflects the highest-volume, repetitive calls.

---

### Phase 2 — The receptionist replacement · 🕓 NEXT

#### 2a. Schedule / reschedule / cancel a pickup on the call
- **What it entails:** give the agent write-access tools so it can create, move, or cancel a booking during the call, then read back a confirmation. Requires a "source of truth" for availability (time-slot capacity per day).
- **Build time:** ~1–2 weeks (backend write endpoints + 3 Retell tools + confirmation logic + guardrails against double-booking).
- **Requires:** a **Google service account** (free) so the backend can *write* to the sheet — public CSV is read-only; or a small database. No new per-call cost.
- **Future-proofs:** turns the bot from "answers about orders" into "books orders" — the single biggest staff-time saver.

#### 2b. Auto-identify the caller by phone number
- **What it entails:** read Retell's inbound `from_number`, match it to the **Phone** column already in the DISPATCH sheet, and greet the known caller by name — most people never have to spell anything.
- **Build time:** ~2–3 days.
- **Requires:** a **provisioned phone number** (Retell/Twilio ≈ **$1–3 / month** for the number) + voice usage (**≈ $0.07–0.10 / minute** all-in for STT + LLM + TTS). Budget a one-time **~$20** for number setup + first-month testing.
- **Future-proofs:** faster, friendlier calls; foundation for outbound reminders (Phase 3).

#### 2c. Callback / message capture (after-hours)
- **What it entails:** when the office is closed or a transfer fails, take a message (name, number, reason) and log it for the team.
- **Build time:** ~2 days.
- **Requires:** a place to drop messages (a sheet tab or an email via a free SendGrid tier). ~$0.
- **Future-proofs:** zero missed leads outside business hours.

---

### Phase 3 — Scale & growth · 🔭 LATER

#### 3a. New-customer registration (sign up on the call)
- **Entails:** capture a new storage sign-up (name, dorm, dates, service) and write it to the intake sheet. **Build:** ~1 week. **Requires:** write-back (2a) + validation. **Future-proofs:** the bot drives *revenue*, not just service.

#### 3b. Text (SMS) confirmations & booking links
- **Entails:** text order details or a payment/booking link after the call. **Build:** ~3 days. **Requires:** **Twilio** (~$1/mo number + **~$0.0079 per SMS**) or Retell SMS. **Future-proofs:** fewer no-shows, written proof for the customer.

#### 3c. Team notifications (email / Slack)
- **Entails:** post-call summaries pushed to staff. **Build:** ~2 days. **Requires:** Slack webhook (free) or SendGrid free tier. **Future-proofs:** the team sees every call without listening to recordings.

#### 3d. Outbound reminders ("your pickup is tomorrow")
- **Entails:** scheduled outbound calls/texts the day before. **Build:** ~1 week. **Requires:** a scheduler + outbound voice/SMS budget. **Future-proofs:** cuts missed pickups (a direct cost — see the data audit).

#### 3e. Spanish for parents · analytics dashboard
- **Entails:** enable multilingual voice; stand up a live metrics dashboard from call + order data. **Build:** ~2 days (language) / ongoing (dashboard — this report is step one). **Requires:** ~$0 extra. **Future-proofs:** reach + data-driven decisions.

---

## From audit to action — what the AI assistant itself will do

The **Data & Revenue Audit** lists six moves. Here is exactly **who runs each**, and — for the ones the assistant runs — whether it can do it **today** or **next (Phase 2, once booking is enabled).**

| Audit recommendation | On the AI assistant? | Status |
|---|---|---|
| Quote consistent, correct pricing (incl. a new box price) | Yes | ✅ **Already does this** — answers from the knowledge base |
| Confirm the caller's building / room (clean-data first step) | Yes | ✅ **Already does this** — part of the identity gate |
| **Smooth the peak** — steer callers to open shoulder days | Yes | 🕓 Next — needs scheduling (Phase 2a) |
| **Upsell** containers & fridges at booking | Yes | 🕓 Next (Phase 2a) |
| **Close billing leakage** — no booking without a non-zero invoice | Yes + backend rule | 🕓 Next (Phase 2a) |
| **Fix data at the source** — capture clean building + phone at booking | Yes | 🕓 Next (Phase 2a) |
| Raise the box price $2 | No — management decision | 👤 Business sets it; the agent then quotes it |
| Clear the not-dispatched backlog | No — dispatch / ops team | 👥 Operations, not a phone task |

### The four the AI caller itself will do
All four are unlocked by the **same Phase 2 booking capability** — build it once and the assistant executes all of them:

1. **Smooth the peak.** When a caller asks for a slammed day (e.g., May 12), the assistant offers the nearest **open** day/time first — "I have 9 AM on the 15th, or a short wait on the 12th" — spreading load off the two peak days that hold **74%** of the season's revenue. *Needs: booking + a per-day capacity check.*
2. **Upsell the basket.** After the core order, it offers the add-ons the data shows people actually take — **Plastic Container ($18)**, **Mini Fridge ($23)** — nudging basket size above the ~7-item average. *Needs: booking + item catalog.*
3. **Close the leak.** The assistant (plus a backend rule) will not finalize a storage booking with a **$0 total or missing invoice** — the exact gap that cost **~$1,056** this season. *Needs: booking + a validation rule.*
4. **Clean the data at the source.** At booking it confirms and records the **correct building** and a **working phone number** — killing the 80 "unknown building" rows and enabling caller-ID recognition next season. *Needs: booking write-back.*

### What it already does today (no new work)
- **Quotes pricing consistently** from the knowledge base — so a box-price increase needs **zero** agent changes.
- **Confirms building / room** on every verified call as part of the identity gate — the first step of clean-data-at-the-source.

The remaining two moves are **not** phone tasks: setting the price is a management decision, and clearing the dispatch backlog belongs to the ops team.

---

## Expansion roadmap — new AI tools & automations

Beyond the phone assistant, the **same foundation** (Retell + the Render backend + your sheets) can power a full suite of tools. We build in three waves — **A → B → C**, one tool at a time, each tested against real data before the next. **Wave D is logged for later.** *(Impact/effort are directional; dollar figures come from the Data & Revenue Audit.)*

### Wave A · Win more bookings — revenue 🟢 building first
| Tool | What it does | Why it matters |
|---|---|---|
| **Photo-to-quote** | Student photographs their pile; AI counts items and returns an instant itemized quote | You already collect item photos + invoices — a unique data moat; drives conversion & upsell |
| **Web + SMS booking assistant** | The phone agent's brain, on text and web chat | Students text, they don't call; reuses the existing backend |
| **Spanish parent line** | Multilingual voice | Parents handle logistics & payment |
| **Group / referral booking** | Roommates / floors book together | Dorms already cluster — cuts cost per stop |

### Wave B · Survive the peak — operations 🟢 after A
| Tool | What it does | Why it matters |
|---|---|---|
| **Smart scheduler** | Steers callers to open shoulder-day slots | Protects the 74%-in-5-days revenue from capacity loss |
| **Reminders & confirmations** | "Your pickup is tomorrow — reply to reschedule" | Cuts no-shows, pre-fills the schedule |
| **Auto-dispatch + routing** | Clusters orders by building, sequences stops, assigns crews | Attacks the 212-order not-dispatched backlog |
| **Movers' field app** | Crew route + item lists + photo/complete, auto-writes back to the sheet | Ends manual data entry & "unknown building" |

### Wave C · Stop leaking money — finance 🟢 after B
| Tool | What it does | Why it matters |
|---|---|---|
| **Invoice automation + leakage guard** | Auto-invoice; block $0 / missing-invoice orders | Recovers the ~$1,056 gap; clean books |
| **Payment chaser** | SMS follow-up with a pay link | Faster cash |
| **Damage / condition vision docs** | Auto-tag item condition from the photos already taken | Dispute protection + a protection-plan upsell |

### Wave D · See & predict — intelligence 🔭 logged for later
Live ops dashboard · demand forecast (per-building, keyed to the academic calendar) · "ask-your-data" staff copilot · fall **return-season** automation (Rental Returns = 25% of volume).

**Build order & method.** A → B → C, one tool at a time; each is built, tested against real data, then wired into the live agent. Detailed engineering steps and the exact third-party accounts required are tracked in a separate technical plan (kept out of this report).

---

## Future-proofing audit (do these before scaling)

Small investments now that prevent expensive breakage later:

| Area | Today | Risk if left | Recommended before scale |
|---|---|---|---|
| **Deploys** | Render auto-deploy is **OFF**; deploys are manual | A fix silently never ships | Re-enable auto-deploy **or** wire a deploy hook; document the one-button process |
| **Data store** | Google Sheets read as CSV per call | Sheets are fine for reads to a few-thousand rows, but **can't handle concurrent writes** (needed for booking) | Move to **Postgres on Render** (free/$7 tier) when Phase 2a lands |
| **Uptime** | Render free tier spins down → cold-start delay on first call | First caller of the hour waits ~30–60s | `keep_alive` helps; a **paid Render instance (~$7/mo)** removes cold starts |
| **Backend access** | Endpoints are open (`CORS *`, no auth) | Anyone can call `lookup_student` | Add a shared secret/header check |
| **Join key** | Name-based join across two sheets | Multi-order customers can mix records | Join on **`order_id`** |
| **Backups** | Live sheets only | Accidental edit = data loss | Nightly export/backup of both sheets |
| **Secrets** | API keys in local config | — | Keep in Render env vars; rotate periodically |

---

## What each phase unlocks

- **Phase 1** deflects the highest-volume, repetitive calls — the front desk stops answering the same questions.
- **Phase 2** lets the assistant *do* the receptionist's work (booking, rescheduling, caller ID) — the biggest staff-time win.
- **Phase 3** drives growth (sign-ups), proactive service, and multilingual reach.

---

## Dependencies & open items

- Phase 2 / 3 backend features deploy to the Render service (**manual deploy** until auto-deploy is re-enabled).
- **Provision a phone number** in Retell when ready to go live on a real line (~$20 to start).
- Optional: **restore any missing detail** in the SERVICE sheet (item lists are sparse on some rows — see the data audit).
