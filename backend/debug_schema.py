import sys
import os
sys.path.append(os.getcwd())

from sqlalchemy import inspect
from app.database.connection import engine

def inspect_schema():
    inspector = inspect(engine)
    table_name = "combinations"
    
    print(f"Inspecting table: {table_name}")
    try:
        columns = inspector.get_columns(table_name)
        if not columns:
            print(f"Table '{table_name}' not found!")
            # Try finding similar tables
            tables = inspector.get_table_names()
            print(f"Available tables: {tables}")
            return
            
        print(f"Columns in '{table_name}':")
        for col in columns:
            print(f" - {col['name']} ({col['type']})")
            
    except Exception as e:
        print(f"Error inspecting schema: {e}")

if __name__ == "__main__":
    inspect_schema()
