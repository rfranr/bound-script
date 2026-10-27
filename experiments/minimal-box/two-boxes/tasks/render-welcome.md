# RenderWelcome

Implement `/implementation/implementation.ts`, exporting `renderWelcome`
conforming to `RenderWelcome` in `/inputs/contract.ts`.

Call the supplied `normalize` dependency exactly once with the original Contact
object, regardless of its contents. Consume the discriminated union it returns:
- `ok: true`: return `Welcome, NAME! <EMAIL>` using `result.contact` exactly.
- `ok: false`: return `Invalid contact: ` followed by `result.errors.join(', ')`.
  Preserve the supplied order and duplicates; do not sort, filter or translate.

For example `{ok: false, errors: ['name.required', 'email.invalid']}` produces
`Invalid contact: name.required, email.invalid`.
Use only the dependency's result, not raw input. Do not duplicate normalization
or validation, mutate the input or dependency result, or add fallbacks. Treat the
injected dependency as authoritative even if its successful strings are empty or
unnormalized, or its failure errors are empty or in an unusual order. If it
throws, propagate the same exception without retrying or substituting a message.

## Dependency permissions and capabilities

The only authorized Box dependency is **NormalizeContact**, whose public contract
is `/inputs/normalize-contact.ts`. Your own task and contract and this dependency
contract are the only authorized Box inputs. Its implementation is unavailable:
the caller supplies it at runtime. No peer task, implementation or acceptance
test is authorized. Use type-only imports for contracts. Do not install packages.

Only `/implementation` is a writable submission area. Node/Pi runtime tooling and
writable disposable authentication/settings state are provisioned outside it.
Pi/tools can technically read the explicitly authorized credentials and use
unrestricted networking. Do not inspect, print, copy or disclose credentials.
These are accepted prototype risks, not source-import or egress enforcement.
