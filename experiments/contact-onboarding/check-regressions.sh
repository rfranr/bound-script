#!/usr/bin/env bash
# Existing trusted regression fixtures also execute only in an offline container.
set -euo pipefail
stage=$(realpath "$1")
assets=$(cd -- "$(dirname -- "$0")" && pwd)
repo=$(cd "$assets/../.." && pwd)
mkdir "$stage/regression-input"
# Only the existing test/build closure, not .git, home, conversations, pilot candidates,
# experiments, sessions, credentials or a full-repository mount.
for path in packages examples tests tooling package.json package-lock.json tsconfig.json tsconfig.base.json tsconfig.tests.json vitest.config.ts; do
    cp -R "$repo/$path" "$stage/regression-input/$path"
done
name="boundscript-contact-regression-$$"
trap 'docker rm -f "$name" >/dev/null 2>&1 || true' EXIT
trap 'exit 130' INT
trap 'exit 143' TERM
docker create --name "$name" --network none --user 1000:1000 --cpus 1 --memory 512m --memory-swap 512m \
    --pids-limit 64 --cap-drop ALL --security-opt no-new-privileges --read-only --log-driver none \
    --tmpfs /scratch:rw,exec,nosuid,nodev,size=256m,mode=1777 --tmpfs /tmp:rw,nosuid,nodev,size=32m,mode=1777 \
    --workdir /scratch --env HOME=/tmp --env UV_THREADPOOL_SIZE=1 --env NODE_OPTIONS=--v8-pool-size=1 \
    --mount "type=bind,src=$stage/regression-input,dst=/regression-input,readonly" \
    --mount "type=bind,src=$repo/node_modules,dst=/dependencies,readonly" \
    node@sha256:55fb5f5a527ea2c5c4a95f963e48ef90aa38c7b346054fdc8ee9957a2b55d205 \
    sh -c 'set -eu
      mkdir /scratch/repo
      cp -R /regression-input/. /scratch/repo/
      cp -R /dependencies /scratch/repo/node_modules
      cd /scratch/repo
      npm run typecheck
      npm test -- --maxWorkers=1
      npm run build --silent
      for demo in director-box box-composition structured-types; do
        npm run --silent "demo:$demo" > /scratch/demo.out
        printf "Hello, World!\n" > /scratch/expected.out
        cmp /scratch/demo.out /scratch/expected.out
      done
      node packages/cli/dist/bin.js examples/hello-minimal.bound > /scratch/hello.out
      cmp /scratch/hello.out /scratch/expected.out
      node packages/cli/dist/bin.js spec examples/structured-types.bound --box Greeter > /scratch/spec.json
      cmp /scratch/spec.json examples/specs/greeter.box-spec.json
      echo "REGRESSIONS PASS: typecheck/tests/build, three demos, Hello World and canonical export"
    ' >/dev/null
# A separate development-regression deadline, not a pilot candidate attempt/suite budget.
timeout --kill-after=5 600 docker start -a "$name" 2>&1 | head -c 1048576
