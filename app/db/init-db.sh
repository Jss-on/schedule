#!/bin/bash
set -e

# Create the database
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE DATABASE driving_school_db;
EOSQL

# Connect to the new database and execute schema.sql
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "driving_school_db" -f /docker-entrypoint-initdb.d/schema.sql
