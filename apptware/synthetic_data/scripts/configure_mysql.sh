#!/bin/bash

ROOT_PASSWORD=${ROOT_PASSWORD:-root}
DB_NAME=${DB_NAME:-pieces_common}
DB_USER=${DB_USER:-pieces_dev}
DB_PASS=${DB_PASS:-pieces_dev}

__setup_credentials() {
    echo "Setting up new DB and user credentials."
    mkdir -p /var/run/mysqld
    chown mysql:mysql /var/run/mysqld
    /usr/sbin/mysqld & sleep 10
    mysql --user=root --password=$ROOT_PASSWORD -e "CREATE DATABASE $DB_NAME"
    mysql --user=root --password=$ROOT_PASSWORD -e "GRANT ALL PRIVILEGES ON $DB_NAME.* TO '$DB_USER'@'localhost' IDENTIFIED BY '$DB_PASS'; FLUSH PRIVILEGES;"
    mysql --user=root --password=$ROOT_PASSWORD -e "GRANT ALL PRIVILEGES ON $DB_NAME.* TO '$DB_USER'@'%' IDENTIFIED BY '$DB_PASS'; FLUSH PRIVILEGES;"
    cat /app/schema/*.sql | mysql --user=root --password=$ROOT_PASSWORD $DB_NAME
    sleep 10
}

__setup_credentials

