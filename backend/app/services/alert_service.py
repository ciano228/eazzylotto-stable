"""
Service d'Alertes Intelligentes
Système proactif de notifications basé sur l'IA et les patterns
"""
import json
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.services.ml_service import MLService
from app.services.gap_analysis_service import GapAnalysisService
from app.services.pattern_detection_service import PatternDetectionService
from app.services.frequency_service import FrequencyService

class AlertService:
    """
    Service principal pour la gestion des alertes intelligentes
    """
    
    # Types d'alertes disponibles
    ALERT_TYPES = {
        'LSTM_HIGH_CONFIDENCE': 'Prédiction LSTM haute confiance',
        'CRITICAL_DELAY': 'Retard critique détecté',
        'PATTERN_ANOMALY': 'Anomalie de pattern',
        'FREQUENCY_SPIKE': 'Pic de fréquence inhabituel',
        'CYCLE_COMPLETION': 'Cycle sur le point de se compléter',
        'CUSTOM_THRESHOLD': 'Seuil personnalisé atteint'
    }
    
    @staticmethod
    def generate_all_alerts(db: Session, universe: str = "mundo", session_id: Optional[int] = None) -> Dict[str, Any]:
        """Génère toutes les alertes pour un univers donné"""
        
        print(f"🚨 Génération des alertes intelligentes pour {universe}...")
        
        alerts = []
        
        # 1. Alertes LSTM haute confiance
        lstm_alerts = AlertService._generate_lstm_alerts(db, universe)
        alerts.extend(lstm_alerts)
        
        # 2. Alertes de retards critiques
        delay_alerts = AlertService._generate_delay_alerts(db, universe, session_id)
        alerts.extend(delay_alerts)
        
        # 3. Alertes d'anomalies de patterns
        pattern_alerts = AlertService._generate_pattern_alerts(db, universe)
        alerts.extend(pattern_alerts)
        
        # 4. Alertes de fréquences
        frequency_alerts = AlertService._generate_frequency_alerts(db, universe, session_id)
        alerts.extend(frequency_alerts)
        
        # Trier par priorité (urgence décroissante)
        alerts.sort(key=lambda x: x['priority'], reverse=True)
        
        # Statistiques des alertes
        alert_stats = AlertService._calculate_alert_stats(alerts)
        
        result = {
            "universe": universe,
            "session_id": session_id,
            "total_alerts": len(alerts),
            "alerts": alerts[:20],  # Top 20 alertes
            "alert_statistics": alert_stats,
            "generation_timestamp": datetime.now().isoformat(),
            "alert_types_available": AlertService.ALERT_TYPES
        }
        
        print(f"✅ {len(alerts)} alertes générées")
        
        return result
    
    @staticmethod
    def _generate_lstm_alerts(db: Session, universe: str) -> List[Dict[str, Any]]:
        """Génère les alertes basées sur les prédictions LSTM"""
        
        alerts = []
        
        try:
            # Obtenir les prédictions LSTM
            lstm_predictions = MLService.predict_all_lstm(db, universe)
            
            if "top_predictions" in lstm_predictions:
                for pred in lstm_predictions["top_predictions"]:
                    confidence = pred.get("confidence_percent", 0)
                    
                    # Alerte si confiance > 85%
                    if confidence > 85:
                        priority = 90 + (confidence - 85)  # 90-105
                        
                        alerts.append({
                            "id": f"lstm_{pred['attribute_type']}_{datetime.now().strftime('%H%M%S')}",
                            "type": "LSTM_HIGH_CONFIDENCE",
                            "title": f"🧠 Prédiction LSTM Haute Confiance",
                            "message": f"L'IA prédit {pred['predicted_value']} pour {pred['attribute_type']} avec {confidence}% de confiance",
                            "attribute_type": pred['attribute_type'],
                            "predicted_value": pred['predicted_value'],
                            "confidence": confidence,
                            "priority": priority,
                            "urgency": "high" if confidence > 90 else "medium",
                            "timestamp": datetime.now().isoformat(),
                            "actionable": True,
                            "action_suggestion": f"Considérer {pred['predicted_value']} pour le prochain tirage"
                        })
            
        except Exception as e:
            print(f"❌ Erreur alertes LSTM: {e}")
        
        return alerts
    
    @staticmethod
    def _generate_delay_alerts(db: Session, universe: str, session_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Génère les alertes de retards critiques"""
        
        alerts = []
        
        try:
            # Adapter l'univers pour les requêtes selon la session
            universe_key = f"{universe}_session_{session_id}" if session_id else universe
            
            # Obtenir les attributs en retard
            overdue_data = GapAnalysisService.get_overdue_attributes(db, universe_key, threshold=2.0)
            
            for attr_type, attributes in overdue_data.items():
                for attr in attributes[:3]:  # Top 3 par type
                    delay_ratio = attr.get("delay_ratio", 0)
                    
                    # Alerte si retard > 3x la moyenne
                    if delay_ratio > 3.0:
                        priority = min(95, 70 + delay_ratio * 5)  # 70-95
                        
                        urgency = "critical" if delay_ratio > 5 else "high"
                        
                        alerts.append({
                            "id": f"delay_{attr_type}_{attr['value']}_{datetime.now().strftime('%H%M%S')}",
                            "type": "CRITICAL_DELAY",
                            "title": f"⏰ Retard Critique Détecté",
                            "message": f"{attr['value']} ({attr_type}) en retard de {delay_ratio:.1f}x la moyenne",
                            "attribute_type": attr_type,
                            "attribute_value": attr['value'],
                            "delay_ratio": delay_ratio,
                            "days_since_last": attr.get("days_since_last", 0),
                            "priority": priority,
                            "urgency": urgency,
                            "timestamp": datetime.now().isoformat(),
                            "actionable": True,
                            "action_suggestion": f"Surveiller {attr['value']} - sortie probable imminente"
                        })
            
        except Exception as e:
            print(f"❌ Erreur alertes retards: {e}")
        
        return alerts
    
    @staticmethod
    def _generate_pattern_alerts(db: Session, universe: str) -> List[Dict[str, Any]]:
        """Génère les alertes d'anomalies de patterns"""
        
        alerts = []
        
        try:
            # Détecter les anomalies
            anomalies = PatternDetectionService.detect_anomalies(db, universe, threshold=2.5)
            
            for anomaly in anomalies.get("anomalies", [])[:5]:  # Top 5
                severity = anomaly.get("severity", 0)
                
                if severity > 2.0:
                    priority = min(85, 50 + severity * 10)  # 50-85
                    
                    alerts.append({
                        "id": f"pattern_{anomaly.get('type', 'unknown')}_{datetime.now().strftime('%H%M%S')}",
                        "type": "PATTERN_ANOMALY",
                        "title": f"🔍 Anomalie de Pattern Détectée",
                        "message": f"Pattern inhabituel: {anomaly.get('description', 'Anomalie détectée')}",
                        "pattern_type": anomaly.get("type"),
                        "severity": severity,
                        "description": anomaly.get("description"),
                        "priority": priority,
                        "urgency": "medium",
                        "timestamp": datetime.now().isoformat(),
                        "actionable": False,
                        "action_suggestion": "Analyser les patterns récents pour comprendre l'anomalie"
                    })
            
        except Exception as e:
            print(f"❌ Erreur alertes patterns: {e}")
        
        return alerts
    
    @staticmethod
    def _generate_frequency_alerts(db: Session, universe: str, session_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Génère les alertes de fréquences inhabituelles"""
        
        alerts = []
        
        try:
            # Adapter l'univers pour les requêtes selon la session
            universe_key = f"{universe}_session_{session_id}" if session_id else universe
            
            # Obtenir les attributs en tendance croissante
            trending = FrequencyService.get_trending_attributes(db, universe_key, "increasing")
            
            for attr_type, attributes in trending.items():
                for attr in attributes[:2]:  # Top 2 par type
                    trend_strength = attr.get("trend_strength", 0)
                    
                    # Alerte si tendance très forte
                    if trend_strength > 0.7:
                        priority = 60 + trend_strength * 20  # 60-80
                        
                        alerts.append({
                            "id": f"freq_{attr_type}_{attr['value']}_{datetime.now().strftime('%H%M%S')}",
                            "type": "FREQUENCY_SPIKE",
                            "title": f"📈 Pic de Fréquence Détecté",
                            "message": f"{attr['value']} ({attr_type}) montre une tendance croissante forte",
                            "attribute_type": attr_type,
                            "attribute_value": attr['value'],
                            "trend_strength": trend_strength,
                            "recent_frequency": attr.get("recent_frequency", 0),
                            "priority": priority,
                            "urgency": "medium",
                            "timestamp": datetime.now().isoformat(),
                            "actionable": True,
                            "action_suggestion": f"Considérer {attr['value']} - fréquence en hausse"
                        })
            
        except Exception as e:
            print(f"❌ Erreur alertes fréquences: {e}")
        
        return alerts
    
    @staticmethod
    def _calculate_alert_stats(alerts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calcule les statistiques des alertes"""
        
        if not alerts:
            return {
                "total": 0,
                "by_type": {},
                "by_urgency": {},
                "actionable_count": 0
            }
        
        # Compter par type
        by_type = {}
        for alert in alerts:
            alert_type = alert.get("type", "unknown")
            by_type[alert_type] = by_type.get(alert_type, 0) + 1
        
        # Compter par urgence
        by_urgency = {}
        for alert in alerts:
            urgency = alert.get("urgency", "low")
            by_urgency[urgency] = by_urgency.get(urgency, 0) + 1
        
        # Compter les alertes actionnables
        actionable_count = len([a for a in alerts if a.get("actionable", False)])
        
        return {
            "total": len(alerts),
            "by_type": by_type,
            "by_urgency": by_urgency,
            "actionable_count": actionable_count,
            "average_priority": sum(a.get("priority", 0) for a in alerts) / len(alerts)
        }
    
    @staticmethod
    def get_alert_by_id(alert_id: str, alerts_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Récupère une alerte spécifique par son ID"""
        
        for alert in alerts_data.get("alerts", []):
            if alert.get("id") == alert_id:
                return alert
        
        return None
    
    @staticmethod
    def filter_alerts(alerts_data: Dict[str, Any], 
                     alert_type: Optional[str] = None,
                     urgency: Optional[str] = None,
                     actionable_only: bool = False) -> Dict[str, Any]:
        """Filtre les alertes selon des critères"""
        
        filtered_alerts = alerts_data.get("alerts", [])
        
        # Filtrer par type
        if alert_type:
            filtered_alerts = [a for a in filtered_alerts if a.get("type") == alert_type]
        
        # Filtrer par urgence
        if urgency:
            filtered_alerts = [a for a in filtered_alerts if a.get("urgency") == urgency]
        
        # Filtrer les actionnables seulement
        if actionable_only:
            filtered_alerts = [a for a in filtered_alerts if a.get("actionable", False)]
        
        # Recalculer les stats
        filtered_stats = AlertService._calculate_alert_stats(filtered_alerts)
        
        return {
            **alerts_data,
            "alerts": filtered_alerts,
            "alert_statistics": filtered_stats,
            "filter_applied": {
                "type": alert_type,
                "urgency": urgency,
                "actionable_only": actionable_only
            }
        }