#!/usr/bin/env bash
# Fixed compile/evaluate commands, not an agent runner. No host candidate execution.
set -euo pipefail
stage=$(realpath "$1"); mode=$2
assets=$(cd -- "$(dirname -- "$0")" && pwd)
repo=$(cd "$assets/../.." && pwd)
image='node@sha256:55fb5f5a527ea2c5c4a95f963e48ef90aa38c7b346054fdc8ee9957a2b55d205'
case "$mode" in normalize|render|integration|controls) ;; *) echo 'Unknown fixed suite' >&2; exit 2;; esac
mounts=(); boxes=(); private_entry=''
if [[ "$mode" == normalize || "$mode" == render ]]; then
    if [[ -n "${4:-}" ]]; then
        [[ "$4" == private:* ]] || { echo 'Expected private:relative/emitted.js' >&2; exit 2; }
        private_entry=${4#private:}
        [[ "$private_entry" == *.js && "$private_entry" != /* && "/$private_entry/" != *"/../"* ]] || exit 2
    fi
fi
add_box() {
    local box=$1 label=$2 source
    test ! -L "$3"
    source=$(realpath "$3")
    test -d "$source" && test -f "$source/implementation.ts"
    # Reject links, special files, config, declarations and excessive inert submissions before copying.
    if [[ -n "$(find "$source" \( -name .pi -o -type l -o \( ! -type d ! -type f \) \) -print -quit)" ]]; then echo 'Unapproved source path' >&2; exit 2; fi
    if [[ -n "$(find "$source" -type f \( ! -name '*.ts' -o -name '*.d.ts' \) -print -quit)" ]]; then echo 'Only .ts submissions allowed' >&2; exit 2; fi
    local size
    size=$(find "$source" -type f -printf '%s\n' | awk '{n+=$1} END {print n+0}')
    ((size <= 10485760)) || { echo 'Submission exceeds 10 MiB' >&2; exit 2; }
    mounts+=(--mount "type=bind,src=$stage/$label/handoff,dst=/input/$box/handoff,readonly"
             --mount "type=bind,src=$source,dst=/input/$box/candidate,readonly")
    boxes+=("$box")
}
case "$mode" in
    normalize|controls) add_box normalize NormalizeContact "$3"; corpus=normalize ;;
    render) add_box render RenderWelcome "$3"; corpus=render ;;
    integration) add_box normalize NormalizeContact "$3"; add_box render RenderWelcome "$4"; corpus=integration ;;
esac
if [[ "$mode" == controls ]]; then
    mounts+=(--mount "type=bind,src=$stage/baseline,dst=/baseline,readonly"
             --mount "type=bind,src=$assets/tests/render.json,dst=/baseline-cases/render.json,readonly"
             --mount "type=bind,src=$assets/tests/integration.json,dst=/baseline-cases/integration.json,readonly")
fi
name="boundscript-contact-$$-$RANDOM"
trap 'docker rm -f "$name" >/dev/null 2>&1 || true' EXIT
trap 'exit 130' INT
trap 'exit 143' TERM
# Limits apply to the whole container, including compiler and candidate descendants.
docker create --name "$name" --network none --user 1000:1000 --cpus 1 --memory 512m --memory-swap 512m --pids-limit 64 \
    --cap-drop ALL --security-opt no-new-privileges --read-only --log-driver none \
    --tmpfs /scratch:rw,nosuid,nodev,size=256m,mode=1777 --tmpfs /tmp:rw,nosuid,nodev,size=16m,mode=1777 \
    --workdir /scratch --env HOME=/tmp --env "SUITE=$mode" --env "PRIVATE_ENTRY=$private_entry" \
    --mount "type=bind,src=$stage/libraries,dst=/libraries,readonly" \
    --mount "type=bind,src=$repo/node_modules/typescript,dst=/tools,readonly" \
    --mount "type=bind,src=$assets/tests/$corpus.json,dst=/cases/corpus.json,readonly" \
    "${mounts[@]}" "$image" sh -c \
    'set -eu; if [ "$SUITE" = controls ]; then timeout -k 2 60 node /tools/lib/tsc.js -p /baseline/tsconfig.json --pretty false; fi; timeout -k 2 60 node /libraries/build.mjs "$@"; if [ -n "$PRIVATE_ENTRY" ]; then timeout -k 2 60 node "/scratch/$SUITE/built/candidate/$PRIVATE_ENTRY"; else timeout -k 2 60 node /libraries/evaluate.mjs "$SUITE"; fi' \
    sh "${boxes[@]}" >/dev/null
# No ambient host variables are passed. SUITE is an explicit nonsecret fixed enum.
docker inspect "$name" | python3 -c '
import json,sys
c=json.load(sys.stdin)[0];h=c["HostConfig"]
assert h["NetworkMode"]=="none" and h["ReadonlyRootfs"] and c["Config"]["User"]=="1000:1000"
assert h["Memory"]==536870912 and h["MemorySwap"]==536870912 and h["PidsLimit"]==64 and h["NanoCpus"]==1000000000
assert not h["Privileged"] and not h["Devices"] and h["PidMode"]!="host" and h["IpcMode"]!="host"
assert "ALL" in h["CapDrop"] and any(x.startswith("no-new-privileges") for x in h["SecurityOpt"])
assert all(not m["RW"] for m in c["Mounts"] if m["Type"]=="bind")
print("CONTAINER SETTINGS PASS: offline, nonroot, read-only binds/root, limits, no capabilities/new privileges")'
# Bounded attached output; trap forcibly removes the entire container even on timeout/failure/SIGPIPE.
timeout --signal=TERM --kill-after=5 130 docker start -a "$name" 2>&1 | head -c 1048576
