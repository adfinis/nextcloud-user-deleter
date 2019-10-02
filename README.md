# Nextcloud user cleanup

If a user is deleted in LDAP, the user is marked as deleted (remnant table) in Nextcloud after running the [LDAP clean-up job](https://docs.nextcloud.com/server/16/admin_manual/configuration_user/user_auth_ldap_cleanup.html) (user auth ldap cleanup), but the data and the user remain intact.

Nextcloud offers a possibility to delete users via the API, but from Nextcloud's point of view they are no longer allowed to be in LDAP at this time. The LDAP synchronization of users who no longer exist runs in the background and checks only 50 users at a time. Therefore it is not predictable when Nextcloud will look at a user as effectively deleted (LDAP remnant Table).

This Script checks the MySQL-Table and permanently deletes the users if they are marked as deleted.

`setup.py` Installs a (disabled per default) Systemd-Timer which runs every Day at 04:00.

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
git clone https://github.com/adfinis-sygroup/nextcloud-user-deleter
cd nextcloud-user-deleter
python setup.py install
```

### Activate Nextcloud User deleter timer

```
systemctl enable nextcloud-user-deleter.timer
```

## Usage

```
nextcloud-user-deleter [-h] --nextcloud-root NEXTCLOUD_ROOT
                              [--php-binary PHP_BINARY] [--dry-run] [--debug]
```
- `--nextcloud-root` is the root directory where nextcloud is installed. Normally this is `/var/www/html/nextcloud`
- `--php-binary` is the binary to run the occ command with. Defaults to `/opt/remi/php72/root/bin/php`
- `--debug` is a flag to display debug output
- `--dry-run` if this flag is specified, only show what the script would delete instead of actually deleting the users
