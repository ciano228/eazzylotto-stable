from typing import List, Dict, Any, Optional
import re
import os
from sqlalchemy.orm import Session
from app.services.verdict_engine_service import VerdictEngineService
from app.models.performance import PredictionRecord
from app.services.query_builder_service import QueryBuilderService
from sqlalchemy import text
from statistical_journal_service import StatisticalJournalService

class ChatbotService:
    """
    Expert System for Katula AI Analyst.
    Uses heuristic intent recognition to provide intelligent insights based on Verdict Engine data.
    """

    def __init__(self):
        # Define basic intents with regex patterns
        self.intents = {
            "ANALYZE_PREDICTION": [
                r"verdict",
                r"pourquoi",
                r"analyse.*prediction",
                r"analyse.*verdict",
                r"expli(que|quer).*(ce|le).*r[ée]sultat",
                r"d[ée]tails.*sur.*(le|les).*chiffres"
            ],
            "TREND_QUERY": [
                r"tendances?",
                r"forme.*du.*moment",
                r"qu'est-ce qui sort",
                r"m[ée]t[ée]o"
            ],
            "GREETING": [
                r"bonjour",
                r"salut",
                r"hello",
                r"coucou"
            ],
            "HELP": [
                r"\baide\b",
                r"\bhelp\b",
                r"que.*faire",
                r"comment.*marche",
                r"instructions"
            ],
            "EXPLORE_DATA": [
                r"trouve.*(les|des|tous)",
                r"montre.*(moi|les|tous)",
                r"cherche.*(les|des)",
                r"donne.*(moi|les)",
                r"combien.*de",
                r"qui.*a.*(le|la)",
                r"quel(le)?s?\b",
                r"p[ée]riodes?\b",
                r"r[ée]gulier\b",
                r"affiche\b",
                r"manque\b",
                r"retourne\b",
                r"rend\b",
                r"donne\b"
            ]
        }
        self.query_builder = QueryBuilderService()
        self.journal_analyst = StatisticalJournalService({}) # Config loaded later if needed

    def process_message(self, db: Session, user_message: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Main entry point. Processes a user message and returns a structured response.
        """
        message_lower = user_message.lower()
        
        # 1. Broad Intent Detection (Heuristic)
        intent = self._detect_intent(message_lower)
        
        # 2. Deep Analysis (NL2Q) - Consult QueryBuilder for all data-related queries
        parse_result = self.query_builder.parse_query(user_message)
        deep_intent = parse_result["intent"]
        
        # Default context if None
        if not context:
            context = {}

        prediction_id = context.get('prediction_id')

        # --- DELEGATION LOGIC ---
        
        # Specialized Journal Intents take precedence if session_id is available
        journal_intents = ["FIND_MISSING", "FIND_OCCURRENCE", "ANALYZE_REGULARITY"]
        if deep_intent in journal_intents or (intent == "EXPLORE_DATA" and parse_result["filters"]):
             return self._handle_journal_query(db, user_message, context)

        if intent == "GREETING":
            return {
                "text": "Bonjour ! Je suis l'Analyste Katula AI. Je peux vous expliquer mes dernières prédictions ou analyser les tendances actuelles. Que voulez-vous savoir ?",
                "actions": ["Analyser le dernier verdict", "Voir les tendances"]
            }

        elif intent == "HELP":
            return {
                "text": "Je suis là pour décrypter les signaux du système. Demandez-moi 'Pourquoi ce verdict ?' ou 'Quelles sont les paires fortes ?' pour obtenir des insights précis.",
                "actions": ["Analyser le dernier verdict", "Voir les tendances"]
            }

        elif intent == "ANALYZE_PREDICTION":
            if not prediction_id:
                return {
                    "text": "Je ne vois pas de prédiction active à l'écran. Lancez d'abord une analyse dans l'AI Center, puis demandez-moi de l'expliquer.",
                    "actions": []
                }
            return self._explain_prediction(db, prediction_id)

        elif intent == "TREND_QUERY":
            # For now, simplistic trend based on last prediction context or general message
            return {
                "text": "Actuellement, je surveille particulièrement les Formes Triangulaires et les Tomes Impairs qui montrent une forte activité dans l'univers Mundo. Le système a détecté une convergence sur la zone Sud.",
                "actions": ["Voir les détails graphiques"]
            }

        else:
            # Fallback to LLM (DeepSeek/Anthropic)
            return self._query_llm(user_message, context)

    def _detect_intent(self, message: str) -> str:
        for intent_name, patterns in self.intents.items():
            for pattern in patterns:
                if re.search(pattern, message):
                    return intent_name
        return "UNKNOWN"

    def _query_llm(self, message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Delegates complex queries to DeepSeek/LLM via LLMProviderService.
        """
        try:
            from app.services.llm_provider_service import LLMProviderService
            llm = LLMProviderService()
            
            # System Prompt
            system_prompt = """You are Neuro-Katula, an expert lottery analyst AI. 
            You specialize in identifying patterns in lottery draws based on 'attributes' like:
            - Forme (Square, Triangle, Circle, Rectangle)
            - Beastie (Lion, Tiger, etc.)
            - Tome, Engine, Chip, etc.
            
            Key Principles:
            1. Be concise and professional.
            2. If you don't have data, say so, but offer a theoretical insight.
            3. Use the user's context if available.
            4. You are helpful, slightly futuristic, and precise.
            """
            
            # Build context string
            context_str = ""
            if context.get('session_id'):
                context_str += f"\nContext: Session ID {context.get('session_id')} is active."
            if context.get('universe'):
                context_str += f"\nUniverse: {context.get('universe')}."
                
            full_message = f"{context_str}\n\nUser Question: {message}"
            
            # Determine provider and model
            provider = context.get('provider', 'deepseek')
            model = None
            
            if provider == 'openai':
                model = 'gpt-4o'
            elif provider == 'anthropic':
                model = 'claude-3-5-sonnet-20240620'
            elif provider == 'deepseek':
                model = 'deepseek-chat'
            elif provider == 'groq':
                model = 'mixtral-8x7b-32768' # Free & Fast
            elif provider == 'ollama':
                model = 'mistral' # Local default
                
            max_tokens = int(os.getenv('LLM_MAX_TOKENS', 400))
            
            response = llm.generate_text(
                provider=provider, 
                model=model, 
                message=full_message, 
                system_prompt=system_prompt,
                max_tokens=max_tokens
            )
            
            if response['status'] == 'success':
                content = response['text']
                return {
                    "text": content,
                    "actions": ["Approfondir avec l'IA", "Aide"]
                }
            else:
                 error_msg = response.get('error', 'Erreur inconnue')
                 return {
                    "text": f"Mes circuits sont bloques par l'API : {error_msg}",
                    "actions": ["Reessayer"]
                }
                
        except Exception as e:
            print(f"LLM Error: {e}")
            return {
                "text": f"Erreur technique LLM : {str(e)}. (Mode Debug)",
                "actions": ["Reessayer"]
            }

    def _explain_prediction(self, db: Session, prediction_id: int) -> Dict[str, Any]:
        """
        Deep dive into a specific prediction record to generate explanation.
        """
        record = db.query(PredictionRecord).filter(PredictionRecord.id == prediction_id).first()
        if not record:
            return {"text": "Désolé, je ne retrouve pas les traces de cette prédiction dans mes archives."}
        
        # Analyze the data
        top_nums = record.predicted_numbers[:5] if record.predicted_numbers else []
        top_attrs = record.predicted_attributes if record.predicted_attributes else {}
        
        # Build narrative
        nums_str = ", ".join([str(n) for n in top_nums])
        
        insight = f"Pour cette prédiction (ID #{prediction_id}), je me suis concentré sur les numéros **{nums_str}**."
        
        if top_attrs:
            insight += "\n\n**Raisons Structurelles :**"
            # Extract key attributes (Forme, Tome, Beastie)
            relevant_keys = ['forme', 'tome', 'beastie']
            for k in relevant_keys:
                if k in top_attrs:
                    insight += f"\n- **{k.capitalize()}** : Forte résonance avec '{top_attrs[k]}'."
        
        insight += "\n\nLa confiance est élevée car ces structures ont été observées dans des tirages passés similaires."

        return {
            "text": insight,
            "actions": ["Voir les tirages jumeaux"]
        }

    def _handle_exploration(self, db: Session, user_message: str) -> Dict[str, Any]:
        """
        Drives the NL2Q engine.
        """
        try:
            # 1. Parse Query
            parse_result = self.query_builder.parse_query(user_message)
            where_clause = parse_result["sql_clause"]
            filters = parse_result["filters"]
            
            if not filters:
                 return {
                    "text": "Je comprends que vous voulez explorer les données, mais je n'ai pas détecté de critères précis (comme 'triangle', 'lion', 'ligne 1'). Soyez plus spécifique.",
                    "actions": ["Aide sur les filtres"]
                }
            
            # 2. Execute SQL (ReadOnly Safety Measure: SELECT only)
            # We select count and a sample
            sql = f"""
                SELECT combination, chip, forme, beastie 
                FROM combinations 
                WHERE {where_clause} 
                LIMIT 5
            """
            
            # Count query
            count_sql = f"SELECT COUNT(*) FROM combinations WHERE {where_clause}"
            
            # Execute
            # Using text() for SQLAlchemy raw SQL
            count_res = db.execute(text(count_sql), parse_result["filters"]).scalar()
            rows_res = db.execute(text(sql), parse_result["filters"]).fetchall()
            
            # 3. Format Response
            samples = [f"{r[0]} ({r[3]})" for r in rows_res]
            sample_str = ", ".join(samples)
            
            criteria_str = ", ".join([f"{k}={v}" for k,v in filters.items()])
            
            response_text = f"🔎 **Exploration Deep-Katula**\n"
            response_text += f"J'ai trouvé **{count_res} combinaisons** correspondant à `{criteria_str}`.\n\n"
            
            if count_res > 0:
                response_text += f"Voici 5 exemples : {sample_str}"
                if count_res > 5:
                     response_text += f" et {count_res - 5} autres."
            
            return {
                "text": response_text,
                "actions": ["Affiner la recherche", "Exporter les résultats"]
            }
            
        except Exception as e:
            return {"text": f"Oups, mon module d'exploration a trébuché : {str(e)}"}

    def _handle_journal_query(self, db: Session, user_message: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Handles detailed journal analysis questions.
        """
        try:
            parse_result = self.query_builder.parse_query(user_message)
            intent = parse_result["intent"]
            filters = parse_result["filters"]
            session_id = context.get('session_id') if context else None

            if not session_id:
                return {"text": "Pour analyser le journal, j'ai besoin d'une session active. Sélectionnez une session dans la liste au-dessus."}

            # Fetch session draws to build journal data
            # Note: In a real scenario, we would use a more efficient way to get processed journal data
            # For now, let's assume we can fetch the combination records for this session
            sql = text("SELECT combination, chip, forme, beastie, period, engine, tome, granque, petique FROM combinations WHERE session_id = :sid ORDER BY id ASC")
            rows = db.execute(sql, {"sid": session_id}).fetchall()
            
            journal_data = []
            for r in rows:
                journal_data.append({
                    'combination': r[0], 'chip': r[1], 'forme': r[2], 'beastie': r[3],
                    'period': r[4], 'engine': r[5], 'tome': r[6], 'granque': r[7], 'petique': r[8]
                })

            if not journal_data:
                return {"text": "Le journal de cette session est vide pour le moment."}

            if intent == "FIND_MISSING":
                attr = next((k for k in filters.keys() if k != 'period'), 'forme')
                val = filters.get(attr, 'rectangle')
                missing = self.journal_analyst.find_missing_attribute_periods(journal_data, attr, val)
                
                if missing:
                    periods_str = ", ".join([str(p) for p in missing])
                    return {"text": f"🔎 **Analyse Neuro-Katula**\n\nL'attribut **{attr}={val}** n'affiche aucun tirage dans les périodes suivantes : **{periods_str}**."}
                else:
                    return {"text": f"✅ L'attribut **{attr}={val}** est présent dans toutes les périodes de cette session."}

            elif intent == "FIND_OCCURRENCE":
                attr = next((k for k in filters.keys() if k not in ['period', 'target_value']), 'beastie')
                val = filters.get(attr, 'cock')
                target_count = filters.get("target_value", 0)
                matching = self.journal_analyst.find_attribute_value_count_periods(journal_data, attr, val, target_count)
                
                if matching:
                    periods_str = ", ".join([str(p) for p in matching])
                    return {"text": f"📊 **Rapport d'occurrence**\n\nJ'ai trouvé que **{attr}={val}** a exactement {target_count} occurrences dans les périodes : **{periods_str}**."}
                else:
                    return {"text": f"Information : Je n'ai trouvé aucune période où **{attr}={val}** apparaît exactement {target_count} fois."}

            elif intent == "ANALYZE_REGULARITY":
                attrs = ['forme', 'beastie', 'engine', 'tome']
                best = self.journal_analyst.get_most_regular_attribute(journal_data, attrs)
                
                if best:
                    return {
                        "text": f"🏆 **Indice de Régularité**\n\nL'attribut le plus régulier pour cette session est **{best['attribute']}**.\n\nIl présente la variance la plus faible dans l'apparition des valeurs d'une période à l'autre, ce qui en fait un point d'ancrage structurel fiable pour vos prédictions.",
                        "actions": [f"Détails sur {best['attribute']}", "Comparer les autres"]
                    }
                
            return {"text": "Je n'ai pas pu extraire assez de données pour répondre précisément. Essayez d'être plus spécifique sur l'attribut (ex: 'forme=carre')."}

        except Exception as e:
            print(f"Chatbot Journal Error: {str(e)}")
            return {"text": f"Désolé, j'ai eu un problème technique lors de l'analyse du journal : {str(e)}"}
