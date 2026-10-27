# NormalizeContact

Implement `/implementation/implementation.ts`, exporting `normalizeContact`
conforming to the `NormalizeContact` type in `/inputs/contract.ts`.

The input always has string `name` and `email` fields; absent fields, null and
non-string values are outside this contract. Never mutate the input.

Normalize name with ECMAScript `String.trim()`, then replace each consecutive run
of ECMAScript whitespace (`/\s+/gu`) with one ASCII space. Preserve case and all
non-whitespace Unicode characters exactly; do not apply Unicode normalization.
Normalize email with `String.trim().toLowerCase()` (not locale-specific). Do not
collapse internal email whitespace or apply Unicode normalization.

Validate the normalized values and accumulate all errors in this exact order:
1. Empty name: `name.required`.
2. Empty email: `email.required`; otherwise, if the email does not match
   `/^[^\s@]+@[^\s@]+\.[^\s@]+$/u`, add `email.invalid`.

This deliberately simple email rule requires exactly one @, a nonempty local
part, and a domain containing a dot with at least one character on each side.
Whitespace and additional @ characters anywhere are forbidden. Unicode and other
non-whitespace punctuation are permitted; consecutive dots are permitted. This
is not RFC validation, IDNA conversion or deliverability checking. ECMAScript
whitespace includes tabs, line breaks, NBSP and em spaces, but not U+200B (zero
width space). Whitespace-only values become empty. Do not reject names for any
other reason. An empty email gets only `email.required`, not `email.invalid`.

Return exactly `{ok: true, contact: {name, email}}` on success, with a new contact
object, or `{ok: false, errors: [...]}` on failure. Do not return partial contact
data on failure, extra fields, fallback values or additional business rules.

## Dependency permissions and capabilities

Authorized Box dependencies: **none**. Read only your own task and contract;
no peer task, contract, implementation, or acceptance test is authorized.
Use type-only imports for contracts. Node/ECMAScript built-ins are runtime tooling,
not authorization to inspect other Boxes. Do not install packages.

Only `/implementation` is a writable submission area. Pi tooling and writable
disposable authentication/settings state are provisioned outside it. As explicitly
accepted for this prototype, Pi/tools can technically read credentials and use
unrestricted network access. Do not inspect, print, copy or disclose credentials.
These instructions do not constitute a credential/network or source-import firewall.
