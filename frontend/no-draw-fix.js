// Correction pour le mode "No Draw"
// Ajoutez ce script à la fin de votre fichier HTML

// Gestion du mode "No Draw" - Version corrigée
function toggleNoDrawMode() {
    const checkbox = document.getElementById('noDrawCheckbox');
    const numbersGrid = document.getElementById('numbersGrid');
    const saveBtn = document.getElementById('saveBtn');
    const nextBtn = document.getElementById('nextBtn');
    
    console.log('Toggle No Draw Mode:', checkbox ? checkbox.checked : 'checkbox not found');
    
    if (checkbox && checkbox.checked) {
        console.log('Activating No Draw mode');
        
        // Griser et désactiver la grille de numéros
        if (numbersGrid) {
            numbersGrid.style.opacity = '0.3';
            numbersGrid.style.pointerEvents = 'none';
            numbersGrid.style.filter = 'grayscale(100%)';
        }
        
        // Désactiver et vider tous les champs de saisie
        if (currentSession && currentSession.numbers_per_draw) {
            for (let i = 1; i <= currentSession.numbers_per_draw; i++) {
                const input = document.getElementById(`num${i}`);
                if (input) {
                    input.disabled = true;
                    input.value = '';
                    input.classList.remove('filled', 'error');
                    input.style.backgroundColor = '#f5f5f5';
                    input.style.cursor = 'not-allowed';
                    input.style.color = '#999';
                }
            }
        }
        
        // Activer immédiatement les boutons
        if (saveBtn) {
            saveBtn.disabled = false;
            saveBtn.textContent = '💾 Sauvegarder (No Draw)';
            saveBtn.style.backgroundColor = '#fa8c16';
            saveBtn.style.borderColor = '#fa8c16';
        }
        if (nextBtn) {
            nextBtn.disabled = false;
            nextBtn.textContent = '➡️ Suivant (No Draw)';
        }
        
        // Afficher un message d'information
        showMessage('Mode "No Draw" activé - Les champs de saisie sont désactivés', 'success');
        
    } else {
        console.log('Deactivating No Draw mode');
        
        // Restaurer la grille de numéros
        if (numbersGrid) {
            numbersGrid.style.opacity = '1';
            numbersGrid.style.pointerEvents = 'auto';
            numbersGrid.style.filter = 'none';
        }
        
        // Réactiver tous les champs de saisie
        if (currentSession && currentSession.numbers_per_draw) {
            for (let i = 1; i <= currentSession.numbers_per_draw; i++) {
                const input = document.getElementById(`num${i}`);
                if (input) {
                    input.disabled = false;
                    input.style.backgroundColor = '';
                    input.style.cursor = '';
                    input.style.color = '';
                }
            }
        }
        
        // Restaurer les boutons
        if (saveBtn) {
            saveBtn.textContent = '💾 Sauvegarder';
            saveBtn.style.backgroundColor = '#52c41a';
            saveBtn.style.borderColor = '#52c41a';
        }
        if (nextBtn) {
            nextBtn.textContent = '➡️ Tirage Suivant';
        }
        
        // Mettre à jour l'état des boutons selon les numéros saisis
        updateButtonStates();
    }
}

// Fonction updateButtonStates corrigée
function updateButtonStates() {
    const checkbox = document.getElementById('noDrawCheckbox');
    const saveBtn = document.getElementById('saveBtn');
    const nextBtn = document.getElementById('nextBtn');
    
    if (checkbox && checkbox.checked) {
        // Mode "No Draw" - boutons toujours activés
        if (saveBtn) saveBtn.disabled = false;
        if (nextBtn) nextBtn.disabled = false;
        return;
    }
    
    // Mode normal - vérifier les numéros
    if (!currentSession || !currentSession.numbers_per_draw) {
        if (saveBtn) saveBtn.disabled = true;
        if (nextBtn) nextBtn.disabled = true;
        return;
    }
    
    const numbers = getCurrentNumbers();
    const isComplete = numbers.length === currentSession.numbers_per_draw && 
                      numbers.every(n => n !== null && n !== undefined);
    
    if (saveBtn) saveBtn.disabled = !isComplete;
    if (nextBtn) nextBtn.disabled = !isComplete;
}

// Fonction getCurrentNumbers corrigée
function getCurrentNumbers() {
    if (!currentSession || !currentSession.numbers_per_draw) {
        return [];
    }
    
    const numbers = [];
    for (let i = 1; i <= currentSession.numbers_per_draw; i++) {
        const input = document.getElementById(`num${i}`);
        if (input && input.value) {
            const value = parseInt(input.value);
            if (!isNaN(value)) {
                numbers.push(value);
            }
        }
    }
    return numbers;
}

// Fonction saveCurrentDraw corrigée
async function saveCurrentDraw() {
    const checkbox = document.getElementById('noDrawCheckbox');
    const isNoDrawMode = checkbox && checkbox.checked;
    
    console.log('Saving draw, No Draw mode:', isNoDrawMode);
    
    if (isNoDrawMode) {
        // Sauvegarder comme "No Draw"
        try {
            const response = await fetch(
                `${API_BASE}/session/sessions/${currentSession.id}/draws/${currentDrawData.draw_number}`,
                {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        numbers: [], // Pas de numéros pour "No Draw"
                        draw_date: currentDrawData.draw_date,
                        is_no_draw: true
                    })
                }
            );
            
            const result = await response.json();
            
            if (response.ok) {
                showMessage('✅ No Draw sauvegardé avec succès!', 'success');
                await loadActiveSession();
                await loadResultsHistory(); // Si cette fonction existe
            } else {
                showMessage('Erreur lors de la sauvegarde: ' + result.detail, 'error');
            }
            
        } catch (error) {
            showMessage('Erreur de connexion: ' + error.message, 'error');
        }
    } else {
        // Sauvegarder normalement
        const numbers = getCurrentNumbers();
        
        if (numbers.length !== currentSession.numbers_per_draw) {
            showMessage('Veuillez remplir tous les numéros', 'error');
            return;
        }

        try {
            const response = await fetch(
                `${API_BASE}/session/sessions/${currentSession.id}/draws/${currentDrawData.draw_number}`,
                {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        numbers: numbers,
                        draw_date: currentDrawData.draw_date
                    })
                }
            );
            
            const result = await response.json();
            
            if (response.ok) {
                showMessage('✅ Tirage sauvegardé avec succès!', 'success');
                await loadActiveSession();
                await loadResultsHistory(); // Si cette fonction existe
            } else {
                showMessage('Erreur lors de la sauvegarde: ' + result.detail, 'error');
            }
            
        } catch (error) {
            showMessage('Erreur de connexion: ' + error.message, 'error');
        }
    }
}

// Fonction pour réinitialiser les champs
function clearInputs() {
    // Réinitialiser la checkbox "No Draw"
    const checkbox = document.getElementById('noDrawCheckbox');
    if (checkbox) {
        checkbox.checked = false;
        toggleNoDrawMode(); // Réactiver les champs
    }
    
    if (currentSession && currentSession.numbers_per_draw) {
        for (let i = 1; i <= currentSession.numbers_per_draw; i++) {
            const input = document.getElementById(`num${i}`);
            if (input) {
                input.value = '';
                input.classList.remove('filled', 'error');
            }
        }
        
        // Focus sur le premier champ
        const firstInput = document.getElementById('num1');
        if (firstInput) {
            firstInput.focus();
        }
    }
    
    updateButtonStates();
}

console.log('No Draw fix script loaded');