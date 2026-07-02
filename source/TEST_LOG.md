# UTrucking AI Phone Assistant — QA & Testing Log

**Prepared:** 2026-07-02
**Agent:** Utrucking Agent (Retell AI) · versions v29 → v33
**How tested:** scripted conversations run against the *live* agent via Retell's playground API, one real phone call, and direct probes of the lookup backend + Google Sheets.

---

## 1. Summary

The assistant was tested across **three layers**: (1) does it behave correctly turn-by-turn, (2) does it hold up to hard/ambiguous names at scale, and (3) does it work on a real call. Headline results:

- **10 / 10 functional scenarios passed** (order lookup, privacy gate, disambiguation, FAQ, transfer, call-end, identity verification).
- **Hard-name stress test:** a garbled name **never** resolved to the wrong student (0 wrong matches across the sample).
- **1 live phone call** completed successfully end-to-end; one minor wording tic was found and fixed.
- **1 privacy risk** in the backend (over-eager name matching) was identified **and mitigated** by an added identity-verification step.

---

## 2. Functional / behavior tests

Each scenario was driven as a real conversation against the published agent.

| # | Scenario | Expected | Result |
|---|----------|----------|--------|
| 1 | Caller gives name, checks order | Confirms identity, then answers | ✅ Pass |
| 2 | One-question-at-a-time answers | Answers only the field asked, briefly | ✅ Pass |
| 3 | Order mentioned *before* a name is given | Asks for the name first, no premature lookup | ✅ Pass (fixed in v30) |
| 4 | Privacy gate — wrong/close name match | Confirms the name; reveals nothing if "that's not me" | ✅ Pass |
| 5 | Ambiguous name → multiple matches | Offers choices, lets caller pick | ✅ Pass |
| 6 | General question (pricing/services) | Brief, accurate answer from knowledge base | ✅ Pass |
| 7 | Caller says goodbye | Warm close, then ends the call | ✅ Pass |
| 8 | Caller asks for a person | Connects to the UTrucking team (transfer) | ✅ Pass |
| 9 | Name not found after spelling | Escalates to the team instead of looping | ✅ Pass (fixed in v32) |
| 10 | Identity verification | Confirms a second detail; if wrong, does not share and transfers | ✅ Pass (added in v33) |

---

## 3. Live phone-call test

A real call was placed to the assistant (caller: a real student record). The assistant fuzzy-matched a mispronounced name, confirmed identity, and answered pickup location, status, order ID, billing, delivery, and website questions — each concisely. **Finding:** the assistant occasionally tacked on filler ("right?", "is that okay?"). **Action:** fixed in v32. Full transcript: `utrucking-test-calls.txt`.

---

## 4. Name-matching stress test

Automated audit against the live roster (~1,655 students).

**A. Misspelled hard-to-pronounce names (18 tested)** — a letter-swap was applied to real names to simulate speech-to-text errors:
- **10** matched to the correct student exactly
- **8** returned "let me confirm which one" (the assistant then disambiguates)
- **0** matched the **wrong** student
- **0** failed to find anything

**B. Fake names not in the system (12 tested)** — should never match a real student:
- **10** correctly rejected
- **2** were over-matched to a real student by the backend (~17%)
- **Mitigation:** the v33 identity-verification step blocks these — the caller cannot confirm a stranger's building, so no data is shared. **Root fix:** tighten the backend match threshold (planned).

---

## 5. Integration / infrastructure checks

| Check | Result |
|-------|--------|
| Backend reachable (`/lookup_student`, `/health`, `/debug_sheets`) | ✅ Online |
| Dispatch Google Sheet | ✅ ~1,655 rows, all expected columns present |
| Service Google Sheet | ⚠️ Returns 0 rows (empty or un-shared) — item-list/invoice answers unavailable |
| Retell tools wired (`lookup_student`, `transfer_to_office`, `end_call`) | ✅ Verified |
| Guardrails (jailbreak/abuse protection) | ✅ Enabled (v33) |

---

## 6. Known issues & mitigations

1. **Backend over-matching** (fake name → real student): mitigated by identity verification; permanent fix = raise the match threshold in the backend and redeploy.
2. **Service sheet empty:** item/invoice details unavailable until the second Google Sheet is restored.
3. **No phone number provisioned yet:** tested via the Retell dashboard/API; a live line can be added when ready.

---

## 7. Method note

Behavior was validated by replaying full conversations against the **live agent** (not a mock) and inspecting every assistant message and tool call. Name matching was audited directly against the production backend and Google Sheets. Testing spanned agent versions v29 through v33; each fix was re-tested before publishing.
