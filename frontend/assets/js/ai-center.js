/**
 * AI Center - Premium Prediction Logic
 */

let currentPredictionId = null;

document.addEventListener('DOMContentLoaded', () => {
    initVerdictInputs();

    // Check for Universal Header
    if (typeof UniversalHeader !== 'undefined') {
        UniversalHeader.injectHeader('header-container', 'ai-center', {
            showNavigation: true,
            showUserInfo: true
        });
    }
});

function initVerdictInputs() {
    const container = document.getElementById('trigger-inputs');
    if (!container) return;
    container.innerHTML = '';
    for (let i = 0; i < 5; i++) {
        const input = document.createElement('input');
        input.type = 'number';
        input.className = 'input-pill';
        input.id = `verdict-input-${i}`;
        input.dataset.index = i;
        input.placeholder = '?';
        input.min = "1";
        input.addEventListener('input', handleVerdictInput);
        container.appendChild(input);
    }
}

function handleVerdictInput(e) {
    const input = e.target;
    const index = parseInt(input.dataset.index, 10);

    // 1. Nettoyer et limiter la saisie
    let value = input.value.replace(/[^0-9]/g, '');
    if (value.length > 2) {
        value = value.slice(0, 2);
    }
    input.value = value;

    // 2. Vérifier les doublons en temps réel
    const allInputs = document.querySelectorAll('#trigger-inputs .input-pill');
    const values = Array.from(allInputs).map(i => i.value).filter(v => v !== '');

    // Réinitialiser les erreurs de doublon
    allInputs.forEach(i => i.classList.remove('is-invalid'));

    const valueCounts = values.reduce((acc, val) => {
        acc[val] = (acc[val] || 0) + 1;
        return acc;
    }, {});

    allInputs.forEach(i => {
        if (i.value && valueCounts[i.value] > 1) {
            i.classList.add('is-invalid');
        }
    });

    // 3. Passer automatiquement au champ suivant
    if (value.length >= 2 && index < allInputs.length - 1) {
        const nextInput = document.getElementById(`verdict-input-${index + 1}`);
        if (nextInput) {
            nextInput.focus();
        }
    }
}

async function launchAIVerdict() {
    const inputs = document.querySelectorAll('.input-pill');
    const numbers = Array.from(inputs).map(i => parseInt(i.value)).filter(n => !isNaN(n));
    const universe = document.getElementById('verdictUniverse').value;

    if (numbers.length < 2) {
        alert("Veuillez saisir au moins 2 numéros pour déclencher l'IA.");
        return;
    }

    // Vérification finale des doublons avant envoi
    const hasDuplicates = document.querySelector('.input-pill.is-invalid');
    if (hasDuplicates) {
        alert("Veuillez corriger les numéros en double (marqués en rouge) avant de lancer l'analyse.");
        return;
    }

    // Show loading state
    const placeholder = document.getElementById('verdict-placeholder');
    const results = document.getElementById('verdict-results');
    placeholder.innerHTML = '<div class="spinner-border text-info" role="status"></div><div class="mt-3">Fusion des modèles en cours...</div>';
    placeholder.style.display = 'flex';
    results.style.display = 'none';

    try {
        // Correction: S'assurer que l'URL inclut le préfixe /api si nécessaire
        const apiBase = API_BASE.endsWith('/api') ? API_BASE : `${API_BASE}/api`;
        const response = await fetch(`${apiBase}/verdict/analyze`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                numbers: numbers,
                universe: universe
            })
        });

        if (!response.ok) throw new Error("Moteur d'intelligence hors ligne");

        const data = await response.json();
        renderVerdict(data);
    } catch (e) {
        let errorMessage = e.message;
        if (e.name === 'AbortError') {
            errorMessage = "Le moteur a mis trop de temps à répondre. Veuillez réessayer.";
        } else if (e.message.includes('Failed to fetch')) {
            errorMessage = "Connexion au moteur impossible. Vérifiez que le serveur est bien démarré.";
        }
        placeholder.innerHTML = `<i class="fas fa-exclamation-triangle fa-3x text-danger mb-3"></i><div class="verdict-error-message">${errorMessage}</div>`;
    }
}

function renderVerdict(data) {
    console.log("Données reçues du verdict:", data);

    // 1. Cacher le loader et afficher les résultats (Force hide)
    const placeholder = document.getElementById('verdict-placeholder');
    const results = document.getElementById('verdict-results');

    if (placeholder) {
        placeholder.style.display = 'none';
        placeholder.innerHTML = ''; // Vider le contenu pour être sûr
    }
    if (results) {
        results.style.display = 'block';
        currentPredictionId = data.prediction_id;
        injectFeedbackPanel();
    }

    // Safety check
    if (!data) return;

    // 1. Confidence Score (Sécurisé)
    try {
        const confNode = document.querySelector('.confidence-val');
        if (confNode) {
            animateValue(confNode, 0, data.confidence_score || 0, 1000);
        }

        // Signal Color
        const circle = document.getElementById('confidence-node');
        const label = document.getElementById('signal-label');
        if (circle && label) {
            const score = data.confidence_score || 0;
            if (score > 70) {
                circle.style.borderColor = '#00f2ff';
                label.className = 'small fw-bold text-info';
                label.innerText = 'SIGNAL FORT';
            } else if (score > 40) {
                circle.style.borderColor = '#ffc107';
                label.className = 'small fw-bold text-warning';
                label.innerText = 'SIGNAL MODÉRÉ';
            } else {
                circle.style.borderColor = '#dc3545';
                label.className = 'small fw-bold text-danger';
                label.innerText = 'SIGNAL FAIBLE';
            }
        }
    } catch (e) {
        console.error("Erreur affichage score:", e);
    }

    // 2. Top Numbers (Sécurisé)
    try {
        const list = document.getElementById('top-numbers-list');
        const topNumbers = data.top_verdict_numbers || [];

        if (list) {
            if (topNumbers.length > 0) {
                list.innerHTML = topNumbers.slice(0, 5).map((n, i) => `
                    <div class="d-flex align-items-center mb-3 bg-dark p-2 rounded border border-secondary">
                        <div class="verdict-number me-3" style="width: 60px;">${n.number}</div>
                        <div class="flex-grow-1">
                            <div class="progress bg-secondary" style="height: 6px;">
                                <div class="progress-bar bg-info" style="width: ${Math.min(n.weighted_score || 0, 100)}%"></div>
                            </div>
                            <div class="small text-muted mt-1">Niveau de Résonance: ${n.weighted_score || 0} points</div>
                        </div>
                        <div class="ms-3 text-info fw-bold">#${i + 1}</div>
                    </div>
                `).join('');
            } else {
                list.innerHTML = '<div class="alert alert-warning text-center">Aucun numéro probable détecté.</div>';
            }
        }
    } catch (e) {
        console.error("Erreur affichage numéros:", e);
    }

    // 3. Stats
    try {
        const sources = data.sources || {};
        const patternRec = sources.pattern_recognition || {};

        const safeSetText = (id, text) => { const el = document.getElementById(id); if (el) el.innerText = text; };
        safeSetText('stat-events', patternRec.events_analyzed || '0');
        safeSetText('stat-match', (patternRec.best_match || '0') + '%');
        safeSetText('stat-eval', `HD-${patternRec.adn_dimension || '42'}`);
    } catch (e) {
        console.error("Erreur affichage stats:", e);
    }

    // 4. Affichage des Tirages Jumeaux (Twin Draws)
    try {
        renderTwinDraws(data);
    } catch (e) {
        console.error("Erreur affichage twin draws:", e);
    }

    // 5. Affichage des Duos Probables (Nouveau)
    try {
        renderProbableDuos(data);
    } catch (e) {
        console.error("Erreur affichage duos:", e);
    }
}

function renderTwinDraws(data) {
    // Trouver ou créer le conteneur pour les tirages jumeaux
    let container = document.getElementById('twin-draws-container');
    if (!container) {
        const detailsCard = document.querySelector('#verdict-results .col-md-12 .power-card');
        if (detailsCard) {
            container = document.createElement('div');
            container.id = 'twin-draws-container';
            container.className = 'mt-4 pt-4 border-top border-secondary';
            detailsCard.appendChild(container);
        }
    }

    if (container) {
        const matchedDraws = data.sources?.pattern_recognition?.matched_draws || [];

        if (matchedDraws.length > 0) {
            const drawsHtml = matchedDraws.slice(0, 6).map(d => {
                const score = Math.round(d.match_score);
                let badgeClass = 'bg-secondary';
                if (score >= 80) badgeClass = 'bg-success';
                else if (score >= 60) badgeClass = 'bg-info';
                else if (score >= 40) badgeClass = 'bg-warning text-dark';

                return `
                <div class="d-flex justify-content-between align-items-center mb-2 p-2 rounded border border-secondary bg-dark-subtle">
                    <div class="d-flex align-items-center">
                        <span class="badge ${badgeClass} me-3" style="width: 70px;">${score}% Match</span>
                        <div>
                            <div class="text-info small fw-bold">${d.date || 'Date inconnue'}</div>
                            <div class="text-muted extra-small">${d.lottery_name || ''}</div>
                        </div>
                    </div>
                    <div class="fw-bold text-white font-monospace fs-5">
                        ${Array.isArray(d.draw_numbers) ? d.draw_numbers.join(' - ') : d.draw_numbers}
                    </div>
                </div>
            `;
            }).join('');

            container.innerHTML = `
                <h6 class="text-uppercase small text-muted mb-3 d-flex justify-content-between">
                    <span><i class="fas fa-fingerprint me-2 text-info"></i>Preuves ADN (Signature HD 42 points)</span>
                    <span class="text-info">${matchedDraws.length} corrélations trouvées</span>
                </h6>
                <div class="twin-draws-list">
                    ${drawsHtml}
                </div>
            `;
        } else {
            container.innerHTML = `
                <div class="mt-3 text-center p-3 border border-dashed border-secondary rounded">
                    <i class="fas fa-search-minus fa-2x mb-2 text-muted opacity-50"></i>
                    <div class="text-muted small">Aucune structure historique similaire identifiée.</div>
                </div>
            `;
        }
    }
}

function renderProbableDuos(data) {
    console.log("Rendu des duos probables réels...");

    // Récupérer les duos du backend
    const duos = data.probable_duos || [];

    // Trouver ou créer le conteneur
    let container = document.getElementById('probable-duos-container');
    if (!container) {
        const topNumbersCard = document.querySelector('#top-numbers-list')?.parentNode;
        if (topNumbersCard) {
            container = document.createElement('div');
            container.id = 'probable-duos-container';
            container.className = 'mt-4 pt-3 border-top border-secondary';
            topNumbersCard.appendChild(container);
        }
    }

    if (container) {
        if (duos.length > 0) {
            const duosHtml = duos.map(d => `
                <div class="d-inline-flex align-items-center me-2 mb-2 p-2 px-3 rounded border border-info bg-dark text-info fw-bold shadow-sm" style="border-left-width: 4px !important;">
                    <i class="fas fa-link me-2 small opacity-75"></i>
                    ${Array.isArray(d.numbers) ? d.numbers.join(' - ') : d.numbers}
                    <span class="badge bg-info text-dark ms-2 small" style="font-size: 0.65rem;">${d.frequency}%</span>
                </div>
            `).join('');

            container.innerHTML = `
                <h6 class="text-uppercase small text-muted mb-3">
                    <i class="fas fa-project-diagram me-2 text-info"></i>Duos à Haute Probabilité
                </h6>
                <div class="duos-list d-flex flex-wrap">${duosHtml}</div>
            `;
        } else {
            container.innerHTML = `
                <div class="text-muted small p-2 border border-dashed border-secondary rounded text-center">
                    Signal de duo insuffisant pour ce tirage.
                </div>
            `;
        }
    }
}

function injectFeedbackPanel() {
    let container = document.getElementById('feedback-panel');
    if (!container) {
        const resultsDiv = document.getElementById('verdict-results');
        container = document.createElement('div');
        container.id = 'feedback-panel';
        container.className = 'power-card mt-4 p-4 border-info';
        container.style.borderStyle = 'dashed';
        resultsDiv.appendChild(container);
    }

    container.innerHTML = `
        <div class="d-flex justify-content-between align-items-center mb-3">
            <h6 class="text-uppercase small text-info mb-0">
                <i class="fas fa-graduation-cap me-2"></i>Entraînement de l'IA : Résultat Réel
            </h6>
            <span class="badge bg-dark border border-info text-info">ID Prédiction: #${currentPredictionId}</span>
        </div>
        <p class="small text-muted mb-3">Saisissez les numéros qui sont réellement sortis pour que l'IA puisse évaluer sa précision et s'améliorer.</p>
        <div class="d-flex gap-2 mb-3" id="feedback-inputs">
            ${[0, 1, 2, 3, 4].map(i => `<input type="number" class="input-pill feedback-input" placeholder="?" min="1" max="90" style="width: 50px; height: 50px;">`).join('')}
        </div>
        <button class="btn btn-outline-info w-100" onclick="submitFeedback()">
            <i class="fas fa-save me-2"></i>Enregistrer le résultat réel & Évaluer
        </button>
        <div id="feedback-status" class="mt-3 small" style="display:none;"></div>
    `;
}

async function submitFeedback() {
    const inputs = document.querySelectorAll('.feedback-input');
    const actualNumbers = Array.from(inputs).map(i => parseInt(i.value)).filter(n => !isNaN(n));
    const statusDiv = document.getElementById('feedback-status');

    if (actualNumbers.length < 2) {
        alert("Veuillez saisir au moins 2 numéros réels.");
        return;
    }

    statusDiv.style.display = 'block';
    statusDiv.className = 'mt-3 small text-info';
    statusDiv.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Calcul de la performance...';

    try {
        const apiBase = API_BASE.endsWith('/api') ? API_BASE : `${API_BASE}/api`;
        const response = await fetch(`${apiBase}/verdict/feedback`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                prediction_id: currentPredictionId,
                actual_numbers: actualNumbers
            })
        });

        if (!response.ok) throw new Error("Erreur lors de l'enregistrement du feedback");

        const result = await response.json();

        statusDiv.className = 'mt-3 p-3 rounded bg-dark border border-success text-success';
        statusDiv.innerHTML = `
            <div class="fw-bold mb-1"><i class="fas fa-check-circle me-2"></i>Résultat Enregistré !</div>
            <div>Précision IA sur ce tirage : <strong>${(result.hit_score * 100).toFixed(0)}%</strong></div>
            <div class="extra-small opacity-75 mt-1">L'IA a détecté ${result.hits_detected} numéro(s) correct(s). Ces données ont été archivées pour l'amélioration continue des modèles.</div>
        `;

        // Disable inputs after success
        inputs.forEach(i => i.disabled = true);
        document.querySelector('#feedback-panel button').disabled = true;

    } catch (e) {
        statusDiv.className = 'mt-3 small text-danger';
        statusDiv.innerHTML = `<i class="fas fa-exclamation-triangle me-2"></i>Erreur: ${e.message}`;
    }
}



function animateValue(obj, start, end, duration) {
    let startTimestamp = null;
    const step = (timestamp) => {
        if (!startTimestamp) startTimestamp = timestamp;
        const progress = Math.min((timestamp - startTimestamp) / duration, 1);
        obj.innerHTML = Math.floor(progress * (end - start) + start);
        if (progress < 1) {
            window.requestAnimationFrame(step);
        }
    };
    window.requestAnimationFrame(step);
}

/* --- CHATBOT LOGIC --- */

function toggleChat() {
    const chatWindow = document.getElementById('chat-window');
    if (chatWindow.style.display === 'flex') {
        chatWindow.style.display = 'none';
        // Restore button visibility/opacity if needed
        document.querySelector('.chat-widget-btn').style.opacity = '1';
    } else {
        chatWindow.style.display = 'flex';
        // Dim button to indicate active state
        document.querySelector('.chat-widget-btn').style.opacity = '0.5';
        // Focus input on open
        setTimeout(() => document.getElementById('chat-input').focus(), 100);
    }
}

function handleChatKey(e) {
    if (e.key === 'Enter') {
        sendMessage();
    }
}

function sendQuickMessage(text) {
    const input = document.getElementById('chat-input');
    input.value = text;
    sendMessage();
}

async function sendMessage() {
    const input = document.getElementById('chat-input');
    const message = input.value.trim();
    if (!message) return;

    // 1. Display User Message
    appendMessage('user', message);
    input.value = '';

    // 2. Show typing indicator
    const typingId = appendMessage('bot', '<i class="fas fa-ellipsis-h fa-fade"></i>');

    try {
        const apiBase = API_BASE.endsWith('/api') ? API_BASE : `${API_BASE}/api`;

        // Prepare context
        const context = {
            prediction_id: currentPredictionId,
            universe: document.getElementById('verdictUniverse').value
        };

        const response = await fetch(`${apiBase}/chat/message`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                message: message,
                context: context
            })
        });

        if (!response.ok) throw new Error("Erreur serveur");

        const data = await response.json();

        // Remove typing indicator
        const typingBubble = document.querySelector(`[data-msg-id="${typingId}"]`);
        if (typingBubble) typingBubble.remove();

        // 3. Display Bot Response
        // Clean markdown-style bolding for HTML display
        let cleanText = data.text
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>') // Bold
            .replace(/\n/g, '<br>'); // Newlines

        let html = cleanText;

        // Add action buttons if any
        if (data.actions && data.actions.length > 0) {
            html += '<div class="chat-actions">';
            data.actions.forEach(action => {
                html += `<button class="chat-action-btn" onclick="sendQuickMessage('${action}')">${action}</button>`;
            });
            html += '</div>';
        }

        appendMessage('bot', html);

    } catch (e) {
        console.error(e);
        // Remove typing indicator if error
        const typingBubble = document.querySelector(`[data-msg-id="${typingId}"]`);
        if (typingBubble) typingBubble.remove();

        appendMessage('bot', "Désolé, je suis momentanément indisponible. Le cerveau numérique redémarre...");
    }
}

function appendMessage(sender, html) {
    const container = document.getElementById('chat-messages');
    const bubble = document.createElement('div');
    bubble.className = `chat-bubble ${sender}`;

    // Unique ID for removing typing indicator
    const msgId = 'msg-' + Date.now() + Math.random().toString(36).substr(2, 9);
    bubble.dataset.msgId = msgId;

    bubble.innerHTML = html;
    container.appendChild(bubble);

    // Auto-scroll to bottom
    container.scrollTop = container.scrollHeight;

    return msgId;
}

