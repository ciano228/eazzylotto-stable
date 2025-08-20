// Sélecteur de tirage simplifié et fonctionnel
function createDrawSelector() {
    return `
        <div class="draw-selector-container">
            <div class="selector-header">
                <h3>🎯 Sélection du Tirage</h3>
                <button class="audio-guide-btn" onclick="playGuide()">
                    🔊 Guide Audio
                </button>
            </div>
            
            <div class="selector-grid">
                <div class="selector-group">
                    <label>📅 Mode de Sélection</label>
                    <select id="selectionMode" onchange="changeMode()">
                        <option value="single">Tirage unique</option>
                        <option value="multiple">Plusieurs tirages</option>
                        <option value="range">Plage de dates</option>
                    </select>
                </div>
                
                <div class="selector-group" id="singleGroup">
                    <label>📅 Date du Tirage</label>
                    <input type="date" id="singleDraw" onchange="updateSelection()" 
                           min="2020-01-01" max="2030-12-31" value="2024-01-15">
                    <small style="color: #666; margin-top: 5px; display: block;">
                        💡 Sélectionnez la date exacte du tirage à analyser
                    </small>
                </div>
                
                <div class="selector-group" id="multipleGroup" style="display: none;">
                    <label>📅 Dates des Tirages</label>
                    <div class="multiple-dates-container">
                        <div class="date-input-row">
                            <input type="date" class="multi-date" onchange="updateSelection()" 
                                   min="2020-01-01" max="2030-12-31" value="2024-01-15">
                            <button type="button" onclick="removeDateInput(this)" class="remove-date-btn">❌</button>
                        </div>
                        <div class="date-input-row">
                            <input type="date" class="multi-date" onchange="updateSelection()" 
                                   min="2020-01-01" max="2030-12-31" value="2024-01-12">
                            <button type="button" onclick="removeDateInput(this)" class="remove-date-btn">❌</button>
                        </div>
                    </div>
                    <button type="button" onclick="addDateInput()" class="add-date-btn">➕ Ajouter une date</button>
                    <small style="color: #666; margin-top: 5px; display: block;">
                        💡 Ajoutez plusieurs dates de tirages à analyser ensemble
                    </small>
                </div>
                
                <div class="selector-group" id="rangeGroup" style="display: none;">
                    <label>📅 Date début</label>
                    <input type="date" id="startDate" onchange="updateSelection()" 
                           min="2020-01-01" max="2030-12-31">
                    <label>📅 Date fin</label>
                    <input type="date" id="endDate" onchange="updateSelection()" 
                           min="2020-01-01" max="2030-12-31">
                </div>
                
                <div class="selector-group">
                    <label>🌍 Univers</label>
                    <select id="universe" onchange="updateSelection()">
                        <option value="mundo">Mundo (par défaut)</option>
                        <option value="fruity">Fruity</option>
                        <option value="trigga">Trigga</option>
                        <option value="roaster">Roaster</option>
                        <option value="sunshine">Sunshine</option>
                    </select>
                </div>
            </div>
            
            <div class="current-selection">
                <div class="selection-info">
                    <span class="info-label">Analyse en cours :</span>
                    <span class="info-value" id="currentAnalysis">
                        Tirage du 15/01/2024 • Univers Mundo
                    </span>
                </div>
                <button class="apply-btn" onclick="applySelection()">
                    ✅ Appliquer l'analyse
                </button>
            </div>
        </div>
    `;
}

function changeMode() {
    const mode = document.getElementById('selectionMode').value;
    
    // Masquer tous les groupes
    document.getElementById('singleGroup').style.display = 'none';
    document.getElementById('multipleGroup').style.display = 'none';
    document.getElementById('rangeGroup').style.display = 'none';
    
    // Afficher le groupe approprié
    switch(mode) {
        case 'single':
            document.getElementById('singleGroup').style.display = 'block';
            break;
        case 'multiple':
            document.getElementById('multipleGroup').style.display = 'block';
            break;
        case 'range':
            document.getElementById('rangeGroup').style.display = 'block';
            break;
    }
    
    updateSelection();
    playModeAudio(mode);
}

function updateSelection() {
    const mode = document.getElementById('selectionMode').value;
    const universe = document.getElementById('universe').value;
    let analysisText = '';
    
    switch(mode) {
        case 'single':
            const singleDraw = document.getElementById('singleDraw').value;
            if (singleDraw) {
                const formattedDate = formatDateDisplay(singleDraw);
                analysisText = `Tirage du ${formattedDate} • Univers ${universe.charAt(0).toUpperCase() + universe.slice(1)}`;
            } else {
                analysisText = `Aucune date sélectionnée • Univers ${universe.charAt(0).toUpperCase() + universe.slice(1)}`;
            }
            break;
        case 'multiple':
            const multiDates = document.querySelectorAll('.multi-date');
            const validDates = Array.from(multiDates).filter(input => input.value).map(input => input.value);
            const count = validDates.length;
            analysisText = `${count} tirage${count > 1 ? 's' : ''} sélectionné${count > 1 ? 's' : ''} • Univers ${universe.charAt(0).toUpperCase() + universe.slice(1)}`;
            break;
        case 'range':
            const startDate = document.getElementById('startDate').value;
            const endDate = document.getElementById('endDate').value;
            if (startDate && endDate) {
                const formattedStart = formatDateDisplay(startDate);
                const formattedEnd = formatDateDisplay(endDate);
                analysisText = `Du ${formattedStart} au ${formattedEnd} • Univers ${universe.charAt(0).toUpperCase() + universe.slice(1)}`;
            } else {
                analysisText = `Plage de dates non définie • Univers ${universe.charAt(0).toUpperCase() + universe.slice(1)}`;
            }
            break;
    }
    
    document.getElementById('currentAnalysis').textContent = analysisText;
}

function formatDateDisplay(dateString) {
    if (!dateString) return '';
    const date = new Date(dateString);
    return date.toLocaleDateString('fr-FR');
}

function addDateInput() {
    const container = document.querySelector('.multiple-dates-container');
    const newRow = document.createElement('div');
    newRow.className = 'date-input-row';
    newRow.innerHTML = `
        <input type="date" class="multi-date" onchange="updateSelection()" 
               min="2020-01-01" max="2030-12-31">
        <button type="button" onclick="removeDateInput(this)" class="remove-date-btn">❌</button>
    `;
    container.appendChild(newRow);
}

function removeDateInput(button) {
    const container = document.querySelector('.multiple-dates-container');
    if (container.children.length > 1) {
        button.parentElement.remove();
        updateSelection();
    }
}

function applySelection() {
    const mode = document.getElementById('selectionMode').value;
    const universe = document.getElementById('universe').value;
    
    let selectionData = {
        mode: mode,
        universe: universe
    };
    
    switch(mode) {
        case 'single':
            const singleDate = document.getElementById('singleDraw').value;
            if (!singleDate) {
                showNotification('❌ Veuillez sélectionner une date de tirage', 'error');
                return;
            }
            
            // Valider la date par rapport à la session
            const validation = validateDateInSession(singleDate);
            if (!validation.valid) {
                showNotification(validation.message, 'error');
                return;
            }
            
            selectionData.draw = singleDate;
            break;
        case 'multiple':
            const multiDates = document.querySelectorAll('.multi-date');
            const validDates = Array.from(multiDates).filter(input => input.value).map(input => input.value);
            if (validDates.length === 0) {
                showNotification('❌ Veuillez sélectionner au moins une date de tirage', 'error');
                return;
            }
            
            // Valider toutes les dates
            for (let date of validDates) {
                const validation = validateDateInSession(date);
                if (!validation.valid) {
                    showNotification(validation.message, 'error');
                    return;
                }
            }
            
            selectionData.draws = validDates;
            break;
        case 'range':
            const startDate = document.getElementById('startDate').value;
            const endDate = document.getElementById('endDate').value;
            if (!startDate || !endDate) {
                showNotification('❌ Veuillez définir une plage de dates complète', 'error');
                return;
            }
            if (new Date(startDate) > new Date(endDate)) {
                showNotification('❌ La date de début doit être antérieure à la date de fin', 'error');
                return;
            }
            
            // Valider la plage par rapport à la session
            const startValidation = validateDateInSession(startDate);
            const endValidation = validateDateInSession(endDate);
            if (!startValidation.valid) {
                showNotification('Date de début: ' + startValidation.message, 'error');
                return;
            }
            if (!endValidation.valid) {
                showNotification('Date de fin: ' + endValidation.message, 'error');
                return;
            }
            
            selectionData.startDate = startDate;
            selectionData.endDate = endDate;
            break;
    }
    
    // Émettre l'événement
    const event = new CustomEvent('drawSelectionChanged', {
        detail: selectionData
    });
    document.dispatchEvent(event);
    
    // Notification
    showNotification('✅ Analyse mise à jour avec succès !');
    
    // Audio de confirmation
    playConfirmationAudio();
}

function playGuide() {
    const message = `Bienvenue dans le sélecteur de tirage KATOOLING. 
                    Vous pouvez choisir entre tirage unique, plusieurs tirages, ou une plage de dates. 
                    L'univers Mundo est recommandé pour les débutants.`;
    speak(message);
}

function playModeAudio(mode) {
    const messages = {
        'single': 'Mode tirage unique sélectionné. Analysez un tirage spécifique.',
        'multiple': 'Mode tirages multiples sélectionné. Maintenez Ctrl pour sélectionner plusieurs tirages.',
        'range': 'Mode plage de dates sélectionné. Définissez une période d\'analyse.'
    };
    speak(messages[mode]);
}

function playConfirmationAudio() {
    speak('Analyse appliquée avec succès.');
}

function speak(text) {
    if ('speechSynthesis' in window) {
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.lang = 'fr-FR';
        utterance.rate = 0.9;
        speechSynthesis.speak(utterance);
    }
}

function showNotification(message) {
    const notification = document.createElement('div');
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: linear-gradient(135deg, #2ed573, #26d0ce);
        color: white;
        padding: 15px 25px;
        border-radius: 8px;
        font-weight: 600;
        z-index: 10000;
        animation: slideIn 0.3s ease;
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.remove();
    }, 3000);
}

// Fonction de validation globale
function validateDateInSession(selectedDate) {
    if (typeof window !== 'undefined' && window.validateDateInSession) {
        return window.validateDateInSession(selectedDate);
    }
    return { valid: true, message: '' };
}

// Initialisation
function initDrawSelector(containerId) {
    const container = document.getElementById(containerId);
    if (container) {
        container.innerHTML = createDrawSelector();
        updateSelection();
    }
}