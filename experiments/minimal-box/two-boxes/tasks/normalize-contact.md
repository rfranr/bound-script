# NormalizeContact

Implement `/implementation/implementation.ts`, exporting `normalizeContact`
conforming to the `NormalizeContact` type in `/inputs/contract.ts`.

Given a Contact containing string `name` and `email` fields, return a new Contact:
- name is the supplied name with leading/trailing whitespace removed (String.trim);
- email is the supplied email trimmed and lowercased (String.toLowerCase).
Do not mutate the input. Preserve internal whitespace. Empty strings are valid.
Do not add validation, fallback values, extra fields, or other business rules.

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
