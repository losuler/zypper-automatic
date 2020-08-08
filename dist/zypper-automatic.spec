Name:           zypper-automatic
Version:        2.0.0
Release:        1
Summary:        Automated updates

License:        GPL-3.0-or-later
URL:            https://gitlab.com/losuler/%{name}
Source0:        https://gitlab.com/losuler/%{name}/-/archive/%{version}/%{name}-%{version}.tar.gz
Patch0:         env-script-interpreter-fix.patch

Requires:       python3
Requires:       python3-requests

BuildArch:      noarch

%description
zypper-automatic is a small program that automatically installs
and notifies of updates at defined intervals.

%prep
%autosetup

%build

%install
mkdir -p %{buildroot}/%{_bindir}
mkdir -p %{buildroot}/%{_sysconfdir}
mkdir -p %{buildroot}/%{_unitdir}
install -m 0755 main.py %{buildroot}/%{_bindir}/%{name}
install -m 0644 config.conf %{buildroot}/%{_sysconfdir}/%{name}.conf
install -m 0644 dist/%{name}.service %{buildroot}/%{_unitdir}/%{name}.service
install -m 0644 dist/%{name}.timer %{buildroot}/%{_unitdir}/%{name}.timer

%files
%license LICENSE.txt
%{_bindir}/%{name}
%config %{_sysconfdir}/%{name}.conf
%{_unitdir}/%{name}.service
%{_unitdir}/%{name}.timer

%changelog
