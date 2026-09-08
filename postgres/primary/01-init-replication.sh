#!/bin/bash
set -e

# Crea el usuario replicador usando las variables de entorno
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE ROLE $REPLICA_USER WITH REPLICATION LOGIN PASSWORD '$REPLICA_PASSWORD';
EOSQL

# Da permisos en pg_hba.conf para permitir conexiones de replicación
echo "host replication $REPLICA_USER 0.0.0.0/0 md5" >> "$PGDATA/pg_hba.conf"
