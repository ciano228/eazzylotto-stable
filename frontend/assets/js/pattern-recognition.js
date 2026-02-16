// frontend/assets/js/pattern-recognition.js

document.addEventListener('DOMContentLoaded', () => {
    // Universal Header Injection
    if (typeof UniversalHeader !== 'undefined') {
        UniversalHeader.injectHeader('header-container', 'pattern-recognition', {
            showNavigation: true,
            showUserInfo: true
        });
    }

    const API_BASE = window.API_BASE || 'http://localhost:8881'; // Fallback if not defined in HTML
    const API_PREFIX = API_BASE.endsWith('/api') ? API_BASE : `${API_BASE}/api`;

    const patternUniverseSelect = document.getElementById('patternUniverse');
    const triggerInputsContainer = document.getElementById('trigger-inputs-container');
    const analyzeDrawButton = document.getElementById('analyzeDrawButton');
    const sessionSelect = document.getElementById('sessionSelect');
    const loadSessionButton = document.getElementById('loadSessionButton');
    const startDateInput = document.getElementById('startDate');
    const endDateInput = document.getElementById('endDate');
    const loadPeriodButton = document.getElementById('loadPeriodButton');

    const patternPlaceholder = document.getElementById('pattern-placeholder');
    const patternResults = document.getElementById('pattern-results');

    // Default to 5 inputs initially, as per ai-center.html pattern, but dynamic
    let currentInputCount = 5;
    createNumberInputs(currentInputCount);

    // --- Event Listeners ---
    analyzeDrawButton.addEventListener('click', analyzeDraw);
    loadSessionButton.addEventListener('click', () => loadSessions(sessionSelect.value));
    loadPeriodButton.addEventListener('click', loadPeriodData);
    patternUniverseSelect.addEventListener('change', () => {
        // Potentially adjust input count based on selected universe (future feature)
        // For now, re-analyze or clear results
        hideResults();
    });

    // --- Input Handling ---
    function createNumberInputs(count) {
        triggerInputsContainer.innerHTML = '';
        for (let i = 0; i < count; i++) {
            const input = document.createElement('input');
            input.type = 'number';
            input.className = 'input-number-pill';
            input.id = `number-input-${i}`;
            input.dataset.index = i;
            input.placeholder = '?';
            input.min = "1";
            input.max = "90"; // Assuming 90 is max for now
            input.addEventListener('input', handleNumberInput);
            triggerInputsContainer.appendChild(input);
        }
    }

    function handleNumberInput(e) {
        const input = e.target;
        const index = parseInt(input.dataset.index, 10);

        let value = input.value.replace(/[^0-9]/g, '');
        if (value.length > 2) {
            value = value.slice(0, 2);
        }
        input.value = value;

        const allInputs = document.querySelectorAll('#trigger-inputs-container .input-number-pill');
        const values = Array.from(allInputs).map(i => i.value).filter(v => v !== '');

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

        if (value.length >= 2 && index < allInputs.length - 1) {
            const nextInput = document.getElementById(`number-input-${index + 1}`);
            if (nextInput) {
                nextInput.focus();
            }
        }
    }

    // --- UI State Management ---
    function showLoading(message = "Analyse en cours...") {
        patternPlaceholder.innerHTML = `<div class="spinner-container"><div class="spinner-border text-info" role="status"></div><div class="mt-3">${message}</div></div>`;
        patternPlaceholder.style.display = 'flex';
        patternResults.style.display = 'none';
    }

    function hideResults() {
        patternPlaceholder.style.display = 'flex';
        patternResults.style.display = 'none';
        patternPlaceholder.innerHTML = `<i class="fas fa-fingerprint fa-4x mb-4 text-secondary opacity-25"></i>
                                        <h3 class="text-secondary">En attente de tirage ou session...</h3>
                                        <p class="text-muted small">Entrez un tirage déclencheur ou chargez une session historique pour commencer l'analyse.</p>`;
    }

    function showError(message) {
        patternPlaceholder.innerHTML = `<div class="spinner-container"><i class="fas fa-exclamation-triangle fa-3x text-danger mb-3"></i><div class="text-danger fw-bold">${message}</div></div>`;
        patternPlaceholder.style.display = 'flex';
        patternResults.style.display = 'none';
    }

    function showResults() {
        patternPlaceholder.style.display = 'none';
        patternResults.style.display = 'block';
    }

    // --- API Calls ---

    async function fetchAvailableSessions() {
        try {
            const response = await fetch(`${API_PREFIX}/unified/session/sessions`);
            if (!response.ok) throw new Error('Failed to fetch sessions');
            const data = await response.json();
            sessionSelect.innerHTML = '<option value="">-- Sélectionner une session --</option>';
            data.sessions.forEach(session => {
                const option = document.createElement('option');
                option.value = session.id;
                option.textContent = `${session.name} (${session.lottery_type} - ${session.start_date})`;
                sessionSelect.appendChild(option);
            });
        } catch (error) {
            console.error('Error fetching sessions:', error);
            showError(`Impossible de charger les sessions: ${error.message}`);
        }
    }

    async function analyzeDraw() {
        const allInputs = document.querySelectorAll('#trigger-inputs-container .input-number-pill');
        const numbers = Array.from(allInputs).map(i => parseInt(i.value)).filter(n => !isNaN(n));
        const universe = patternUniverseSelect.value;

        if (numbers.length < 2) {
            alert("Veuillez saisir au moins 2 numéros pour l'analyse.");
            return;
        }
        if (document.querySelector('.input-number-pill.is-invalid')) {
            alert("Veuillez corriger les numéros en double ou invalides.");
            return;
        }

        showLoading("Analyse de la signature...");

        try {
            // Step 1: Get Signature
            const signatureResponse = await fetch(`${API_PREFIX}/patterns/signature?numbers=${numbers.join(',')}&universe=${universe}`);
            if (!signatureResponse.ok) throw new Error('Failed to fetch signature');
            const signatureData = await signatureResponse.json();
            renderSignature(signatureData);

            // Step 2: Get Twin Draws (Matches) via unique GET endpoint
            const twinDrawsResponse = await fetch(`${API_PREFIX}/patterns/analyze?numbers=${numbers.join(',')}&universe=${universe}&threshold=20`);
            if (!twinDrawsResponse.ok) throw new Error('Failed to fetch twin draws');
            const twinDrawsData = await twinDrawsResponse.json();
            renderTwinDraws(twinDrawsData);

            // Step 3: Get Predictions from Consequences
            if (twinDrawsData.consequences) {
                const cons = twinDrawsData.consequences;
                const predictionData = {
                    watchNumbers: (cons.next_number_frequencies || []).slice(0, 5).map(f => ({
                        number: f.number,
                        score: Math.round(f.frequency)
                    })),
                    probableDuos: (cons.most_frequent_pairs || []).slice(0, 5).map(p => p.pair),
                    attributeWeather: cons.dominant_patterns || []
                };
                renderPredictions(predictionData);
            }

            showResults();

        } catch (error) {
            console.error('Error analyzing draw:', error);
            showError(`Erreur lors de l'analyse du tirage: ${error.message}`);
        }
    }

    async function loadSessions(sessionId) {
        if (!sessionId) {
            alert("Veuillez sélectionner une session à charger.");
            return;
        }

        const universe = patternUniverseSelect.value;
        showLoading("Chargement de la session...");

        try {
            // This endpoint might need to be adjusted based on actual backend implementation
            const sessionDataResponse = await fetch(`${API_PREFIX}/unified/sessions/${sessionId}/draws?universe=${universe}`);
            if (!sessionDataResponse.ok) throw new Error('Failed to load session draws');
            const sessionData = await sessionDataResponse.json();

            renderSessionProgress(sessionData.draws); // Assuming sessionData.draws is an array of draws

            showResults();

        } catch (error) {
            console.error('Error loading session:', error);
            showError(`Erreur lors du chargement de la session: ${error.message}`);
        }
    }

    async function loadPeriodData() {
        const universe = patternUniverseSelect.value;
        const startDate = startDateInput.value;
        const endDate = endDateInput.value;

        if (!startDate || !endDate) {
            alert("Veuillez sélectionner une date de début et une date de fin.");
            return;
        }

        showLoading("Chargement des données de période...");

        try {
            // Endpoint to fetch draws for a period, potentially similar to /draws/real/{univers}
            const periodDataResponse = await fetch(`${API_PREFIX}/draws/real/${universe}?date_start=${startDate}&date_end=${endDate}`);
            if (!periodDataResponse.ok) throw new Error('Failed to load period data');
            const periodData = await periodDataResponse.json();

            renderSessionProgress(periodData.draws); // Assuming periodData.draws is an array of draws

            showResults();

        } catch (error) {
            console.error('Error loading period data:', error);
            showError(`Erreur lors du chargement des données de période: ${error.message}`);
        }
    }

    // --- Rendering Functions ---

    function renderSignature(data) {
        console.log('API Response for signature:', JSON.stringify(data, null, 2));
        const signatureDisplay = document.getElementById('signature-display');
        const signatureEmpty = document.getElementById('signature-empty');
        signatureDisplay.innerHTML = '';

        if (!data || !Array.isArray(data.signature) || data.signature.length === 0) {
            signatureEmpty.style.display = 'block';
            return;
        }
        signatureEmpty.style.display = 'none';

        data.signature.forEach(pair => {
            const pairElement = document.createElement('div');
            pairElement.className = 'col-md-6 col-lg-4 mb-3';

            // Defensive check in case a "pair" is not an object
            if (typeof pair !== 'object' || pair === null) {
                console.error('Invalid item in signature array:', pair);
                return; // Skip this iteration
            }

            const numbersText = Array.isArray(pair.numbers) ? pair.numbers.join('-') : 'N/A';
            const typeText = pair.type || 'N/A';
            const formeText = pair.forme || 'N/A';
            const denominationText = pair.denomination || 'N/A';
            const tomeText = pair.tome || 'N/A';

            pairElement.innerHTML = `
                <div class="pattern-attribute">
                    <div>
                        <strong>${numbersText}</strong> <span class="text-muted small">(${typeText})</span><br>
                        <span class="small">${formeText}, ${denominationText}</span>
                    </div>
                    <span class="badge bg-secondary">${tomeText}</span>
                </div>
            `;
            signatureDisplay.appendChild(pairElement);
        });
    }

    function renderTwinDraws(data) {
        const twinDrawsList = document.getElementById('twin-draws-list');
        const twinDrawsEmpty = document.getElementById('twin-draws-empty');
        twinDrawsList.innerHTML = '';

        if (!data || !data.matched_draws || data.matched_draws.length === 0) {
            twinDrawsEmpty.style.display = 'block';
            return;
        }
        twinDrawsEmpty.style.display = 'none';

        data.matched_draws.forEach(draw => {
            const drawElement = document.createElement('div');
            drawElement.className = 'd-flex justify-content-between align-items-center mb-2 p-2 rounded'
            drawElement.style.background = 'rgba(142, 45, 226, 0.05)';

            const numbersText = Array.isArray(draw.numbers) ? draw.numbers.join('-') : 'N/A';
            const dateText = draw.date || 'N/A';

            drawElement.innerHTML = `
                <div>
                    <i class="fas fa-calendar-alt text-muted me-2"></i>
                    <span class="text-info small">${dateText}</span>
                </div>
                <span class="fw-bold text-white font-monospace">${numbersText}</span>
            `;
            twinDrawsList.appendChild(drawElement);
        });
    }

    function renderPredictions(data) {
        const watchNumbersList = document.getElementById('watch-numbers-list');
        const probableDuosList = document.getElementById('probable-duos-list');
        const attributeWeatherDisplay = document.getElementById('attribute-weather-display');
        const predictionEmpty = document.getElementById('prediction-empty');

        watchNumbersList.innerHTML = '';
        probableDuosList.innerHTML = '';
        attributeWeatherDisplay.innerHTML = '';

        if ((!data.watchNumbers || data.watchNumbers.length === 0) &&
            (!data.probableDuos || data.probableDuos.length === 0) &&
            (!data.attributeWeather || data.attributeWeather.length === 0)) {
            predictionEmpty.style.display = 'block';
            return;
        }
        predictionEmpty.style.display = 'none';

        data.watchNumbers.forEach(num => {
            const li = document.createElement('li');
            li.className = 'list-group-item bg-transparent text-white d-flex justify-content-between align-items-center';
            li.innerHTML = `Numéro ${num.number} <span class="badge bg-primary rounded-pill">${num.score}%</span>`;
            watchNumbersList.appendChild(li);
        });

        data.probableDuos.forEach(duo => {
            const li = document.createElement('li');
            li.className = 'list-group-item bg-transparent text-white';
            li.textContent = duo.join(' - ');
            probableDuosList.appendChild(li);
        });

        data.attributeWeather.forEach(message => {
            const alert = document.createElement('div');
            alert.className = 'alert alert-info small';
            alert.textContent = message;
            attributeWeatherDisplay.appendChild(alert);
        });
    }

    function renderSessionProgress(draws) {
        const sessionProgressTimeline = document.getElementById('session-progress-timeline');
        const sessionProgressEmpty = document.getElementById('session-progress-empty');
        sessionProgressTimeline.innerHTML = '';

        if (!draws || draws.length === 0) {
            sessionProgressEmpty.style.display = 'block';
            return;
        }
        sessionProgressEmpty.style.display = 'none';

        draws.forEach(draw => {
            const drawElement = document.createElement('div');
            drawElement.className = 'timeline-item mb-4';
            drawElement.innerHTML = `
                <div class="timeline-item-header">
                    <h6 class="text-white mb-0">${draw.draw_date} - Tirage n°${draw.draw_number}</h6>
                    <span class="badge bg-pattern">${draw.lottery_name}</span>
                </div>
                <div class="timeline-item-body">
                    <p class="mb-1">Numéros: <strong class="text-info">${draw.winning_numbers.join(' - ')}</strong></p>
                    ${draw.katula_analysis ? `<p class="mb-0 small text-muted">Combinaisons analysées: ${draw.katula_analysis.total_combinations}</p>` : ''}
                </div>
            `;
            sessionProgressTimeline.appendChild(drawElement);
        });
    }

    // Initial fetch for sessions
    fetchAvailableSessions();
});