#!/usr/bin/env python3
"""
Run the periodicity fixer for all sessions in the `work_sessions` table.
This script imports `analyze_and_fix` from `fix_session_periodicity.py` and
applies it to every session, skipping sessions that already have a `cycle_length`.
"""
import os
import psycopg2
from psycopg2.extras import RealDictCursor

DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', 5432)),
    'dbname': os.getenv('DB_NAME', 'katooling_main_system'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'Katulaa_33')
}


def connect():
    return psycopg2.connect(
        host=DB_CONFIG['host'], port=DB_CONFIG['port'], dbname=DB_CONFIG['dbname'],
        user=DB_CONFIG['user'], password=DB_CONFIG['password']
    )


def main():
    conn = connect()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    # fetch sessions
    cur.execute("SELECT id, name, cycle_length FROM work_sessions ORDER BY id")
    sessions = cur.fetchall()
    if not sessions:
        print('No sessions found')
        return

    from fix_session_periodicity import analyze_and_fix

    results = []
    for s in sessions:
        sid = s['id']
        name = s.get('name')
        existing = s.get('cycle_length')
        if existing:
            print(f"Skipping session {sid} ({name}) — already has cycle_length={existing}")
            continue

        try:
            print(f"Processing session {sid} ({name})...")
            res = analyze_and_fix(session_id=sid)
            print(f" -> Updated: {res}")
            results.append((sid, True, res))
        except Exception as e:
            print(f" -> Error updating session {sid}: {e}")
            results.append((sid, False, str(e)))

    cur.close()
    conn.close()

    print('\nSummary:')
    success = [r for r in results if r[1]]
    failed = [r for r in results if not r[1]]
    print(f"Total processed: {len(results)}, success: {len(success)}, failed: {len(failed)}")


if __name__ == '__main__':
    main()
