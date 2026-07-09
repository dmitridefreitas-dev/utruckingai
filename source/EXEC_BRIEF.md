# UTrucking AI — Executive Brief

*One page. What's live, what's next, and the biggest levers. Every number is from our own data.*

---

## Where it stands
A **live AI phone assistant** plus a **data-backed plan** to automate the front desk and tighten the back office. Built, tested, and deployed.

## ✅ Live today
- **Answers the phone** — looks up any student's order, verifies who they are, and transfers to the team. Deflects the repetitive calls.
- **Quotes prices on the call** — *"five boxes and a mini fridge"* → *"about $133"* in one sentence.
- **Protects the busy days** — steers callers to open days so the two peak days that carry **74% of revenue** stop overflowing.
- **Backend fixed** — invoice/item data that was showing empty now loads (654 records); wrong-person matches tightened.

## 🟢 Just built (one deploy from live)
- **One dashboard, six tools** — a single link opens chat, voice, estimate, ask-your-data, business insights and a staff ops center, in a polished branded interface that works on any phone.
- **Self-serve estimate page** — a customer photographs their pile *and/or* types what they have and gets a price on the spot. Understands typos, word-quantities and **any item** — things not on the price list are AI-matched to the closest priced item, shown transparently (*"1× Skateboard — you said 'baseball bat'"*). Free AI vision, no subscription.
- **Web chat + browser voice** — the live phone agent's exact brain, testable by text or voice for **free** (no call minutes), with the same identity-verified order lookup.
- **Business insights + ask-your-data** — a live dashboard of revenue/demand/data-quality, and a plain-English analyst that answers questions like *"how much should I raise prices?"* with concrete numbers.
- **Ops command center + demand forecast** — staff pick a day and get balanced crew routes with **sequenced, printable run sheets**, plus a next-season forecast that now projects the peak week, the crews it needs (the live peak day runs **334 pickups**), and the **revenue** in that window. A one-screen **staff console** rolls up today's route, billing to recover, forecast, and data health. Repeat customers with multiple orders are handled cleanly on the phone.
- **Sells smarter on every quote + protects on every move** — each quote suggests the add-ons students actually store together, now **ranked by the dollar lift they add to a typical order**: a boxes-only cart (**~36% of all orders**) gets steered to the higher-value **rolling cart** instead of the cheaper mini fridge. A **photo condition check** reads good/wear/damage for dispute protection, the chat now **answers in Spanish**, and staff get a **truck-space estimate** on each quote for crew planning. The order lookup can also recognize a returning **caller by their phone number**.
- **Built to stay up** — a caching layer keeps quotes and lookups working through a transient Google Sheets outage, learned AI item-matches are cached so repeats are instant and free, and a **172-test automated suite runs on every code change** so nothing quietly breaks.
- **Every call is graded, automatically** — the moment a call ends, an AI reviewer scores it: did the assistant verify identity before sharing anything, did it promise something it can't do, did it get a fact wrong, was the caller frustrated? Staff see a **Voice QA** scoreboard with the score, the caller's mood, how fast the assistant responded and what the call cost. A mistake now surfaces on the first call that hits it, instead of at the next audit.
- **Nothing ships untested** — 12 simulated callers (including someone impersonating a student and refusing to verify, and a prompt-injection attack) run against every new version of the assistant before it goes live. This caught a real flaw: the assistant was answering off-topic questions instead of politely redirecting. Fixed before release.
- **Sounds right on a noisy move-out day** — background-speech filtering, correct pronunciation of the dorm names, keypad entry for a phone number or order number, a backup voice if the speech provider goes down, and voicemail detection so it never talks to an answering machine.
- **Your data, inside Claude** — the same secure backend can now be connected to Claude as a private data source, so the owner can ask *"how many pickups tomorrow, and which buildings?"* from their phone. Aggregate business data only; customer details stay locked behind the same identity gate.

## 📊 The numbers that matter
| | |
|---|---|
| **$87,782** | invoiced in a **13-day** move-out sprint — **74% in 5 days** |
| **65%** | of revenue from one product (the UTrucking Box), on **96.9%** of orders |
| **86%** | of orders completed · **~$1,056** billing leakage found · **212** orders left un-dispatched |

## 🎯 Highest-impact moves (ranked)
1. **Raise the box $2 → +$5,186/year (+5.9%).** One number, near-zero risk.
2. **Smooth the peak.** The assistant fills the slow days so the busy days stop dropping orders — protects the 74%.
3. **Photo-to-quote — now built.** Customers photograph their pile; AI quotes instantly. Our item photos make this a moat no competitor has.

## ⏭️ What's next
Turn the assistant from *answering* to *doing*: **book pickups on the call**, **text reminders & confirmations**, **auto-generate invoices**, and **run the fall return-season outreach** by text. All of it rides on the system already built — the crew-routing and forecast pieces are done.

---

**Bottom line:** front-desk deflection is live, and the assistant already quotes *and upsells* on every estimate. The next build adds the last receptionist move — **booking the pickup on the call** — at a fraction of the cost of a hire.
