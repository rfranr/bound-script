#!/usr/bin/env bash
# Trusted preparation controls only. No implementation agent or pilot execution.
set -euo pipefail
stage=$(realpath "$1")
assets=$(cd -- "$(dirname -- "$0")" && pwd)
mkdir "$stage/control-normalize" "$stage/control-render"
cp "$assets/controls/normalize.ts" "$stage/control-normalize/implementation.ts"
cp "$assets/controls/private-tests.ts" "$stage/control-normalize/private-tests.ts"
cp "$assets/controls/render.ts" "$stage/control-render/implementation.ts"
bash "$assets/evaluate.sh" "$stage" normalize "$stage/control-normalize"
bash "$assets/evaluate.sh" "$stage" render "$stage/control-render"
bash "$assets/evaluate.sh" "$stage" integration "$stage/control-normalize" "$stage/control-render"
bash "$assets/evaluate.sh" "$stage" controls "$stage/control-normalize"
bash "$assets/evaluate.sh" "$stage" normalize "$stage/control-normalize" private:private-tests.js
negative() {
    local source=$1 pattern=$2 status=0
    mkdir "$stage/control-$source"
    cp "$assets/controls/$source.ts" "$stage/control-$source/implementation.ts"
    bash "$assets/evaluate.sh" "$stage" normalize "$stage/control-$source" >"$stage/$source.log" 2>&1 || status=$?
    ((status != 0)) || { echo "Negative control unexpectedly passed: $source" >&2; exit 1; }
    grep -q "$pattern" "$stage/$source.log"
    echo "EXPECTED FAILURE PASS: $source ($pattern); remaining independent cases unrun"
}
negative compile-error TS2322
negative missing-export TS2305
negative load-error 'Trusted load failure control'
negative malformed invalid-output
negative predicate postcondition-failure
negative behavior functional

# Trusted hung parent plus detached child. No compiler, candidate, repository or credentials mounted.
name="boundscript-contact-lifecycle-$$"
trap 'docker rm -f "$name" >/dev/null 2>&1 || true' EXIT
trap 'exit 130' INT
trap 'exit 143' TERM
docker create --name "$name" --network none --user 1000:1000 --cpus 1 --memory 512m --memory-swap 512m \
    --pids-limit 64 --cap-drop ALL --security-opt no-new-privileges --read-only --log-driver none \
    --tmpfs /tmp:rw,nosuid,nodev,size=16m,mode=1777 --env HOME=/tmp \
    --mount "type=bind,src=$assets/controls/lifecycle.mjs,dst=/probe.mjs,readonly" \
    node@sha256:55fb5f5a527ea2c5c4a95f963e48ef90aa38c7b346054fdc8ee9957a2b55d205 \
    sh -c 'timeout -k 1 2 node /probe.mjs' >/dev/null
docker start "$name" >/dev/null
sleep 0.5
# Observe the detached worker as well as its parent before the timeout.
docker top "$name" -eo pid,args > "$stage/lifecycle-processes.log"
grep -q 'setInterval' "$stage/lifecycle-processes.log"
status=$(timeout --kill-after=2 10 docker wait "$name")
[[ "$status" == 124 ]]
docker rm -f "$name" >/dev/null
if docker inspect "$name" >/dev/null 2>&1; then echo 'Container survived cleanup' >&2; exit 1; fi
# The evaluation wrapper also removes all successful/failed suite containers via its EXIT trap.
if [[ -n "$(docker ps -aq --filter 'name=boundscript-contact-')" ]]; then echo 'Evaluation container leaked' >&2; exit 1; fi
echo 'LIFECYCLE PASS: hung trusted parent/detached descendant, timeout 124, whole-container removal, no surviving evaluation containers'
