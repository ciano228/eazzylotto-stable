/**
 * Client pour Poids Structurels - Intégration avec Statistiques Avancées
 * Complète le système observé avec les probabilités structurelles
 */

class StructuralWeightsClient {
    constructor(baseUrl = '') {
        this.baseUrl = baseUrl;
        this.cache = new Map();
        this.cacheExpiry = 3600000; // 1 heure
    }

    async getStructuralWeight(universe, attributeType, attributeValue) {
        const cacheKey = `${universe}_${attributeType}_${attributeValue}`;
        const cached = this.cache.get(cacheKey);
        
        if (cached && Date.now() - cached.timestamp < this.cacheExpiry) {
            return cached.data;
        }

        try {
            const response = await fetch(
                `${this.baseUrl}/api/structural-weights/${universe}/${attributeType}/${attributeValue}`
            );
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            
            const data = await response.json();
            this.cache.set(cacheKey, { data, timestamp: Date.now() });
            return data;
        } catch (error) {
            console.warn(`Structural weight unavailable for ${cacheKey}:`, error);
            return null;
        }
    }

    async getAllWeightsForType(universe, attributeType) {
        const cacheKey = `${universe}_${attributeType}_all`;
        const cached = this.cache.get(cacheKey);
        
        if (cached && Date.now() - cached.timestamp < this.cacheExpiry) {
            return cached.data;
        }

        try {
            const response = await fetch(
                `${this.baseUrl}/api/structural-weights/${universe}/${attributeType}`
            );
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            
            const data = await response.json();
            this.cache.set(cacheKey, { data, timestamp: Date.now() });
            return data;
        } catch (error) {
            console.warn(`Structural weights unavailable for ${universe}/${attributeType}:`, error);
            return null;
        }
    }

    async preloadWeights(universe, attributeTypes) {
        const promises = attributeTypes.map(type => 
            this.getAllWeightsForType(universe, type)
        );
        await Promise.all(promises);
    }

    calculateStructuralGapScore(currentGap, expectedGap) {
        if (!expectedGap || expectedGap <= 0) return null;
        return currentGap / expectedGap;
    }

    getGapScoreColor(gapScore) {
        if (gapScore === null) return '#95a5a6';
        if (gapScore < 0.8) return '#27ae60'; // En avance
        if (gapScore < 1.2) return '#3498db'; // Normal
        if (gapScore < 2.0) return '#f39c12'; // En retard
        return '#e74c3c'; // Très en retard
    }

    getGapScoreLabel(gapScore) {
        if (gapScore === null) return 'N/A';
        if (gapScore < 0.8) return '🟢 En avance';
        if (gapScore < 1.2) return '🔵 Normal';
        if (gapScore < 2.0) return '🟠 En retard';
        return '🔴 Très en retard';
    }

    formatTooltip(observed, structural) {
        if (!structural) {
            return `📊 Observé: ${observed.expectedGap?.toFixed(2) || 'N/A'} tirages`;
        }

        return `📊 Observé: ${observed.expectedGap?.toFixed(2) || 'N/A'} tirages
🔬 Structurel: ${structural.expected_gap?.toFixed(2) || 'N/A'} tirages
📐 Cardinalité: ${structural.cardinality || 'N/A'}
🎯 Probabilité: ${(structural.probability * 100)?.toFixed(2) || 'N/A'}%

Score Observé: ${observed.gapScore?.toFixed(2) || 'N/A'}
Score Structurel: ${structural.gap_score?.toFixed(2) || 'N/A'}`;
    }

    clearCache() {
        this.cache.clear();
    }
}

// Instance globale
window.structuralWeightsClient = new StructuralWeightsClient();

// Alias globaux pour compatibilité avec les appels HTML inline
if (typeof onAttributeChange === 'undefined') {
    window.onAttributeChange = window.onAttributeChange || function() {};
}
if (typeof showPartialJournal === 'undefined') {
    window.showPartialJournal = window.showPartialJournal || function() {};
}
