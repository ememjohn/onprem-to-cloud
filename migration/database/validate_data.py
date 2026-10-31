#!/usr/bin/env python3
import sys
import hashlib
import psycopg2
from psycopg2.extras import RealDictCursor

def get_connection(conn_str):
    try:
        return psycopg2.connect(conn_str)
    except Exception as exc:
        print(f"[!] Database connection failure: {exc}")
        return None

def fetch_table_summary(conn, table_name):
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(f"SELECT COUNT(*) AS total_count FROM {table_name};")
        count = cur.fetchone()["total_count"]

        cur.execute(f"SELECT * FROM {table_name} ORDER BY id;")
        rows = cur.fetchall()

        hasher = hashlib.sha256()
        for row in rows:
            hasher.update(str(sorted(row.items())).encode("utf-8"))
        checksum = hasher.hexdigest()[:16]

        return count, checksum

def compare_databases(source_url, target_url):
    print("=" * 70)
    print("  SABAY PREMIUM BANK: CORE LEDGER SYSTEM: DATA INTEGRITY AND CHECKSUM VALIDATION")
    print("=" * 70)

    src_conn = get_connection(source_url)
    tgt_conn = get_connection(target_url)

    if not src_conn or not tgt_conn:
        print("[CRITICAL] Unable to establish dual database connections. Aborting.")
        sys.exit(1)

    tables = ["customers", "orders"]
    all_matched = True

    print(f"{'Table':<15} | {'Source Count':<12} | {'Target Count':<12} | {'Checksum Match':<15}")
    print("-" * 70)

    for tbl in tables:
        src_count, src_hash = fetch_table_summary(src_conn, tbl)
        tgt_count, tgt_hash = fetch_table_summary(tgt_conn, tbl)

        match = (src_count == tgt_count) and (src_hash == tgt_hash)
        if not match:
            all_matched = False

        status = "PASSED" if match else "FAILED"
        print(f"{tbl:<15} | {src_count:<12} | {tgt_count:<12} | {status:<15}")

    src_conn.close()
    tgt_conn.close()

    print("=" * 70)
    if all_matched:
        print("[SUCCESS] Zero data loss detected. Source and target are mathematically identical.")
        sys.exit(0)
    else:
        print("[FAILURE] Data discrepancy or checksum mismatch detected.")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 validate_data.py <SOURCE_DATABASE_URL> <TARGET_DATABASE_URL>")
        sys.exit(1)

    compare_databases(sys.argv[1], sys.argv[2])
