# Setup — Google Service Account (booking write-back)

**Status:** 🟡 *Prepared, NOT wired.* Nothing in the live backend uses this yet. When you send the SMS number, I'll wire booking (create / reschedule / cancel + invoice guard) using the account you set up here.

**Why we need it:** the backend currently *reads* your sheets as public CSV — read-only. To *write* a booking back to a sheet, the backend needs an identity Google trusts. A **service account** is a free "robot" Google login for exactly that.

**Cost: $0.** The Google Sheets API is free, needs **no billing account**, and its free quota (300 requests/minute) is far beyond what we'll use. The "huge Google bill" fear applies to paid products (BigQuery, Maps, compute) — **not** Sheets. See "Keeping it free" below.

Total time: ~10 minutes, once.

---

## Part 1 — Create the service account

1. Go to **https://console.cloud.google.com** and sign in (any Google account is fine — the sheet just has to be *shared* with the robot later).
2. **Create a project:** top bar → project dropdown → **New Project** → name it `utrucking-booking` → **Create**. *(You do NOT need to set up billing. If it ever asks, skip it.)*
3. **Enable the Sheets API:** with the project selected, open
   **https://console.cloud.google.com/apis/library/sheets.googleapis.com** → **Enable**.
4. **Create the service account:** left menu → **APIs & Services → Credentials** → **+ Create Credentials** → **Service account** → name it `utrucking-writer` → **Create and Continue** → skip the optional role/user steps → **Done**.
5. **Make a key:** on **Credentials**, click the new `utrucking-writer` account → **Keys** tab → **Add Key → Create new key → JSON → Create**. A `.json` file downloads. **This is a password — keep it private, never email or commit it.**
6. **Copy the robot's email** (on that same page). It looks like:
   `utrucking-writer@utrucking-booking.iam.gserviceaccount.com`

## Part 2 — Give the robot access to your sheets

7. Open **each** Google Sheet (the **DISPATCH** sheet and the **SERVICE** sheet) → **Share** → paste the robot email → set it to **Editor** → **Send** (uncheck "notify" — robots don't read email).

## Part 3 — Add it to Render

8. Open the downloaded `.json` in a text editor and **copy the entire contents**.
9. Render → your `utrucking-mcp` service → **Environment** → **Add Environment Variable**:
   - **Key:** `GOOGLE_SERVICE_ACCOUNT_JSON`
   - **Value:** paste the whole JSON (a single long line is fine)
   - **Save.** (Render will redeploy.)

That's it — the account is ready. **Tell me the SMS number and I'll wire the booking flow against it.**

---

## Keeping it free (and safe)

- **Free:** the Sheets API bills **nothing**, and a service account is free. Don't enable paid APIs (BigQuery, Maps, Vertex, etc.).
- **Belt & suspenders:** if you ever attach a billing account for something else, add a **$0 budget alert** under *Billing → Budgets & alerts* so you're notified before any charge.
- **Security:** the JSON key is a credential — it lives **only** in the Render env var. If it ever leaks, delete that key in *Credentials → Keys* and create a new one (30 seconds).
- **Bonus security win:** once this is set, we can switch the sheet **reads** from "anyone with the link" public CSV to this authenticated account — then lock the sheets down to private, closing the current customer-PII exposure.

---

## What I'll wire when you send the number (reference — not live yet)

- `POST /book` on the backend (create / reschedule / cancel) using the service account.
- **Identity gate** (same as the voice agent) so nobody can book/cancel on someone else's order.
- **Invoice guard** — refuse to finalize a booking with a `$0` total or missing invoice (the ~$1,056 leakage fix).
- Retell agent tools + the SMS confirmation, tested against a throwaway row first, then switched live.

**Ready-to-drop-in write helper** (kept here, *not* in the live app; deps `gspread google-auth` get added at wiring time):

```python
import os, json, gspread
from google.oauth2.service_account import Credentials

def _client():
    info = json.loads(os.environ["GOOGLE_SERVICE_ACCOUNT_JSON"])
    creds = Credentials.from_service_account_info(
        info, scopes=["https://www.googleapis.com/auth/spreadsheets"])
    return gspread.authorize(creds)

def append_booking(sheet_id: str, worksheet: str, row_values: list) -> bool:
    """Append one booking row. open_by_key needs only the Sheets API scope."""
    ws = _client().open_by_key(sheet_id).worksheet(worksheet)
    ws.append_row(row_values, value_input_option="USER_ENTERED")
    return True
```
