# 0046 — Complete-Source Credential Scanning and Snapshot Binding

Status: In Review
Type: Implementation — step 1 only of approved design 0045

## Authorization and scope

The Product Owner approved the verification-only direction of design 0045 and authorized its first implementation step only. Implement complete-source credential scanning and safe deterministic scan/snapshot binding with credential-free tests, preserving current sandbox restrictions, security boundaries and single-file compatibility.

Do not implement generation orchestration/CLI mode, change prompts, invoke models or modify the verifier. Do not add tree promotion, quarantine, retention, artifact abstractions or unrelated infrastructure. Keep changes uncommitted; no pushes.

## Plan

- Reuse source-tree policy/inventory with a narrowly validated exception for the exact workflow-created contract. Default standalone staging continues to reject candidate-owned contracts. Add the approved deterministic compact inventory digest.
- Add a trusted Node scanner, supplied to the existing container through stdin without mounting repository/tooling inputs. Pass only trusted limits, known paths and protected contract metadata—not credential values. Scan all generated file/path bytes against original/refreshed literal credential values; return only a digest or silent failure.
- Extend the workspace helper behind a default-off source-tree parameter. Reuse all existing lifecycle/mount/probe/auth/cleanup checks; scan before host candidate copying, destroy generation writers before staging, require scan/snapshot digest equality, and yield a private pure source snapshot within a cleanup context. Leave the legacy file branch unchanged.
- Test the real scanner with synthetic credential files and inert source fixtures, metadata/object/size/path failures, inventory parity, tampering, safe diagnostics and cleanup. Simulate completion events instead of executing Pi. Reuse existing single-file and source-tree regression tests; use Docker explicitly for real sandbox evidence.

This delivery is not authorization for step 2 or live generation and must not be self-accepted.

## Step 1 delivery and verification

- Resumed the existing working-tree implementation without replacing it. Added a newline-directory rejection case to the scanner/staging policy parity test; no verifier, prompt, orchestration or sandbox-policy changes.
- The original `/tmp/boundscript-0046-check.log` records a 30-second timeout in the existing forbidden-import/reference regression. That test passed on its isolated rerun, and the subsequent full check passed without changing its timeout or assertions.
- `BOUNDSCRIPT_RUNTIME=docker npm run check`: passed, including 76 internal tests (six opt-in skips), remaining unit/tooling/contract checks and existing Docker baseline verification.
- Explicit Docker scanner/workspace/staging checks: 24 tests passed, including the real scanner with synthetic credentials and no Pi execution. No scan-test container remained. This does not claim that all other opt-in engine tests ran.
- Local verification logs: `/tmp/boundscript-0046-resume-import-check.log`, `/tmp/boundscript-0046-resume-scan-final.log` and `/tmp/boundscript-0046-resume-check.log`. The original interrupted log is preserved.
- Changes remain uncommitted. No model-backed Box generation, step 2 implementation, commit or push was performed. Implementation acceptance remains with the Product Owner.
