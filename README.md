# Nextcloud user cleanup

Nextcloud allows to delete users via the API (e.g., using `occ user:delete`), but from Nextcloud's point of view they need to be deleted in LDAP first. If a user is deleted in LDAP, the user is marked as deleted in Nextcloud after the [LDAP clean-up job](https://docs.nextcloud.com/server/16/admin_manual/configuration_user/user_auth_ldap_cleanup.html) (user auth ldap cleanup), but the data and the user in Nextclouds filesystem and database remain intact (remnant table, `occ ldap:show-remnants`).

LDAP users that do not exist anymore are recognized by the clean-up job. The job is running in the background and examines 50 users at a time. Therefore, the exact time when Nextcloud will effectively see a user as "deleted" (LDAP remnant table) is not predictable .

This Script checks the MySQL-Table `oc_preferences` for remnant LDAP users and permanently deletes the users in Nextclouds database.

`setup.py` installs a Systemd-Timer which runs at 04:00 daily, but is disabled per default.

## Installation

### Script Installation

Prerequisites:
- EPEL Repository activated

Procedure:
- Install requirements:
```
yum install mysql-connector-python python-setuptools
```
- Install the Script:
```
git clone https://github.com/adfinis-sygroup/nextcloud-user-cleanup
cd nextcloud-user-cleanup
python setup.py install
```

### Activate Nextcloud User cleanup timer

```
systemctl enable nextcloud-user-cleanup.timer
```

## Usage

```
nextcloud-user-cleanup [-h] --nextcloud-root NEXTCLOUD_ROOT
                              [--php-binary PHP_BINARY] [--dry-run] [--debug]
```
- `--nextcloud-root` is the root directory where nextcloud is installed. Normally this is `/var/www/html/nextcloud`
- `--php-binary` is the binary to run the occ command with. Defaults to `/opt/remi/php72/root/bin/php`
- `--debug` is a flag to display debug output
- `--dry-run` if this flag is specified, only show what the script would delete instead of actually deleting the users
