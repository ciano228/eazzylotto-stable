/**
 * Katooling Tracking Hub - Core Logic
 * Unifie l'Analyse Temporelle et le Split Strategy
 */

const CONFIG = {
    API_BASE: '/api/analytics',
    SESSION_ENDPOINTS: [
        '/api/unified/session/sessions',
        '/api/session/sessions',
        '/unified/session/sessions'
    ]
};

document.addEventListener('DOMContentLoaded', () => {
    initHub();
});

async function initHub() {
    console.log("🚀 Initializing Katooling Hub...");

    // Set default universe to mundo
    const univSelect = document.getElementById('universeSelect');
    if (univSelect) univSelect.value = 'mundo';

    await loadSessions();
    setupEventListeners();

    // Auto-scan initial
    performGlobalScan();
}

function setupEventListeners() {
    document.getElementById('scanBtn').addEventListener('click', () => {
        performGlobalScan();
    });

    document.getElementById('universeSelect').addEventListener('change', () => {
        performGlobalScan();
    });
}

/**
 * Charge les sessions actives pour le sélecteur
 */
async function loadSessions() {
    const select = document.getElementById('sessionSelect');
    select.innerHTML = '<option value="">Chargement des sessions...</option>';

    // Essayer les variantes de points d'entrée
    const endpoints = [
        '/api/unified/session/sessions',   // integrated_server: /api + /unified + /session/sessions
        '/api/session/sessions',           // integrated_server: /api + /session + /sessions
        '/api/sessions'                    // main.py direct
    ];

    for (const url of endpoints) {
        try {
            console.log(`🔍 Tentative de chargement des sessions via: ${url}`);
            const resp = await fetch(url);
            if (!resp.ok) continue;

            const data = await resp.json();
            console.log(`📦 Données reçues via ${url}:`, data);

            const sessions = data.sessions || data.value || (Array.isArray(data) ? data : null);

            if (sessions && Array.isArray(sessions) && sessions.length > 0) {
                select.innerHTML = '';
                sessions.forEach(s => {
                    const opt = document.createElement('option');
                    opt.value = s.id || s.session_id;

                    // Récupérer les dates
                    const startDate = s.start_date || (s.progress && s.progress.start_date);
                    const endDate = s.end_date || (s.progress && s.progress.end_date);

                    const dateInfo = (startDate && endDate)
                        ? ` (${formatDate(startDate)} - ${formatDate(endDate)})`
                        : "";

                    opt.textContent = (s.name || s.session_name || `Session ${s.id}`) + dateInfo;

                    // Stocker les dates pour utilisation ultérieure
                    if (startDate) opt.dataset.start = startDate;
                    if (endDate) opt.dataset.end = endDate;

                    select.appendChild(opt);
                });
                console.log(`✅ ${sessions.length} sessions chargées depuis ${url}`);
                return;
            }
        } catch (e) {
            console.warn(`Erreur sur ${url}:`, e);
        }
    }

    select.innerHTML = '<option value="">Aucune session trouvée (Vérifiez la DB)</option>';
}

/**
 * Scanne les opportunités basées sur l'analyse temporelle
 */
async function performGlobalScan() {
    const universe = document.getElementById('universeSelect').value;
    const scanner = document.getElementById('opportunityScanner');

    scanner.innerHTML = `
        <div style="text-align:center; padding: 20px;">
            <div class="loading-shimmer" style="width: 50px; height: 50px; border-radius: 50%; margin: 0 auto 10px;"></div>
            <p>Analyse de l'univers ${universe.toUpperCase()}...</p>
        </div>
    `;

    try {
        const sessionSelect = document.getElementById('sessionSelect');
        const selectedOption = sessionSelect.options[sessionSelect.selectedIndex];
        const sessionId = sessionSelect.value;

        let dateStart = "2024-01-01";
        let dateEnd = "2024-12-31";
        let histStart = "2023-01-01";
        let histEnd = "2023-12-31";

        if (selectedOption && selectedOption.dataset.start && selectedOption.dataset.end) {
            dateStart = selectedOption.dataset.start.split('T')[0];
            dateEnd = selectedOption.dataset.end.split('T')[0];

            // Calculer une période historique (ex: 6 mois avant la session)
            const ds = new Date(dateStart);
            const de = new Date(dateEnd);
            const diff = de - ds;

            const hs = new Date(ds.getTime() - diff - (24 * 60 * 60 * 1000));
            const he = new Date(ds.getTime() - (24 * 60 * 60 * 1000));

            histStart = hs.toISOString().split('T')[0];
            histEnd = he.toISOString().split('T')[0];
        }

        const payload = {
            session_id: sessionId || null,
            tables_config: [
                { title: "Session", dateStart: dateStart, dateEnd: dateEnd, type: "historical" },
                { title: "Pré-Session", dateStart: histStart, dateEnd: histEnd, type: "historical" }
            ],
            marking_type: "chip"
        };

        const scanUrl = `${CONFIG.API_BASE}/temporal-analysis/${universe}`;
        console.log(`🔍 Scan global sur: ${scanUrl}`);

        const resp = await fetch(scanUrl, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        if (!resp.ok) throw new Error(`HTTP ${resp.status}`);

        const result = await resp.json();

        if (result.status === 'success' && result.patterns && result.patterns.length > 0) {
            renderOpportunities(result.patterns);
        } else {
            scanner.innerHTML = '<div style="color:var(--text-dim); text-align:center; padding: 20px;">Aucune opportunité statistique claire détectée pour le moment.</div>';
        }

    } catch (e) {
        console.error("Erreur Scan:", e);
        scanner.innerHTML = '<div style="color:#ef4444; padding: 20px;">Erreur lors du scan des opportunités.</div>';
    }
}

function renderOpportunities(patterns) {
    const scanner = document.getElementById('opportunityScanner');
    scanner.innerHTML = '';

    patterns.forEach(p => {
        const card = document.createElement('div');
        card.className = 'opportunity-card';

        // Déterminer le type d'attribut pour le split
        let attrType = p.attribute || 'chip';
        let attrValue = p.data?.value || p.chipNumber || "";

        // Mapping spécial pour les types backend vs split service
        if (attrType === 'granque') attrType = 'petique';

        card.innerHTML = `
            <div class="opp-header">
                <span class="opp-type">${p.type}</span>
                <span class="opp-confidence">${p.confidence}% Confiance</span>
            </div>
            <div style="font-weight: 600; margin-bottom: 5px;">${p.description}</div>
            <div style="font-size: 0.85rem; color: var(--text-dim);">${p.details}</div>
        `;

        card.onclick = () => {
            // Highlight
            document.querySelectorAll('.opportunity-card').forEach(c => c.classList.remove('tracking-active'));
            card.classList.add('tracking-active');

            // Trigger Split Refinement
            loadSplitRefinement(attrType, attrValue);
        };

        scanner.appendChild(card);
    });
}

/**
 * Charge le Split (Ya-Played vs Not-Yet-Played) pour l'attribut choisi
 */
async function loadSplitRefinement(attrType, attrValue) {
    const viz = document.getElementById('refinementViz');
    const universe = document.getElementById('universeSelect').value;
    const sessionId = document.getElementById('sessionSelect').value;

    viz.innerHTML = `
        <div style="text-align:center; padding-top: 100px;">
            <div class="loading-shimmer" style="width: 200px; height: 10px; margin: 0 auto 10px;"></div>
            <p>Calcul du split Katooling en cours...</p>
        </div>
    `;

    if (!sessionId) {
        viz.innerHTML = '<div style="color:#ef4444; padding: 20px;">Veuillez sélectionner une session pour le split.</div>';
        return;
    }

    try {
        const url = `${CONFIG.API_BASE}/katooling/split/${universe}/${sessionId}?attribute_type=${attrType}&attribute_value=${attrValue}`;
        const resp = await fetch(url);
        const result = await resp.json();

        if (result.status === 'success') {
            renderSplit(result);
        } else {
            viz.innerHTML = `<div style="color:#ef4444; padding: 20px;">${result.message || "Erreur Split"}</div>`;
        }
    } catch (e) {
        console.error("Erreur Split:", e);
        viz.innerHTML = '<div style="color:#ef4444; padding: 20px;">Erreur de connexion au service de split.</div>';
    }
}

function renderSplit(data) {
    const viz = document.getElementById('refinementViz');

    viz.innerHTML = `
        <div style="margin-bottom: 25px;">
            <h3 style="margin-top:0;">Raffinement: ${data.attribute}</h3>
            <p style="font-size: 0.85rem; color: var(--text-dim);">
                Analyse sur <b>${data.period_days} jours</b> (${data.analysis_bounds.start} au ${data.analysis_bounds.end}).<br>
                Total combinaisons : ${data.total_count}
            </p>
        </div>

        <div class="split-results">
            <!-- YA PLAYED -->
            <div class="split-box box-played">
                <div class="box-title">
                    <span>Déjà Sortis (Dette Payée)</span>
                    <span style="color: #ef4444;">${data.ya_played.count}</span>
                </div>
                <div class="combo-grid">
                    ${data.ya_played.combinations.map(c => {
        const datesStr = (c.apparition_dates && c.apparition_dates.length > 0)
            ? `\nDates: ${c.apparition_dates.map(ds => formatDate(ds)).join(', ')}`
            : "";
        return `<div class="combo-chip" title="${c.denomination || ''} #${c.alpha_ranking || ''} (Apparu ${c.apparition_count} fois)${datesStr}">${formatCombo(c.combination)}</div>`;
    }).join('')}
                </div>
            </div>

            <!-- POTENTIAL -->
            <div class="split-box box-potential">
                <div class="box-title">
                    <span>À Venir (Débiteurs)</span>
                    <span style="color: #22c55e;">${data.not_yet_played.count}</span>
                </div>
                <div class="combo-grid">
                    ${data.not_yet_played.combinations.map(c => `
                        <div class="combo-chip" title="${c.denomination || ''} #${c.alpha_ranking || ''}" onclick="copyToClipboard('${c.combination}')">${formatCombo(c.combination)}</div>
                    `).join('')}
                </div>
                <div style="margin-top: 20px; font-size: 0.75rem; color: var(--text-dim); text-align: center;">
                    Cible d'investissement recommandée : les <b>Débiteurs</b>.
                </div>
            </div>
        </div>
    `;
}

function formatCombo(comboStr) {
    if (!comboStr) return "-";
    // Si c'est "05-12", on peut garder tel quel ou formater
    return comboStr;
}

function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        alert("Combinaison copiée : " + text);
    });
} function formatDate(dateStr) {
    if (!dateStr) return "";
    try {
        const d = new Date(dateStr);
        return d.toLocaleDateString('fr-FR');
    } catch (e) {
        return dateStr;
    }
}
