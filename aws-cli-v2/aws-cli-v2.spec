Name:           aws-cli-v2
Version:        2.40.4
Release:        0
%global debug_package %{nil}
# AWS CLI Team signing key, as published in the AWS CLI user guide.
%global aws_key_fingerprint FB5DB77FD5C118B80511ADA8A6310ACC4672475C
Summary:        Official AWS Command Line Interface, version 2
# The upstream bundle ships its own Python runtime and dependencies; their
# licenses are listed in THIRD_PARTY_LICENSES, installed with the package.
License:        Apache-2.0
URL:            https://aws.amazon.com/cli/
Source0:        awscli-exe-linux-x86_64-%{version}.zip
Source1:        awscli-exe-linux-x86_64-%{version}.zip.sig
Source2:        aws-cli-team.asc
Source3:        LICENSE.txt
BuildRequires:  gpg2
BuildRequires:  unzip
ExclusiveArch:  x86_64
# openSUSE ships AWS CLI v1 as aws-cli-cmd; both install /usr/bin/aws.
Conflicts:      aws-cli-cmd

# The upstream bundle is a frozen Python application with private copies of
# libpython and its extension modules, loaded from its own directory. They
# are not system libraries: keep them out of automatic Provides/Requires.
%global __provides_exclude_from ^%{_libexecdir}/aws-cli/.*$
%global __requires_exclude_from ^%{_libexecdir}/aws-cli/.*$

%description
The AWS Command Line Interface (AWS CLI) v2 is Amazon's official tool to
manage AWS services from the terminal. This package repackages the
official Linux installer bundle for the signed Lyra OS OBS repositories:
the archive is pinned by SHA-256 and its detached signature is checked
against the AWS CLI Team key at build time, as the AWS CLI user guide
describes. The bundle carries its own Python runtime.

%prep
%setup -q -c -T
# Verify the detached signature with only the pinned AWS CLI Team key.
mkdir -m 0700 gnupg
gpg --homedir gnupg --batch --quiet --import %{SOURCE2}
gpg --homedir gnupg --batch --with-colons --fingerprint | grep -qx 'fpr:::::::::%{aws_key_fingerprint}:'
gpg --homedir gnupg --batch --status-fd 1 --verify %{SOURCE1} %{SOURCE0} | grep -q '^\[GNUPG:\] VALIDSIG %{aws_key_fingerprint} '
unzip -q %{SOURCE0}
cp %{SOURCE3} .

%build
# Prebuilt upstream bundle; there is no compilation step.

%install
mkdir -p %{buildroot}%{_libexecdir}/aws-cli
cp -a aws/dist/. %{buildroot}%{_libexecdir}/aws-cli/
mkdir -p %{buildroot}%{_bindir}
ln -s ../libexec/aws-cli/aws %{buildroot}%{_bindir}/aws
ln -s ../libexec/aws-cli/aws_completer %{buildroot}%{_bindir}/aws_completer
mkdir -p %{buildroot}%{_datadir}/bash-completion/completions
echo 'complete -C %{_bindir}/aws_completer aws' > %{buildroot}%{_datadir}/bash-completion/completions/aws

%check
%{buildroot}%{_libexecdir}/aws-cli/aws --version | grep -q '^aws-cli/%{version} '

%files
%license LICENSE.txt aws/THIRD_PARTY_LICENSES
%{_bindir}/aws
%{_bindir}/aws_completer
%{_libexecdir}/aws-cli/
%{_datadir}/bash-completion/completions/aws

%changelog
