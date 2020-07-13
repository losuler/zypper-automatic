Name:           zypper-automatic
Version:        1.0.0
Release:        1%{?dist}
Summary:        Zypper Updater

License:        GPL-3.0-or-later
URL:            https://gitlab.com/losuler/%{name}
Source0:        https://gitlab.com/losuler/%{name}/-/archive/%{version}/%{name}-%{version}.tar.gz

Requires:       python3
BuildArch:      noarch

%description
zypper-automatic is a small script that automatically updates
and patches software at defined intervals.

%prep
%autosetup

%build

%install
mkdir -p %{buildroot}/%{_bindir}
mkdir -p %{buildroot}/%{_sysconfdir}
mkdir -p %{buildroot}/%{_unitdir}
install -m 0755 %{name}.py %{buildroot}/%{_bindir}/%{name}
install -m 0644 %{name}.ini %{buildroot}/%{_sysconfdir}/%{name}.ini
install -m 0644 %{name}.service %{buildroot}/%{_unitdir}/%{name}.service
install -m 0644 %{name}.timer %{buildroot}/%{_unitdir}/%{name}.timer

%files
%license LICENSE
%{_bindir}/%{name}
%{_sysconfdir}/%{name}.ini
%{_unitdir}/%{name}.service
%{_unitdir}/%{name}.timer

%changelog
