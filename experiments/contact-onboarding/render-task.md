# RenderWelcome functional task

Use the supplied contract/declarations as the sole public interface. Do not redefine them. Implement the selected operation as named `implement` in `candidate/implementation.ts`, with a type-only import of `Implementation` from `../handoff/generated/contract.js`. ECMAScript only; deterministic, no external side effects, no input mutation. Synchronous or async is permitted.

**Renderer — responsibility: make a message/suppression decision from the supplied record, not repeat normalization.**

| ID | Required behavior |
| --- | --- |
| R-01 | Copy request identity exactly. If `valid` is false, suppress with `send = false`, empty recipient/HTML, subject `Not sent`, and the supplied reason. This wins over lack of consent. If valid but consent is false, suppress identically except reason `NO_CONSENT`. |
| R-02 | Otherwise set `send = true`, recipient to the supplied email, and reason `OK`. Use French only when locale is exactly `fr`; otherwise use English. Do not recanonicalize or revalidate names, addresses, identifiers, or days. Canonical producer values are the integration domain; standalone renderer tests also specify direct flag/locale behavior without assuming a peer implementation. |
| R-03 | English subject is exactly `Welcome`; French subject exactly `Bienvenue`. HTML begins with `<p>Hello, NAME!</p>` or `<p>Bonjour, NAME !</p>`. Replace NAME by escaped display name: original `&`, `<`, `>`, `"`, and `'` become `&amp;`, `&lt;`, `&gt;`, `&quot;`, and `&#39;`, respectively, once per original character. Do not trim or otherwise alter the name. |
| R-04 | Append, without extra whitespace/newline, `<p>Your trial lasts D days.</p>` or `<p>Votre essai dure D jours.</p>` when days is nonzero; D is JavaScript's string representation of the supplied finite number. For zero append `<p>No trial is included.</p>` or `<p>Aucun essai inclus.</p>`. Plural wording is intentionally fixed even for one day. |
| R-05 | Output only the specified fields. Never send email, fetch templates, consult time/randomness/environment, or read external data. The renderer's nonempty-subject predicate is only a narrow formal check; trusted assertions establish the richer behavior above. |

R-01 passes through a supplied reason even for a direct type-valid but semantically inconsistent record; do not invent missing producer intent.


Examples: see below. Full private checks cover only these published rules, not secret requirements. They include repeated-call equality and unchanged inputs.

```json
[
  {
    "input": {
      "requestId": "r-7",
      "displayName": "Ada <Lovelace>",
      "email": "ada@example.com",
      "locale": "fr",
      "consent": true,
      "trialDays": 7,
      "valid": true,
      "reason": "OK"
    },
    "expected": {
      "requestId": "r-7",
      "send": true,
      "recipient": "ada@example.com",
      "subject": "Bienvenue",
      "html": "<p>Bonjour, Ada &lt;Lovelace&gt; !</p><p>Votre essai dure 7 jours.</p>",
      "reason": "OK"
    }
  },
  {
    "input": {
      "requestId": "r1",
      "displayName": "Ada",
      "email": "ada@example.com",
      "locale": "en",
      "consent": true,
      "trialDays": 0,
      "valid": true,
      "reason": "OK"
    },
    "expected": {
      "requestId": "r1",
      "send": true,
      "recipient": "ada@example.com",
      "subject": "Welcome",
      "html": "<p>Hello, Ada!</p><p>No trial is included.</p>",
      "reason": "OK"
    }
  },
  {
    "input": {
      "requestId": "r1",
      "displayName": "A&B \"C\" 'D' <E>",
      "email": "ada@example.com",
      "locale": "en",
      "consent": true,
      "trialDays": 7,
      "valid": true,
      "reason": "OK"
    },
    "expected": {
      "requestId": "r1",
      "send": true,
      "recipient": "ada@example.com",
      "subject": "Welcome",
      "html": "<p>Hello, A&amp;B &quot;C&quot; &#39;D&#39; &lt;E&gt;!</p><p>Your trial lasts 7 days.</p>",
      "reason": "OK"
    }
  },
  {
    "input": {
      "requestId": "r1",
      "displayName": "Ada",
      "email": "ada@example.com",
      "locale": "en",
      "consent": false,
      "trialDays": 7,
      "valid": true,
      "reason": "OK"
    },
    "expected": {
      "requestId": "r1",
      "send": false,
      "recipient": "",
      "subject": "Not sent",
      "html": "",
      "reason": "NO_CONSENT"
    }
  },
  {
    "input": {
      "requestId": "r1",
      "displayName": "Ada",
      "email": "bad",
      "locale": "en",
      "consent": false,
      "trialDays": 31,
      "valid": false,
      "reason": "BAD_EMAIL"
    },
    "expected": {
      "requestId": "r1",
      "send": false,
      "recipient": "",
      "subject": "Not sent",
      "html": "",
      "reason": "BAD_EMAIL"
    }
  }
]
```
