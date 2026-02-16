/**
 * Logic for Performance Tracking & Learning Feedback
 */

// Local state for last analysis to be saved as prediction
let LAST_ANALYSIS_DATA = null;

window.saveCurrentAsPrediction = async function () {
    if (!LAST_ANALYSIS_DATA) {
        alert("Aucune analyse active à enregistrer.");
        return;
    }

    const payload = {
        universe: STATE.universe,
        trigger_numbers: LAST_ANALYSIS_DATA.target_numbers,
        predicted_numbers: LAST_ANALYSIS_DATA.consequences.most_frequent_numbers,
        predicted_pairs: LAST_ANALYSIS_DATA.consequences.most_frequent_pairs,
        predicted_attributes: LAST_ANALYSIS_DATA.consequences.most_frequent_attributes
    };

    try {
        const res = await fetch(`${API_BASE}/api/performance/record`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        if (res.ok) {
            alert("🎯 Prédiction enregistrée ! Elle sera évaluée dès que le prochain tirage réel sera saisi.");
        } else {
            const err = await res.json();
            alert("Erreur lors de l'enregistrement: " + err.detail);
        }
    } catch (e) {
        console.error(e);
        alert("Erreur de connexion au serveur.");
    }
};

window.loadPerformanceStats = async function () {
    try {
        const res = await fetch(`${API_BASE}/api/performance/stats?universe=${STATE.universe}`);
        if (!res.ok) return;

        const data = await res.json();
        renderPerformanceDashboard(data);
    } catch (e) {
        console.error("Error loading stats:", e);
    }
};

function renderPerformanceDashboard(data) {
    if (!data || data.status === "No data yet") {
        document.getElementById('perf-accuracy-hero').innerText = "--%";
        document.getElementById('perf-total-count').innerText = "0";
        return;
    }

    // 1. Hero Stat
    document.getElementById('perf-accuracy-hero').innerText = `${data.global_accuracy}%`;
    document.getElementById('perf-total-count').innerText = data.total_evaluated;

    // 2. History List
    const historyList = document.getElementById('perf-history-list');
    historyList.innerHTML = (data.last_predictions || []).map(p => `
        <div class="list-group-item bg-transparent text-white border-secondary px-0">
            <div class="d-flex justify-content-between">
                <span class="small text-muted">${new Date(p.date).toLocaleDateString()}</span>
                <span class="badge ${p.score > 0 ? 'bg-success' : 'bg-danger'}">${p.score}% Success</span>
            </div>
            <div class="mt-1 small">
                Tirage: <span class="text-warning">${p.trigger.join('-')}</span><br>
                Résultat: <span class="text-info">${p.actual ? p.actual.join('-') : 'En attente...'}</span>
            </div>
        </div>
    `).join('') || '<div class="text-muted small italic">Aucun historique évalué.</div>';

    // 3. DNA Chart (Simple CSS Bars for now)
    const chartContainer = document.getElementById('perf-dna-chart');
    // For now we simulate/use some attributes if we have them. 
    // In a future update, the backend service_stats will provide specific attribute accuracy.
    const mockDnaData = [
        { label: 'Engine', score: 75 },
        { label: 'Tome', score: 62 },
        { label: 'Chip', score: 88 },
        { label: 'Forme', score: 54 }
    ];

    chartContainer.innerHTML = mockDnaData.map(d => `
        <div class="mb-3">
            <div class="d-flex justify-content-between small mb-1">
                <span>${d.label}</span>
                <span>${d.score}%</span>
            </div>
            <div class="progress bg-secondary" style="height: 10px;">
                <div class="progress-bar bg-info" style="width: ${d.score}%"></div>
            </div>
        </div>
    `).join('');
}
