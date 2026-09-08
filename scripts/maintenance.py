import os
import subprocess
from datetime import datetime
import psycopg2

DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_PORT = os.getenv("DB_PORT", 5000)
DB_NAME = os.getenv("POSTGRES_DB", "app_db")
DB_USER = os.getenv("POSTGRES_USER", "postgres")
DB_PASS = os.getenv("POSTGRES_PASSWORD", "supersecretpassword")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKUP_DIR = os.getenv("BACKUP_DIR", os.path.join(BASE_DIR, "backups"))

def check_replication():
    print("[*] Consultando estado de replicación...")
    try:
        conn = psycopg2.connect(
            host=DB_HOST, port=DB_PORT, dbname=DB_NAME, user=DB_USER, password=DB_PASS
        )
        cur = conn.cursor()
        cur.execute("""
            SELECT client_addr, state, sync_state,
                   pg_wal_lsn_diff(pg_current_wal_lsn(), replay_lsn) AS lag_bytes
            FROM pg_stat_replication;
        """)
        rows = cur.fetchall()
        if rows:
            for r in rows:
                print(f" -> IP Réplica: {r[0]} | Estado: {r[1]} | Modo: {r[2]} | Desfase: {r[3]} bytes")
        else:
            print(" [!] No se detectaron réplicas activas.")
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error al conectar con la base de datos: {e}")

def run_backup():
    print("\n[*] Generando backup lógico de la base de datos...")
    os.makedirs(BACKUP_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = os.path.join(BACKUP_DIR, f"backup_{DB_NAME}_{timestamp}.sql")
    cmd = f"podman exec pg-primary pg_dump -U {DB_USER} {DB_NAME} > \"{backup_file}\""
    try:
        subprocess.run(cmd, shell=True, check=True)
        print(f" -> Backup completado con éxito: {backup_file}")
    except subprocess.CalledProcessError as e:
        print(f"Error al ejecutar backup: {e}")

if __name__ == "__main__":
    check_replication()
    run_backup()
