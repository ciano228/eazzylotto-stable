from app.services.chatbot_service import ChatbotService
from app.services.query_builder_service import QueryBuilderService

def test_refinements():
    cb = ChatbotService()
    qb = QueryBuilderService()
    
    queries = [
        "quelle periode renvoie beastie=elephant=null?",
        "quelle periode affiche beastie=elephant=0?",
        "quelle periode n'affiche aucun forme=rectangle",
        "quel est l'attribut le plus régulier?",
        "affiche moi les triangles",
        "période 5 manque de lion"
    ]
    
    print("--- Testing Neuro-Katula Refinements ---")
    for q in queries:
        print(f"\nQuery: {q}")
        parse = qb.parse_query(q)
        print(f"Intent detected: {parse['intent']}")
        print(f"Filters: {parse['filters']}")
        
        # Test intent detection in ChatbotService
        intent_cb = cb._detect_intent(q.lower())
        print(f"Chatbot Intent: {intent_cb}")

if __name__ == "__main__":
    test_refinements()
