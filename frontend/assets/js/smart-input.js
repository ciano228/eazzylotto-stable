// Configuration
const API_BASE = 'http://localhost:8000/api';
let currentSession = null;
let currentDrawData = null;
let editMode = false;

// Initialisation
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 DOM chargé, initialisation...');
    initializeApp();
});

async function initializeApp() {
    // Initialisation des event listeners
    document.getElementById('refreshButton')?.addEventListener('click', loadSessions);
    document.getElementById('newSessionButton')?.addEventListener('click', showCreateSessionModal);
    document.getElementById('saveButton')?.addEventListener('click', saveResult);
    document.getElementById('randomButton')?.addEventListener('click', generateRandomNumbers);
    document.getElementById('noDrawButton')?.addEventListener('click', saveNoDrawResult);
    document.getElementById('clearButton')?.addEventListener('click', clearInputs);
    document.getElementById('planningButton')?.addEventListener('click', showScheduleOverview);
    document.getElementById('refreshHistoryButton')?.addEventListener('click', refreshHistory);
    document.getElementById('cancelSessionButton')?.addEventListener('click', closeSessionModal);
    document.getElementById('createSessionButton')?.addEventListener('click', createSessionFromModal);

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

    select.addEventListener('change', function() {
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
