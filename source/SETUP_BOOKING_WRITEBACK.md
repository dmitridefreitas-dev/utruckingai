# Setup — Booking write-back via Google Apps Script

**Status:** 🟡 *Prepared, NOT wired.* Nothing in the live backend uses this yet. When you send the SMS number, I wire booking (create / reschedule / cancel + invoice guard) to the endpoint you set up here.

**Why this approach:** the backend currently *reads* your sheets as public CSV — read-only. To *write* a booking, we add a tiny **Google Apps Script** "receiver" that lives on your sheet. The backend sends it the booking; the script writes the row.

**No Google Cloud. No service account. No billing screen.** The script runs under your own Google account, inside Apps Script's free quota. **Cost: $0.** Total time: ~5 minutes.

---

## Part 1 — Open the script editor
1. Open the Google Sheet you want bookings written to (I'd suggest the **DISPATCH** sheet, or make a fresh tab named `Bookings`).
2. Menu: **Extensions → Apps Script**. A code editor opens in a new tab.

## Part 2 — Paste the code + set a secret
3. Delete whatever's in `Code.gs` and paste the **script at the bottom of this file**.
4. On the first line, change `SECRET` from `CHANGE-ME...` to your own **long random string** (letters + numbers, ~20 chars). This is the password the backend uses — keep it private.
5. Click the **💾 Save** icon.

## Part 3 — Deploy it as a Web App
6. Top right: **Deploy → New deployment**.
7. Click the gear ⚙ next to "Select type" → choose **Web app**.
8. Set:
   - **Execute as:** *Me* (your account)
   - **Who has access:** *Anyone*  ← required so the backend can POST; the SECRET protects it
9. **Deploy.** Google asks you to **authorize** — because it's your own script it'll warn "Google hasn't verified this app": click **Advanced → Go to (your project) (unsafe)** → **Allow**. *(This is safe — it's your own script accessing your own sheet.)*
10. Copy the **Web app URL** it gives you (ends in `/exec`).

## Part 4 — Hand it to me
11. Send me the **Web app URL** + the **SECRET** you chose — or, if you want to add them yourself: Render → your service → **Environment**, add:
    - `SHEETS_WEBAPP_URL` = the `/exec` URL
    - `SHEETS_WEBAPP_SECRET` = your secret

That's it. **Tell me the SMS number and I'll wire booking to this.**

---

## Test it works (optional, before handing over)
In the Apps Script editor, or with any tool, POST this to your `/exec` URL:
```json
{ "secret": "your-secret-here", "action": "ping" }
```
A healthy deploy replies `{"ok":true,"pong":true}`.

## Keeping it safe
- The **SECRET** gates every write — without it, requests are rejected.
- The URL is long and unguessable; still, don't post it publicly.
- To rotate: change `SECRET` in the script, **Deploy → Manage deployments → edit → New version**, update `SHEETS_WEBAPP_SECRET` in Render.
- If you ever want to revoke it entirely: **Manage deployments → Archive**.

---

## The script — paste this into `Code.gs`

```javascript
// UTrucking booking write-back — Apps Script Web App (bound to this sheet).
// Deploy: Deploy > New deployment > Web app > Execute as: Me > Who has access: Anyone.
const SECRET = 'CHANGE-ME-to-a-long-random-string';   // must match SHEETS_WEBAPP_SECRET in Render

function doPost(e) {
  try {
    const body = JSON.parse((e && e.postData && e.postData.contents) || '{}');
    if (body.secret !== SECRET) return _json({ ok: false, error: 'unauthorized' });

    const action = body.action || 'append';
    if (action === 'ping') return _json({ ok: true, pong: true });

    const ss = SpreadsheetApp.getActiveSpreadsheet();
    const tab = body.tab || 'Bookings';
    let sheet = ss.getSheetByName(tab);
    if (!sheet) { sheet = ss.insertSheet(tab); }

    if (action === 'append') {
      let row = body.row;                       // an array of cell values, OR:
      if (!row && body.record) {                // an object keyed by the header row
        const width = Math.max(sheet.getLastColumn(), 1);
        const headers = sheet.getRange(1, 1, 1, width).getValues()[0];
        row = headers.map(function (h) { return body.record[h] != null ? body.record[h] : ''; });
      }
      if (!row || !row.length) return _json({ ok: false, error: 'no row/record' });
      sheet.appendRow(row);
      return _json({ ok: true, appended: sheet.getLastRow() });
    }
    return _json({ ok: false, error: 'unknown action' });
  } catch (err) {
    return _json({ ok: false, error: String(err) });
  }
}

function doGet() { return _json({ ok: true, service: 'utrucking-sheets-webapp' }); }

function _json(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj))
    .setMimeType(ContentService.MimeType.JSON);
}
```

## Backend side (reference — kept here, NOT in the live app yet)
```python
import os, httpx

async def append_booking(record: dict, tab: str = "Bookings") -> dict:
    """Send one booking row to the Apps Script web app. Apps Script 302-redirects to
    googleusercontent, so follow_redirects must be on."""
    payload = {"secret": os.environ["SHEETS_WEBAPP_SECRET"],
               "action": "append", "tab": tab, "record": record}
    async with httpx.AsyncClient(timeout=20.0, follow_redirects=True) as c:
        r = await c.post(os.environ["SHEETS_WEBAPP_URL"], json=payload)
        r.raise_for_status()
        return r.json()
```

---

## What I'll wire when you send the number
- `POST /book` on the backend (create / reschedule / cancel) calling `append_booking`.
- **Identity gate** (same as the voice agent) so nobody can book/cancel on someone else's order.
- **Invoice guard** — refuse a booking with a `$0` total or missing invoice (the ~$1,056 leakage fix).
- Retell agent tools + SMS confirmation, tested against the `Bookings` tab first, then live.
