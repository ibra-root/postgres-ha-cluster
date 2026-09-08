#!/bin/sh
set -e

# Si el directorio de datos está vacío, clonamos el primario
if [ ! -s "$PGDATA/PG_VERSION" ]; then
    echo "[*] Esperando a que el nodo primario esté listo..."
    until pg_isready -h pg-primary -p 5432 -U "$POSTGRES_USER"; do
        sleep 1
    done

    echo "[*] Clonando base de datos desde pg-primary vía pg_basebackup..."
    export PGPASSWORD="$REPLICA_PASSWORD"
    pg_basebackup -h pg-primary -U "$REPLICA_USER" -D "$PGDATA" -Fp -Xs -R
    chmod 0700 "$PGDATA"
    echo "[*] Clonación completada."
fi

# Inicia PostgreSQL con el entrypoint oficial
exec docker-entrypoint.sh postgres
