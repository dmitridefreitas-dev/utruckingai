# Phone Line & SMS — Setup Plan

*What it takes to turn on the **real phone line** and **text messaging**, in order — what you do, and what I wire up. The web/chat tools already work today with none of this.*

---

## Where each channel stands

| Channel | Status | What it needs |
|---|---|---|
| **Web chat + estimate page** | ✅ **Live now** | Nothing — no number, no registration |
| **Voice phone line** | ⏳ Needs a number | A phone number + a Business Profile |
| **Text messaging (SMS)** | ⏳ Needs registration | US carrier registration (EIN **or** Sole-Proprietor path) |
| **Booking write-back** | ⏳ Needs sheet edit access | Google Apps Script on the sheet (currently view-only — owner must enable) |

---

## The rollout — 4 steps

**Step 1 · Get the number + Business Profile** *(you)*
Create the account, fill the **Business Profile form** (fields below), and buy a number (~$1–3/mo). A number for **voice** can be used right away.

**Step 2 · Register for SMS** *(you)*
US texting requires carrier registration. Two paths:
- **Sole Proprietor** — no EIN; uses personal info. Lower volume, fine for reminders.
- **Standard** — needs a free **EIN** (see below). Higher volume.

**Step 3 · Enable booking write-back** *(owner — optional, do when ready)*
Booking/rescheduling writes to the sheet, which needs **edit access** via a free Google Apps Script (see `SETUP_BOOKING_WRITEBACK.md`). *Current blocker: this account has view-only access — the sheet owner needs to add the script.*

**Step 4 · I wire it all up** *(me)*
Send me the **number** (and, when ready, the Apps Script URL + secret). I connect the voice tools + SMS + booking, run tests against a scratch record, and switch it live. Then **we query/test again** and confirm before real customers hit it.

> **Flow:** fill the form → get the number → (EIN if needed) → send it to me → I wire + test → we verify together → live.

---

## The Business Profile form — what to fill

Fill each field from the business's **official** records (it gets vetted — mismatches get rejected).

| Field | What to put |
|---|---|
| **Business Name** | Legal registered name, exactly as on tax docs |
| **Business Type** | LLC / Corporation / **Sole Proprietor** / Partnership / Non-profit |
| **Business Industry** | Transportation / Logistics (closest to storage & moving) |
| **Business Registration ID Type** | **EIN** (United States) |
| **Business Registration Number** | The 9-digit **EIN** |
| **Region of Operation** | USA |
| **Website URL** | The real site (helps approval) |
| **Physical Address** | Real registered address (St. Louis, MO) — street, city, state, ZIP |
| **Authorized Representative** | Owner/manager — First, Last, Email (business-domain email is best) |
| **Phone Number** | A real number that can receive a verification text/call (digits only) |
| **Business Title** | Director / Owner / CEO / Manager |

---

## About the EIN (only needed for the Standard SMS path)

- **Free** and instant from the IRS — never pay a third-party site. Apply at *irs.gov → "Apply for an EIN online"* (open Mon–Fri, 7am–10pm ET).
- You do **not** need an LLC to get one; a Sole Proprietor can.
- **Important:** this bot is being built **for the business owner**, not the developer. The **owner** (or whoever files the taxes) should provide the EIN / do the registration — the business almost certainly **already has an EIN** if it files taxes. Don't register the company under the developer's personal SSN.
- Don't want an EIN at all? Use the **Sole-Proprietor** SMS path (personal info, lower limits) — or skip SMS and run **voice + web chat** only.

---

## Cost recap

| Item | Cost |
|---|---|
| Web chat + estimate page | **$0** (live) |
| Phone number | ~$1–3 / mo + ~$0.07–0.10 / min |
| SMS | ~$1–2 / mo + ~$0.008 / text |
| EIN | **free** |
| Booking write-back (Apps Script) | **free** |
