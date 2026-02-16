# -*- coding: utf-8 -*-
import psycopg2
from itertools import combinations

conn = psycopg2.connect(
    host='localhost',
    database='katooling_main_system',
    user='postgres',
    password='Katulaa_33',
    port=5432
)
cur = conn.cursor()

nums = [1, 2, 3, 4, 5]
combos = list(combinations(nums, 2))

print("Combinaisons testees:", [(min(a,b), max(a,b)) for a,b in combos])
print()

for universe in ['mundo', 'fruity', 'trigga', 'roaster', 'sunshine']:
    print(f"\n=== {universe.upper()} ===")
    found = 0
    for n1, n2 in combos:
        num1, num2 = (n1, n2) if n1 < n2 else (n2, n1)
        cur.execute(
            "SELECT combination, denomination FROM combinations WHERE univers=%s AND num1=%s AND num2=%s",
            (universe, num1, num2)
        )
        result = cur.fetchone()
        if result:
            found += 1
            print(f"  {num1}-{num2}: {result[0]} ({result[1]})")
    
    if found == 0:
        print(f"  => NO-HOLD (aucune combinaison)")
    else:
        print(f"  => {found}/{len(combos)} combinaisons trouvees")

cur.close()
conn.close()
