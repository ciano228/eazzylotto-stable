"""
Quick script to check tome3 frequency in existing data
"""
import psycopg2
from itertools import combinations

db_config = {
    'dbname': 'katooling_main_system',
    'user': 'postgres',
    'password': 'Katulaa_33',
    'host': 'localhost',
    'port': '5432'
}

conn = psycopg2.connect(**db_config)
cur = conn.cursor()

# Get all draws
cur.execute("""
    SELECT winning_numbers 
    FROM session_draws 
    WHERE jsonb_array_length(winning_numbers::jsonb) > 0
      AND is_completed = TRUE
""")

total_draws = 0
tome3_count = 0

for (numbers,) in cur.fetchall():
    if isinstance(numbers, str):
        import json
        numbers = json.loads(numbers)
    
    total_draws += 1
    
    # Check each pair for tome3
    found_tome3 = False
    for pair in combinations(numbers, 2):
        cur2 = conn.cursor()
        cur2.execute("""
            SELECT tome 
            FROM combinations 
            WHERE univers = 'mundo' AND num1 = %s AND num2 = %s
        """, (min(pair), max(pair)))
        
        row = cur2.fetchone()
        if row and row[0] == 'tome3':
            found_tome3 = True
            break
        cur2.close()
    
    if found_tome3:
        tome3_count += 1

conn.close()

frequency = (tome3_count / total_draws * 100) if total_draws > 0 else 0

print(f"\n{'='*50}")
print(f"TOME3 FREQUENCY ANALYSIS")
print(f"{'='*50}")
print(f"Total draws analyzed: {total_draws}")
print(f"Draws with tome3: {tome3_count}")
print(f"Frequency: {frequency:.2f}%")
print(f"{'='*50}\n")
print(f"Recommended threshold for pattern discovery: {int(frequency * 0.8)}%")
