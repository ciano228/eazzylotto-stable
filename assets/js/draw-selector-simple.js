/**
 * Sélecteur de tirages simple pour advanced-journal
 */

function initDrawSelector(containerId) {
    console.log('🎯 Initialisation du sélecteur de tirages simple');
    
    const container = document.getElementById(containerId);
    if (!container) {
        console.error('Container non trouvé:', containerId);
        return;
    }
    
    // Créer l'interface du sélecteur
    container.innerHTML = `
        <div class="draw-selector-simple">
            <div class="selector-header">
                <h3>🎯 Sélection de Tirages Spécifiques</h3>
                <p>Choisissez les tirages à analyser dans le journal</p>
            </div>
            
            <div class="selector-controls">
                <div class="control-group">
                    <label for="drawMode">Mode de sélection:</label>
                    <select id="drawMode" onchange="onDrawModeChange()">
                        <option value="single">Tirage unique</option>
                        <option value="multiple">Tirages multiples</option>
                        <option value="range">Plage de dates</option>
                    </select>
                </div>
                
                <div class="control-group" id="singleDrawGroup">
                    <label for="singleDrawDate">Date du tirage:</label>
                    <input type="date" id="singleDrawDate" onchange="onDrawSelectionChange()">
                </div>
                
                <div class="control-group" id="multipleDatesGroup" style="display: none;">
                    <label for="multipleDates">Dates des tirages (une par ligne):</label>
                    <textarea id="multipleDates" rows="4" placeholder="2024-01-15&#10;2024-01-22&#10;2024-01-29" onchange="onDrawSelectionChange()"></textarea>
                </div>
                
                <div class="control-group" id="dateRangeGroup" style="display: none;">
                    <label for="rangeStartDate">Date de début:</label>
                    <input type="date" id="rangeStartDate" onchange="onDrawSelectionChange()">
                    <label for="rangeEndDate">Date de fin:</label>
                    <input type="date" id="rangeEndDate" onchange="onDrawSelectionChange()">
                </div>
                
                <div class="control-group">
                    <label for="drawUniverse">Univers (optionnel):</label>
                    <select id="drawUniverse" onchange="onDrawSelectionChange()">
                        <option value="">Utiliser le filtre principal</option>
                        <option value="mundo">Mundo</option>
                        <option value="fruity">Fruity</option>
                        <option value="trigga">Trigga</option>
                        <option value="roaster">Roaster</option>
                        <option value="sunshine">Sunshine</option>
                    </select>
                </div>
            </div>
        </div>
    `;
    
    // Initialiser les dates par défaut
    const today = new Date().toISOString().split('T')[0];
    const weekAgo = new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0];
    
    document.getElementById('singleDrawDate').value = today;
    document.getElementById('rangeStartDate').value = weekAgo;
    document.getElementById('rangeEndDate').value = today;
    
    // Déclencher l'événement initial
    onDrawSelectionChange();
}

function onDrawModeChange() {
    const mode = document.getElementById('drawMode').value;
    
    // Cacher tous les groupes
    document.getElementById('singleDrawGroup').style.display = 'none';
    document.getElementById('multipleDatesGroup').style.display = 'none';
    document.getElementById('dateRangeGroup').style.display = 'none';
    
    // Afficher le groupe approprié
    switch(mode) {
        case 'single':
            document.getElementById('singleDrawGroup').style.display = 'block';
            break;
        case 'multiple':
            document.getElementById('multipleDatesGroup').style.display = 'block';
            break;
        case 'range':
            document.getElementById('dateRangeGroup').style.display = 'block';
            break;
    }
    
    // Déclencher le changement de sélection
    onDrawSelectionChange();
}

function onDrawSelectionChange() {
    const mode = document.getElementById('drawMode').value;
    const universe = document.getElementById('drawUniverse').value;
    
    let selection = { mode: mode };
    
    switch(mode) {
        case 'single':
            const singleDate = document.getElementById('singleDrawDate').value;
            if (singleDate) {
                selection.draw = singleDate;
            }
            break;
            
        case 'multiple':
            const multipleDates = document.getElementById('multipleDates').value;
            if (multipleDates.trim()) {
                selection.draws = multipleDates.split('\n')
                    .map(d => d.trim())
                    .filter(d => d && d.match(/^\d{4}-\d{2}-\d{2}$/));
            }
            break;
            
        case 'range':
            const startDate = document.getElementById('rangeStartDate').value;
            const endDate = document.getElementById('rangeEndDate').value;
            if (startDate && endDate) {
                selection.startDate = startDate;
                selection.endDate = endDate;
            }
            break;
    }
    
    if (universe) {
        selection.universe = universe;
        // Synchroniser avec le filtre principal
        const universeSelect = document.getElementById('universe');
        if (universeSelect) {
            universeSelect.value = universe;
        }
    }
    
    // Stocker la sélection globalement
    window.currentDrawSelection = selection;
    
    // Déclencher l'événement personnalisé
    const event = new CustomEvent('drawSelectionChanged', {
        detail: selection
    });
    document.dispatchEvent(event);
    
    console.log('🎯 Sélection de tirage mise à jour:', selection);
}

// Export global pour compatibilité
window.initDrawSelector = initDrawSelector;
window.onDrawModeChange = onDrawModeChange;
window.onDrawSelectionChange = onDrawSelectionChange;