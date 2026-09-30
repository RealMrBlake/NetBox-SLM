# NetBox SLM

Software lifecycle and license management for NetBox: software products,
versions, installations and licenses — with expiry notifications and optional
tenant assignment.

| | |
|---|---|
| **Plugin name** | `netbox_slm` |
| **Package** | `netbox-slm` |
| **NetBox** | `4.6.5` |
| **Python** | `>=3.11` |
| **Repository** | <https://git.mrblake.cc/MrBlake/NetBox-SLM> |

## Features

- Manage software products and manufacturers
- Track versions, release types and support periods
- Assign installations to devices, virtual machines or clusters
- Manage software licenses including term, scope and storage location
- Lifetime licenses or renewal intervals in days, months or years
- Store license files, license keys and links to the vendor portal
- Expiry warnings one month and one week before license end by default
- Additional custom warning period in days, weeks or months
- NetBox notifications and optional e-mail via NetBox's SMTP configuration
- Assign licenses to tenant groups and tenants
- Full NetBox UI and REST API
- Filters, bulk import and bulk edit
- UI available in English and German (follows the user's NetBox language)

> **Note:** License keys are stored in the NetBox database and license files in
> NetBox's media directory. Protect and back up the database, REST API and media
> directory accordingly.

## Compatibility

- NetBox `4.6.5`
- Python `>=3.11`

## Installation

All paths assume a standard installation under `/opt/netbox`.

### 1. Install the package

```bash
/opt/netbox/venv/bin/pip install --upgrade --force-reinstall \
  "git+https://git.mrblake.cc/MrBlake/NetBox-SLM.git@master"
```

For reproducible production installs, replace `master` with a release tag or a
full commit ID.

### 2. Add the plugin to `local_requirements.txt`

This makes `upgrade.sh` reinstall the plugin automatically on every NetBox upgrade:

```bash
grep -qxF "git+https://git.mrblake.cc/MrBlake/NetBox-SLM.git@master" /opt/netbox/local_requirements.txt \
  || echo "git+https://git.mrblake.cc/MrBlake/NetBox-SLM.git@master" | sudo tee -a /opt/netbox/local_requirements.txt
```

If the repository is private, the NetBox server needs a read-only deploy token
or an SSH key. Do not store credentials in `local_requirements.txt`.

### 3. Enable the plugin

In `/opt/netbox/netbox/netbox/configuration.py`:

```python
PLUGINS = [
    "netbox_slm",
]
```

If other plugins are already configured, add `netbox_slm` to the existing list.
No `PLUGINS_CONFIG` is required for standard operation.

### 4. Apply migrations, collect static files, restart

```bash
cd /opt/netbox/netbox
/opt/netbox/venv/bin/python manage.py migrate netbox_slm
/opt/netbox/venv/bin/python manage.py collectstatic --no-input
sudo systemctl restart netbox netbox-rq
```

Check the installed version:

```bash
/opt/netbox/venv/bin/pip show netbox-slm
```

## Update

```bash
/opt/netbox/venv/bin/pip install --upgrade --force-reinstall \
  "git+https://git.mrblake.cc/MrBlake/NetBox-SLM.git@master"

cd /opt/netbox/netbox
/opt/netbox/venv/bin/python manage.py migrate netbox_slm
/opt/netbox/venv/bin/python manage.py collectstatic --no-input
sudo systemctl restart netbox netbox-rq
```

`--force-reinstall` makes pip pick up branch changes even if the package
version has not been bumped.

When NetBox itself is upgraded, `upgrade.sh` reinstalls the plugin from
`local_requirements.txt` and runs migrations and `collectstatic`:

```bash
sudo /opt/netbox/upgrade.sh
sudo systemctl restart netbox netbox-rq
```

## Uninstall

1. Remove `"netbox_slm"` from `PLUGINS`.
2. Remove the line from `/opt/netbox/local_requirements.txt`.
3. Uninstall the package and restart NetBox:

```bash
/opt/netbox/venv/bin/pip uninstall netbox-slm
sudo systemctl restart netbox netbox-rq
```

The plugin's database tables are not dropped automatically.

## Usage

### Expiry notifications

Notifications are enabled by default for licenses with an expiry date. The
default reminders are one month and one week before expiry. Per license, an
additional custom warning period can be set or the defaults can be disabled.

Recipients decide themselves whether they are notified: sales, the responsible
technician or other users open the license and click the NetBox **Subscribe**
action (**Unsubscribe** stops it). Without subscribers no message is sent.

A NetBox notification is always created. If **E-mail notifications** is enabled
on the license, the plugin also sends an e-mail to the address stored in the
user account; NetBox SMTP must be configured for this.

Enabling e-mail delivery can only be changed by administrators or users with
the permission `netbox_slm.manage_softwarelicense_email_notifications`. SMTP
credentials are maintained only in the NetBox server configuration and are not
visible in the plugin.

The check runs once a day as a NetBox system job. Once the first configured
reminder date is reached, subscribers are notified on every job run up to and
including the expiry date. The NetBox RQ worker must run with scheduler support,
which is the default for a standard NetBox installation with `rqworker`.

## Origin and license

This repository is based on the original project
[ICTU/netbox_slm](https://github.com/ICTU/netbox_slm). **ICTU** is the original
author and publisher; [Mart Visser](https://github.com/MartVisser) is named as
the contact in the original project.

The changes in this fork are maintained at
[git.mrblake.cc/MrBlake/NetBox-SLM](https://git.mrblake.cc/MrBlake/NetBox-SLM).

Licensed under the [Apache License 2.0](LICENSE). Notices of the original
authors are retained.
