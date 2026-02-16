// Configuration
const API_BASE = 'http://localhost:8000/api';
let currentSession = null;
let currentDrawData = null;
let editMode = false;

// Initialisation
document.addEventListener('DOMContentLoaded', function () {
    console.log('🚀 DOM chargé, initialisation...');
    initializeApp();
});

async function initializeApp() {
    console.log('🚀 Initialisation de l\'application...');

    // Initialisation des event listeners
    document.getElementById('refreshButton')?.addEventListener('click', loadSessions);
    document.getElementById('newSessionButton')?.addEventListener('click', showCreateSessionModal);
    document.getElementById('saveButton')?.addEventListener('click', saveResult);

    // Listeners pour les boutons principaux
    document.getElementById('activateButton')?.addEventListener('click', () => {
        const select = document.getElementById('sessionSelect');
        if (select && select.value) activateSession(select.value);
    });

    document.getElementById('nextButton')?.addEventListener('click', loadCurrentDraw);
    document.getElementById('journalButton')?.addEventListener('click', openStatisticalJournal);
    document.getElementById('historyButton')?.addEventListener('click', showResultsHistory);
    document.getElementById('closeHistoryButton')?.addEventListener('click', showResultsHistory);
    document.getElementById('closeModalButton')?.addEventListener('click', closeCreateSessionModal);

    // Listeners pour fonctionnalités supplémentaires (si présents)
    document.getElementById('randomButton')?.addEventListener('click', generateRandomNumbers);
    document.getElementById('noDrawButton')?.addEventListener('click', saveNoDrawResult);
    document.getElementById('clearButton')?.addEventListener('click', clearInputs);
    document.getElementById('planningButton')?.addEventListener('click', showScheduleOverview);
    document.getElementById('refreshHistoryButton')?.addEventListener('click', refreshHistory);

    // Chargement des données
    await Promise.all([
        loadSessions(),
        loadActiveSession()
    ]);
}

// Utilitaires
function extractLotteryRange(lotteryType) {
    const match = lotteryType.match(/(\d+)\/(\d+)/);
    return match ? { min: 1, max: parseInt(match[2]) } : { min: 1, max: 90 };
}

function showMessage(message, type = 'info') {
    const container = document.getElementById('messageContainer');
    if (!container) return;

    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}`;
    messageDiv.textContent = message;

    container.appendChild(messageDiv);

    setTimeout(() => messageDiv.remove(), 5000);
}

// Gestion des dates
function formatDrawDate(dateString, shortFormat = false) {
    try {
        let date;
        if (dateString.includes('/')) {
            const parts = dateString.split('/');
            date = new Date(parts[2], parts[1] - 1, parts[0]);
        } else {
            date = new Date(dateString);
        }

        if (isNaN(date.getTime())) throw new Error('Date invalide');

        const options = shortFormat ?
            { day: '2-digit', month: '2-digit', year: 'numeric' } :
            { weekday: 'long', day: '2-digit', month: 'long', year: 'numeric' };

        return date.toLocaleDateString('fr-FR', options);
    } catch (error) {
        console.error('Erreur de formatage de date:', error);
        return dateString;
    }
}

// Gestion des sessions
async function loadSessions() {
    try {
        const response = await fetch(`${API_BASE}/session/sessions`);
        if (!response.ok) throw new Error(`HTTP ${response.status}`);

        const sessions = await response.json();
        updateSessionList(sessions);
    } catch (error) {
        console.error('Erreur loadSessions:', error);
        showMessage('Erreur lors du chargement des sessions', 'error');
    }
}

function updateSessionList(sessions) {
    const select = document.getElementById('sessionSelect');
    if (!select) return;

    select.innerHTML = '<option value="">Sélectionner une session...</option>';

    sessions.forEach(session => {
        const option = document.createElement('option');
        option.value = session.id;
        option.textContent = `${session.name} (${session.lottery_type})`;

        if (session.is_active) {
            option.selected = true;
            currentSession = session;
            updateSessionDisplay();
            loadCurrentDraw();
        }

        select.appendChild(option);
    });

    select.addEventListener('change', function () {
        if (this.value) activateSession(this.value);
    });
}

async function loadActiveSession() {
    try {
        const response = await fetch(`${API_BASE}/session/sessions/active`);
        if (!response.ok) throw new Error('Session active non trouvée');

        const data = await response.json();
        if (data.session) {
            currentSession = data.session;
            updateSessionDisplay();
            await loadCurrentDraw();
        }
    } catch (error) {
        console.error('Erreur loadActiveSession:', error);
    }
}

async function activateSession(sessionId) {
    try {
        const response = await fetch(`${API_BASE}/session/sessions/${sessionId}/activate`, {
            method: 'POST'
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Erreur inconnue');
        }

        showMessage('Session activée avec succès', 'success');
        await loadActiveSession();
    } catch (error) {
        console.error('Erreur activateSession:', error);
        showMessage(error.message, 'error');
    }
}

// Gestion des tirages
async function loadCurrentDraw() {
    if (!currentSession) return;

    try {
        const response = await fetch(`${API_BASE}/session/sessions/${currentSession.id}/current-draw`);
        if (!response.ok) throw new Error('Erreur lors du chargement du tirage');

        const draw = await response.json();
        currentDrawData = draw;
        updateDrawDisplay();
    } catch (error) {
        console.error('Erreur loadCurrentDraw:', error);
        showMessage('Erreur lors du chargement du tirage', 'error');
    }
}

function updateDrawDisplay() {
    if (!currentDrawData) return;

    const drawNumber = document.getElementById('drawNumber');
    const drawStat = document.getElementById('currentDrawStat');

    if (drawNumber) {
        drawNumber.textContent = currentDrawData.draw_number;
    }

    if (drawStat) {
        drawStat.textContent = `${currentDrawData.draw_number}/${currentSession.total_draws}`;
    }

    generateNumberInputs();
    initializeInputListeners();
}

function generateNumberInputs() {
    const container = document.getElementById('numbersInput');
    if (!container || !currentSession) return;

    container.innerHTML = '';
    const range = extractLotteryRange(currentSession.lottery_type);

    for (let i = 1; i <= currentSession.numbers_per_draw; i++) {
        const div = document.createElement('div');
        div.style.position = 'relative';

        const input = document.createElement('input');
        input.type = 'text';
        input.id = `num${i}`;
        input.className = 'number-input';
        input.placeholder = `N°${i}`;
        input.maxLength = 2;
        input.setAttribute('data-index', i);
        input.setAttribute('data-max', range.max);
        input.setAttribute('data-min', range.min);

        div.appendChild(input);
        container.appendChild(div);
    }
}

function initializeInputListeners() {
    document.querySelectorAll('.number-input').forEach(input => {
        input.addEventListener('input', handleSmartInput);
        input.addEventListener('keydown', handleKeyNavigation);
        input.addEventListener('paste', handlePaste);
    });

    document.querySelectorAll('.edit-button').forEach(button => {
        button.addEventListener('click', () => {
            const { id, number } = button.dataset;
            if (id && number) editResult(id, number);
        });
    });

    document.querySelectorAll('.delete-button').forEach(button => {
        button.addEventListener('click', () => {
            const { id, number } = button.dataset;
            if (id && number) deleteResult(id, number);
        });
    });
}
// Gestion des entrées utilisateur
function handleSmartInput(event) {
    const input = event.target;
    const value = input.value.replace(/\D/g, '');

    if (value) {
        const num = parseInt(value);
        const max = parseInt(input.dataset.max);
        const min = parseInt(input.dataset.min);

        if (num < min || num > max) {
            input.classList.add('invalid');
            return;
        }

        input.classList.remove('invalid');
        input.value = num;

        if (value.length === 2 || num > 9) {
            const nextInput = document.querySelector(`input[data-index="${parseInt(input.dataset.index) + 1}"]`);
            if (nextInput) nextInput.focus();
        }
    }

    input.classList.remove('invalid');
}

function handleKeyNavigation(event) {
    if (event.key !== 'ArrowLeft' && event.key !== 'ArrowRight') return;

    const currentIndex = parseInt(event.target.dataset.index);
    const nextIndex = event.key === 'ArrowLeft' ? currentIndex - 1 : currentIndex + 1;
    const nextInput = document.querySelector(`input[data-index="${nextIndex}"]`);

    if (nextInput) {
        nextInput.focus();
        event.preventDefault();
    }
}

function handlePaste(event) {
    event.preventDefault();

    const paste = (event.clipboardData || window.clipboardData).getData('text');
    const numbers = paste.match(/\d+/g);

    if (!numbers) return;

    const inputs = Array.from(document.querySelectorAll('.number-input'));
    numbers.forEach((num, index) => {
        if (index < inputs.length) {
            const input = inputs[index];
            const max = parseInt(input.dataset.max);
            const min = parseInt(input.dataset.min);
            const parsedNum = parseInt(num);

            if (parsedNum >= min && parsedNum <= max) {
                input.value = parsedNum;
                input.classList.remove('invalid');
            } else {
                input.classList.add('invalid');
            }
        }
    });
}

// Gestion des résultats
async function saveResult() {
    if (!currentSession || !currentDrawData) {
        showMessage('Aucune session active', 'error');
        return;
    }

    const numbers = collectInputNumbers();
    if (!validateNumbers(numbers)) return;

    try {
        const response = await fetch(`${API_BASE}/session/sessions/${currentSession.id}/draws/${currentDrawData.draw_number}/results`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ numbers })
        });

        if (!response.ok) throw new Error('Erreur lors de la sauvegarde');

        showMessage('Résultat enregistré avec succès', 'success');
        await loadCurrentDraw();
        await loadResultsHistory();
    } catch (error) {
        console.error('Erreur saveResult:', error);
        showMessage('Erreur lors de la sauvegarde', 'error');
    }
}

function collectInputNumbers() {
    return Array.from(document.querySelectorAll('.number-input'))
        .map(input => parseInt(input.value))
        .filter(num => !isNaN(num));
}

function validateNumbers(numbers) {
    if (!currentSession) return false;

    if (numbers.length !== currentSession.numbers_per_draw) {
        showMessage(`Veuillez entrer ${currentSession.numbers_per_draw} numéros`, 'error');
        return false;
    }

    const range = extractLotteryRange(currentSession.lottery_type);
    const invalidNumbers = numbers.filter(n => n < range.min || n > range.max);

    if (invalidNumbers.length > 0) {
        showMessage(`Numéros invalides: ${invalidNumbers.join(', ')}`, 'error');
        return false;
    }

    const duplicates = numbers.filter((num, index) => numbers.indexOf(num) !== index);
    if (duplicates.length > 0) {
        showMessage('Les numéros ne peuvent pas être répétés', 'error');
        return false;
    }

    return true;
}

// Export des fonctions pour utilisation externe
window.smartInput = {
    initializeApp,
    loadSessions,
    saveResult,
    generateRandomNumbers: () => {
        // À implémenter
    },
    clearInputs: () => {
        document.querySelectorAll('.number-input').forEach(input => {
            input.value = '';
            input.classList.remove('invalid');
        });
    }
};

// --- Fonctions pour le Modal de Création (Migrées depuis smart-input.html) ---

function showCreateSessionModal() {
    const modal = document.getElementById('createSessionModal');
    if (modal) {
        modal.style.display = 'block';
        // Générer les slots par défaut si vide
        const container = document.getElementById('scheduleSlots');
        if (container && container.children.length === 0) {
            generateScheduleSlots();
        }
    }
}

function closeCreateSessionModal() {
    const modal = document.getElementById('createSessionModal');
    if (modal) {
        modal.style.display = 'none';
        // Reset form
        const form = document.getElementById('createSessionForm');
        if (form) form.reset();
        const slots = document.getElementById('scheduleSlots');
        if (slots) slots.innerHTML = ''; // Clear slots
    }
}

// Alias pour la compatibilité avec le HTML si nécessaire
window.closeSessionModal = closeCreateSessionModal;

function generateScheduleSlots() {
    const totalDrawsInput = document.getElementById('totalDraws');
    if (!totalDrawsInput) return;

    const totalDraws = parseInt(totalDrawsInput.value) || 7;
    const container = document.getElementById('scheduleSlots');
    if (!container) return;

    container.innerHTML = '';

    const days = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche'];

    for (let i = 0; i < totalDraws; i++) {
        const dayName = days[i % 7];
        const slotDiv = document.createElement('div');
        slotDiv.className = 'schedule-slot';
        slotDiv.style.cssText = 'display: flex; gap: 10px; margin-bottom: 10px; align-items: center; background: white; padding: 10px; border-radius: 6px; border: 1px solid #eee;';

        slotDiv.innerHTML = `
            <span style="font-weight: bold; color: #1890ff; min-width: 30px;">#${i + 1}</span>
            <select class="slot-day" style="padding: 8px; border: 1px solid #d9d9d9; border-radius: 4px; width: 120px;">
                ${days.map(d => `<option value="${d}" ${d === dayName ? 'selected' : ''}>${d}</option>`).join('')}
            </select>
            <input type="text" class="slot-name" placeholder="Nom du Loto (ex: Bonanza)" 
                   style="flex: 1; padding: 8px; border: 1px solid #d9d9d9; border-radius: 4px;" required>
        `;
        container.appendChild(slotDiv);
    }

    updateLotteryLimit();
}

function updateLotteryLimit() {
    const totalDrawsInput = document.getElementById('totalDraws');
    if (!totalDrawsInput) return;

    const totalDraws = parseInt(totalDrawsInput.value) || 0;
    const infoText = document.getElementById('lotteryLimitInfo');
    if (infoText) {
        infoText.textContent = `📋 Configuration pour ${totalDraws} tirages par période`;
    }
}

// --- Historique des Résultats ---

async function loadResultsHistory() {
    if (!currentSession) return;

    try {
        // Recharger les données de la session pour avoir les derniers résultats
        const response = await fetch(`${API_BASE}/session/sessions/${currentSession.id}`);
        if (!response.ok) throw new Error('Erreur chargement session');

        const data = await response.json();
        const sessionData = data.session || data;

        const completedDraws = sessionData.draws.filter(d => d.is_completed).sort((a, b) => b.draw_number - a.draw_number);

        const historySection = document.getElementById('resultsHistorySection');
        if (historySection) {
            if (completedDraws.length > 0) {
                displayResultsHistory(completedDraws);
                historySection.style.display = 'block';
            } else {
                historySection.style.display = 'none';
            }
        }
    } catch (error) {
        console.error("Erreur chargement historique:", error);
    }
}

function showResultsHistory() {
    const section = document.getElementById('resultsHistorySection');
    if (section) {
        if (section.style.display === 'none') {
            loadResultsHistory();
            section.style.display = 'block';
            // Scroll to history
            section.scrollIntoView({ behavior: 'smooth' });
        } else {
            section.style.display = 'none';
        }
    }
}

function displayResultsHistory(draws) {
    const container = document.getElementById('resultsHistory');
    if (!container) return;

    container.innerHTML = '';

    if (draws.length === 0) {
        container.innerHTML = '<p style="text-align:center; color:#999;">Aucun résultat enregistré.</p>';
        return;
    }

    draws.forEach(draw => {
        const card = document.createElement('div');
        card.className = 'result-card';
        card.style.cssText = 'background:white; padding:15px; margin-bottom:15px; border-radius:8px; border-left: 5px solid #52c41a; box-shadow: 0 2px 5px rgba(0,0,0,0.05);';

        const numbersHtml = (draw.winning_numbers && draw.winning_numbers.length > 0) 
            ? draw.winning_numbers.map(n =>
                `<span style="display:inline-block; width:30px; height:30px; line-height:30px; text-align:center; background:#f0f2f5; border-radius:50%; margin-right:5px; font-weight:bold; color:#1890ff;">${n}</span>`
              ).join('')
            : '<span style="display:inline-block; padding:5px 10px; background:#ff4d4f; color:white; border-radius:4px; font-weight:bold; font-size:0.9em;">NO-DRAW</span>';

        card.innerHTML = `
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <div>
                    <h4 style="margin:0 0 5px 0;">${draw.lottery_name} <small style="color:#999; font-weight:normal;">#${draw.draw_number}</small></h4>
                    <div style="color:#666; font-size:0.9em;">${draw.draw_date}</div>
                </div>
                <div>
                    ${numbersHtml}
                </div>
                <button class="edit-history-btn" data-draw="${draw.draw_number}" style="background:none; border:none; cursor:pointer; color:#1890ff; font-size:1.2em;" title="Modifier">✏️</button>
            </div>
        `;
        container.appendChild(card);
    });

    // Ajouter les event listeners pour les boutons d'édition
    container.querySelectorAll('.edit-history-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const drawNum = parseInt(e.currentTarget.dataset.draw);
            editResult(drawNum);
        });
    });
}

async function editResult(drawNumber) {
    if (!currentSession) return;

    // Il faut peut-être recharger la session pour être sûr d'avoir les draws à jour
    // Mais on utilise currentSession.draws pour l'instant
    // Note: currentSession.draws pourrait ne pas être à jour si on n'a pas rechargé récemment

    // Chercher dans les draws chargés
    let draw = null;
    if (currentSession.draws) {
        draw = currentSession.draws.find(d => d.draw_number === drawNumber);
    }

    if (!draw) return;

    const newNumbersStr = prompt(`Modifier les résultats pour ${draw.lottery_name} (séparés par des virgules):`, draw.winning_numbers.join(','));

    if (newNumbersStr !== null) {
        const numbersArr = newNumbersStr.split(',').map(n => parseInt(n.trim())).filter(n => !isNaN(n));

        if (numbersArr.length !== currentSession.numbers_per_draw) {
            alert(`Il faut exactement ${currentSession.numbers_per_draw} numéros.`);
            return;
        }

        try {
            // Utiliser le bon endpoint API
            await fetch(`${API_BASE}/session/sessions/${currentSession.id}/draws/${drawNumber}/results`, {
                method: 'POST', // ou PUT selon l'API, ici POST écrase souvent
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ numbers: numbersArr })
            });
            await loadActiveSession(); // Recharger tout
            showMessage('Résultat modifié', 'success');
            loadResultsHistory(); // Rafraîchir l'historique
        } catch (error) {
            console.error(error);
            showMessage('Erreur lors de la modification', 'error');
        }
    }
}

// Fonction pour ouvrir le journal statistique
function openStatisticalJournal() {
    if (!currentSession) {
        showMessage('Aucune session active. Veuillez d\'abord activer une session.', 'error');
        return;
    }

    // Rediriger vers le journal avec l'ID de session
    // Note: session_id vs id
    const id = currentSession.id || currentSession.session_id;
    const url = `advanced-journal.html?session=${id}&universe=mundo`;
    window.open(url, '_blank');
}

// Initialisation des listeners supplémentaires
document.addEventListener('DOMContentLoaded', function () {
    // Écouteur pour le changement de nombre de tirages
    document.getElementById('totalDraws')?.addEventListener('change', generateScheduleSlots);

    // Soumission du formulaire de création
    document.getElementById('createSessionForm')?.addEventListener('submit', async function (e) {
        e.preventDefault();

        const sessionName = document.getElementById('sessionName').value;
        const description = document.getElementById('sessionDescription').value;
        const lotteryType = document.getElementById('lotteryType').value;
        const numbersPerDraw = parseInt(document.getElementById('numbersPerDraw').value);
        const totalDraws = parseInt(document.getElementById('totalDraws').value);
        const numberRange = document.getElementById('numberRange').value;
        const startDate = document.getElementById('startDate').value;

        const [min, max] = numberRange.split('-').map(Number);

        // Récupérer le planning
        const schedule = [];
        const slots = document.querySelectorAll('.schedule-slot');
        slots.forEach(slot => {
            const day = slot.querySelector('.slot-day').value;
            const name = slot.querySelector('.slot-name').value;
            if (name) {
                schedule.push({ day, name });
            }
        });

        if (schedule.length !== totalDraws) {
            alert(`Veuillez définir les noms pour les ${totalDraws} tirages.`);
            return;
        }

        const sessionData = {
            name: sessionName, // API attend 'name'
            description: description,
            lottery_type: lotteryType,
            numbers_per_draw: numbersPerDraw,
            total_draws: totalDraws,
            number_range_min: min,
            number_range_max: max,
            start_date: startDate,
            schedule: schedule
        };

        try {
            const response = await fetch(`${API_BASE}/session/sessions`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(sessionData)
            });

            const result = await response.json();

            if (response.ok) {
                alert('Session créée avec succès !');
                closeCreateSessionModal();
                loadSessions(); // Recharger la liste
            } else {
                alert('Erreur: ' + (result.detail || 'Erreur inconnue'));
            }

        } catch (error) {
            console.error('Erreur:', error);
            alert('Erreur de connexion');
        }
    });

    // Fermer le modal en cliquant à l'extérieur
    window.onclick = function (event) {
        const modal = document.getElementById('createSessionModal');
        if (event.target === modal) {
            closeCreateSessionModal();
        }
    }
});
