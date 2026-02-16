#!/usr/bin/env python3
"""
Analyze a work session's draws to detect periodicity and set `cycle_length` and
`lottery_schedule` in `work_sessions`. Also adjust `start_date` and `end_date`
to align to weekly cycles (Monday-Sunday) as described.

Usage:
  python fix_session_periodicity.py --session-id 23
  or
  python fix_session_periodicity.py --session-name Sim_2024_Mon-Sun_weekly
"""
import os
import argparse
from datetime import timedelta
import psycopg2
from psycopg2.extras import RealDictCursor, Json

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


def analyze_and_fix(session_id=None, session_name=None):
    if not session_id and not session_name:
        raise ValueError('session_id or session_name required')

    conn = connect()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    # fetch session id if name provided
    if session_name and not session_id:
        cur.execute("SELECT id FROM work_sessions WHERE name = %s", (session_name,))
        row = cur.fetchone()
        if not row:
            raise RuntimeError(f"Session named {session_name} not found")
        session_id = row['id']

    # get draws for session
    cur.execute("SELECT draw_number, lottery_name, draw_date FROM session_draws WHERE session_id = %s ORDER BY draw_date", (session_id,))
    draws = cur.fetchall()
    if not draws:
        raise RuntimeError(f"No draws found for session {session_id}")

    # build weekday -> {lottery_name: count}
    weekday_map = {i: {} for i in range(7)}
    dates = []
    for d in draws:
        dt = d['draw_date']
        if isinstance(dt, str):
            # try parse
            from datetime import datetime
            dt = datetime.fromisoformat(dt)
        wd = dt.weekday()
        dates.append(dt.date())
        name = d.get('lottery_name') or d.get('lottery') or f"lottery_{wd}"
        cnts = weekday_map.setdefault(wd, {})
        cnts[name] = cnts.get(name, 0) + 1

    # pick most common name per weekday
    schedule = {}
    active_days = []
    for wd in range(7):
        cnts = weekday_map.get(wd, {})
        if cnts:
            # pick name with max count
            name = max(cnts.items(), key=lambda x: x[1])[0]
            schedule[str(wd)] = name
            active_days.append(wd)
        else:
            schedule[str(wd)] = None

    full_week = len(active_days) == 7

    earliest = min(dates)
    # compute start_date: if full_week -> align to Monday on or before earliest
    # else -> align to next Monday after earliest (so that cycle runs Mon-Sun)
    if earliest.weekday() == 0:
        monday_on_or_after = earliest
    else:
        # next monday
        days_until_next_monday = (7 - earliest.weekday()) % 7
        monday_on_or_after = earliest + timedelta(days=days_until_next_monday)

    if full_week:
        # start at Monday on or before earliest
        start_date = earliest - timedelta(days=earliest.weekday())
    else:
        # start at next Monday (monday_on_or_after)
        start_date = monday_on_or_after

    end_date = start_date + timedelta(days=6)

    cycle_length = 7

    # Update work_sessions
    update_fields = {
        'cycle_length': cycle_length,
        'lottery_schedule': schedule,
        'start_date': start_date,
        'end_date': end_date
    }

    # Build SQL dynamically only for columns that exist
    cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name='work_sessions'")
    available = {r['column_name'] for r in cur.fetchall()}

    set_parts = []
    params = []
    for k, v in update_fields.items():
        if k in available:
            set_parts.append(f"{k} = %s")
            if k == 'lottery_schedule':
                params.append(Json(v))
            else:
                params.append(v)

    if not set_parts:
        raise RuntimeError('No updateable fields present in work_sessions')

    sql = f"UPDATE work_sessions SET {', '.join(set_parts)} WHERE id = %s"
    params.append(session_id)
    cur.execute(sql, tuple(params))
    conn.commit()
    cur.close()
    conn.close()

    return {
        'session_id': session_id,
        'cycle_length': cycle_length,
        'lottery_schedule': schedule,
        'start_date': str(start_date),
        'end_date': str(end_date),
        'full_week': full_week,
        'active_days': active_days
    }


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--session-id', type=int)
    parser.add_argument('--session-name', type=str)
    args = parser.parse_args()

    res = analyze_and_fix(session_id=args.session_id, session_name=args.session_name)
    print('Updated session:', res)
