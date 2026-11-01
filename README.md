# Cloud CLIs packaging

RPM packaging of the official command-line tools of the major clouds for
the signed Lyra OS OBS repositories (`home:rodrigosbrito:lyra`). None of
them is Lyra-authored code; this repository holds packaging metadata only.

| Package | Command | Upstream source | Verification |
| --- | --- | --- | --- |
| `aws-cli-v2` | `aws` | official Linux installer bundle (`awscli-exe-linux-x86_64-<ver>.zip`) | SHA-256 in `_service` + detached PGP signature checked at build time against the pinned AWS CLI Team key (`FB5D B77F D5C1 18B8 0511 ADA8 A631 0ACC 4672 475C`) |
| `azure-cli` | `az` | official `azure-cli` wheels from PyPI, run by the system Python 3.13 | every wheel hash-pinned in `requirements.lock`, installed with `pip --require-hashes` |
| `doctl` | `doctl` | official GitHub release tarball | SHA-256 in `_service` (matches upstream `checksums.sha256`) |
| `google-cloud-cli` | `gcloud`, `gsutil`, `bq` | official versioned Linux archive | SHA-256 in `_service` |

Why not the vendors' repositories:

- AWS publishes no RPM repository for CLI v2; openSUSE only ships v1
  (`aws-cli-cmd`), which `aws-cli-v2` conflicts with.
- Microsoft's openSUSE repository stopped at azure-cli 2.38, and its RHEL 9
  RPM requires Python 3.12, absent from Leap 16.
- DigitalOcean only documents the release tarball and Snap.
- Google's RPM repository targets RHEL; this package keeps the same layout
  (`/usr/lib64/google-cloud-sdk`) and package-manager mode, so updates
  come from Zypper instead of `gcloud components update`.

## Updating

- `aws-cli-v2`, `doctl`, `google-cloud-cli`: bump `Version:` and the paths
  and checksums in `_service`, then add a `.changes` entry. For AWS, verify
  the new `.sig` locally before pinning the checksum.
- `azure-cli`: `azure-cli/make-wheels.sh --lock <version>` regenerates
  `requirements.lock` and the spec version; `azure-cli/make-wheels.sh`
  builds `azure-cli-<version>-wheels.tar.gz`, uploaded to OBS next to the
  spec (it is not committed here).

## Validation

```sh
python3 -m unittest discover -s tests -v
for spec in */*.spec; do rpmspec -P "$spec" >/dev/null; done
```
