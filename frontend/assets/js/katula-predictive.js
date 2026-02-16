
// Configuration API
const API_BASE = '/api';

async function loadPredictiveData() {
    const universe = document.getElementById('universeSelector').value || 'mundo';

    // 1. Charger les corrélations
    loadCorrelations(universe);

    // 2. Charger les prédictions Oracle
    loadOracle(universe);
}

async function loadCorrelations(universe) {
    const container = document.getElementById('correlationContainer');
    container.innerHTML = '<div style="text-align:center; padding:20px; color:#7f8c8d;"><i class="fas fa-spinner fa-spin"></i> Analyse des corrélations en cours...</div>';

    try {
        const response = await fetch(`${API_BASE}/analytics/correlations/${universe}`);
        const result = await response.json();

        if (result.error) {
            container.innerHTML = `<div style="color:#e74c3c; padding:10px; background:#fadbd8; border-radius:4px;">Erreur: ${result.error}</div>`;
            return;
        }

        const data = result.data || {};
        const rules = data.top_correlations || [];

        if (rules.length === 0) {
            container.innerHTML = '<div style="padding:15px; color:#7f8c8d; font-style:italic;">Aucune corrélation significative trouvée pour cet univers.</div>';
            return;
        }

        let html = `
            <table class="rule-table">
                <thead>
                    <tr>
                        <th>Si (Antécédent)</th>
                        <th>Alors (Conséquent)</th>
                        <th>Confiance</th>
                    </tr>
                </thead>
                <tbody>
        `;

        // Afficher top 20
        rules.slice(0, 20).forEach(rule => {
            // Seuil visuel
            const confClass = rule.confidence >= 0.8 ? 'high-conf' : 'med-conf';

            html += `
                <tr>
                    <td>${formatKey(rule.antecedent)}</td>
                    <td><b>${formatKey(rule.consequent)}</b></td>
                    <td class="${confClass}">
                        ${(rule.confidence * 100).toFixed(0)}%
                        <div style="font-size:0.7em; color:#95a5a6; font-weight:normal;">(Support: ${(rule.support * 100).toFixed(1)}%)</div>
                    </td>
                </tr>
            `;
        });

        html += '</tbody></table>';
        container.innerHTML = html;

    } catch (e) {
        console.error(e);
        container.innerHTML = `<div style="color:#e74c3c">Erreur de connexion au serveur.</div>`;
    }
}

async function loadOracle(universe) {
    const container = document.getElementById('oracleContainer');
    container.innerHTML = '<div style="text-align:center; padding:20px; color:#7f8c8d;"><i class="fas fa-microchip"></i> Consultation de l\'Oracle LSTM...</div>';

    try {
        // Nouvel endpoint qui renvoie tout d'un coup
        const response = await fetch(`${API_BASE}/analytics/predict/next/${universe}`);
        const result = await response.json();

        if (result.status === 'error' || result.error) {
            container.innerHTML = `<div style="color:#e74c3c; padding:10px;">Erreur Oracle: ${result.message || result.error}</div>`;
            return;
        }

        const predictions = result.predictions || {};
        const attributes = ['forme', 'engine', 'beastie'];

        let html = '';

        attributes.forEach(attr => {
            const attrData = predictions[attr];

            html += `<div style="margin-bottom: 25px; border-bottom:1px solid #eee; padding-bottom:15px;">
                        <h5 style="color:#2c3e50; border-bottom: 2px solid #3498db; display:inline-block; padding-bottom:3px; margin-bottom:15px;">
                            ${attr.toUpperCase()}
                        </h5>`;

            if (!attrData || attrData.status === 'error' || attrData.status === 'model_not_trained') {
                const msg = attrData ? attrData.message : 'Non disponible';
                html += `<div style="color:#95a5a6; font-style:italic;">${msg}</div>`;
            } else if (attrData.predictions && attrData.predictions.length > 0) {
                // Top 3
                attrData.predictions.slice(0, 3).forEach(p => {
                    html += `
                        <div style="margin-bottom: 12px;">
                            <div style="display:flex; justify-content:space-between; font-size:0.95em; color:#34495e; font-weight:500;">
                                <span>${p.predicted_value}</span>
                                <span>${p.confidence_percent}%</span>
                            </div>
                            <div class="confidence-bar">
                                <div class="confidence-fill" style="width: ${p.confidence_percent}%; background: ${getColorForConfidence(p.confidence)}"></div>
                            </div>
                        </div>
                    `;
                });
            } else {
                html += `<div style="color:#95a5a6;">Aucune prédiction fiable.</div>`;
            }

            html += `</div>`;
        });

        container.innerHTML = html;

    } catch (e) {
        console.error(e);
        container.innerHTML = `<div style="color:#e74c3c">Erreur lors de la prédiction.</div>`;
    }
}

function getColorForConfidence(conf) {
    if (conf >= 0.7) return '#27ae60'; // Green
    if (conf >= 0.4) return '#f39c12'; // Orange
    return '#bdc3c7'; // Grey
}

function formatKey(key) {
    // text:value -> Value (Text)
    if (!key) return '-';

    // Si c'est juste une valeur sans ':'
    if (key.indexOf(':') === -1) return key;

    const parts = key.split(':');
    if (parts.length === 2) {
        // Met la valeur en premier, le type en petit
        return `${parts[1]} <span style="color:#95a5a6; font-size:0.8em; font-weight:normal;">(${parts[0]})</span>`;
    }
    return key;
}

// Auto-load on start
document.addEventListener('DOMContentLoaded', () => {
    loadPredictiveData();
});
