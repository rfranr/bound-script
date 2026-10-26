# 0023 — final consistency review and asset freeze

## Authority and frozen revision

The Product Owner independently ran the preparation/validation commands, reported all tests passing, and **accepted the technical preparation**. The subsequent instruction delegated a final expected-value consistency review and authorized freezing the current assets if no discrepancies were found. This record fulfils that conditional instruction; it is **not permission to launch agents**.

**Frozen revision:** `aee34e3f8445f1a0285c120f2a2bca5ef0b3e3f9`.

Freeze the **entire `experiments/contact-onboarding/` tree at that revision**, including source, M2 bindings, tasks/examples/scopes/policy, common generation instructions, literal corpus/order, tests/wiring/configuration, controls, scripts, event template and conventional baseline declarations/contexts/assertions/evaluation plan. Build trusted M1/M2/library dependencies from the same repository revision with the recorded tools. Use an ordinary dedicated trusted checkout of that revision, not mutable HEAD, for execution preparation. No tag, manifest, new approval engine or infrastructure is needed.

**No asset bytes were changed for this review/freeze.** Historical “acceptance pending” language inside that immutable tree describes its delivery state; this later Product Owner-directed freeze record supersedes that state without rewriting the accepted inputs. A later defect requires a reported discrepancy, visible diff, approval and rechecks; never repair the frozen corpus to fit observed implementations. Changes after trial start invalidate the affected frozen-input trial and require a newly approved trial ID.

## Review method and result

**Result: no discrepancies found.** Reviewed all **39 normalizer, 24 renderer and 18 integration rows**, including both intermediate/final expectations (99 expected record occurrences), against approved 0020 Section 3.3 N-01–N-05/R-01–R-05. Also reviewed the public task examples and their identical conventional-arm copies. This was a requirement-to-literal review, not another run of the reference pair or a newly implemented oracle. It does not claim that the author is an independent human reviewer; the Product Owner's separately reported execution validates the technical preparation, while this final review completes the delegated consistency check.

| Requirements | Consistency findings |
| --- | --- |
| N-01 | Only space/tab/CR/LF are trimmed/collapsed; NBSP, HTML characters, composed/decomposed Unicode and emoji remain unchanged. Name text is not title-cased, escaped or Unicode-normalized. |
| N-02 | IDs preserve case; explicit lengths 1/32/33 and invalid empty/space/Unicode/NBSP cases agree with the ASCII rule. Names of 0/1/80/81 units and 40/41 emoji agree with UTF-16 length limits; NUL/vertical tab/DEL remain invalid controls. |
| N-03 | ASCII-only lowercasing preserves `İ` while lowercasing its domain; that address remains invalid. The numeric address `1@2.3` is intentionally valid under the approved limited regex. Dotted/plus/underscore/hyphen local parts and domain hyphens/multiple labels match the specified subset; all rejection rows agree. No RFC/deliverability rule is substituted. |
| N-04 | en/fr/fallback locales, unchanged consent/days, inclusive 0–30 integers and unclamped negative/above-range/fractional values agree. Non-finite inputs belong to the existing M1 harness controls, not business-invalid JSON cases. |
| N-05 | Complete normalized records are retained even on failure; the competing-error ladder correctly selects BAD_ID, BAD_NAME, BAD_EMAIL, then BAD_DAYS. Canonicalization still occurs on invalid inputs. Otherwise valid/reason is true/OK. |
| R-01 | Invalid wins over no consent, with exact identity, supplied reason, empty recipient/HTML and subject `Not sent`. Valid non-consent uses NO_CONSENT. Direct invalid input with empty reason intentionally passes it through: the renderer has no input nonempty-reason predicate. |
| R-02 | Sent results use the supplied identity/email and reason OK, even with a contradictory supplied reason. Only exact `fr` selects French. Direct mixed-case `FR`, raw email/name, negative/fractional/exponent days are not recanonicalized/revalidated. |
| R-03 | Subjects, punctuation and spaces match both templates. All five original special characters are escaped once; literal `&lt;` becomes `&amp;lt;` and literal `&amp;` becomes `&amp;amp;`, not a second pass over replacement text. Unicode/name spaces are preserved. |
| R-04 | Zero uses the exact no-trial paragraph; nonzero uses exact fixed-plural paragraphs, including `1 days`/`1 jours`. Direct finite `1e21` correctly renders JavaScript `1e+21`. No extra whitespace/newline appears. |
| R-05 | All expected messages contain exactly the six specified fields. Expected values contain no delivery/external-data behavior. Literal review cannot prove purity or absence of arbitrary side effects; the existing tests, policy and restricted containers retain their stated limits. |

Read-only data checks confirmed complete expected key sets, matching overlapping normalizer/integration expectations, every integration intermediate/final pair matching its corresponding independent renderer case, public-example/corpus/baseline agreement, declared boundary lengths and preserved Unicode codepoints. No candidate-shaped code was compiled/imported/executed, no new functional evaluator was introduced, and no agent, provider probe or container was launched in this review.

## Transition to execution proposal

- Assignment 0023's accepted technical preparation and conditional freeze are complete. This does not close M3; **M3 remains Planned**.
- [Assignment 0022](../assignments/0022-run-bounded-independent-implementation-pilot.md) is now prepared for explicit execution approval against this fixed revision, not a combined asset-authoring/execution task.
- Preserve the approved model/settings, independence, tool-free generation, container-only evaluation, failure/feedback protocol, metrics and preregistered baseline. M6 remains unexecuted and separately authorized.
- Remaining approval: authorize the specific trial and its model-response/time budget, and choose a monetary spending policy/ceiling (or explicitly approve usage/time-only limits if native billing is not observable). Effective empty tools and ordinary container readiness are pre-call operational checks after approval, not new infrastructure research or a reason to reopen 0021.
