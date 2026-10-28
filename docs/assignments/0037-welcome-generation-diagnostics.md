# 0037 — Fix RenderWelcome generation failure and diagnostics

## Status
In Review (host configuration remediation still required)

## Requirements and authorization
The user requests fixing `BOUNDSCRIPT_RUNTIME=podman npm run generate:welcome`
failing with `Generation stopped: ValueError; no raw diagnostics emitted`, and
adding developer-visible traces sufficient to identify root causes. Follow the
project development workflow. The user subsequently authorized a local commit
of this delivery. No push or acceptance is authorized.

## Scope
Investigate the generation failure, correct its cause, and add safe actionable
generation diagnostics and regression coverage. Preserve isolation, credential
protection, independent verification and verify-before-promotion.

## Verification
Reproduce the relevant failure without exposing credentials; test the correction
and diagnostic redaction, and run relevant existing checks. Record limitations
where live generation or engine checks cannot be performed.

## Delivery and evidence
- Reproduced without credentials/model calls: generation container exposes
  `memory.max=max`; `int('max')` caused the original ValueError. Podman reports
  no systemd user session and fallback to cgroupfs. The confirmed failure is
  ineffective resource isolation; the exact host delegation repair remains
  an administrator/environment concern.
- Replaced numeric conversion crashes with explicit fail-closed resource-policy
  classifications for memory, swap, CPU and PID evidence, retaining all required
  limits. Added generation stage markers and safe repository code-location
  traces in the welcome CLI; arbitrary exception/engine/provider payloads stay
  withheld. Added regression tests and host troubleshooting instructions.
- `npm run test:unit`: passed (54 tests run, 6 skipped opt-in engine tests).
- `npm run check`: Python units, both validator suites (3 tests each), and
  public-contract compilation passed. Baseline container verification failed
  on the default Docker adapter's environment assertion in this environment.
- `BOUNDSCRIPT_RUNTIME=podman npm test`: blocked by the confirmed unlimited
  memory resource policy, now explicitly diagnosed rather than ValueError.
- `BOUNDSCRIPT_RUNTIME=podman npm run generate:welcome`: Typia build passed;
  generation stopped before copying auth or starting Pi, printing the resource
  root cause, setup guidance and code locations. Container removal ran.
- `git diff --check`: passed. No billable generation, candidate promotion, host
  configuration changes or commits performed. End-to-end generation remains
  blocked until the host enforces cgroup limits; no security checks were relaxed.
