<div align="center">
<p align="center">
  <a href="https://gitlab.com/losuler/zypper-automatic">
  </a>

  <p align="center">
    <h3 align="center">Zypper Automatic</h3>
    <p align="center">
      An automatic updater for Zypper designed for openSUSE.
    </p>
  </p>
</p>
</div>

<hr />

The benefits this has over [`yast2-online-update-configuration`](https://github.com/yast/yast-online-update-configuration) is the integration with systemd services/timers and email notifications similar to what's provided in [`dnf-automatic`](https://dnf.readthedocs.io/en/latest/automatic.html) or [`unattended-upgrades`](https://wiki.debian.org/UnattendedUpgrades).

## Builds

Builds are available on OBS at https://build.opensuse.org/package/show/home:losuler/zypper-automatic.

This repo can be added on supported systems by:

```bash
# openSUSE Tumbleweed
zypper addrepo https://download.opensuse.org/repositories/home:losuler/openSUSE_Tumbleweed/home:losuler.repo
# openSUSE Leap 15.2
zypper addrepo https://download.opensuse.org/repositories/home:losuler/openSUSE_Leap_15.2/home:losuler.repo

zypper refresh
zypper install zypper-automatic
```

## Config

The configuration file `zypper-automatic.ini` has three main sections. The already filled in values in the example config are the defaults.

### Zypper

```toml
[ZYPPER]
PATCH_CATEGORIES =
WITH_INTERACTIVE =
LIST_ONLY =
```

`PATCH_CATEGORIES` is a list delimited by commas `,` of patches you'd like to install. "Commonly used values for category are security, recommended, optional, feature, document or yast".[1]

`WITH_INTERACTIVE` when set to `TRUE` will install "interactive patches, that is, those that need reboot, contain a message, or update a package whose license needs to be confirmed."[2]

`LIST_ONLY` when set to `TRUE` will only send a list of the patches waiting to be installed and will not install them.

[1]: https://en.opensuse.org/SDB:Zypper_manual#CONCEPTS
[2]: https://en.opensuse.org/SDB:Zypper_manual#COMMANDS

### Emitters

```toml
[EMITTERS]
EMITTER =
```

The `EMITTER` refers to one of the message services listed in the subsections below.

#### Email

```toml
[EMAIL]
EMAIL_TO =
```

`EMAIL_TO` is the email in which to send the notification to. It requires a Sendmail compatible MTA (Mail Transfer Agent) to be setup.

#### Telegram

```toml
[TELEGRAM]
TOKEN =
CHAT_ID =
```

`TOKEN` is the token for the Telegram bot, which is provided by creating a bot by following the steps provided in the [Telegram bot API documentation](https://core.telegram.org/bots#3-how-do-i-create-a-bot).

`CHAT_ID` is the unique identifier for the target chat. It can be obtained by messaging the bot and executing the following command (replace `$BOT_TOKEN`). The ID may be found at `"chat": {"id": 12345678},`:

```sh
curl https://api.telegram.org/bot$BOT_TOKEN/getUpdates | python -m json.tool
```
