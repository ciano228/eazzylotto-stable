#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test de l'endpoint d'analyse Katula
"""
import requests
import json

# Test avec la session Test Session (ID 11)
session_id = 11

print("=" * 80)
print("TEST ENDPOINT KATULA ANALYZE-SESSION")
print("=" * 80)

# 1. Récupérer les tirages de la session
print(f"\n1. Recuperation des tirages de la session {session_id}...")
draws_response = requests.get(f"http://localhost:8881/api/unified/sessions/{session_id}/draws")

if draws_response.status_code == 200:
    draws = draws_response.json()
    print(f"   SUCCES: {len(draws)} tirages recuperes")
    
    # Afficher les 3 premiers tirages
    for i, draw in enumerate(draws[:3]):
        print(f"   - Tirage {i+1}: {draw.get('draw_date')} - {draw.get('winning_numbers')}")
    
    # 2. Appeler l'endpoint d'analyse Katula
    print(f"\n2. Appel endpoint analyse Katula...")
    
    analysis_payload = {
        "session_id": session_id,
        "draws": draws,
        "universe": "mundo"
    }
    
    analysis_response = requests.post(
        "http://localhost:8881/api/katula/analyze-session",
        json=analysis_payload,
        headers={"Content-Type": "application/json"}
    )
    
    if analysis_response.status_code == 200:
        analysis_data = analysis_response.json()
        print(f"   SUCCES: Analyse completee")
        print(f"   Status: {analysis_data.get('status')}")
        print(f"   Total draws analyses: {analysis_data.get('total_draws')}")
        
        if analysis_data.get('analyzed_draws'):
            first_draw = analysis_data['analyzed_draws'][0]
            print(f"\n3. Premier tirage analyse:")
            print(f"   Date: {first_draw.get('draw_date')}")
            print(f"   Numeros: {first_draw.get('winning_numbers')}")
            
            katula = first_draw.get('katula_analysis', {})
            print(f"   Total combinaisons: {katula.get('total_combinations')}")
            
            if katula.get('journal_entries'):
                first_entry = katula['journal_entries'][0]
                print(f"\n   Premiere entree journal:")
                print(f"   - Combination: {first_entry.get('combination')}")
                print(f"   - Num1: {first_entry.get('num1_analysis', {}).get('number')}")
                print(f"   - Forme: {first_entry.get('num1_analysis', {}).get('forme')}")
                print(f"   - Granque: {first_entry.get('num1_analysis', {}).get('granque_name')}")
                print(f"   - Petique: {first_entry.get('num1_analysis', {}).get('petique')}")
                print(f"   - Tome: {first_entry.get('num1_analysis', {}).get('tome')}")
            
            # Sauvegarder la réponse complète
            with open('katula_analysis_response.json', 'w', encoding='utf-8') as f:
                json.dump(analysis_data, f, indent=2, ensure_ascii=False)
            print(f"\n   Reponse complete sauvegardee dans: katula_analysis_response.json")
        else:
            print("   ERREUR: Aucun tirage analyse")
    else:
        print(f"   ERREUR: {analysis_response.status_code}")
        print(f"   Message: {analysis_response.text}")
else:
    print(f"   ERREUR: {draws_response.status_code}")
    print(f"   Message: {draws_response.text}")

print("\n" + "=" * 80)
