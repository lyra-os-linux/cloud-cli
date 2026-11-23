Name:           google-cloud-cli
Version:        594.0.1
Release:        0
%global debug_package %{nil}
%global sdkdir %{_prefix}/lib64/google-cloud-sdk
Summary:        Google Cloud CLI (gcloud, gsutil and bq)
# The upstream archive bundles its own Python runtime and third-party
# libraries; their licenses ship inside the SDK tree.
License:        Apache-2.0
URL:            https://cloud.google.com/sdk/
Source0:        google-cloud-cli-%{version}-linux-x86_64.tar.gz
ExclusiveArch:  x86_64
Provides:       google-cloud-sdk = %{version}
# Same layout and dependency policy as Google's own RPM: the SDK runs on
# its bundled Python, and nothing inside it is a system library.
AutoReqProv:    no
Requires:       /bin/sh

%description
The Google Cloud CLI manages Google Cloud resources from the terminal:
gcloud for most services, gsutil for Cloud Storage and bq for BigQuery.
This package repackages the official versioned Linux archive (pinned by
SHA-256) for the signed Lyra OS OBS repositories, with the same layout as
Google's RPM: the SDK lives in %{sdkdir}, it runs on its bundled
Python, and "gcloud components" is switched to package-manager mode, so
updates come from Zypper. Extra components (kubectl, emulators, ...) are
not shipped.

%prep
%setup -q -c -T
tar -xzf %{SOURCE0}

%build
# Prebuilt upstream archive; there is no compilation step.

%install
cd google-cloud-sdk
# Package-manager mode, as in Google's RPM: the component manager refuses
# to update a root-owned install and points at the package manager.
sed -i 's/"disable_updater": false/"disable_updater": true/' lib/googlecloudsdk/core/config.json
cp rpm/mapping/command_mapping.yaml rpm/mapping/component_mapping.yaml .install/
rm -rf rpm deb install.sh install.bat
mkdir -p %{buildroot}%{sdkdir}
cp -a . %{buildroot}%{sdkdir}/
mkdir -p %{buildroot}%{_bindir}
for tool in gcloud gsutil bq docker-credential-gcloud git-credential-gcloud.sh; do
    ln -s ../lib64/google-cloud-sdk/bin/$tool %{buildroot}%{_bindir}/$tool
done
install -D -m 0644 completion.bash.inc %{buildroot}%{_datadir}/bash-completion/completions/gcloud
for tool in gsutil bq; do
    ln -s gcloud %{buildroot}%{_datadir}/bash-completion/completions/$tool
done

%check
grep -q '"disable_updater": true' %{buildroot}%{sdkdir}/lib/googlecloudsdk/core/config.json
test -f %{buildroot}%{sdkdir}/.install/component_mapping.yaml
test "$(cat %{buildroot}%{sdkdir}/VERSION)" = "%{version}"
test -x %{buildroot}%{sdkdir}/platform/bundledpythonunix/bin/python3

%files
%license google-cloud-sdk/LICENSE
%{_bindir}/gcloud
%{_bindir}/gsutil
%{_bindir}/bq
%{_bindir}/docker-credential-gcloud
%{_bindir}/git-credential-gcloud.sh
%{sdkdir}/
%{_datadir}/bash-completion/completions/gcloud
%{_datadir}/bash-completion/completions/gsutil
%{_datadir}/bash-completion/completions/bq

%changelog
