# NormalizeContact functional task

Use the supplied contract/declarations as the sole public interface. Do not redefine them. Implement the selected operation as named `implement` in `candidate/implementation.ts`, with a type-only import of `Implementation` from `../handoff/generated/contract.js`. ECMAScript only; deterministic, no external side effects, no input mutation. Synchronous or async is permitted.

**Normalizer — responsibility: canonicalize and classify, not render or decide whether to send.**

| ID | Required behavior |
| --- | --- |
| N-01 | For this experiment, trimming removes only ASCII space, tab, CR, and LF from string ends. Collapse runs of those characters inside the trimmed name to one ASCII space. Preserve other characters, including Unicode and HTML metacharacters; do not title-case, HTML-escape, or Unicode-normalize names. |
| N-02 | Trim the identifier and preserve its case. It is valid iff it matches `[A-Za-z0-9_-]{1,32}` in full. The normalized name must have 1–80 UTF-16 code units and no remaining C0 control characters or DEL. |
| N-03 | Trim email and lowercase ASCII A–Z only. The complete result must match `^[a-z0-9]+(?:[._+-][a-z0-9]+)*@[a-z0-9]+(?:-[a-z0-9]+)*(?:\.[a-z0-9]+(?:-[a-z0-9]+)*)+$`. This is an intentionally limited experiment rule, not RFC email validation or a deliverability claim. |
| N-04 | Trim locale and lowercase ASCII A–Z; preserve exactly `en` or `fr`, otherwise use `en`. Consent is copied unchanged. Trial duration is copied unchanged and valid iff it is an integer in inclusive range 0–30; do not clamp or round it. The conventional input assertions reject non-finite values before candidate invocation. |
| N-05 | Apply the above canonicalization even on invalid submissions. Return `valid = false` and the first applicable reason in this fixed priority: `BAD_ID`, `BAD_NAME`, `BAD_EMAIL`, `BAD_DAYS`; otherwise `valid = true`, reason `OK`. Invalid results still contain every contract field. No throw for a type-valid business-invalid submission. |

Examples: see below. Full private checks cover only these published rules, not secret requirements. They include repeated-call equality and unchanged inputs.

```json
[
  {
    "input": {
      "requestId": " r-7 ",
      "name": "  Ada\t  <Lovelace>  ",
      "email": " ADA@EXAMPLE.COM ",
      "locale": " FR ",
      "consent": true,
      "trialDays": 7
    },
    "expected": {
      "requestId": "r-7",
      "displayName": "Ada <Lovelace>",
      "email": "ada@example.com",
      "locale": "fr",
      "consent": true,
      "trialDays": 7,
      "valid": true,
      "reason": "OK"
    }
  },
  {
    "input": {
      "requestId": "r1",
      "name": "Ada",
      "email": "ada@example.com",
      "locale": "es",
      "consent": false,
      "trialDays": 0
    },
    "expected": {
      "requestId": "r1",
      "displayName": "Ada",
      "email": "ada@example.com",
      "locale": "en",
      "consent": false,
      "trialDays": 0,
      "valid": true,
      "reason": "OK"
    }
  },
  {
    "input": {
      "requestId": "",
      "name": " \t",
      "email": "bad",
      "locale": "en",
      "consent": true,
      "trialDays": 0.5
    },
    "expected": {
      "requestId": "",
      "displayName": "",
      "email": "bad",
      "locale": "en",
      "consent": true,
      "trialDays": 0.5,
      "valid": false,
      "reason": "BAD_ID"
    }
  },
  {
    "input": {
      "requestId": "r1",
      "name": " \t\r\n",
      "email": "bad",
      "locale": "en",
      "consent": true,
      "trialDays": -1
    },
    "expected": {
      "requestId": "r1",
      "displayName": "",
      "email": "bad",
      "locale": "en",
      "consent": true,
      "trialDays": -1,
      "valid": false,
      "reason": "BAD_NAME"
    }
  },
  {
    "input": {
      "requestId": "r1",
      "name": "Ada",
      "email": " BAD ",
      "locale": "en",
      "consent": false,
      "trialDays": 31
    },
    "expected": {
      "requestId": "r1",
      "displayName": "Ada",
      "email": "bad",
      "locale": "en",
      "consent": false,
      "trialDays": 31,
      "valid": false,
      "reason": "BAD_EMAIL"
    }
  }
]
```
