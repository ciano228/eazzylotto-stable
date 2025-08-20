// Sélecteur de tirage avec guide audio
class DrawSelector {
    constructor() {
        this.currentDraw = null;
        this.currentPeriod = null;
        this.currentUniverse = 'mundo';
        this.audioEnabled = true;
        this.init();
    }

    init() {
        this.loadDefaultDraw();
    }

    createSelector() {
        const selectorHTML = `
            <div class="draw-selector-container">
                <div class="selector-header">
                    <h3>🎯 Sélection du Tirage</h3>
                    <button class="audio-guide-btn">
                        🔊 Guide Audio
                    </button>
                </div>
                
                <div class="selector-grid">
                    <div class="selector-group">
                        <label>📅 Mode de Sélection</label>
                        <select id="selectionMode">
                            <option value="single">Tirage unique</option>
                            <option value="multiple">Plusieurs tirages</option>
                            <option value="range">Plage de dates</option>
                            <option value="period">Par période</option>
                        </select>
                    </div>
                    
                    <div class="selector-group" id="singleDrawGroup">
                        <label>📅 Tirage</label>
                        <select id="drawSelect">
                            <option value="latest">Dernier tirage (15/01/2024)</option>
                            <option value="2024-01-12">Tirage du 12/01/2024</option>
                            <option value="2024-01-10">Tirage du 10/01/2024</option>
                            <option value="2024-01-08">Tirage du 08/01/2024</option>
                        </select>
                    </div>
                    
                    <div class="selector-group" id="multipleDrawGroup" style="display: none;">
                        <label>📅 Tirages (maintenir Ctrl pour sélection multiple)</label>
                        <select id="multiDrawSelect" multiple size="4">
                            <option value="2024-01-15">15/01/2024 - [7,12,23,34,41]</option>
                            <option value="2024-01-12">12/01/2024 - [3,18,25,39,47]</option>
                            <option value="2024-01-10">10/01/2024 - [9,16,28,35,44]</option>
                            <option value="2024-01-08">08/01/2024 - [2,14,21,33,46]</option>
                            <option value="2024-01-05">05/01/2024 - [11,19,27,38,42]</option>
                        </select>
                    </div>
                    
                    <div class="selector-group" id="dateRangeGroup" style="display: none;">
                        <label>📅 Date début</label>
                        <input type="date" id="startDateRange">
                        <label>📅 Date fin</label>
                        <input type="date" id="endDateRange">
                    </div>
                    
                    <div class="selector-group">
                        <label>🌍 Univers</label>
                        <select id="universeSelect">
                            <option value="mundo">Mundo (par défaut)</option>
                            <option value="fruity">Fruity</option>
                            <option value="trigga">Trigga</option>
                            <option value="roaster">Roaster</option>
                            <option value="sunshine">Sunshine</option>
                        </select>
                    </div>
                    
                    <div class="selector-group">
                        <label>📊 Période</label>
                        <select id="periodSelect">
                            <option value="6">6 derniers tirages</option>
                            <option value="12">12 derniers tirages</option>
                            <option value="24">24 derniers tirages</option>
                            <option value="custom">Période personnalisée</option>
                        </select>
                    </div>
                </div>
                
                <div class="current-selection">
                    <div class="selection-info">
                        <span class="info-label">Analyse en cours :</span>
                        <span class="info-value" id="currentAnalysis">
                            Dernier tirage • Univers Mundo • 6 périodes
                        </span>
                    </div>
                    <button class="apply-btn" id="applyBtn">
                        ✅ Appliquer l'analyse
                    </button>
                </div>
            </div>
        `;
        
        return selectorHTML;
    }

    onModeChange() {
        const mode = document.getElementById('selectionMode').value;
        this.currentMode = mode;
        
        // Masquer tous les groupes
        document.getElementById('singleDrawGroup').style.display = 'none';
        document.getElementById('multipleDrawGroup').style.display = 'none';
        document.getElementById('dateRangeGroup').style.display = 'none';
        
        // Afficher le groupe approprié
        switch(mode) {
            case 'single':
                document.getElementById('singleDrawGroup').style.display = 'block';
                break;
            case 'multiple':
                document.getElementById('multipleDrawGroup').style.display = 'block';
                break;
            case 'range':
                document.getElementById('dateRangeGroup').style.display = 'block';
                break;
            case 'period':
                // Utiliser les contrôles de période existants
                break;
        }
        
        this.updateCurrentAnalysis();
        this.playModeGuide();
    }
    
    onDrawChange() {
        const drawSelect = document.getElementById('drawSelect');
        this.currentDraw = drawSelect.value;
        this.selectedDraws = [drawSelect.value];
        this.updateCurrentAnalysis();
        this.playSelectionFeedback();
    }
    
    onMultiDrawChange() {
        const multiSelect = document.getElementById('multiDrawSelect');
        this.selectedDraws = Array.from(multiSelect.selectedOptions).map(option => option.value);
        this.updateCurrentAnalysis();
        this.playMultiSelectionFeedback();
    }
    
    onDateRangeChange() {
        const startDate = document.getElementById('startDateRange').value;
        const endDate = document.getElementById('endDateRange').value;
        
        if (startDate && endDate) {
            this.dateRange = { start: startDate, end: endDate };
            this.updateCurrentAnalysis();
            this.playDateRangeFeedback();
        }
    }

    onUniverseChange() {
        const universeSelect = document.getElementById('universeSelect');
        this.currentUniverse = universeSelect.value;
        this.updateCurrentAnalysis();
        this.playUniverseGuide();
    }

    onPeriodChange() {
        const periodSelect = document.getElementById('periodSelect');
        this.currentPeriod = periodSelect.value;
        this.updateCurrentAnalysis();
    }

    updateCurrentAnalysis() {
        const analysisElement = document.getElementById('currentAnalysis');
        if (analysisElement) {
            const drawText = this.getDrawText();
            const universeText = this.getUniverseText();
            const periodText = this.getPeriodText();
            
            analysisElement.textContent = `${drawText} • ${universeText} • ${periodText}`;
        }
    }

    getDrawText() {
        switch(this.currentMode) {
            case 'single':
                if (this.currentDraw === 'latest') return 'Dernier tirage';
                return `Tirage du ${this.currentDraw}`;
            case 'multiple':
                if (!this.selectedDraws || this.selectedDraws.length === 0) return 'Aucun tirage sélectionné';
                return `${this.selectedDraws.length} tirages sélectionnés`;
            case 'range':
                if (!this.dateRange) return 'Plage de dates non définie';
                return `Du ${this.dateRange.start} au ${this.dateRange.end}`;
            case 'period':
                return `Analyse par période`;
            default:
                return 'Sélection non définie';
        }
    }

    getUniverseText() {
        const universes = {
            'mundo': 'Univers Mundo',
            'fruity': 'Univers Fruity',
            'trigga': 'Univers Trigga',
            'roaster': 'Univers Roaster',
            'sunshine': 'Univers Sunshine'
        };
        return universes[this.currentUniverse] || 'Univers Mundo';
    }

    getPeriodText() {
        if (this.currentPeriod === 'custom') return 'Période personnalisée';
        return `${this.currentPeriod} périodes`;
    }

    loadDefaultDraw() {
        this.currentMode = 'single';
        this.currentDraw = 'latest';
        this.selectedDraws = ['latest'];
        this.currentUniverse = 'mundo';
        this.currentPeriod = '6';
        this.dateRange = null;
        
        // Mettre à jour les valeurs dans l'interface après un délai
        setTimeout(() => {
            const modeSelect = document.getElementById('selectionMode');
            const universeSelect = document.getElementById('universeSelect');
            const periodSelect = document.getElementById('periodSelect');
            
            if (modeSelect) modeSelect.value = this.currentMode;
            if (universeSelect) universeSelect.value = this.currentUniverse;
            if (periodSelect) periodSelect.value = this.currentPeriod;
            
            this.updateCurrentAnalysis();
        }, 100);
    }

    applySelection() {
        // Valider la sélection
        if (!this.validateSelection()) {
            this.showNotification('❌ Sélection invalide. Veuillez vérifier vos paramètres.', 'error');
            return;
        }
        
        // Déclencher l'analyse avec les paramètres sélectionnés
        this.playConfirmationAudio();
        
        // Préparer les données selon le mode
        const selectionData = this.prepareSelectionData();
        
        // Émettre un événement pour notifier les autres composants
        const event = new CustomEvent('drawSelectionChanged', {
            detail: selectionData
        });
        document.dispatchEvent(event);
        
        // Afficher une notification
        this.showNotification('✅ Analyse mise à jour avec succès !');
    }
    
    validateSelection() {
        switch(this.currentMode) {
            case 'single':
                return this.currentDraw !== null;
            case 'multiple':
                return this.selectedDraws && this.selectedDraws.length > 0;
            case 'range':
                return this.dateRange && this.dateRange.start && this.dateRange.end;
            case 'period':
                return this.currentPeriod !== null;
            default:
                return false;
        }
    }
    
    prepareSelectionData() {
        const baseData = {
            mode: this.currentMode,
            universe: this.currentUniverse,
            period: this.currentPeriod
        };
        
        switch(this.currentMode) {
            case 'single':
                return { ...baseData, draw: this.currentDraw };
            case 'multiple':
                return { ...baseData, draws: this.selectedDraws };
            case 'range':
                return { ...baseData, dateRange: this.dateRange };
            case 'period':
                return { ...baseData, periodAnalysis: true };
            default:
                return baseData;
        }
    }

    // Guides audio
    playGuide() {
        if (!this.audioEnabled) return;
        
        const message = `Bienvenue dans le sélecteur de tirage KATOOLING. 
                        Vous pouvez choisir le tirage à analyser, l'univers d'analyse, et la période. 
                        Par défaut, nous analysons le dernier tirage dans l'univers Mundo sur 6 périodes. 
                        L'univers Mundo est recommandé pour les débutants car il offre une analyse équilibrée.`;
        
        this.speak(message);
    }

    playUniverseGuide() {
        if (!this.audioEnabled) return;
        
        const universeGuides = {
            'mundo': 'Univers Mundo sélectionné. Cet univers offre une analyse équilibrée, idéal pour débuter.',
            'fruity': 'Univers Fruity sélectionné. Spécialisé dans les patterns de fréquence.',
            'trigga': 'Univers Trigga sélectionné. Analyse les déclencheurs et signaux.',
            'roaster': 'Univers Roaster sélectionné. Focus sur les combinaisons chaudes.',
            'sunshine': 'Univers Sunshine sélectionné. Optimisé pour les séquences lumineuses.'
        };
        
        this.speak(universeGuides[this.currentUniverse]);
    }

    playSelectionFeedback() {
        if (!this.audioEnabled) return;
        
        const message = `Tirage sélectionné. Prêt pour l'analyse.`;
        this.speak(message);
    }

    playModeGuide() {
        if (!this.audioEnabled) return;
        
        const modeGuides = {
            'single': 'Mode tirage unique sélectionné. Analysez un tirage spécifique.',
            'multiple': 'Mode tirages multiples sélectionné. Maintenez Ctrl pour sélectionner plusieurs tirages.',
            'range': 'Mode plage de dates sélectionné. Définissez une période d\'analyse.',
            'period': 'Mode analyse par période sélectionné. Utilisez les contrôles de période.'
        };
        
        this.speak(modeGuides[this.currentMode]);
    }
    
    playMultiSelectionFeedback() {
        if (!this.audioEnabled) return;
        
        const count = this.selectedDraws ? this.selectedDraws.length : 0;
        const message = `${count} tirage${count > 1 ? 's' : ''} sélectionné${count > 1 ? 's' : ''}.`;
        this.speak(message);
    }
    
    playDateRangeFeedback() {
        if (!this.audioEnabled) return;
        
        const message = `Plage de dates définie du ${this.dateRange.start} au ${this.dateRange.end}.`;
        this.speak(message);
    }
    
    playConfirmationAudio() {
        if (!this.audioEnabled) return;
        
        const message = `Analyse appliquée. Le journal statistique est maintenant généré pour ${this.getDrawText()}, ${this.getUniverseText()}, sur ${this.getPeriodText()}.`;
        this.speak(message);
    }

    speak(text) {
        if ('speechSynthesis' in window) {
            const utterance = new SpeechSynthesisUtterance(text);
            utterance.lang = 'fr-FR';
            utterance.rate = 0.9;
            utterance.pitch = 1;
            speechSynthesis.speak(utterance);
        }
    }

    showNotification(message, type = 'success') {
        const notification = document.createElement('div');
        notification.className = 'draw-notification';
        notification.textContent = message;
        
        const colors = {
            success: 'linear-gradient(135deg, #2ed573, #26d0ce)',
            error: 'linear-gradient(135deg, #ff4757, #ff3742)',
            warning: 'linear-gradient(135deg, #ffa502, #ff6348)'
        };
        
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: ${colors[type]};
            color: white;
            padding: 15px 25px;
            border-radius: 8px;
            font-weight: 600;
            z-index: 10000;
            animation: slideIn 0.3s ease;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.remove();
        }, 3000);
    }

    // Méthode pour injecter le sélecteur dans une page
    injectSelector(containerId) {
        const container = document.getElementById(containerId);
        if (container) {
            container.innerHTML = this.createSelector();
            this.loadDefaultDraw();
            this.attachEventListeners();
        }
    }
    
    attachEventListeners() {
        // Mode de sélection
        const modeSelect = document.getElementById('selectionMode');
        if (modeSelect) {
            modeSelect.addEventListener('change', () => this.onModeChange());
        }
        
        // Tirage unique
        const drawSelect = document.getElementById('drawSelect');
        if (drawSelect) {
            drawSelect.addEventListener('change', () => this.onDrawChange());
        }
        
        // Tirages multiples
        const multiDrawSelect = document.getElementById('multiDrawSelect');
        if (multiDrawSelect) {
            multiDrawSelect.addEventListener('change', () => this.onMultiDrawChange());
        }
        
        // Plage de dates
        const startDateRange = document.getElementById('startDateRange');
        const endDateRange = document.getElementById('endDateRange');
        if (startDateRange) {
            startDateRange.addEventListener('change', () => this.onDateRangeChange());
        }
        if (endDateRange) {
            endDateRange.addEventListener('change', () => this.onDateRangeChange());
        }
        
        // Univers
        const universeSelect = document.getElementById('universeSelect');
        if (universeSelect) {
            universeSelect.addEventListener('change', () => this.onUniverseChange());
        }
        
        // Période
        const periodSelect = document.getElementById('periodSelect');
        if (periodSelect) {
            periodSelect.addEventListener('change', () => this.onPeriodChange());
        }
        
        // Bouton appliquer
        const applyBtn = document.getElementById('applyBtn');
        if (applyBtn) {
            applyBtn.addEventListener('click', () => this.applySelection());
        }
        
        // Guide audio
        const audioBtn = document.querySelector('.audio-guide-btn');
        if (audioBtn) {
            audioBtn.addEventListener('click', () => this.playGuide());
        }
    }
}

// Instance globale
const drawSelector = new DrawSelector();