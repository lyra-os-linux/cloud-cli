#!/bin/bash
# Rebuilds azure-cli-<version>-wheels.tar.gz, the vendored source of the
# azure-cli package: every wheel listed (and hash-pinned) in
# requirements.lock, for CPython 3.13 on manylinux x86_64. OBS has no
# network access at build time, so this tarball is uploaded next to the
# spec; the spec installs it with pip --require-hashes, which rejects any
# wheel whose SHA-256 differs from requirements.lock.
#
# To move to a new release, regenerate the lock first:
#   ./make-wheels.sh --lock 2.92.0
# then build the tarball from it:
#   ./make-wheels.sh
set -euo pipefail
cd "$(dirname "$0")"

platforms=(--platform manylinux_2_28_x86_64 --platform manylinux_2_17_x86_64 --platform manylinux2014_x86_64)
common=(--only-binary=:all: --python-version 3.13 --implementation cp "${platforms[@]}")

if [[ "${1:-}" == "--lock" ]]; then
    version="${2:?usage: $0 --lock <azure-cli version>}"
    work="$(mktemp -d)"
    trap 'rm -rf "$work"' EXIT
    python3.13 -m pip download -q "${common[@]}" -d "$work" "azure-cli==$version"
    python3.13 -I - "$work" > requirements.lock <<'PY'
import hashlib, os, sys
d = sys.argv[1]
for f in sorted(os.listdir(d)):
    name, version = f.split("-")[:2]
    digest = hashlib.sha256(open(os.path.join(d, f), "rb").read()).hexdigest()
    print(f"{name.replace('_', '-').lower()}=={version} --hash=sha256:{digest}")
PY
    sed -i "s/^Version:.*/Version:        $version/" azure-cli.spec
    exit 0
fi

version="$(sed -n 's/^Version:[[:space:]]*//p' azure-cli.spec)"
work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT
python3.13 -m pip download -q "${common[@]}" --no-deps --require-hashes -d "$work/wheels" -r requirements.lock
tar --sort=name --owner=0 --group=0 --numeric-owner --mtime=@0 \
    -C "$work" -czf "azure-cli-$version-wheels.tar.gz" wheels
echo "azure-cli-$version-wheels.tar.gz"
