## About

`zypper-automatic` is an automatic updater for zypper designed for OpenSUSE Leap. 

The benefits this has over [`yast2-online-update-configuration`](https://github.com/yast/yast-online-update-configuration) is the integration with systemd services/timers and email notifications similar to whats provided in [`dnf-automatic`](https://dnf.readthedocs.io/en/latest/automatic.html) or [`unattended-upgrades`](https://wiki.debian.org/UnattendedUpgrades).

## Building

The following is a brief summary of the steps required for creating a binary RPM for `zypper-automatic`.

For a complete guide on RPM packaging see: https://rpm-packaging-guide.github.io/ 

1. Create the RPM build tree.

> **Note:** This creates a directory structure under `~/rpmbuild`. If you want this anywhere else, see the following: http://ftp.rpm.org/max-rpm/s1-rpm-anywhere-different-build-area.html

```
rpmdev-setuptree
```

2. Copy `zypper-automatic.spec` to `~/rpmbuild/SPECS`

```
cp zypper-automatic.spec ~/rpmbuild/SPECS/
```

3. Build the binary RPM.

```
rpmbuild -bb ~/rpmbuild/SPECS/zypper-automatic.spec
```
