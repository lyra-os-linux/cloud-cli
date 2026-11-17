Name:           azure-cli
Version:        2.93.0
Release:        0
%global debug_package %{nil}
%global azdir %{_prefix}/lib64/az
Summary:        Microsoft Azure command-line interface
# azure-cli itself is MIT; the vendored dependencies are under MIT,
# Apache-2.0, BSD-3-Clause, BSD-2-Clause, MPL-2.0, PSF-2.0 and ISC.
License:        MIT AND Apache-2.0 AND BSD-3-Clause AND BSD-2-Clause AND MPL-2.0 AND PSF-2.0 AND ISC
URL:            https://learn.microsoft.com/cli/azure/
# Wheels from PyPI, hash-pinned in requirements.lock; see make-wheels.sh.
Source0:        azure-cli-%{version}-wheels.tar.gz
Source1:        requirements.lock
Source2:        az
Source3:        make-wheels.sh
BuildRequires:  python313
BuildRequires:  python313-pip
Requires:       python313
ExclusiveArch:  x86_64

# The vendored wheels carry private extension modules (cryptography,
# psutil, ...) for this tree only: keep them out of the system-wide
# automatic Provides/Requires.
%global __provides_exclude_from ^%{azdir}/.*$
%global __requires_exclude_from ^%{azdir}/.*$

%description
The Azure CLI (az) manages Microsoft Azure resources from the terminal.
Microsoft's own openSUSE repository stopped at 2.38 and its RHEL RPM
needs Python 3.12, which Leap 16 does not ship; this package installs the
official azure-cli release from PyPI on the system Python 3.13, with the
same layout as Microsoft's RPM (%{azdir}). Every wheel is pinned by
SHA-256 in requirements.lock and verified by pip at build time. Updates
come from Zypper; "az extension add" keeps working per user.

%prep
%setup -q -c -T
tar -xzf %{SOURCE0}

%build
# Wheels are installed as-is; there is no compilation step.

%install
python3.13 -m pip install --no-index --find-links wheels --require-hashes \
    --no-deps --no-compile --disable-pip-version-check --no-warn-script-location \
    --target %{buildroot}%{azdir}/lib -r %{SOURCE1}
# Console scripts carry the build root in their shebangs; /usr/bin/az
# (Source2) replaces them. Keep the argcomplete-based completion only.
rm -rf %{buildroot}%{azdir}/lib/bin
PYTHONPATH=%{buildroot}%{azdir}/lib python3.13 -s -m argcomplete.scripts.register_python_argcomplete --shell bash az > az.bash
install -D -m 0644 az.bash %{buildroot}%{_datadir}/bash-completion/completions/az
install -D -m 0755 %{SOURCE2} %{buildroot}%{_bindir}/az
cp %{buildroot}%{azdir}/lib/azure_cli-%{version}.dist-info/licenses/LICENSE.txt .
python3.13 -m compileall -q -j0 -s %{buildroot} -p / %{buildroot}%{azdir}/lib

%check
PYTHONPATH=%{buildroot}%{azdir}/lib python3.13 -sm azure.cli --version > version.txt 2>&1 || :
grep -Eq '^azure-cli +%{version}' version.txt
sh -n %{buildroot}%{_bindir}/az

%files
%license LICENSE.txt
%{_bindir}/az
%{azdir}/
%{_datadir}/bash-completion/completions/az

%changelog
