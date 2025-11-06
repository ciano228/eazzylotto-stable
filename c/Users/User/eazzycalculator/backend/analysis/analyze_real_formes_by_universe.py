#!/usr/bin/env python3
"""
Analyser les formes réelles par univers depuis katooling_main_system
"""
import sqlite3
import json
from collections import defaultdict

def analyze_formes_by_universe():
    """Analyser les formes réelles pour chaque univers"""
    
    # Connexion à la BD réelle
    conn = sqlite3.connect('backend/data/katula.db')
    cursor = conn.cursor()
    
    print("=== ANALYSE DES FORMES PAR UNIVERS ===\n")
    
    # Requête pour extraire toutes les formes par univers
    query = """
    SELECT DISTINCT 
        univers,
        forme,
        COUNT(*) as count
    FROM katooling_main_system 
    WHERE forme IS NOT NULL 
    AND forme != ''
    GROUP BY univers, forme
    ORDER BY univers, count DESC
    """
    
    cursor.execute(query)
    results = cursor.fetchall()
    
    # Organiser par univers
    formes_by_universe = defaultdict(list)
    
    for univers, forme, count in results:
        formes_by_universe[univers].append({
            'forme': forme,
            'count': count
        })
    
    # Afficher les résultats
    for univers, formes in formes_by_universe.items():
        print(f"🌍 UNIVERS: {univers.upper()}")
        print(f"   Total formes: {len(formes)}")
        
        # Top 10 formes les plus fréquentes
        for i, forme_data in enumerate(formes[:10]):
            print(f"   {i+1:2d}. {forme_data['forme']:20} ({forme_data['count']:3d} fois)")
        
        if len(formes) > 10:
            print(f"   ... et {len(formes) - 10} autres formes")
        print()
    
    # Analyser les types de formes
    print("=== ANALYSE DES TYPES DE FORMES ===\n")
    
    for univers, formes in formes_by_universe.items():
        simples = []
        composites = []
        
        for forme_data in formes:
            forme = forme_data['forme']
            if '-' in forme:
                composites.append(forme_data)
            else:
                simples.append(forme_data)
        
        print(f"🌍 {univers.upper()}:")
        print(f"   Formes simples: {len(simples)}")
        if simples:
            print(f"   → {', '.join([f['forme'] for f in simples[:5]])}")
        
        print(f"   Formes composites: {len(composites)}")
        if composites:
            print(f"   → {', '.join([f['forme'] for f in composites[:5]])}")
        print()
    
    # Sauvegarder en JSON
    output = {}
    for univers, formes in formes_by_universe.items():
        output[univers] = {
            'total_formes': len(formes),
            'formes_list': [f['forme'] for f in formes],
            'formes_with_count': formes,
            'simples': [f['forme'] for f in formes if '-' not in f['forme']],
            'composites': [f['forme'] for f in formes if '-' in f['forme']]
        }
    
    with open('backend/formes_by_universe.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print("✅ Résultats sauvegardés dans: backend/formes_by_universe.json")
    
    conn.close()
    return output

if __name__ == "__main__":
    analyze_formes_by_universe()