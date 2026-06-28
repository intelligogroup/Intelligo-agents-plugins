# Assumption forwarding & worked example

## The mapping (step 3)

When you call `get_scoping_profiles`, forward the `value` of **every** assumption that appeared in step 2's `get_scoping_area` response — regardless of `source` (both `'explicit'` and `'default'` matter; the backend resolved them and profile assembly needs the resolved values to avoid re-deriving on a stale cell).

| step-2 assumption field            | → `get_scoping_profiles` input        |
|------------------------------------|----------------------------------------|
| `assumptions.subjectType.value`            | `subjectTypeConfirmed`            |
| `assumptions.ibTransactionType.value`      | `ibContext.transactionType`       |
| `assumptions.ibIncludeCounterparty.value`  | `ibContext.includeCounterparty`   |
| `assumptions.ibPersonFocus.value`          | `ibContext.personFocus`           |
| `assumptions.pelmmIncludeAddOn.value`      | `pelmmIncludeAddOn`               |

Skip the fields that weren't present in `assumptions` — they didn't apply to the resolved pattern.

## Worked example — step 2 disclosure (IB engagement on Acme Corp)

`get_scoping_area` returns `status: "ready"` with:

```json
"assumptions": {
  "subjectType":           { "value": "opco", "source": "default", "options": ["fund_manager","opco","ib_advisory"] },
  "ibTransactionType":     { "value": "advisory_other", "source": "default", "options": ["ma_buy_side","ma_sell_side","capital_markets","restructuring","advisory_other"] },
  "ibIncludeCounterparty": { "value": false, "source": "default" }
}
```

All three are `source: "default"`, so all three need disclosure. Your message to the user opens with:

> *"A couple of assumptions I made — Acme is an operating company (not a fund or M&A advisory work), this is general advisory rather than a specific M&A / capital-markets / restructuring deal, and I'm scoping only the principal (no counterparty). Tell me if any of those are wrong. Otherwise, here's the recommendation: [area]…"*

If the user corrects ("no, it's M&A sell-side, and yes include the counterparty"), re-call `get_scoping_area` with the explicit values in the right input slots (`ibContext.transactionType: "ma_sell_side"`, `ibContext.includeCounterparty: true`). Those come back as `source: "explicit"` next time and no longer need disclosure.

Where an upstream phrase exists (e.g. Clarity's `industry` field on the subject), prefer anchoring the disclosure in it — *"Per Clarity, Acme is tagged 'X' — I mapped that to an operating company…"* — so the client can verify against their own data.
