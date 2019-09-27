#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import logging
import argparse
import subprocess

import mysql.connector


logger = logging.getLogger(__name__)


class ArgparseDirFullPaths(argparse.Action):
    """Expand user- and relative-paths"""
    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, os.path.abspath(os.path.expanduser(values)))


def argparse_is_dir(dirname):
    """Checks if a path is an actual directory"""
    if not os.path.isdir(dirname):
        msg = "{0} is not a directory".format(dirname)
        raise argparse.ArgumentTypeError(msg)
    else:
        return dirname


def setup_logging(debug=False):
    """Configure logging to stdout."""
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)

    stdout_handler = logging.StreamHandler(sys.stdout)

    stdout_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    stdout_handler.setLevel(logging.INFO)
    if debug:
        stdout_handler.setLevel(logging.DEBUG)
    stdout_handler.setFormatter(stdout_formatter)

    root.addHandler(stdout_handler)



class App:

    def __init__(self):
        """
        This function gets called when initing the class
        """
        pass


    def main(self):
        """
        Main function which controls the app
        """
        self.parse_args()
        setup_logging(self.args.debug)
        self.get_config()
        self.connect_db()
        self.delete_old_users()


    def parse_args(self):
        """
        parses the arguments passed to the script
        """
        parser = argparse.ArgumentParser(
            description="Nextcloud user purger"
        )
        parser.add_argument(
            "--nextcloud-root",
            type=argparse_is_dir,
            action=ArgparseDirFullPaths,
            required=True
        )
        parser.add_argument(
            "--php-binary",
            default="/opt/remi/php72/root/bin/php",
            type=argparse.FileType('r'),
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            default=False
        )
        parser.add_argument(
            '--debug',
            action='store_true',
            default=False
        )
        self.args = parser.parse_args()

        self.args.php_binary.close()
        self.args.php_binary = self.args.php_binary.name


    def get_config(self):
        """
        get nextcloud config and extracts
        database connection
        """
        logger.debug("getting database settings from occ command")
        self.occ_bin = os.path.join(
            self.args.nextcloud_root,
            "occ"
        )

        try:
            db_hostport = subprocess.check_output([
                self.args.php_binary,
                self.occ_bin,
                "config:system:get",
                "dbhost"
            ])
            self.db_host, self.db_port = db_hostport.strip().split(":")
            self.db_user = subprocess.check_output([
                self.args.php_binary,
                self.occ_bin,
                "config:system:get",
                "dbuser"
            ]).strip()

            self.db_pass = subprocess.check_output([
                self.args.php_binary,
                self.occ_bin,
                "config:system:get",
                "dbpassword"
            ]).strip()

            self.db_name = subprocess.check_output([
                self.args.php_binary,
                self.occ_bin,
                "config:system:get",
                "dbname"
            ]).strip()

        except subprocess.CalledProcessError:
            logger.error("Failed to get occ settings")
            sys.exit(1)

        logger.debug("DB settings from occ-command: host={0}, port={1}, user={2}, db={3}".format(
            self.db_host, self.db_port, self.db_user, self.db_name
        ))
        pass



    def connect_db(self):
        """
        connects to the database and exits the app
        if something is wrong
        """
        try:
            self.db_connection = mysql.connector.connect(
                user=self.db_user,
                password=self.db_pass,
                host=self.db_host,
                port=self.db_port,
                database=self.db_name
            )
            self.db_cursor = self.db_connection.cursor()
        except:
            logger.error("cannot connect to database")
            sys.exit(1)

        logger.debug("connected database: {0}/{1} as user {2}".format(
            self.db_host,
            self.db_name,
            self.db_user
        ))



    def delete_old_users(self):
        """
        this function does the actual deletion of users
        """

        # fetch list of all disabled users in mattermost
        self.db_cursor.execute(
            "SELECT userid FROM oc_preferences WHERE configkey='isDeleted' AND configvalue=1;"
        )
        delete_candidates = self.db_cursor.fetchall()
        for user in delete_candidates:
            user = user[0]
            logger.info("Delete user {0}".format(
                user
            ))
            if not self.args.dry_run:
                self.delete_nc_user(user)



    def delete_nc_user(self, user):
        """
        delete the user over the mattermost cli interface
        """

        logger.info("actually deleting user with ID {0}".format(
            user
        ))
        cmd = [
            self.args.php_binary,
            self.occ_bin,
            "user:delete",
            user,
        ]
        subprocess.check_output(cmd)


def main():
    app = App()
    app.main()


if __name__ == '__main__':
    main()
