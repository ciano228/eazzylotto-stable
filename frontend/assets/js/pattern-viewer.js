// Pattern Viewer - Consolidated Logic
const API_BASE = 'http://localhost:8000';

const STATE = {
    inputCount: 5,
    maxInputs: 10,
    minInputs: 2,
    universe: 'mundo',
    currentTab: 'gaps'
};

document.addEventListener('DOMContentLoaded', () => {
    console.log('Pattern Viewer Initialized');

    // Sync state with global selector
    const globalSelector = document.getElementById('globalUniverseSelect');
    if (globalSelector) {
        STATE.universe = globalSelector.value;
    }

    // Init Gaps Tab
    loadGapsAnalysis();

    // Init Signature Tab
    initInputs();

    // Init Session Tab
    loadSessions();
});

// --- GLOBAL UNIVERSE HANDLER ---
window.onUniverseChange = function () {
    const globalSelector = document.getElementById('globalUniverseSelect');
    if (globalSelector) {
        STATE.universe = globalSelector.value;
        console.log('Universe changed to:', STATE.universe);

        // Auto-refresh based on active tab
        if (STATE.currentTab === 'gaps') {
            loadGapsAnalysis();
        } else if (STATE.currentTab === 'signature') {
            // Clear previous results as they are universe-specific
            document.getElementById('signature-results').style.display = 'none';
        } else if (STATE.currentTab === 'session') {
            // Optional: Re-analyze if a session is already selected
            if (document.getElementById('session-select').value) {
                analyzeSessionEvolution();
            }
        } else if (STATE.currentTab === 'performance') {
            loadPerformanceStats();
        }
    }
}

// --- TAB MANAGEMENT ---
window.switchTab = function (tabName) {
    STATE.currentTab = tabName;

    // Update Buttons
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    document.querySelector(`.tab-btn[onclick="switchTab('${tabName}')"]`).classList.add('active');

    // Update Content
    document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
    document.getElementById(`tab-${tabName}`).classList.add('active');

    // Load stats if needed
    if (tabName === 'performance') {
        loadPerformanceStats();
    }
}

// ==========================================
// TAB 1: GAPS ANALYSIS (Existing Logic)
// ==========================================

window.loadGapsAnalysis = async function () {
    const universe = STATE.universe; // Use global state
    const container = document.getElementById('predictionsContainer');

    container.innerHTML = '<div class="text-white">Chargement des écarts...</div>';

    try {
        const response = await fetch(`${API_BASE}/api/analytics/gaps/${universe}`);
        if (!response.ok) throw new Error("Erreur de chargement");

        const data = await response.json();

        displayPredictions(data.overdue_attributes, data.hot_attributes);
        displayPatterns(data.gaps_analysis);
        displayTrends(data.summary);

    } catch (e) {
        console.error("Gaps Error", e);
        container.innerHTML = `<div class="text-danger">Erreur: ${e.message}. Vérifiez que le backend tourne.</div>`;
    }
}

function displayPredictions(overdue, hot) {
    let html = '';

    // Overdue
    for (const [attrType, attributes] of Object.entries(overdue || {})) {
        attributes.slice(0, 3).forEach(attr => {
            const strength = attr.delay_ratio > 5 ? 'EXTRÊME' : attr.delay_ratio > 3 ? 'FORTE' : 'MOYENNE';
            html += `
                <div class="prediction-card">
                    <h3>${attrType.toUpperCase()}</h3>
                    <div class="value">${attr.value}</div>
                    <div class="details">
                        Force: <strong>${strength}</strong><br>
                        Écart: ${attr.current_gap} (Moy: ${attr.average_gap})
                    </div>
                </div>
            `;
        });
    }

    // Hot
    for (const [attrType, attributes] of Object.entries(hot || {})) {
        attributes.slice(0, 2).forEach(attr => {
            html += `
                <div class="prediction-card hot">
                    <h3>${attrType.toUpperCase()} 🔥</h3>
                    <div class="value">${attr.value}</div>
                    <div class="details">
                        Hyper Actif<br>
                        Écart: ${attr.current_gap}
                    </div>
                </div>
            `;
        });
    }

    document.getElementById('predictionsContainer').innerHTML = html || '<p class="text-muted">Rien à signaler.</p>';
}

function displayPatterns(gapsData) {
    let html = '';
    for (const [attrType, values] of Object.entries(gapsData || {})) {
        // Simple logic to show interesting gaps
        const interesting = Object.entries(values)
            .filter(([_, stats]) => stats.current_gap > 10)
            .sort((a, b) => b[1].current_gap - a[1].current_gap)
            .slice(0, 5);

        if (interesting.length > 0) {
            html += `<div class="pattern-item">
                <h4>${attrType}</h4>
                <div class="small text-muted">
                    ${interesting.map(x => `${x[0]} (${x[1].current_gap})`).join(', ')}
                </div>
            </div>`;
        }
    }
    document.getElementById('patternsContainer').innerHTML = html;
}

function displayTrends(summary) {
    let html = '';
    for (const [attrType, stats] of Object.entries(summary || {})) {
        html += `<div class="pattern-item">
            <h4>${attrType}</h4>
            <div class="small text-muted">
                Moyenne Écarts: ${stats.avg_current_gap.toFixed(1)}
            </div>
        </div>`;
    }
    document.getElementById('trendsContainer').innerHTML = html;
}


// ==========================================
// TAB 2: SIGNATURE SEARCH
// ==========================================

window.initInputs = function () {
    const container = document.getElementById('input-container');
    container.innerHTML = '';
    for (let i = 0; i < STATE.inputCount; i++) {
        createInputBall(container, i);
    }
}

function createInputBall(container, index) {
    const input = document.createElement('input');
    input.type = 'number';
    input.className = 'input-ball';
    input.placeholder = '?';
    input.min = "1";
    input.oninput = (e) => {
        // Prevent negative signs & decimals
        e.target.value = e.target.value.replace(/[^0-9]/g, '');
        if (e.target.value.length > 2) e.target.value = e.target.value.slice(0, 2);
    };
    // Double check on keydown to block '-'
    input.onkeydown = (e) => {
        if (e.key === '-' || e.key === 'e' || e.key === '.') e.preventDefault();
    };
    container.appendChild(input);
}

window.addInputSlot = function () {
    if (STATE.inputCount < STATE.maxInputs) {
        STATE.inputCount++;
        createInputBall(document.getElementById('input-container'), STATE.inputCount - 1);
    }
}

window.removeInputSlot = function () {
    if (STATE.inputCount > STATE.minInputs) {
        STATE.inputCount--;
        const container = document.getElementById('input-container');
        container.removeChild(container.lastChild);
    }
}

window.clearInputs = function () {
    document.querySelectorAll('.input-ball').forEach(inp => inp.value = '');
}

window.analyzeManualDraw = async function () {
    const inputs = document.querySelectorAll('.input-ball');
    const numbers = Array.from(inputs).map(i => parseInt(i.value)).filter(n => !isNaN(n));

    // VALIDATION
    if (numbers.length < 2) {
        alert("Entrez au moins 2 numéros.");
        return;
    }

    // Duplicate Check
    const duplicates = numbers.filter((item, index) => numbers.indexOf(item) !== index);
    if (duplicates.length > 0) {
        alert(`Doublons détectés : ${duplicates.join(', ')}. Chaque numéro doit être unique.`);
        inputs.forEach(inp => {
            if (duplicates.includes(parseInt(inp.value))) {
                inp.style.borderColor = 'red';
                inp.style.boxShadow = '0 0 10px red';
            }
        });
        return;
    }

    // Reset styles
    inputs.forEach(inp => {
        inp.style.borderColor = '';
        inp.style.boxShadow = '';
    });

    try {
        const response = await fetch(`${API_BASE}/api/patterns/analyze-draw`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                numbers: numbers,
                universe: STATE.universe,
                threshold: 50
            })
        });

        if (!response.ok) throw new Error("Erreur serveur");

        const data = await response.json();
        LAST_ANALYSIS_DATA = data; // Stockage pour le feedback loop
        renderSignatureResults(data);

    } catch (e) {
        alert("Erreur: " + e.message);
    }
}

function renderSignatureResults(data) {
    document.getElementById('signature-results').style.display = 'block';

    // 1. Fetch exact signature structure for display
    fetch(`${API_BASE}/api/patterns/signature?numbers=${data.target_numbers.join(',')}&universe=${STATE.universe}`)
        .then(r => r.json())
        .then(sigData => {
            renderSignatureCards(sigData.signature, data.target_numbers);
        });

    // 2. Predictions
    const cons = data.consequences || {};
    const analyzedCount = cons.analyzed_events || 0;

    // Update summary title with count
    const predTitle = document.querySelector('#tab-signature h3');
    if (predTitle) predTitle.innerHTML = `<i class="fas fa-magic"></i> Analyse des Conséquences (${analyzedCount} événements trouvés)`;

    if (analyzedCount === 0) {
        const msg = '<div class="text-muted small italic">Pas assez de données historiques pour une prédiction fiable.</div>';
        document.getElementById('pred-numbers-list').innerHTML = msg;
        document.getElementById('pred-pairs-list').innerHTML = msg;
        document.getElementById('pred-attrs-list').innerHTML = msg;
    } else {
        // Numbers
        document.getElementById('pred-numbers-list').innerHTML = (cons.most_frequent_numbers || [])
            .slice(0, 5).map(n => `<div class="d-flex justify-content-between"><span>${n.number}</span> <span class="text-warning">${n.frequency}%</span></div>`).join('');

        // Pairs
        document.getElementById('pred-pairs-list').innerHTML = (cons.most_frequent_pairs || [])
            .slice(0, 5).map(p => `<div class="d-flex justify-content-between"><span>${p.pair}</span> <span class="text-info">${p.frequency}%</span></div>`).join('');

        // Attributes
        let attrHtml = '';
        if (cons.most_frequent_attributes) {
            for (const [type, stats] of Object.entries(cons.most_frequent_attributes)) {
                if (stats && stats.length > 0) {
                    attrHtml += `<div class="d-flex justify-content-between"><span class="small text-muted">${type}</span> <span class="text-danger">${stats[0].value} (${stats[0].frequency}%)</span></div>`;
                }
            }
        }
        document.getElementById('pred-attrs-list').innerHTML = attrHtml || '<div class="text-muted">N/A</div>';
    }

    // 3. Matches
    const tbody = document.getElementById('matches-table-body');
    tbody.innerHTML = '';
    data.matches.forEach(m => {
        tbody.innerHTML += `
            <tr>
                <td>${m.draw_date ? new Date(m.draw_date).toLocaleDateString() : '-'}</td>
                <td class="small text-muted">${m.session_name || '-'}</td>
                <td class="small text-info">${m.lottery_name || '-'}</td>
                <td class="text-warning fw-bold">${m.draw_numbers.join('-')}</td>
                <td>${Math.round(m.match_score)}%</td>
                <td>${m.match_type}</td>
            </tr>
        `;
    });
}

function renderSignatureCards(signature, numbers) {
    const container = document.getElementById('signature-container');
    container.innerHTML = '';

    const sortedNums = [...numbers].sort((a, b) => a - b);
    let pairIdx = 0;

    for (let i = 0; i < sortedNums.length; i++) {
        for (let j = i + 1; j < sortedNums.length; j++) {
            const pNums = [sortedNums[i], sortedNums[j]];
            const attrs = signature[pairIdx] || {};
            pairIdx++;

            let badges = '';
            for (const [k, v] of Object.entries(attrs)) {
                if (v && v !== '---') badges += `<span class="attr-badge">${v}</span> `;
            }

            const div = document.createElement('div');
            div.className = 'signature-pair';
            div.style.flex = "1 0 200px";
            div.innerHTML = `
                <div class="pair-numbers">${pNums[0]}-${pNums[1]}</div>
                <div class="pair-attributes">${badges}</div>
            `;
            container.appendChild(div);
        }
    }
}


// ==========================================
// TAB 3: SESSION EVOLUTION
// ==========================================

async function loadSessions() {
    const select = document.getElementById('session-select');
    try {
        const res = await fetch(`${API_BASE}/api/session/sessions`); // Unified endpoint
        if (res.ok) {
            const data = await res.json();
            // Unified endpoint returns object {status: 'success', sessions: [...]}
            const sessions = data.sessions || data;

            sessions.forEach(s => {
                const opt = document.createElement('option');
                opt.value = s.id;
                opt.textContent = s.name;
                select.appendChild(opt);
            });
        }
    } catch (e) {
        console.warn("Sessions load failed", e);
        select.innerHTML = '<option value="1">Session Principale (Mundo)</option>';
    }
}

window.analyzeSessionEvolution = async function () {
    const sessionId = document.getElementById('session-select').value || 1;
    const start = document.getElementById('start-date').value;
    const end = document.getElementById('end-date').value;

    const container = document.getElementById('evolution-timeline');
    container.innerHTML = '<div class="text-white p-3">Chargement...</div>';
    document.getElementById('evolution-results').style.display = 'block';

    try {
        let url = `${API_BASE}/api/patterns/analyze-session?session_id=${sessionId}&universe=${STATE.universe}`;
        if (start) url += `&start_date=${start}`;
        if (end) url += `&end_date=${end}`;

        const res = await fetch(url);
        if (!res.ok) throw new Error("Erreur Analyse");
        const data = await res.json();

        container.innerHTML = '';
        data.evolution_timeline.forEach(item => {
            let attrSum = '';
            for (const [t, vals] of Object.entries(item.attributes)) {
                attrSum += `<div class="attr-badge mb-1">${t}: ${vals[0]}</div>`;
            }

            const div = document.createElement('div');
            div.className = 'timeline-item';
            div.innerHTML = `
                <div class="small text-muted mb-1">${new Date(item.date).toLocaleDateString()}</div>
                <div class="fw-bold text-warning mb-2">${item.numbers.join('-')}</div>
                <div>${attrSum}</div>
            `;
            container.appendChild(div);
        });

        // Global Stats
        const statsC = document.getElementById('session-stats-container');
        statsC.innerHTML = '';
        for (const [type, vals] of Object.entries(data.global_stats)) {
            const top = vals[0];
            if (top) {
                statsC.innerHTML += `
                    <div class="text-center bg-dark p-2 rounded border border-secondary">
                        <div class="small text-muted text-uppercase">${type}</div>
                        <div class="fw-bold text-success fs-4">${top.value}</div>
                        <div class="small">Freq: ${(top.frequency).toFixed(1)}</div>
                    </div>
                 `;
            }
        }

    } catch (e) {
        container.innerHTML = `<div class="text-danger">Erreur: ${e.message}</div>`;
    }
}
