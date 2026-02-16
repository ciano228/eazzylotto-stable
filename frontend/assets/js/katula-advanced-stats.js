// Store for the statistics data
window.advancedStatsData = null;

// Titles for the cards
const attributeTitles = {
    'denomination': 'Dénominations',
    'alpha_ranking': 'Classements Alpha',
    'granque': 'Granques',
    'petique': 'Petiques',
    'ligne': 'Lignes',
    'colonne': 'Colonnes',
    'parite': 'Parités',
    'unidos': 'Unidos',
    'region': 'Régions',
    'quartier': 'Quartiers',
    'gentile': 'Gentilés',
    'chip': 'Chips',
    'drawer': 'Drawers',
    'forme': 'Formes',
    'engine': 'Engines',
    'beastie': 'Beasties',
    'tome': 'Tomes'
};

// Shape Icons Mapping
const FORME_ICONS = {
    'carre': '■',
    'triangle': '▲',
    'cercle': '●',
    'rectangle': '▬',
    'losange': '◆',
    'etoile': '★',
    'coeur': '♥',
    'trefle': '♣',
    'pique': '♠',
    'carreau': '♦',
    'rond': '○',
    'croix': '✚'
};

function getFormeIcon(forme) {
    if (!forme) return '<span class="icon icon-carre"></span>';

    const formeStr = forme.toLowerCase();

    // Handle composite shapes (e.g., "carre-rectangle", "triangle-cercle")
    if (formeStr.includes('-')) {
        const formes = formeStr.split('-');
        let iconsHtml = '';

        formes.forEach(f => {
            const iconClass = getSingleFormeIcon(f.trim());
            iconsHtml += `<span class="icon ${iconClass}"></span>`;
        });

        return iconsHtml;
    }

    // Simple shape
    const iconClass = getSingleFormeIcon(formeStr);
    return `<span class="icon ${iconClass}"></span>`;
}

function getSingleFormeIcon(forme) {
    const formeMap = {
        // Basic Shapes (Mundo)
        'carre': 'icon-carre',
        'triangle': 'icon-triangle',
        'cercle': 'icon-cercle',
        'rectangle': 'icon-rectangle',

        // Compound Shapes for Trigga
        'triangle_inverse': 'icon-triangle-inverse',
        'losange': 'icon-losange',
        'etoile': 'icon-etoile',
        'hexagone': 'icon-hexagone',

        // Compound Shapes for Sunshine
        'soleil': 'icon-soleil',
        'lune': 'icon-lune',
        'nuage': 'icon-nuage',
        'eclair': 'icon-eclair',

        // Compound Shapes for Roaster
        'flamme': 'icon-flamme',
        'braise': 'icon-braise',
        'fumee': 'icon-fumee',
        'cendre': 'icon-cendre'
    };

    return formeMap[forme] || 'icon-carre';
}

function getEngineIcon(engine) {
    if (!engine) return '';
    const engineIcons = {
        'car': '🚗',
        'train': '🚂',
        'bus': '🚌',
        'truck': '🚚',
        'bike': '🚲',
        'motorcycle': '🏍️',
        'plane': '✈️',
        'boat': '🚤',
        'ship': '🚢',
        'rocket': '🚀',
        'helicopter': '🚁',
        'helicoptere': '🚁',
        'taxi': '🚕',
        'ambulance': '🚑',
        'fire_truck': '🚒',
        'police_car': '🚓',
        'tractor': '🚜',
        'scooter': '🛵',
        'skateboard': '🛹',
        'roller_skates': '🛼'
    };

    const icon = engineIcons[engine.toLowerCase()] || '⚙️';
    return `<span style="font-size: 1.2em; margin-right: 5px;">${icon}</span> ${engine}`;
}

function getBeastieIcon(beastie) {
    if (!beastie) return '';
    const beastieIcons = {
        'lion': '🦁',
        'tiger': '🐅',
        'cow': '🐄',
        'horse': '🐎',
        'pig': '🐷',
        'sheep': '🐑',
        'goat': '🐐',
        'dog': '🐕',
        'cat': '🐱',
        'rabbit': '🐰',
        'mouse': '🐭',
        'bear': '🐻',
        'elephant': '🐘',
        'crocodile': '🐊',
        'scorpion': '🦂'
    };

    const icon = beastieIcons[beastie.toLowerCase()] || '🐲';
    return `<span style="font-size: 1.2em; margin-right: 5px;">${icon}</span> ${beastie}`;
}

function getTomeIcon(tome) {
    if (!tome) return '';
    // Extract tome number (e.g., "tome1" -> 1)
    const tomeNumber = parseInt(tome.toString().replace(/\D/g, '')) || 1;

    const tomeIcons = {
        1: 'Ⅰ',
        2: 'Ⅱ',
        3: 'Ⅲ',
        4: 'Ⅳ',
        5: 'Ⅴ'
    };

    const icon = tomeIcons[tomeNumber] || 'Ⅰ';
    return `<span style="font-weight: bold; color: #722ed1; margin-right: 5px;">${icon}</span> Tome ${tomeNumber}`;
}

// This function should be defined in advanced-journal.html, but we copy it here for robustness.
function parseEntryDate(dateString) {
    if (!dateString) return new Date(0);
    // Handle YYYY-MM-DD from inputs
    let match = dateString.match(/^(\d{4})-(\d{2})-(\d{2})$/);
    if (match) return new Date(match[1], match[2] - 1, match[3]);
    // Handle DD/MM/YYYY from display
    match = dateString.match(/^(\d{2})\/(\d{2})\/(\d{4})$/);
    if (match) return new Date(match[3], match[2] - 1, match[1]);
    // Handle DD-MM-YYYY
    match = dateString.match(/^(\d{2})-(\d{2})-(\d{4})$/);
    if (match) return new Date(match[3], match[2] - 1, match[1]);
    // Fallback for other ISO formats
    const d = new Date(dateString);
    if (!isNaN(d.getTime())) return d;
    return new Date(0);
}


// Gestion des onglets
function switchTab(tabName) {
    // Masquer tous les contenus
    document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
    document.querySelectorAll('.tab-btn').forEach(el => el.classList.remove('active'));

    // Afficher le contenu sélectionné
    const content = document.getElementById(`tab-${tabName}`);
    if (content) content.classList.add('active');

    // Activer le bouton
    const btn = document.querySelector(`.tab-btn[onclick="switchTab('${tabName}')"]`);
    if (btn) btn.classList.add('active');

    // Charger les données si nécessaire
    if (tabName === 'stats') {
        // The sessionId is implicitly handled by checking currentJournalData
        loadAdvancedStats();
    }
}

// Chargement et calcul des statistiques avancées à partir des données du journal
async function loadAdvancedStats() {
    const container = document.getElementById('advancedStatsContainer');
    if (!container) return;

    if (!window.currentJournalData || !window.currentJournalData.journal || window.currentJournalData.journal.length === 0) {
        container.innerHTML = '<div class="empty-state"><p>Chargez d\'abord le journal pour calculer les statistiques.</p></div>';
        // Ensure dropdown is reset
        const statsAttribute = document.getElementById('statsAttribute');
        if (statsAttribute) statsAttribute.value = "";
        return;
    }

    container.innerHTML = '<div class="loading"><div class="spinner"></div><div>Calcul des statistiques...</div></div>';

    try {
        const fullJournal = window.currentJournalData.journal;
        const selectedUniverse = document.getElementById('universe').value;

        // Précharger les poids structurels pour tous les attributs
        if (window.structuralWeightsClient) {
            const attributeTypes = Object.keys(attributeTitles);
            await window.structuralWeightsClient.preloadWeights(selectedUniverse, attributeTypes);
            console.log('🔬 Poids structurels préchargés pour', selectedUniverse);
        }

        // Filter journal by the selected universe and exclude empty placeholders
        const journal = fullJournal.filter(entry =>
            entry.univers === selectedUniverse &&
            entry.winning_numbers &&
            entry.winning_numbers.length > 0
        );

        if (journal.length === 0) {
            container.innerHTML = `<div class="empty-state"><p>Aucune donnée de journal trouvée pour l'univers <strong>${selectedUniverse}</strong>.</p></div>`;
            window.advancedStatsData = null; // Clear previous stats
            return;
        }

        const stats = {};

        // 1. Get unique draws from the *filtered* journal, sorted by date (most recent first)
        const uniqueDraws = [...new Map(journal.map(entry => [entry.date, entry])).values()]
            .sort((a, b) => parseEntryDate(b.date) - parseEntryDate(a.date));

        // 2. Iterate over each attribute to calculate stats
        for (const attribute in attributeTitles) {
            const valueMap = new Map();

            // First pass: count occurrences and find last appearance date
            journal.forEach((entry) => {
                const value = entry[attribute];
                // Filter out invalid/placeholder values
                if (value !== undefined && value !== null && value !== 'N/A' && value !== 'N-D' && value !== 'N-H' && value !== '') {
                    if (!valueMap.has(value)) {
                        valueMap.set(value, {
                            value: value,
                            count: 0,
                            last_appearance_date: new Date(0),
                            periods_seen: new Set() // Track distinct PERIODS (cycle-based, not dates)
                        });
                    }
                    const statEntry = valueMap.get(value);
                    statEntry.count++;
                    if (entry.period !== undefined && entry.period !== null) {
                        statEntry.periods_seen.add(entry.period); // Track real cycle-based period
                    }
                    const entryDate = parseEntryDate(entry.date);
                    if (entryDate > statEntry.last_appearance_date) {
                        statEntry.last_appearance_date = entryDate;
                    }
                }
            });

            const totalValidEntries = journal.filter(e => e[attribute] !== undefined && e[attribute] !== null && e[attribute] !== 'N/A' && e[attribute] !== 'N-D' && e[attribute] !== 'N-H' && e[attribute] !== '').length;
            const totalUniqueDraws = uniqueDraws.length;
            // Compute totalPeriods directly from entry.period values (based on cycle_length)
            const allPeriodNumbers = new Set(journal.map(e => e.period).filter(p => p !== undefined && p !== null));
            const totalPeriods = allPeriodNumbers.size > 0 ? allPeriodNumbers.size : totalUniqueDraws;
            const processedValues = [];

            valueMap.forEach(statEntry => {
                // Find the index of the draw where this value last appeared
                const lastAppearanceDateStr = statEntry.last_appearance_date.toISOString().split('T')[0];
                const dueIndex = uniqueDraws.findIndex(draw => parseEntryDate(draw.date).toISOString().split('T')[0] === lastAppearanceDateStr);

                const periodsPresent = statEntry.periods_seen.size;
                const due = dueIndex !== -1 ? dueIndex : uniqueDraws.length;
                // Proportional Gap Score: accounts for attribute density
                const expectedGap = statEntry.count > 0 ? (totalUniqueDraws / statEntry.count) : totalUniqueDraws;
                const gapScore = expectedGap > 0 ? parseFloat((due / expectedGap).toFixed(2)) : 0;

                // Récupérer les poids structurels si disponibles
                let structuralData = null;
                if (window.structuralWeightsClient) {
                    const cached = window.structuralWeightsClient.cache.get(`${selectedUniverse}_${attribute}_${statEntry.value}`);
                    if (cached) structuralData = cached.data;
                }

                processedValues.push({
                    value: statEntry.value,
                    count: statEntry.count,
                    frequency: totalValidEntries > 0 ? Math.round((statEntry.count / totalValidEntries) * 100) : 0,
                    last_appearance: lastAppearanceDateStr,
                    due: due,
                    expectedGap: parseFloat(expectedGap.toFixed(1)),
                    gapScore: gapScore,
                    // Occurrence metrics
                    totalDraws: totalUniqueDraws,
                    periodsPresent: periodsPresent,
                    totalPeriods: totalPeriods,
                    drawRatio: totalUniqueDraws > 0 ? Math.round((statEntry.count / totalUniqueDraws) * 100) : 0,
                    periodRatio: totalPeriods > 0 ? Math.round((periodsPresent / totalPeriods) * 100) : 0,
                    // Poids structurels
                    structural: structuralData
                });
            });

            stats[attribute] = processedValues;
        }

        window.advancedStatsData = stats;

        // Calculate Trend Performance for the current attribute selection
        const selectedAttributeForTrend = document.getElementById('statsAttribute').value;
        if (selectedAttributeForTrend) {
            window.trendPerformance = calculateTrendPerformance(journal, selectedAttributeForTrend);
        }

        console.log(`📊 Advanced stats calculated for universe ${selectedUniverse}:`, stats);
        renderAttributeStats(); // Render the currently selected attribute

    } catch (error) {
        window.advancedStatsData = null;
        console.error('Erreur calcul stats avancées:', error);
        container.innerHTML = `<div class="error">Erreur lors du calcul des statistiques: ${error.message}</div>`;
    }
}

/**
 * Calcule la performance historique de la tendance (Backtesting)
 */
function calculateTrendPerformance(journal, attribute) {
    if (!journal || journal.length < 5) return null;

    // Trier chronologiquement pour le backtesting (plus ancien au plus récent)
    const chronoJournal = [...journal].sort((a, b) => parseEntryDate(a.date) - parseEntryDate(b.date));

    // Grouper par date unique
    const uniqueDraws = [];
    const drawsByDate = new Map();

    chronoJournal.forEach(entry => {
        if (!drawsByDate.has(entry.date)) {
            drawsByDate.set(entry.date, []);
            uniqueDraws.push(entry.date);
        }
        drawsByDate.get(entry.date).push(entry[attribute]);
    });

    uniqueDraws.forEach(d => console.log(`📅 Draw Date: ${d}, Values:`, drawsByDate.get(d)));

    if (uniqueDraws.length < 5) {
        console.warn(`⚠️ Pas assez de tirages uniques (${uniqueDraws.length}) pour la tendance.`);
        return null;
    }

    let hitsX1 = 0; // Apparition à X+1
    let hitsX23 = 0; // Apparition à X+2 ou X+3
    let totalTests = 0;

    // On s'arrête 3 tirages avant la fin pour pouvoir vérifier X+1, X+2, X+3
    // On s'arrête 3 tirages avant la fin pour pouvoir vérifier X+1, X+2, X+3
    // On commence après au moins 3 tirages pour avoir un minimum d'historique (écart)
    for (let i = 3; i < uniqueDraws.length - 1; i++) {
        // ... (Logique simplifiée pour éviter les calculs trop lourds dans le browser)
        const currentDrawIndex = i;

        // Simuler les attendus à l'instant X
        const countsUntilX = {};
        const lastAppUntilX = {};

        for (let j = 0; j <= i; j++) {
            const values = drawsByDate.get(uniqueDraws[j]);
            values.forEach(v => {
                if (v === undefined || v === null || v === 'N/A' || v === 'N-D' || v === 'N-H' || v === '') return;
                countsUntilX[v] = (countsUntilX[v] || 0) + 1;
                lastAppUntilX[v] = j;
            });
        }

        // Top 10 des attendus (les plus grands écarts)
        const expectedAtX = Object.keys(lastAppUntilX).map(val => ({
            value: val,
            due: i - lastAppUntilX[val]
        })).sort((a, b) => b.due - a.due).slice(0, 10);

        const expectedValuesAtX = expectedAtX.map(e => e.value);

        // Vérifier dans les tirages suivants (X+1, optionnellement X+2/X+3 si dispos)
        const valuesX1 = drawsByDate.get(uniqueDraws[i + 1]) || [];
        const valuesX2 = (i + 2 < uniqueDraws.length) ? (drawsByDate.get(uniqueDraws[i + 2]) || []) : [];
        const valuesX3 = (i + 3 < uniqueDraws.length) ? (drawsByDate.get(uniqueDraws[i + 3]) || []) : [];

        let hitX1 = valuesX1.some(v => expectedValuesAtX.includes(v));
        let hitX2 = valuesX2.some(v => expectedValuesAtX.includes(v));
        let hitX3 = valuesX3.some(v => expectedValuesAtX.includes(v));

        if (hitX1) hitsX1++;
        if (hitX1 || hitX2 || hitX3) hitsX23++;
        totalTests++;
    }

    const hitRateX1 = totalTests > 0 ? (hitsX1 / totalTests) * 100 : 0;
    const hitRateTotal = totalTests > 0 ? (hitsX23 / totalTests) * 100 : 0;

    return {
        hitRateX1: Math.round(hitRateX1),
        hitRateTotal: Math.round(hitRateTotal),
        totalTests: totalTests
    };
}


function renderAttributeStats() {
    const container = document.getElementById('advancedStatsContainer');
    const selectedAttribute = document.getElementById('statsAttribute').value;

    if (!container) return;

    if (!selectedAttribute) {
        container.innerHTML = '<div class="empty-state"><p>Sélectionnez un attribut pour afficher les statistiques.</p></div>';
        return;
    }

    if (!window.advancedStatsData) {
        // This message is now more accurate.
        container.innerHTML = '<div class="empty-state"><p>Les données de statistiques ne sont pas calculées. Chargez le journal d\'abord.</p></div>';
        return;
    }

    const items = window.advancedStatsData[selectedAttribute];

    if (!items || items.length === 0) {
        container.innerHTML = `<div class="empty-state"><h3>Pas de données</h3><p>Aucune donnée statistique pour l\'attribut "${selectedAttribute}".</p></div>`;
        return;
    }

    container.innerHTML = ''; // Clear container

    // Ajouter la légende explicative
    const legend = document.createElement('div');
    legend.className = 'structural-legend';
    legend.innerHTML = `
        <h4>🔬 Système de Scores à Deux Niveaux</h4>
        <div class="legend-grid">
            <div class="legend-item">
                <span class="legend-icon">🔬</span>
                <span><strong>Structurel:</strong> Basé sur cardinalité naturelle</span>
            </div>
            <div class="legend-item">
                <span class="legend-icon">📊</span>
                <span><strong>Observé:</strong> Basé sur fréquence historique</span>
            </div>
            <div class="legend-item">
                <span class="legend-icon">🟢</span>
                <span>Score < 0.8: En avance</span>
            </div>
            <div class="legend-item">
                <span class="legend-icon">🔵</span>
                <span>Score 0.8-1.2: Normal</span>
            </div>
            <div class="legend-item">
                <span class="legend-icon">🟠</span>
                <span>Score 1.2-2.0: En retard</span>
            </div>
            <div class="legend-item">
                <span class="legend-icon">🔴</span>
                <span>Score ≥ 2.0: Très en retard</span>
            </div>
        </div>
    `;
    container.appendChild(legend);

    // Group items by universe if the attribute is 'drawer'
    const isDrawer = selectedAttribute === 'drawer';
    const universes = ['mundo', 'fruity', 'trigga', 'roaster', 'sunshine'];
    const groupedItems = {};

    if (isDrawer) {
        universes.forEach(u => groupedItems[u] = []);
        items.forEach(item => {
            let assigned = false;
            for (const u of universes) {
                if (item.value.toLowerCase().includes(u)) {
                    groupedItems[u].push(item);
                    assigned = true;
                    break;
                }
            }
            if (!assigned) {
                if (!groupedItems['other']) groupedItems['other'] = [];
                groupedItems['other'].push(item);
            }
        });
    } else {
        groupedItems['all'] = items;
    }

    for (const groupName in groupedItems) {
        const groupItems = groupedItems[groupName];
        if (groupItems.length === 0) continue;

        const card = document.createElement('div');
        card.className = 'stat-card';

        let title = attributeTitles[selectedAttribute] || selectedAttribute.charAt(0).toUpperCase() + selectedAttribute.slice(1);
        if (isDrawer && groupName !== 'all') {
            title += ` - ${groupName.charAt(0).toUpperCase() + groupName.slice(1)}`;
        }


        // Sort by proportional gapScore descending (most overdue first)
        const sortedByDue = [...groupItems].sort((a, b) => b.gapScore - a.gapScore);

        // For analysis, find the most frequent items
        const sortedByFreq = [...groupItems].sort((a, b) => b.count - a.count);

        // --- Build Summary ---
        let summaryHtml = '';
        if (sortedByDue.length > 0) {
            const mostDueItem = sortedByDue[0];
            const mostFreqItems = sortedByFreq.slice(0, 2);

            // Calculer la moyenne du score proportionnel
            const avgScore = parseFloat((groupItems.reduce((acc, item) => acc + item.gapScore, 0) / groupItems.length).toFixed(2));

            let conseil = "";
            if (mostDueItem.gapScore >= 2.0) {
                conseil = `<span style="color: #f5222d; font-weight: bold;">⚠️ Score ${mostDueItem.gapScore} — Très en retard par rapport à sa fréquence naturelle.</span>`;
            } else if (mostDueItem.gapScore >= 1.2) {
                conseil = `<span style="color: #fa8c16; font-weight: bold;">⚡ Score ${mostDueItem.gapScore} — En retard proportionnel. À surveiller.</span>`;
            } else {
                conseil = `<span style="color: #52c41a;">✅ Score ${mostDueItem.gapScore} — Distribution équilibrée.</span>`;
            }

            // Calculate Trend Performance dynamically for the current attribute
            const journal = window.currentJournalData.journal;
            const selectedUniverse = document.getElementById('universe').value;
            const filteredJournal = journal.filter(entry => entry.univers === selectedUniverse);
            const trendPerf = calculateTrendPerformance(filteredJournal, selectedAttribute);

            let perfHtml = '';
            if (trendPerf && trendPerf.totalTests > 0) {
                const colorX1 = trendPerf.hitRateX1 > 50 ? '#52c41a' : (trendPerf.hitRateX1 > 25 ? '#faad14' : '#f5222d');
                perfHtml = `
                    <div style="margin-top: 15px; background: #f0f5ff; padding: 10px; border-radius: 8px; border: 1px solid #adc6ff;">
                        <div style="font-weight: bold; color: #1e3c72; font-size: 0.9rem; margin-bottom: 5px;">📈 Performance de la Tendance</div>
                        <div style="display: flex; gap: 15px; align-items: center;">
                            <div>
                                <div style="font-size: 0.75rem; color: #666;">Précision X+1</div>
                                <div style="font-size: 1.2rem; font-weight: bold; color: ${colorX1}">${trendPerf.hitRateX1}%</div>
                            </div>
                            <div style="flex: 1; height: 8px; background: #d9d9d9; border-radius: 4px; overflow: hidden;">
                                <div style="height: 100%; width: ${trendPerf.hitRateTotal}%; background: linear-gradient(90deg, #1890ff, #52c41a);"></div>
                            </div>
                            <div>
                                <div style="font-size: 0.75rem; color: #666;">Global (X+3)</div>
                                <div style="font-size: 1.2rem; font-weight: bold; color: #52c41a">${trendPerf.hitRateTotal}%</div>
                            </div>
                        </div>
                        <div style="font-size: 0.7rem; color: #888; margin-top: 4px;">Basé sur ${trendPerf.totalTests} tests chronologiques.</div>
                    </div>
                `;
            } else {
                perfHtml = `
                    <div style="margin-top: 15px; background: #fff7e6; padding: 10px; border-radius: 8px; border: 1px solid #ffd591;">
                        <div style="font-weight: bold; color: #d46b08; font-size: 0.9rem;">📈 Performance de la Tendance</div>
                        <p style="font-size: 0.8rem; color: #8c8c8c; margin: 5px 0 0 0;">
                            Données insuffisantes pour calculer le score (min. 15 tirages requis).
                        </p>
                    </div>
                `;
            }

            summaryHtml = `
                <div class="stat-card-footer">
                    <div class="footer-title">💡 Analyse & Tendance</div>
                    <p>
                        <span class="tendance-label">Le plus attendu:</span>
                        <span class="tendance-value">${mostDueItem.value}</span>
                        <span class="tendance-detail">(écart de ${mostDueItem.due})</span>
                    </p>
                    <p>
                        <span class="tendance-label">Les plus fréquents:</span>
                        <span class="tendance-value">${mostFreqItems.map(i => i.value).join(', ')}</span>
                         <span class="tendance-detail">(${mostFreqItems.map(i => i.frequency + '%').join(', ')})</span>
                    </p>
                    ${perfHtml}
                    <p style="margin-top: 10px; border-top: 1px dashed #d9d9d9; padding-top: 8px;">
                        <span class="tendance-label">Verdict:</span> ${conseil}
                    </p>
                </div>
            `;
        }
        // --- End Summary ---


        // The main table is sorted by proportional gapScore
        let tableRows = '';
        sortedByDue.forEach(item => {
            const due = item.due;
            const gs = item.gapScore;

            // Color based on proportional score, not raw gap
            let scoreColor = '#52c41a'; // Green: normal
            let scoreIcon = '🟢';
            let scoreLabel = 'Normal';
            if (gs >= 2.0) {
                scoreColor = '#f5222d'; scoreIcon = '🔴'; scoreLabel = 'Tres en retard';
            } else if (gs >= 1.2) {
                scoreColor = '#fa8c16'; scoreIcon = '🟠'; scoreLabel = 'En retard';
            } else if (gs >= 0.8) {
                scoreColor = '#1890ff'; scoreIcon = '🔵'; scoreLabel = 'Normal';
            } else {
                scoreColor = '#52c41a'; scoreIcon = '🟢'; scoreLabel = 'En avance';
            }

            // Poids structurels
            const hasStructural = item.structural && item.structural.expected_gap;
            const structuralIcon = hasStructural ? '🔬' : '📊';
            const structuralGapScore = hasStructural ? 
                window.structuralWeightsClient.calculateStructuralGapScore(due, item.structural.expected_gap) : null;
            const structuralColor = hasStructural ? 
                window.structuralWeightsClient.getGapScoreColor(structuralGapScore) : scoreColor;
            
            const tooltip = hasStructural ? 
                window.structuralWeightsClient.formatTooltip(
                    { expectedGap: item.expectedGap, gapScore: gs },
                    item.structural
                ) : `📊 Observé: ${item.expectedGap?.toFixed(2) || 'N/A'} tirages\nScore: ${gs}`;

            let valueDisplay = item.value;

            tableRows += `
                <tr>
                    <td>
                        <div style="font-weight: 600; color: #1e3c72;">${valueDisplay}</div>
                        <div class="freq-bar-bg">
                            <div class="freq-bar-fill" style="width: ${item.frequency}%"></div>
                        </div>
                    </td>
                    <td style="text-align: center;"><strong>${item.count}</strong></td>
                    <td style="text-align: center; font-size: 0.75rem; cursor: help;" title="Densite: ${item.count} apparitions sur ${item.totalDraws} tirages au total">
                        <strong>${item.count}</strong>/${item.totalDraws}
                        <div style="color: #1890ff; font-weight: bold;">${item.drawRatio}%</div>
                    </td>
                    <td style="text-align: center; font-size: 0.75rem; cursor: help;" title="Regularite: Present dans ${item.periodsPresent} periodes sur ${item.totalPeriods} (1 periode = groupe de tirages defini par le cycle)">
                        <strong>${item.periodsPresent}</strong>/${item.totalPeriods}
                        <div style="color: #722ed1; font-weight: bold;">${item.periodRatio}%</div>
                    </td>
                    <td style="text-align: center; font-size: 0.8rem;">${item.last_appearance ? formatDateSimple(item.last_appearance) : '-'}</td>
                    <td style="text-align: center; cursor: help;" title="${tooltip}">
                        <div style="font-size: 0.75rem; color: #999;">${due}</div>
                        <div style="font-weight: bold; font-size: 1rem; color: ${hasStructural ? structuralColor : scoreColor};">
                            ${structuralIcon} ${hasStructural ? structuralGapScore?.toFixed(2) : gs}
                        </div>
                    </td>
                </tr>
            `;
        });

        // --- Build Chart (using proportional gapScore) ---
        const maxScore = sortedByDue.length > 0 ? sortedByDue[0].gapScore : 0;
        let chartHtml = `
            <div class="due-chart">
                <div class="chart-title">🔥 Top 10 — Score d'Écart Proportionnel</div>
        `;

        sortedByDue.slice(0, 10).reverse().forEach((item, idx) => {
            const barWidth = maxScore > 0 ? Math.max((item.gapScore / maxScore) * 100, 5) : 5;
            const gs = item.gapScore;
            let dueClass = 'low';
            if (gs >= 0.8 && gs < 1.2) dueClass = 'low';
            if (gs >= 1.2 && gs < 2.0) dueClass = 'med';
            if (gs >= 2.0) dueClass = 'high';

            // --- Trend Indicators (X+1, X+2, X+3) ---
            // On vérifie les tirages récents (les tout derniers du journal actuel)
            // Pour marquer le Top 10 actuel par rapport à la réalité
            const journal = window.currentJournalData.journal;
            const uniqueDraws = [...new Map(journal.map(e => [e.date, e])).values()]
                .sort((a, b) => parseEntryDate(a.date) - parseEntryDate(b.date));

            // On regarde si l'item est apparu dans les tirages les plus récents
            // (Note: C'est un indicateur visuel direct demandé par l'user)
            let trendMark = '';
            if (uniqueDraws.length > 0) {
                const latestValues = journal.filter(e => e.date === uniqueDraws[uniqueDraws.length - 1].date).map(e => e[selectedAttribute]);
                const prevValues1 = uniqueDraws.length > 1 ? journal.filter(e => e.date === uniqueDraws[uniqueDraws.length - 2].date).map(e => e[selectedAttribute]) : [];
                const prevValues2 = uniqueDraws.length > 2 ? journal.filter(e => e.date === uniqueDraws[uniqueDraws.length - 3].date).map(e => e[selectedAttribute]) : [];

                if (latestValues.includes(item.value)) {
                    trendMark = '<span title="Apparu au dernier tirage" style="color: #52c41a; margin-left:8px; font-weight:bold;">✅</span>';
                } else if (prevValues1.includes(item.value) || prevValues2.includes(item.value)) {
                    trendMark = '<span title="Apparu récemment (X-1 ou X-2)" style="color: #faad14; margin-left:8px; font-weight:bold;">✴️</span>';
                } else {
                    trendMark = '<span title="Non apparu récemment" style="color: #f5222d; margin-left:8px; font-weight:bold;">❌</span>';
                }
            }

            chartHtml += `
                <div class="chart-bar-item">
                    <div class="chart-label" title="${item.value}">${item.value}${trendMark}</div>
                    <div class="chart-bar-container">
                        <div class="chart-bar due-bg-${dueClass}" style="width: ${barWidth}%">
                            <span>${item.gapScore} (${item.due})</span>
                        </div>
                    </div>
                </div>
            `;
        });
        chartHtml += '</div>';
        // --- End Chart ---


        card.innerHTML = `
            <div class="stat-card-header">
                <span>${title}</span>
                <span class="stat-badge" style="background: #e6f7ff; color: #1890ff; font-weight: bold; border: 1px solid #91d5ff;">
                    ${groupItems.length} éléments
                </span>
            </div>
            <div class="stat-card-body">
                ${chartHtml}
                <div class="table-wrapper" style="padding: 10px;">
                    <table class="stats-table">
                    <thead>
                        <tr>
                            <th>Valeur</th>
                            <th style="text-align: center;">Total</th>
                            <th style="text-align: center; color: #1890ff; cursor: help;" title="Nombre d'apparitions de cet attribut divise par le nombre total de tirages dans la session. Mesure la DENSITE.">Occ/Tir.</th>
                            <th style="text-align: center; color: #722ed1; cursor: help;" title="Nombre de periodes (cycles) ou cet attribut est present, divise par le total des periodes. Mesure la REGULARITE.">Occ/Per.</th>
                            <th style="text-align: center;">Dernier</th>
                            <th style="text-align: center; cursor: help;" title="Score d'Ecart Proportionnel = Ecart reel / Ecart attendu. Tient compte de la frequence naturelle de chaque valeur. >1.2 = en retard, >2.0 = tres en retard.">Score</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${tableRows}
                    </tbody>
                </table>
            </div>
            ${summaryHtml}
        `;

        container.appendChild(card);

    }
}


function formatDateSimple(dateStr) {
    if (!dateStr) return '';
    try {
        const d = new Date(dateStr);
        // Add time zone offset to avoid date changing
        const userTimezoneOffset = d.getTimezoneOffset() * 60000;
        const correctedDate = new Date(d.getTime() + userTimezoneOffset);
        return `${String(correctedDate.getDate()).padStart(2, '0')}/${String(correctedDate.getMonth() + 1).padStart(2, '0')}`;
    } catch (e) {
        return dateStr;
    }
}

// --- Partial Journal View ---

// --- Isolation & Highlighting Logic ---

async function fetchGlobalAttributeValues(universe, attr) {
    if (!universe || !attr) return [];

    // Mapping of attributes to their API endpoints
    const apiMap = {
        'forme': `/api/analytics/katula/formes/${universe}`,
        'granque': `/api/analytics/granque-tome/${universe}`,
        'tome': `/api/analytics/granque-tome/${universe}`,
        'petique': `/api/analytics/granque-tome/${universe}`,
    };

    if (!apiMap[attr]) {
        // Fallback to what we have in the current journal for non-geometric attributes
        if (window.advancedStatsData && window.advancedStatsData[attr]) {
            return window.advancedStatsData[attr].map(item => item.value);
        }

        // Static fallbacks for common attributes
        if (attr === 'parite') return ['Pair', 'Impair'];
        if (attr === 'ligne') return ['L1', 'L2', 'L3', 'L4', 'L5', 'L6', 'L7', 'L8'];
        if (attr === 'colonne') return ['C1', 'C2', 'C3', 'C4', 'C5', 'C6'];
        if (attr === 'region') return ['NORD', 'SUD', 'EST', 'OUEST'];
        if (attr === 'chip') return Array.from({ length: 48 }, (_, i) => i + 1);

        return [];
    }

    try {
        const response = await fetch(apiMap[attr]);
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
        const data = await response.json();

        if (attr === 'forme') return data.formes || [];

        // Format for granque-tome endpoint
        if (attr === 'granque') return Object.keys(data.granque_data || {});
        if (attr === 'tome') return Object.keys(data.tome_data || {});
        if (attr === 'petique') return Object.keys(data.petique_data || {});

        return [];
    } catch (e) {
        console.error(`[Stats] Error fetching global values for ${attr}:`, e);
        // Fallback to journal data
        if (window.advancedStatsData && window.advancedStatsData[attr]) {
            return window.advancedStatsData[attr].map(item => item.value);
        }
        return [];
    }
}

window.onAttributeChange = async function (attr) {
    console.log("[Stats] Attribute changed to:", attr);
    const valueSelect = document.getElementById('statsValue');
    const universe = document.getElementById('universe')?.value || 'mundo';

    if (!valueSelect) {
        console.warn("[Stats] Element #statsValue not found.");
        return;
    }

    if (!attr) {
        valueSelect.style.display = 'none';
        valueSelect.value = '';
        renderAttributeStats();
        return;
    }

    // Populate values for this attribute (Global Search)
    valueSelect.innerHTML = '<option value="">...Chargement...</option>';
    valueSelect.style.display = 'inline-block';

    const globalValues = await fetchGlobalAttributeValues(universe, attr);

    valueSelect.innerHTML = '<option value="">Toutes les valeurs (Relief OFF)</option>';

    if (globalValues && globalValues.length > 0) {
        // Sort values to make them easy to find
        const sortedValues = [...new Set(globalValues)].sort((a, b) => String(a).localeCompare(String(b), undefined, { numeric: true }));

        sortedValues.forEach(val => {
            const opt = document.createElement('option');
            opt.value = val;
            opt.textContent = val;
            valueSelect.appendChild(opt);
        });
        console.log("[Stats] Populated dropdown with", sortedValues.length, "global values.");
    } else {
        console.warn("[Stats] No global values found for attribute:", attr);
        const opt = document.createElement('option');
        opt.disabled = true;
        opt.textContent = "Aucune valeur trouvée";
        valueSelect.appendChild(opt);
    }

    valueSelect.value = '';
    renderAttributeStats();

    // Auto-update partial journal if open
    const partialPanel = document.getElementById('partialJournalPanel');
    if (partialPanel && partialPanel.style.display !== 'none') {
        window.showPartialJournal(attr);
    }
};

window.onValueChange = function (val) {
    console.log("[Stats] Value isolation focus:", val);
    updateIsolation(val);

    // Auto-update partial journal if open to show vertical evolution
    const attrSelect = document.getElementById('statsAttribute');
    const attr = attrSelect ? attrSelect.value : "";
    const partialPanel = document.getElementById('partialJournalPanel');

    if (attr && partialPanel && (partialPanel.style.display !== 'none')) {
        window.showPartialJournal(attr);
    }

    // Interaction with chart
    const timeline = document.getElementById('evolutionTimelineContainer');
    if (timeline) timeline.innerHTML = '';
};

function updateIsolation(selectedValue) {
    const table = document.querySelector('.stats-table');
    const selectedValueStr = (selectedValue !== undefined && selectedValue !== null) ? String(selectedValue).trim() : "";

    if (table) {
        const rows = table.querySelectorAll('tbody tr');
        rows.forEach(row => {
            const valueCell = row.querySelector('td div');
            if (!valueCell) return;

            const rowValue = valueCell.textContent.trim();

            if (!selectedValueStr) {
                row.classList.remove('stat-row-isolated', 'stat-row-dimmed');
            } else if (rowValue === selectedValueStr) {
                row.classList.add('stat-row-isolated');
                row.classList.remove('stat-row-dimmed');
            } else {
                row.classList.add('stat-row-dimmed');
                row.classList.remove('stat-row-isolated');
            }
        });
    }

    // Also isolate in chart
    const chartBars = document.querySelectorAll('.chart-bar-item');
    chartBars.forEach(item => {
        const label = item.querySelector('.chart-label');
        if (!label) return;
        const barValue = (label.getAttribute('title') || label.textContent.split('✅')[0].split('✴️')[0].split('❌')[0].trim()).trim();

        if (!selectedValueStr) {
            item.style.opacity = '1';
            item.style.filter = 'none';
            item.style.transform = 'scale(1)';
        } else if (barValue === selectedValueStr) {
            item.style.opacity = '1';
            item.style.filter = 'none';
            item.style.transform = 'scale(1.05)';
            item.style.zIndex = '10';
        } else {
            item.style.opacity = '0.2';
            item.style.filter = 'grayscale(100%)';
            item.style.transform = 'scale(1)';
            item.style.zIndex = '1';
        }
    });
}

// Partial Journal Logic
window.showPartialJournal = function (attribute) {
    const valueSelect = document.getElementById('statsValue');
    const selectedValue = valueSelect ? valueSelect.value.trim() : "";

    console.log("[Stats] Opening Partial Journal for:", attribute, "Isolated value:", selectedValue);

    if (!attribute) {
        alert('Veuillez sélectionner un attribut.');
        return;
    }

    if (!window.currentJournalData || !window.currentJournalData.journal) {
        alert('Aucune donnée de journal disponible.');
        return;
    }

    const panel = document.getElementById('partialJournalPanel');
    const title = document.getElementById('partialJournalTitle');
    const tbody = document.getElementById('partialJournalBody');
    const attrHeader = document.getElementById('partialAttrHeader');

    if (!panel || !tbody) {
        console.error("[Stats] Partial Journal elements not found.");
        return;
    }

    const attrName = (attributeTitles[attribute]) || attribute;
    title.innerHTML = `<span>📋 Journal Partiel - ${attrName}</span> ${selectedValue ? `<span style="background:#1890ff; color:white; padding:2px 8px; border-radius:10px; font-size:0.7em; margin-left:10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">ISO: ${selectedValue}</span>` : ''}`;
    attrHeader.textContent = attrName;

    const universeSelect = document.getElementById('universe');
    const selectedUniverse = universeSelect ? universeSelect.value : "";

    // Filter by universe and include draw status
    let rawData = window.currentJournalData.journal.filter(entry =>
        entry.univers === selectedUniverse ||
        entry.status === 'no_draw' ||
        entry.is_no_draw
    );

    // Sort by date descending
    rawData.sort((a, b) => parseEntryDate(b.date) - parseEntryDate(a.date));

    // Group by Date for rowspan
    const groupedByDate = {};
    rawData.forEach(entry => {
        const dateKey = entry.date;
        if (!groupedByDate[dateKey]) groupedByDate[dateKey] = [];
        groupedByDate[dateKey].push(entry);
    });

    tbody.innerHTML = '';
    if (rawData.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5" style="text-align:center; padding: 20px; color: #999;">Aucune donnée pour cet univers.</td></tr>';
    } else {
        let currentPeriod = null;
        const periodicityInput = document.getElementById('periodicity');
        const periodicity = parseInt(periodicityInput ? periodicityInput.value : 7) || 7;

        Object.keys(groupedByDate).forEach((dateKey) => {
            const group = groupedByDate[dateKey];

            group.forEach((entry, entryIndex) => {
                // Period logic
                const entryPeriod = entry.period || (entry.draw_number ? Math.ceil(entry.draw_number / periodicity) : null);

                // --- Period Separator Row ---
                if (entryPeriod !== null && currentPeriod !== null && entryPeriod !== currentPeriod) {
                    const sepRow = document.createElement('tr');
                    sepRow.innerHTML = `
                        <td colspan="5" style="padding: 15px 0 5px 0; border-top: 4px solid #ff4d4f; text-align: center; background: transparent;">
                            <span style="background: white; padding: 0 10px; color: #ff4d4f; font-weight: bold; font-size: 0.8em; position: relative; top: -25px; z-index: 1;">
                                ⬆️ FIN DE PÉRIODE ${entryPeriod} / DÉBUT PÉRIODE ${currentPeriod} ⬆️
                            </span>
                        </td>
                    `;
                    tbody.appendChild(sepRow);
                }
                else if (currentPeriod === null && entryPeriod !== null) {
                    const headRow = document.createElement('tr');
                    headRow.style.backgroundColor = '#f0f9ff';
                    headRow.style.color = '#1890ff';
                    headRow.style.fontWeight = 'bold';
                    headRow.innerHTML = `<td colspan="5" style="padding: 8px; text-align: center; border-bottom: 2px solid #1890ff;">📅 PÉRIODE ${entryPeriod}</td>`;
                    tbody.appendChild(headRow);
                }
                currentPeriod = entryPeriod;

                const row = document.createElement('tr');

                // Robust comparison
                const entryValue = entry[attribute];
                const entryValueStr = (entryValue !== undefined && entryValue !== null) ? String(entryValue).trim() : "";
                const isTarget = selectedValue !== "" && entryValueStr === selectedValue;

                const isNoDraw = entry.status === 'no_draw' || entry.is_no_draw;
                const isNoHold = entry.status === 'no_hold' || entry.combination === 'NO-HOLD';

                if (selectedValue !== "") {
                    if (isTarget) {
                        row.style.background = 'rgba(24, 144, 255, 0.12)';
                        row.style.fontWeight = 'bold';
                        row.style.opacity = '1';
                    } else {
                        row.style.opacity = '0.45';
                    }
                }

                let valueDisplay = entryValue || '-';
                if (isNoDraw) {
                    valueDisplay = `<span class="no-draw-indicator" style="background:#ff4f4f; color:white; padding:2px 6px; border-radius:4px; font-weight:bold; font-size:0.75rem;">N-D</span>`;
                } else if (isNoHold) {
                    valueDisplay = `<span class="no-hold-indicator" style="background:#fa8c16; color:white; padding:2px 6px; border-radius:4px; font-weight:bold; font-size:0.75rem;">N-H</span>`;
                } else if (attribute === 'forme') {
                    valueDisplay = `${getFormeIcon(entryValue)} <span style="margin-left:5px">${entryValue}</span>`;
                } else if (attribute === 'engine') {
                    valueDisplay = getEngineIcon(entryValue);
                } else if (attribute === 'beastie') {
                    valueDisplay = getBeastieIcon(entryValue);
                } else if (attribute === 'tome') {
                    valueDisplay = getTomeIcon(entryValue);
                }

                // Vertical Evolution Marker
                let evolCellContent = '';
                if (selectedValue !== "") {
                    const dotClass = `timeline-dot-v ${isTarget ? 'active' : ''} ${isNoDraw ? 'no-draw' : ''}`;
                    const titleText = isTarget ? 'PRÉSENT' : (isNoDraw ? 'PAS DE TIRAGE' : 'ABSENT');
                    evolCellContent = `<div class="${dotClass}" title="${titleText}" style="margin: 0 auto;"></div>`;
                } else {
                    evolCellContent = '<span style="color:#ddd">-</span>';
                }

                // Row construction with rowspan
                let rowHtml = '';
                if (entryIndex === 0) {
                    rowHtml += `<td style="text-align:center; vertical-align: middle; background: #fafafa; font-weight: bold; border-right: 1px solid #f0f0f0;" rowspan="${group.length}">P${entryPeriod || '?'}</td>`;
                    rowHtml += `<td style="text-align:center; vertical-align: middle; background: #fafafa; border-right: 1px solid #f0f0f0;" rowspan="${group.length}">${formatDateSimple(entry.date)}</td>`;
                    rowHtml += `<td style="text-align:center; vertical-align: middle; border-right: 1px solid #f0f0f0;" rowspan="${group.length}">${entry.lottery_name}</td>`;
                }
                rowHtml += `<td>${valueDisplay}</td>
                            <td style="text-align:center; vertical-align: middle;">${evolCellContent}</td>`;

                row.innerHTML = rowHtml;
                tbody.appendChild(row);
            });
        });
    }

    panel.style.display = 'flex';
};

function closePartialJournal() {
    const modal = document.getElementById('partialJournalModal');
    if (modal) modal.classList.remove('active');

    // Also handle panel version
    const panel = document.getElementById('partialJournalPanel');
    if (panel) panel.style.display = 'none';
}

// Close on click outside for modal
document.addEventListener('click', function (event) {
    const modal = document.getElementById('partialJournalModal');
    if (modal && event.target === modal) {
        closePartialJournal();
    }
});
