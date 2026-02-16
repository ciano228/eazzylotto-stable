#!/usr/bin/env python3
"""
Analyze the schema differences between session, work_sessions, and unified_sessions
"""
import psycopg2
import json

DB_CONFIG = {
    'host': 'localhost',
    'database': 'katooling_main_system',
    'user': 'postgres',
    'password': 'Katulaa_33',
    'port': 5432
}

def get_table_schema(cursor, table_name):
    """Get column information for a table"""
    cursor.execute("""
        SELECT column_name, data_type, is_nullable, column_default
        FROM information_schema.columns
        WHERE table_name = %s
        ORDER BY ordinal_position
    """, (table_name,))
    
    columns = []
    for row in cursor.fetchall():
        columns.append({
            'column_name': row[0],
            'data_type': row[1],
            'is_nullable': row[2],
            'column_default': row[3]
        })
    return columns

def get_table_count(cursor, table_name):
    """Get row count for a table"""
    try:
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        return cursor.fetchone()[0]
    except:
        return 0

def main():
    print("=" * 80)
    print("SESSION TABLES ANALYSIS")
    print("=" * 80)
    
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Check which tables exist
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name IN ('session', 'work_sessions', 'unified_sessions')
            ORDER BY table_name
        """)
        
        existing_tables = [row[0] for row in cursor.fetchall()]
        print(f"\n📋 Existing tables: {existing_tables}\n")
        
        # Analyze each table
        all_schemas = {}
        all_counts = {}
        
        for table in existing_tables:
            print(f"\n{'='*80}")
            print(f"TABLE: {table}")
            print(f"{'='*80}")
            
            schema = get_table_schema(cursor, table)
            count = get_table_count(cursor, table)
            
            all_schemas[table] = schema
            all_counts[table] = count
            
            print(f"Row count: {count}")
            print(f"Column count: {len(schema)}\n")
            
            print(f"{'Column Name':<30} {'Data Type':<20} {'Nullable':<10} {'Default'}")
            print("-" * 80)
            
            for col in schema:
                default_str = str(col['column_default'])[:20] if col['column_default'] else '-'
                print(f"{col['column_name']:<30} {col['data_type']:<20} {col['is_nullable']:<10} {default_str}")
        
        # Find column differences
        print(f"\n{'='*80}")
        print("COLUMN COMPARISON")
        print(f"{'='*80}")
        
        all_columns = set()
        for schema in all_schemas.values():
            for col in schema:
                all_columns.add(col['column_name'])
        
        print(f"\n{'Column Name':<30}", end='')
        for table in existing_tables:
            print(f" {table:<20}", end='')
        print()
        print("-" * 100)
        
        for col_name in sorted(all_columns):
            print(f"{col_name:<30}", end='')
            for table in existing_tables:
                table_cols = [c['column_name'] for c in all_schemas[table]]
                if col_name in table_cols:
                    print(f" ✓ {'':<19}", end='')
                else:
                    print(f" ✗ {'':<19}", end='')
            print()
        
        # Sample data from each table
        print(f"\n{'='*80}")
        print("SAMPLE DATA")
        print(f"{'='*80}")
        
        for table in existing_tables:
            print(f"\n{table}: (showing first 3 rows)")
            cursor.execute(f"SELECT * FROM {table} LIMIT 3")
            rows = cursor.fetchall()
            col_names = [c['column_name'] for c in all_schemas[table]]
            
            for row in rows:
                print(f"  Row: {dict(zip(col_names, row))}")
        
        cursor.close()
        conn.close()
        
        print(f"\n{'='*80}")
        print("✅ Analysis complete!")
        print(f"{'='*80}\n")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
