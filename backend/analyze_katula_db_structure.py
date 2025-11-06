"""
Analyze the complete Katula database structure and relationships.
This script connects to katooling_main_system and extracts:
1. Complete schema
2. Table relationships
3. Data patterns and constraints
"""
import psycopg2
from psycopg2.extras import RealDictCursor
import json
from collections import defaultdict
from typing import Dict, List, Set, Any
import os

class KatulaDBAnalyzer:
    def __init__(self):
        self.conn = psycopg2.connect(
            host='localhost',
            database='katooling_main_system',
            user='postgres',
            password='Katulaa_33',
            port=5432
        )
        self.cur = self.conn.cursor(cursor_factory=RealDictCursor)
        
    def analyze_schema(self) -> Dict[str, Any]:
        """Extract complete database schema including tables, columns, and constraints"""
        schema = {}
        
        # Get all tables
        self.cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """)
        tables = [record['table_name'] for record in self.cur.fetchall()]
        
        for table in tables:
            # Get columns and their properties
            self.cur.execute("""
                SELECT 
                    column_name,
                    data_type,
                    is_nullable,
                    column_default
                FROM information_schema.columns
                WHERE table_schema = 'public'
                AND table_name = %s
            """, (table,))
            columns = self.cur.fetchall()
            
            # Get constraints
            self.cur.execute("""
                SELECT
                    con.conname as constraint_name,
                    con.contype as constraint_type,
                    array_agg(col.attname) as columns,
                    ref.table_name as referenced_table,
                    array_agg(ref_col.attname) as referenced_columns
                FROM pg_constraint con
                JOIN pg_class tbl ON tbl.oid = con.conrelid
                JOIN pg_attribute col ON col.attrelid = tbl.oid 
                    AND col.attnum = ANY(con.conkey)
                LEFT JOIN pg_class ref_tbl ON ref_tbl.oid = con.confrelid
                LEFT JOIN information_schema.tables ref ON ref.table_name = ref_tbl.relname
                LEFT JOIN pg_attribute ref_col ON ref_col.attrelid = ref_tbl.oid 
                    AND ref_col.attnum = ANY(con.confkey)
                WHERE tbl.relname = %s
                GROUP BY con.conname, con.contype, ref.table_name
            """, (table,))
            constraints = self.cur.fetchall()
            
            schema[table] = {
                'columns': columns,
                'constraints': constraints
            }
            
        return schema

    def analyze_relationships(self) -> Dict[str, List[Dict]]:
        """Extract and analyze table relationships"""
        self.cur.execute("""
            SELECT
                tc.table_name as table_name,
                kcu.column_name as column_name,
                ccu.table_name AS foreign_table_name,
                ccu.column_name AS foreign_column_name
            FROM 
                information_schema.table_constraints AS tc 
                JOIN information_schema.key_column_usage AS kcu
                    ON tc.constraint_name = kcu.constraint_name
                JOIN information_schema.constraint_column_usage AS ccu
                    ON ccu.constraint_name = tc.constraint_name
            WHERE constraint_type = 'FOREIGN KEY'
        """)
        return self.cur.fetchall()

    def analyze_universe_structure(self) -> Dict[str, Any]:
        """Analyze structure and patterns for each universe"""
        universe_data = {}
        
        # Get list of universes
        self.cur.execute("SELECT DISTINCT univers FROM combinations ORDER BY univers")
        universes = [r['univers'] for r in self.cur.fetchall()]
        
        for universe in universes:
            # Analyze forms per universe
            self.cur.execute("""
                SELECT DISTINCT forme 
                FROM combinations 
                WHERE univers = %s 
                ORDER BY forme
            """, (universe,))
            forms = [r['forme'] for r in self.cur.fetchall()]
            
            # Analyze denomination patterns
            self.cur.execute("""
                SELECT 
                    c.chip,
                    nd.full_name as denomination,
                    c.forme,
                    c.granque_name,
                    c.tome
                FROM combinations c
                JOIN numbered_denominations nd ON c.denomination_id = nd.denomination_id
                WHERE c.univers = %s
                ORDER BY c.chip, c.forme
            """, (universe,))
            chips = defaultdict(list)
            for record in self.cur.fetchall():
                chips[record['chip']].append({
                    'denomination': record['denomination'],
                    'forme': record['forme'],
                    'granque': record['granque_name'],
                    'tome': record['tome']
                })
            
            universe_data[universe] = {
                'forms': forms,
                'chips': dict(chips)
            }
            
        return universe_data

    def analyze_rules(self) -> Dict[str, Any]:
        """Extract and analyze business rules from functions"""
        self.cur.execute("""
            SELECT 
                p.proname as function_name,
                pg_get_functiondef(p.oid) as definition
            FROM pg_proc p
            JOIN pg_namespace n ON p.pronamespace = n.oid
            WHERE n.nspname = 'public'
        """)
        return self.cur.fetchall()

    def generate_complete_analysis(self) -> None:
        """Generate complete analysis and save to files"""
        os.makedirs('analysis_output', exist_ok=True)
        
        # 1. Schema Analysis
        schema = self.analyze_schema()
        with open('analysis_output/schema_analysis.json', 'w') as f:
            json.dump(schema, f, indent=2, default=str)
            
        # 2. Relationships Analysis
        relationships = self.analyze_relationships()
        with open('analysis_output/relationships_analysis.json', 'w') as f:
            json.dump(relationships, f, indent=2, default=str)
            
        # 3. Universe Structure Analysis
        universe_structure = self.analyze_universe_structure()
        with open('analysis_output/universe_structure_analysis.json', 'w') as f:
            json.dump(universe_structure, f, indent=2, default=str)
            
        # 4. Rules Analysis
        rules = self.analyze_rules()
        with open('analysis_output/rules_analysis.json', 'w') as f:
            json.dump(rules, f, indent=2, default=str)
            
        # Generate visualization
        self.generate_visualization()
            
    def generate_visualization(self) -> None:
        """Generate GraphViz DOT file for schema visualization"""
        dot_content = ['digraph KatulaDB {', 'rankdir=LR;', 'node [shape=record];']
        
        schema = self.analyze_schema()
        relationships = self.analyze_relationships()
        
        # Add tables
        for table, info in schema.items():
            columns = [col['column_name'] for col in info['columns']]
            dot_content.append(f'{table} [label="{table}|{"|".join(columns)}"];')
            
        # Add relationships
        for rel in relationships:
            dot_content.append(
                f'{rel["table_name"]} -> {rel["foreign_table_name"]} '
                f'[label="{rel["column_name"]} -> {rel["foreign_column_name"]}"];'
            )
            
        dot_content.append('}')
        
        with open('analysis_output/schema_visualization.dot', 'w') as f:
            f.write('\n'.join(dot_content))

if __name__ == "__main__":
    analyzer = KatulaDBAnalyzer()
    analyzer.generate_complete_analysis()
    print("Analysis complete. Check the analysis_output directory for results.")