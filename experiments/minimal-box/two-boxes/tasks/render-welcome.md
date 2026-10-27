# RenderWelcome

Implement `/implementation/implementation.ts`, exporting `renderWelcome`
conforming to `RenderWelcome` in `/inputs/contract.ts`.

Call the supplied `normalize` dependency exactly once with the original Contact
object. Return `Welcome, NAME! <EMAIL>`, substituting the dependency's normalized
name and email and retaining the literal punctuation. For example, if the
supplied dependency returns `{name: 'Ada', email: 'ada@example.test'}`, return
`Welcome, Ada! <ada@example.test>`.

Use the dependency's returned values, not the raw input. Do not implement your
own normalization, mutate the input, add fallbacks, validation or other rules.
The input and normalized strings may be empty.

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
