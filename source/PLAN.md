# UTrucking AI Phone Assistant — Plan, Progress & Roadmap

**Last updated:** 2026-07-03 · **Live agent:** v34 · **Backend:** latest pushed (`f4734b3`; one-click Render deploy activates the newest tools)

> **How to read this.** Four parts, in order:
> **1 — What's been done** (built, tested, live). **2 — Where the value is added** (in dollars, from our own data). **3 — What's next** (the roadmap). **4 — What's required** to get there (a phone number, SMS, accounts, and their costs).

---

# Part 1 — What's been done

The assistant is **live and fully tested**. It answers calls in a warm, natural voice, looks up any student's order across **both** data sheets, verifies the caller's identity before sharing anything, answers one question at a time, quotes prices on the call, handles general questions from a knowledge base, and transfers to the team on request. The backend is fixed and current: the item/invoice sheet now loads (**654 records**) and the name-match was tightened to reduce wrong-person matches.

### Delivered & live

| Capability | Status |
|---|---|
| Order lookup by name (handles mispronounced / misspelled names) | ✅ Live |
| Natural, one-answer-at-a-time conversation (no rambling) | ✅ Live |
| Identity verification — name **plus** a second detail | ✅ Live |
| Privacy protection — never reveals another student's data | ✅ Live |
| Two-sheet join (dispatch logistics + invoice/item detail) | ✅ Live |
| **Instant price quote on the call** — *"five boxes and a mini fridge" → "about $133"* | ✅ Live (v34) |
| **Busy-day steering** — offers open days when a caller asks for a slammed one | ✅ Live (v34) |
| Pricing / service questions from the knowledge base | ✅ Live |
| Transfer to the office at (314) 266-8878 | ✅ Live |
| Safety guardrails (stays on-task, resists misuse) | ✅ Live |
| Post-call logging (found, order ID, resolution, sentiment) | ✅ Live |

### Built & ready (activate on the next one-click deploy)

| Capability | Status |
|---|---|
| **One front-facing dashboard** — all tools behind six cards (chat, voice, estimate, ask-your-data, insights, ops); Back button / Esc to return. Redesigned: animated starfield, orbit hub, glass cards, one brand family across every tool page, fully mobile-checked | 🟢 Built — deploy to go live |
| **Estimate: photo + description together** — typed counts override the photo, extra typed items are added, every line shows its source; typo-tolerant parser with visible closest-match ("you said X") | 🟢 Built — deploy to go live |
| **Any-item pricing (AI matching)** — items not on the price list are matched to the closest priced item and shown transparently; verified on an 80-item student-goods gauntlet (80/80, nothing dropped). AI calls ride a 3-model fallback chain so free-tier rate limits don't take tools down | 🟢 Built — deploy to go live |
| **Customer self-serve estimate page** — snap a photo *or* type items → instant price | 🟢 Built — deploy to go live |
| **Photo-to-quote (AI vision)** — detects items in a photo and prices them (free Gemini tier) | 🟢 Built — deploy to go live |
| **Web chat assistant (SMS preview)** — quotes, pickup dates & identity-verified order lookup; no phone number needed | 🟢 Built — testable now |
| **Browser voice assistant** — same brain, spoken in the browser (free, no Retell minutes) | 🟢 Built — deploy to go live |
| **Business insights dashboard** — live revenue, top items, upsell pairs, demand, funnel, data-quality scorecard | 🟢 Built — deploy to go live |
| **Ask-your-data staff copilot** — plain-English questions on aggregate stats (refuses individual-customer data) | 🟢 Built — deploy to go live |
| **Billing-leakage audit** — flags $0 / missing-invoice / missing-order rows | 🟢 Built |
| **Dispatch / route planner** — clusters a day's pickups by building and splits crews | 🟢 Built |
| **Ops Command Center** — staff page: pick a day → balanced crew routes + printable run sheets (staff-key-gated) | 🟢 Built — deploy to go live |
| **Next-season demand forecast** — projects the peak window, crews needed, and the fall return season from this year's shape; shown as an Insights planner card | 🟢 Built — deploy to go live |
| **Repeat-customer multi-order lookup** — a caller with several orders picks which one (by order #, service, or month) before the identity gate | 🟢 Built — deploy to go live |

> **Privacy note (identity gate).** Order lookups verify a **second detail** — the caller's building or the last-4 of their phone — before any personal data is shared, on both the phone line and the web chat. This works today with **no phone number**. **Future option:** once a texting number is live, this gate can be upgraded to a **one-time SMS code** (the strongest identity check) with no change to the rest of the flow.

### Documentation
Flow maps, connections inventory, QA log, executive deck, and a full **Data & Revenue Audit** — all in this report.

---

# Part 2 — Where the value is added

Every number below is from UTrucking's own dispatch and invoice data (see the **Data & Revenue Audit**).

- **It protects the money-days.** **$87,782** was invoiced in a **13-day** move-out sprint, and **74% of it landed in just 5 days**. When a caller asks for one of those packed days, the assistant now steers them to an open day — so the peak stops overflowing and dropping orders.
- **It quotes instantly, consistently.** The box drives **65% of revenue** on **96.9%** of orders. The assistant (and the new estimate page) price it the same way every time — no under-quoting, no waiting for a callback.
- **It turns your photo data into a moat.** UTrucking already collects item photos at pickup. The **photo-to-quote** tool turns that into an instant customer-facing estimate no competitor can easily copy.
- **It plugs the leaks.** The audit found **~$1,056** of billing leakage ($0 / missing-invoice orders) and **212** un-dispatched orders. The billing audit surfaces the leakage today; the booking flow (Part 3) stops it at the source.
- **It deflects the repetitive calls.** "Where's my stuff / what did I order / how much" now get answered without a person — the front desk stops repeating itself.

**The single biggest lever, from the data:** raise the box price **$2 → +$5,186/year (+5.9%)** at near-zero risk. It's a management decision; the assistant then quotes the new price automatically.

---

# Part 3 — What's next

The theme: turn the assistant from **answering** into **doing**. We build in three outcome-focused waves, one tool at a time, each tested against real data before the next. **Wave D is logged for later.**

### Wave A · Win more bookings  🟢 building first
| Tool | What it does |
|---|---|
| **Customer estimate page** (photo or text) | Self-serve instant quote — *built, deploys next* |
| **Web + SMS booking assistant** | The phone agent's brain, on text and web chat — students text, they don't call |
| **Spanish parent line** | Multilingual voice so parents can handle logistics & payment |
| **Group / referral booking** | Roommates / floors book together — dorms already cluster, cutting cost per stop |

### Wave B · Survive the peak  🟢 after A
| Tool | What it does |
|---|---|
| **Book / reschedule / cancel on the call** | The receptionist replacement — the biggest staff-time win |
| **Reminders & confirmations** | *"Your pickup is tomorrow — reply to reschedule"* — cuts no-shows |
| **Auto-dispatch + routing** | Clusters orders by building, sequences stops, assigns crews — attacks the 212-order backlog |
| **Movers' field app** | Crew route + item lists + photo/complete, auto-writes status back — ends "unknown building" |

### Wave C · Stop leaking money  🟢 after B
| Tool | What it does |
|---|---|
| **Invoice automation + leakage guard** | Auto-invoice; block $0 / missing-invoice orders — recovers the ~$1,056 gap |
| **Payment chaser** | SMS follow-up with a pay link — faster cash |
| **Damage / condition vision docs** | Auto-tags item condition from photos already taken — dispute protection + a protection-plan upsell |

### Wave D · See & predict  🟢 built
The **live ops dashboard** (Business insights), the **"ask-your-data" staff copilot**, the **Ops Command Center** (daily crew routing + run sheets), and a **next-season demand forecast** are all **built and verified against the live sheets**. The forecast projects the peak window and the crews it needs (live: the peak day runs **334 pickups → ~23 crews' worth of work**), the move-out-window share, and the fall **return season** (Rental Returns ≈ 13–25% of volume). Repeat customers with several orders are now disambiguated before the identity gate. Still logged for later: fall return-season **outbound automation** ("want your stuff back?" SMS), which needs booking write-back + a texting number.

### The four moves the AI caller itself will run
All four unlock from the **same booking capability** (Wave B) — build it once, the assistant executes all of them:

1. **Smooth the peak** — offer the nearest open day first, spreading load off the two days that hold 74% of revenue.
2. **Upsell the basket** — after the core order, offer the add-ons the data shows people take (Plastic Container $18, Mini Fridge $23).
3. **Close the leak** — never finalize a storage booking with a $0 total or missing invoice.
4. **Clean the data at the source** — confirm the correct building and a working phone at booking, killing the "unknown building" rows and enabling caller-ID next season.

*(Two audit moves are **not** phone tasks: setting the box price is management's call; clearing the dispatch backlog is the ops team's.)*

---

# Part 4 — What's required to go further

What's built runs on the current setup at **no extra cost**. Everything below needs a simple account — costs are small and mostly usage-based.

| To enable… | You provide | Rough cost |
|---|---|---|
| Quote engine · estimate page · scheduler · route planner · billing audit | **Already built** on the current backend | **$0 extra** |
| **A real phone line** for the assistant | A phone number in Retell (or port a Twilio number) | ~$1–3 / mo + ~$0.07–0.10 / min |
| **Text / SMS** (reminders, confirmations, pay-links) | A **Twilio** account + number | ~$1–2 / mo + ~$0.008 / text |
| **Photo-to-quote** & damage-photo tagging (AI vision) | A vision-AI key — **free tier (Google Gemini)** | **$0** on the free tier |
| **Booking / rescheduling + auto-invoices** | A **Google service account** (edit access) *or* a small database | **free** |
| **Card payments / pay-links** | A **Stripe** account | per-transaction fee |

**The key unlock is booking write-back.** Reading the sheets is free and live; *writing* to them (to book, reschedule, or invoice) needs the free Google service account or a small database. That one piece turns on most of Wave B and C.

**To go live on a real phone line:** provision a Retell number (budget a one-time **~$20** for the number + first-month testing), then the caller-ID greeting and outbound reminders become possible.

---

## Appendix — Future-proofing before scale

Small investments now that prevent expensive breakage later:

| Area | Today | Risk if left | Recommended before scale |
|---|---|---|---|
| **Deploys** | Render auto-deploy is **OFF**; deploys are manual | A fix silently never ships | Re-enable auto-deploy **or** wire a deploy hook |
| **Data store** | Google Sheets read as CSV per call | Fine for reads; **can't handle concurrent writes** (needed for booking) | Move to **Postgres on Render** (free/$7 tier) when booking lands |
| **Uptime** | Render free tier spins down → cold start on first call | First caller of the hour waits ~30–60s | `keep_alive` helps; a **paid instance (~$7/mo)** removes cold starts |
| **Backend access** | Endpoints are open (`CORS *`, no auth) | Anyone can call the API | Add a shared secret/header check |
| **Join key** | Name-based join across two sheets | Multi-order customers can mix records | Join on **`order_id`** |
| **Backups** | Live sheets only | Accidental edit = data loss | Nightly export/backup of both sheets |
| **Secrets** | Keys in Render env vars | Exposure if a repo is public | Keep in env vars; rotate periodically; keep the backend repo private |
