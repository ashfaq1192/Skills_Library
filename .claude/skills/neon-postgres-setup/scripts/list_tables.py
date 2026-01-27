#!/usr/bin/env python3
"""List tables in Neon database for validation."""
import sys, argparse
try:
    import psycopg2
except ImportError:
    print("❌ psycopg2 not installed: pip install psycopg2-binary")
    sys.exit(1)

def list_tables(connection_string):
    try:
        conn = psycopg2.connect(connection_string)
        cur = conn.cursor()

        # Get all tables
        cur.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)

        tables = cur.fetchall()

        if not tables:
            print("⚠ No tables found in database")
            print("→ Run: python scripts/init_schemas.py --connection-string <conn-string>")
            return 1

        print(f"✓ Database tables ({len(tables)} found):")
        for table in tables:
            # Get row count
            cur.execute(f"SELECT COUNT(*) FROM {table[0]}")
            count = cur.fetchone()[0]
            print(f"  - {table[0]} ({count} rows)")

        cur.close()
        conn.close()
        return 0

    except Exception as e:
        print(f"❌ Failed to list tables: {e}")
        return 1

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--connection-string", required=True)
    args = parser.parse_args()
    sys.exit(list_tables(args.connection_string))
