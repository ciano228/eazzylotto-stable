import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app.services.query_builder_service import QueryBuilderService
from app.services.chatbot_service import ChatbotService
import json

def test_nl2q():
    qb = QueryBuilderService()
    
    test_queries = [
        "Montre moi tous les triangles",
        "Donne moi les combinaisons dans la ligne 1",
        "Qui a le tome 3 ?",
        "Cherche les lions",  # Implicit 'beastie' + plural
        "Je veux voir les combinaisons de mundo", # Universe
        "Montre moi les lion de mundo", # Combined
        "y a t il des zebres dans fruity ?" # Combined + Plural
    ]
    
    print("=== TEST NL2Q PARSER ===")
    for q in test_queries:
        res = qb.parse_query(q)
        print(f"\nQUERY: {q}")
        print(f"FILTERS: {res['filters']}")
        print(f"SQL: {res['sql_clause']}")  # Now just a string

def test_intent_detection():
    bot = ChatbotService()
    
    test_msgs = [
        "Aide",
        "Analyser le verdict",
        "Analyse cette prediction",
        "Bonjour",
        "Trouve les triangles",
        "Quelle est la tendance ?",
        "Gimme help",
        "Explique moi ce verdict"
    ]
    
    print("\n=== TEST INTENT DETECTION ===")
    for msg in test_msgs:
        intent = bot._detect_intent(msg.lower())
        print(f"MSG: '{msg}' -> INTENT: {intent}")

if __name__ == "__main__":
    test_nl2q()
    test_intent_detection()
