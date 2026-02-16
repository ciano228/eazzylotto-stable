#!/usr/bin/env python3
"""
Créer une session simulée 2024 : 7 tirages par semaine (lundi..dimanche),
du premier lundi 2024 au dernier dimanche 2024. Chaque tirage contient 5 numéros
générés aléatoirement. Les entrées sont insérées dans `work_sessions` et
`session_draws` pour être utilisables par les services existants.

Usage: python create_2024_weekly_session.py
"""
import os
import random
from datetime import date, datetime, timedelta
import psycopg2
from psycopg2.extras import Json


DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', 5432)),
    'dbname': os.getenv('DB_NAME', 'katooling_main_system'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'Katulaa_33')
}


def first_monday_2024():
    return date(2024, 1, 1)  # 2024-01-01 is Monday


def last_sunday_2024():
    return date(2024, 12, 29)  # last Sunday inclusive to cover full weeks


LOTO_NAMES = {
    0: 'monday-loto',
    1: 'tuesday-loto',
    2: 'wednesday-loto',
    3: 'thursday-loto',
    4: 'friday-loto',
    5: 'saturday-loto',
    6: 'sunday-loto'
}


def connect():
    conn = psycopg2.connect(
        host=DB_CONFIG['host'],
        port=DB_CONFIG['port'],
        dbname=DB_CONFIG['dbname'],
        user=DB_CONFIG['user'],
        password=DB_CONFIG['password']
    )
    return conn


def create_work_session(conn, name, start_date, end_date):
    cur = conn.cursor()
    now = datetime.now()

    # Inspect available columns in work_sessions and build insert accordingly
    cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name='work_sessions' ORDER BY ordinal_position")
    cols = [r[0] for r in cur.fetchall()]

    insert_cols = []
    insert_vals = []

    # Map possible fields to values
    if 'name' in cols:
        insert_cols.append('name'); insert_vals.append(name)
    if 'description' in cols:
        insert_cols.append('description'); insert_vals.append('Simulated weekly session 2024')
    if 'start_date' in cols:
        insert_cols.append('start_date'); insert_vals.append(start_date)
    if 'lottery_type' in cols and 'lottery_type' not in insert_cols:
        insert_cols.append('lottery_type'); insert_vals.append('simulated_weekly')
    if 'end_date' in cols:
        insert_cols.append('end_date'); insert_vals.append(end_date)
    if 'created_at' in cols:
        insert_cols.append('created_at'); insert_vals.append(now)
    if 'is_active' in cols:
        insert_cols.append('is_active'); insert_vals.append(False)
    if 'total_draws' in cols:
        insert_cols.append('total_draws'); insert_vals.append((end_date - start_date).days + 1)
    if 'numbers_per_draw' in cols:
        insert_cols.append('numbers_per_draw'); insert_vals.append(5)
    if 'number_range_min' in cols:
        insert_cols.append('number_range_min'); insert_vals.append(1)
    if 'number_range_max' in cols:
        insert_cols.append('number_range_max'); insert_vals.append(90)
    if 'cycle_length' in cols:
        insert_cols.append('cycle_length'); insert_vals.append(7)

    if not insert_cols:
        raise RuntimeError('No suitable columns found in work_sessions to insert session')

    cols_sql = ', '.join(insert_cols)
    placeholders = ', '.join(['%s'] * len(insert_vals))
    sql = f"INSERT INTO work_sessions ({cols_sql}) VALUES ({placeholders}) RETURNING id"

    cur.execute(sql, tuple(insert_vals))
    session_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    return session_id


def insert_draw(conn, session_id, draw_number, lottery_name, draw_date, numbers):
    cur = conn.cursor()
    try:
        # Try to insert into session_draws with expected columns
        cur.execute(
            """
            INSERT INTO session_draws (session_id, draw_number, lottery_name, draw_date, winning_numbers, is_completed, is_no_draw)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (session_id, draw_number, lottery_name, draw_date, Json(numbers), True, False)
        )
    except Exception:
        conn.rollback()
        # Fallback: try fewer columns
        cur.execute(
            """
            INSERT INTO session_draws (session_id, draw_number, lottery_name, draw_date, winning_numbers)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (session_id, draw_number, lottery_name, draw_date, Json(numbers))
        )

    conn.commit()
    cur.close()


def generate_numbers(n=5, low=1, high=90):
    return sorted(random.sample(range(low, high+1), n))


def main():
    start = first_monday_2024()
    end = last_sunday_2024()

    name = "Sim_2024_Mon-Sun_weekly"
    print(f"Connecting to DB {DB_CONFIG['dbname']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}")
    conn = connect()

    print(f"Creating work session '{name}' from {start} to {end}...")
    session_id = create_work_session(conn, name, start, end)
    print(f"Created session id: {session_id}")

    current = start
    draw_number = 1
    inserted = 0
    while current <= end:
        weekday = current.weekday()  # 0=Mon ..6=Sun
        lottery_name = LOTO_NAMES.get(weekday, f"loto_{weekday}")
        numbers = generate_numbers(5, 1, 90)

        insert_draw(conn, session_id, draw_number, lottery_name, current, numbers)
        inserted += 1
        if draw_number % 50 == 0:
            print(f"Inserted {draw_number} draws so far...")

        draw_number += 1
        current = current + timedelta(days=1)

    print(f"Finished inserting {inserted} draws for session {session_id}")
    # After inserting draws, run periodicity detection to set cycle_length and schedule
    try:
        from fix_session_periodicity import analyze_and_fix
        print(f"Running periodicity fixer for session {session_id}...")
        res = analyze_and_fix(session_id=session_id)
        print('Periodicity fixer result:', res)
    except Exception as e:
        print('Periodicity fixer failed:', e)

    conn.close()


if __name__ == '__main__':
    main()
