# Backend — UTrucking lookup & automation service

Python (FastMCP + Starlette) service deployed on Render. Reads two Google Sheets live as CSV and serves the voice agent.

> **Note:** the live Google Sheet IDs are redacted (`REDACTED_*_SHEET_ID`) in this public copy. The running service uses the real IDs via its own configuration.

## Endpoints

| Route | Purpose |
|---|---|
| `POST /lookup_student` | Fuzzy name → merged order record (dispatch + invoice sheets) |
| `POST /quote` | Instant itemized quote from a list or free text |
| `POST /availability` | Per-day booking load vs capacity + open alternative days |
| `GET  /billing_audit` | Flags `$0` / missing-invoice / missing-order leakage |
| `GET  /health` · `GET /debug_sheets` | Health + data diagnostics |

## Files

- `main.py` — the Starlette/FastMCP app, sheet fetch, name matching, endpoints
- `engines.py` — pure business logic for quote / availability / billing (unit-tested against real data)
- `requirements.txt` · `python-version` — runtime

Name matching uses `difflib` with a token-based first/last strategy and a `0.6` cutoff to limit false positives; the voice agent adds an identity-verification gate on top.
