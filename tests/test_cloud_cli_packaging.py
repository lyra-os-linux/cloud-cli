from __future__ import annotations

import re
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKAGES = {
    "aws-cli-v2": {"awscli.amazonaws.com", "raw.githubusercontent.com"},
    "doctl": {"github.com", "raw.githubusercontent.com"},
    "google-cloud-cli": {"dl.google.com"},
}
AWS_KEY = "FB5DB77FD5C118B80511ADA8A6310ACC4672475C"


def spec(package: str) -> str:
    return (ROOT / package / f"{package}.spec").read_text(encoding="utf-8")


def version(package: str) -> str:
    match = re.search(r"^Version:\s+(\S+)$", spec(package), re.MULTILINE)
    assert match
    return match.group(1)


class DownloadedSourcesTests(unittest.TestCase):
    def test_every_download_is_https_versioned_and_sha256_pinned(self) -> None:
        for package, hosts in PACKAGES.items():
            with self.subTest(package=package):
                services = ET.parse(ROOT / package / "_service").getroot().findall("service")
                downloads = [s for s in services if s.get("name") == "download_url"]
                verifiers = [s for s in services if s.get("name") == "verify_file"]
                self.assertTrue(downloads)
                fetched = set()
                for service in downloads:
                    params = {p.get("name"): (p.text or "") for p in service}
                    self.assertEqual(params["protocol"], "https")
                    self.assertIn(params["host"], hosts)
                    self.assertIn(version(package), params["path"])
                    self.assertNotIn("latest", params["path"].lower())
                    fetched.add(Path(params["path"]).name)
                verified = set()
                for service in verifiers:
                    params = {p.get("name"): (p.text or "") for p in service}
                    self.assertEqual(params["verifier"], "sha256")
                    self.assertRegex(params["checksum"], r"^[0-9a-f]{64}$")
                    verified.add(params["file"].removeprefix("_service:download_url:"))
                self.assertEqual(fetched, verified)


class AwsTests(unittest.TestCase):
    def test_signature_is_checked_against_the_pinned_aws_cli_team_key(self) -> None:
        text = spec("aws-cli-v2")
        self.assertIn(f"%global aws_key_fingerprint {AWS_KEY}", text)
        self.assertIn("VALIDSIG %{aws_key_fingerprint}", text)
        self.assertIn("Source2:        aws-cli-team.asc", text)
        key = (ROOT / "aws-cli-v2" / "aws-cli-team.asc").read_text(encoding="ascii")
        self.assertTrue(key.startswith("-----BEGIN PGP PUBLIC KEY BLOCK-----"))

    def test_conflicts_with_opensuse_aws_cli_v1(self) -> None:
        self.assertRegex(spec("aws-cli-v2"), r"(?m)^Conflicts:\s+aws-cli-cmd$")


class GoogleTests(unittest.TestCase):
    def test_component_manager_is_switched_to_package_manager_mode(self) -> None:
        text = spec("google-cloud-cli")
        self.assertIn('"disable_updater": true', text)
        self.assertIn("component_mapping.yaml", text)
        self.assertRegex(text, r"(?m)^AutoReqProv:\s+no$")


class AzureTests(unittest.TestCase):
    def test_every_wheel_is_hash_pinned(self) -> None:
        lines = (ROOT / "azure-cli" / "requirements.lock").read_text(encoding="utf-8").splitlines()
        self.assertGreater(len(lines), 100)
        for line in lines:
            self.assertRegex(line, r"^[a-z0-9.-]+==[^ ]+ --hash=sha256:[0-9a-f]{64}$")
        self.assertIn(f"azure-cli=={version('azure-cli')} ", "\n".join(lines) + " ")

    def test_install_is_offline_and_hash_checked(self) -> None:
        text = spec("azure-cli")
        self.assertIn("--no-index", text)
        self.assertIn("--require-hashes", text)
        self.assertIn("--no-deps", text)

    def test_wrapper_runs_the_system_python(self) -> None:
        wrapper = (ROOT / "azure-cli" / "az").read_text(encoding="utf-8")
        self.assertIn("AZ_INSTALLER=RPM", wrapper)
        self.assertIn("exec /usr/bin/python3.13 -sm azure.cli", wrapper)


if __name__ == "__main__":
    unittest.main()
