const API_BASE = `${window.location.origin}/api/analytics`;
let currentAnalysisData = null;
let tablesConfiguration = [];
let globalAvailablePeriods = []; // Stocker les périodes disponibles pour l'univers
let currentViewMode = 'grid'; // 'grid' or 'scatter'

let markingOptions = {
    type: 'chip',
    style: 'cross',
    colors: {
        1: '#e74c3c',
        2: '#f39c12',
        3: '#8e44ad'
    },
    showCount: true,
    showTooltip: true,
    animateMarking: false
};

// Système de marquage des zones
let selectedChips = new Set();
let markedZones = new Set();

let currentSelection = {
    chips: [],
    periods: [],
    universe: null
};

let drawResults = [];
let globalReferenceData = null; // Stocker les données de référence

// Constantes copiées de katula-dynamic.js
const FORME_ICONS = {
    'carre': '■', 'triangle': '▲', 'cercle': '●', 'rectangle': '▬',
    'carre-triangle': '■▲', 'carre-cercle': '■●', 'carre-rectangle': '■▬',
    'triangle-carre': '▲■', 'triangle-cercle': '▲●', 'triangle-rectangle': '▲▬',
    'cercle-carre': '●■', 'cercle-triangle': '●▲', 'cercle-rectangle': '●▬',
    'rectangle-carre': '▬■', 'rectangle-triangle': '▬▲', 'rectangle-cercle': '▬●'
};

const FORME_COLORS = {
    'carre': '#3498db', 'triangle': '#2ecc71', 'cercle': '#f1c40f', 'rectangle': '#e74c3c'
};

const DRAWER_ORDER = {
    mundo: ['carre', 'triangle', 'cercle', 'rectangle'],
    fruity: ['carre', 'triangle', 'cercle', 'rectangle'],
    trigga: ['carre', 'triangle', 'cercle', 'rectangle', 'triangle-cercle', 'triangle-rectangle', 'cercle-rectangle', 'cercle-triangle', 'rectangle-cercle', 'rectangle-triangle'],
    roaster: ['carre-triangle', 'carre-cercle', 'carre-rectangle', 'triangle-carre', 'triangle-cercle', 'triangle-rectangle', 'cercle-carre', 'cercle-triangle', 'cercle-rectangle', 'rectangle-carre', 'rectangle-triangle', 'rectangle-cercle'],
    sunshine: ['carre', 'triangle', 'cercle', 'rectangle', 'carre-triangle', 'carre-cercle', 'carre-rectangle', 'triangle-carre', 'triangle-cercle', 'triangle-rectangle', 'cercle-carre', 'cercle-triangle', 'cercle-rectangle', 'rectangle-carre', 'rectangle-triangle', 'rectangle-cercle']
};

// Fonction utilitaires copiées
function getFormeColor(forme) {
    if (FORME_COLORS[forme]) return FORME_COLORS[forme];
    if (forme.includes('-')) {
        const [forme1] = forme.split('-');
        return FORME_COLORS[forme1] || '#95a5a6';
    }
    return '#95a5a6';
}

function generateCompositeIcon(forme) {
    if (!forme.includes('-')) {
        const icon = FORME_ICONS[forme] || '?';
        const color = getFormeColor(forme);
        return `<span style="color: ${color}">${icon}</span>`;
    }
    const [forme1, forme2] = forme.split('-');
    const icon1 = FORME_ICONS[forme1] || '?';
    const icon2 = FORME_ICONS[forme2] || '?';
    const color1 = FORME_COLORS[forme1] || '#95a5a6';
    const color2 = FORME_COLORS[forme2] || '#95a5a6';
    return `<span style="color: ${color1}">${icon1}</span><span style="color: ${color2}">${icon2}</span>`;
}

function getQuadrant(row, col) {
    const chipNumber = (row - 1) * 6 + col;
    const q1Chips = [1, 2, 3, 7, 8, 9, 13, 14, 15, 19, 20, 21];
    const q2Chips = [4, 5, 6, 10, 11, 12, 16, 17, 18, 22, 23, 24];
    const q3Chips = [25, 26, 27, 31, 32, 33, 37, 38, 39, 43, 44, 45];
    const q4Chips = [28, 29, 30, 34, 35, 36, 40, 41, 42, 46, 47, 48];
    if (q1Chips.includes(chipNumber)) return 'q1';
    if (q2Chips.includes(chipNumber)) return 'q2';
    if (q3Chips.includes(chipNumber)) return 'q3';
    if (q4Chips.includes(chipNumber)) return 'q4';
    return 'q1';
}

// Récupérer les données temporelles pour une période
// Récupérer les données temporelles pour une période (Version simulée robuste)
async function getTemporalData(universe, year, period, type) {
    const occurrences = {};
    const numOccurrences = Math.floor(Math.random() * 8) + 3; // 3-10 occurrences
    const formes = DRAWER_ORDER[universe] || ['carre', 'triangle', 'cercle', 'rectangle'];

    for (let i = 0; i < numOccurrences; i++) {
        const chipNumber = Math.floor(Math.random() * 48) + 1;
        const randomForme = formes[Math.floor(Math.random() * formes.length)];

        if (!occurrences[chipNumber]) {
            occurrences[chipNumber] = {
                count: 1,
                details: [{ forme: randomForme, denomination: 'simulated' }]
            };
        } else {
            occurrences[chipNumber].count++;
            occurrences[chipNumber].details.push({ forme: randomForme, denomination: 'simulated' });
        }
    }

    return {
        year,
        period,
        type,
        universe,
        occurrences: occurrences,
        totalDraws: Math.floor(Math.random() * 20) + 10
    };
}

function displayTemporalTables(analysisData) {
    const container = document.getElementById('tablesContainer');
    const universe = analysisData.universe || 'mundo';
    const shapes = DRAWER_ORDER[universe] || [];

    // Restauration de la Légende "Carte Complète"
    let html = '';
    html += `<div class="mini-table-container legend-container-wrapper" style="grid-row: span 2; border: 3px solid #34495e;">
        <div class="mini-table-header" style="background: #2c3e50;">LÉGENDE / RÉFÉRENCE ${universe.toUpperCase()}</div>
        ${generateReferenceTableHTML(globalReferenceData, universe)}
        <div class="table-controls"><small>Carte de référence des tiroirs</small></div>
    </div>`;

    analysisData.tablesData.forEach((tableData, index) => {
        const isPrediction = tableData.type === 'prediction';
        const headerClass = isPrediction ? 'style="background: #e67e22;"' : '';
        const dateRange = `${tableData.dateStart || ''} → ${tableData.dateEnd || ''}`;
        const title = tableData.title ? `${tableData.title}` : dateRange;
        // Correction calcul count occurrences (support object/array)
        let occurrenceCount = 0;
        if (Array.isArray(tableData.occurrences)) occurrenceCount = tableData.occurrences.length;
        else occurrenceCount = Object.keys(tableData.occurrences || {}).filter(k => tableData.occurrences[k].count > 0).length;

        const gridClass = currentViewMode === 'scatter' ? 'mini-katula-scatter' : 'mini-katula-grid';
        const gridContent = currentViewMode === 'scatter' ? generateScatterPlotGrid(tableData) : generateMiniKatulaGrid(tableData);

        html += `<div class="mini-table-container">
            <div class="mini-table-header"${headerClass}>${title}</div>
            <div class="table-period-info">📊 ${occurrenceCount} chips | ${tableData.totalDraws || 0} tirages</div>
            <div class="${gridClass}">${gridContent}</div>
            <div class="table-controls">
                <button onclick="showTableDetails(${index})">Détails</button>
                <button onclick="showTableStats(${index})">Stats</button>
            </div>
        </div>`;
    });
    container.innerHTML = html;
}

async function fetchReferenceData(universe) {
    const matrix = {};
    try {
        const response = await fetch(`${API_BASE}/katula/matrix/${universe}`);
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        const bulkData = await response.json();
        console.log('Réponse brute de /api/analytics/katula/matrix:', bulkData);
        if (bulkData && bulkData.status === 'success' && bulkData.matrix) {
            bulkData.matrix.forEach((rowChips, rowIndex) => {
                const r = rowIndex + 1;
                matrix[r] = {};
                rowChips.forEach((chipInfo, colIndex) => {
                    const c = colIndex + 1;
                    if (chipInfo) {
                        const elements = [];
                        const formeOrder = DRAWER_ORDER[universe] || ['carre', 'triangle', 'cercle', 'rectangle'];
                        const compartmentsMap = {};
                        if (chipInfo.compartments && Array.isArray(chipInfo.compartments)) {
                            chipInfo.compartments.forEach(comp => {
                                if (comp) {
                                    compartmentsMap[comp.forme] = comp;
                                }
                            });
                        }
                        // Conserver la structure des tiroirs même si la dénomination est absente
                        formeOrder.forEach(forme => {
                            const comp = compartmentsMap[forme];
                            if (comp) {
                                const denom = (comp.denomination && comp.denomination !== "---") ? comp.denomination : null;
                                elements.push({
                                    forme: forme,
                                    denomination: denom
                                });
                            } else {
                                // tiroir absent dans les données -> représenter comme vide
                                elements.push({
                                    forme: forme,
                                    denomination: null
                                });
                            }
                        });
                        matrix[r][c] = {
                            elements: elements,
                            chipNumber: chipInfo.chip_number
                        };
                    }
                });
            });
            return { matrix, universe, success: true };
        }
        return { matrix: {}, universe, success: false, error: "Invalid data" };
    } catch (e) {
        console.error("Erreur fetchReferenceData", e);
        return { matrix: {}, universe, success: false, error: e.message };
    }
}

function generateReferenceTableHTML(data, universe) {
    if (!data || !data.success || !data.matrix) {
        return '<div style="padding:20px; text-align:center;">Données de référence non disponibles</div>';
    }
    let html = '<div class="mini-table-container legend-container-wrapper"><div class="mini-table-header" style="background: #2c3e50; color: white; padding: 10px; text-align: center; font-weight: bold;">LÉGENDE / RÉFÉRENCE</div>';
    html += '<div class="katula-legend-responsive">';
    for (let chipNumber = 1; chipNumber <= 48; chipNumber++) {
        const r = Math.ceil(chipNumber / 6);
        const c = (chipNumber - 1) % 6 + 1;
        const cellData = data.matrix[r] ? data.matrix[r][c] : null;
        const quadrant = getQuadrant(r, c);
        const debugColors = {
            'q1': 'rgba(52, 152, 219, 0.1)', 'q2': 'rgba(46, 204, 113, 0.1)', 'q3': 'rgba(243, 156, 18, 0.1)', 'q4': 'rgba(155, 89, 182, 0.1)'
        };

        // Préparer un objet occurrence agrégé depuis les données d'analyse (si disponibles)
        const occurrenceAggregated = getAggregatedOccurrence(chipNumber);
        // Renseigner aussi la dénomination/forme issue de la matrice de référence si présente
        if (cellData && cellData.elements && cellData.elements.length > 0) {
            occurrenceAggregated.denomination = occurrenceAggregated.denomination || cellData.elements[0].denomination || null;
            occurrenceAggregated.forme = occurrenceAggregated.forme || cellData.elements[0].forme || null;
        }

        html += `<div class="mini-chip-cell legend-chip-cell ${quadrant}" data-chip="${chipNumber}" data-table="legend" data-universe="${universe}" style="background-color: ${debugColors[quadrant]}; flex-direction: column; justify-content: flex-start; align-items: stretch; padding: 1px;" onclick="showChipTemporalDetails(${chipNumber}, 'LÉGENDE', ${JSON.stringify(occurrenceAggregated).replace(/\"/g, '&quot;')}, event)"><div class="chip-name" style="font-size: 0.5em; background: #eee; text-align: center; width: 100%; margin-bottom: 1px;">chip${chipNumber}</div>`;
        const universeFormes = DRAWER_ORDER[universe] || [];
        const elementsMap = {};
        if (cellData && cellData.elements) {
            cellData.elements.forEach(el => elementsMap[el.forme] = el);
        }
        universeFormes.forEach(forme => {
            const element = elementsMap[forme];
            const icon = generateCompositeIcon(forme);
            const denom = element && element.denomination ? element.denomination : null;
            let displayDenom = denom || '';
            if (displayDenom.length > 8 && displayDenom.includes('/')) displayDenom = displayDenom.split('/')[0] + '...';
            const isEmpty = !denom;
            const emptyClass = isEmpty ? ' empty-drawer' : '';
            const drawerOccurrence = { denomination: denom, forme: forme };
            html += `<div class="chip-drawer drawer-${forme}${emptyClass}" style="display: flex; align-items: center; font-size: 0.55em; line-height: 1; padding: 0 1px;">
                    <span style="margin-right:1px; cursor: pointer;" onclick="showLegendAttribute(${chipNumber}, ${JSON.stringify(forme).replace(/\"/g, '&quot;')}, 'forme', 'LÉGENDE', ${JSON.stringify(drawerOccurrence).replace(/\"/g, '&quot;')}, event)">${icon}</span>
                    <span style="overflow:hidden; text-overflow:ellipsis; white-space: nowrap; cursor: pointer;" onclick="showLegendAttribute(${chipNumber}, ${JSON.stringify(denom || ('<empty:' + forme + '>')).replace(/\"/g, '&quot;')}, 'denomination', 'LÉGENDE', ${JSON.stringify(drawerOccurrence).replace(/\"/g, '&quot;')}, event)">${displayDenom || '—'}</span>
                </div>`;
        });
        html += `</div>`;
    }
    html += `</div></div>`;
    return html;
}
function analyzeSequencePatterns(historicalTables) {
    const patterns = [];
    const transitions = {};
    for (let i = 0; i < historicalTables.length - 1; i++) {
        const currentChips = new Set(Object.keys(historicalTables[i].occurrences).filter(c => historicalTables[i].occurrences[c].count > 0));
        const nextChips = new Set(Object.keys(historicalTables[i + 1].occurrences).filter(c => historicalTables[i + 1].occurrences[c].count > 0));
        currentChips.forEach(chip => {
            if (!transitions[chip]) transitions[chip] = { followed: [], preceded: [] };
            nextChips.forEach(nextChip => {
                if (chip !== nextChip) {
                    transitions[chip].followed.push(nextChip);
                    if (!transitions[nextChip]) transitions[nextChip] = { followed: [], preceded: [] };
                    transitions[nextChip].preceded.push(chip);
                }
            });
        });
    }
    Object.entries(transitions).forEach(([chip, data]) => {
        const followedCounts = {};
        data.followed.forEach(f => followedCounts[f] = (followedCounts[f] || 0) + 1);
        Object.entries(followedCounts).forEach(([followedChip, count]) => {
            if (count >= 2) {
                const probability = count / data.followed.length;
                patterns.push({
                    type: 'Séquence Fréquente',
                    category: 'Séquence',
                    description: `Chip ${chip} → Chip ${followedChip}`,
                    details: `Transition observée ${count} fois(probabilité: ${(probability * 100).toFixed(0)}%)`,
                    confidence: probability * 70 + count * 10,
                    chipNumber: parseInt(chip),
                    data: { followedChip: parseInt(followedChip), count, probability }
                });
            }
        });
    });
    return patterns;
}

function analyzeSpatialPatterns(historicalTables) {
    const patterns = [];
    const quadrantActivity = { q1: [], q2: [], q3: [], q4: [] };
    const chipToQuadrant = (chip) => {
        const row = Math.ceil(chip / 6);
        const col = ((chip - 1) % 6) + 1;
        if (row <= 4 && col <= 3) return 'q1';
        if (row <= 4 && col > 3) return 'q2';
        if (row > 4 && col <= 3) return 'q3';
        return 'q4';
    };
    historicalTables.forEach((table, index) => {
        const quadrantCounts = { q1: 0, q2: 0, q3: 0, q4: 0 };
        Object.entries(table.occurrences).forEach(([chip, data]) => {
            if (data.count > 0) {
                const quadrant = chipToQuadrant(parseInt(chip));
                quadrantCounts[quadrant] += data.count;
            }
        });
        Object.entries(quadrantCounts).forEach(([quadrant, count]) => {
            quadrantActivity[quadrant].push(count);
        });
    });
    Object.entries(quadrantActivity).forEach(([quadrant, activity]) => {
        const avgActivity = activity.reduce((a, b) => a + b, 0) / activity.length;
        const consistency = activity.filter(a => a > 0).length / activity.length;
        if (avgActivity >= 2 && consistency >= 0.6) {
            patterns.push({
                type: 'Zone Active',
                category: 'Spatial',
                description: `Quadrant ${quadrant.toUpperCase()} très actif`,
                details: `Activité moyenne: ${avgActivity.toFixed(1)}, Consistance: ${(consistency * 100).toFixed(0)}%`,
                confidence: (avgActivity * 10) + (consistency * 40),
                data: { quadrant, avgActivity, consistency }
            });
        }
    });
    return patterns;
}

function analyzeCorrelations(historicalTables) {
    const patterns = [];
    const chipPairs = {};
    historicalTables.forEach(table => {
        const activeChips = Object.keys(table.occurrences).filter(c => table.occurrences[c].count > 0);
        for (let i = 0; i < activeChips.length; i++) {
            for (let j = i + 1; j < activeChips.length; j++) {
                const pair = `${activeChips[i]}-${activeChips[j]}`;
                chipPairs[pair] = (chipPairs[pair] || 0) + 1;
            }
        }
    });
    Object.entries(chipPairs).forEach(([pair, count]) => {
        if (count >= 2) {
            const [chip1, chip2] = pair.split('-');
            const correlation = count / historicalTables.length;
            if (correlation >= 0.4) {
                patterns.push({
                    type: 'Corrélation Forte',
                    category: 'Corrélation',
                    description: `Chips ${chip1} et ${chip2} apparaissent ensemble`,
                    details: `Co-occurrence dans ${count}/${historicalTables.length} périodes(${(correlation * 100).toFixed(0)}%)`,
                    confidence: correlation * 80,
                    data: { chip1: parseInt(chip1), chip2: parseInt(chip2), correlation }
                });
            }
        }
    });
    return patterns;
}

function generatePredictions(patterns, historicalTables) {
    const predictions = [];
    const strongRecurrences = patterns.filter(p => p.category === 'Récurrence' && p.confidence >= 70);
    strongRecurrences.forEach(pattern => {
        predictions.push({
            type: 'Prédiction Forte',
            category: 'Prédiction',
            description: `Chip ${pattern.chipNumber} probable dans la prochaine période`,
            details: `Basé sur une récurrence de ${(pattern.data.consistency * 100).toFixed(0)}%`,
            confidence: pattern.confidence * 0.8,
            chipNumber: pattern.chipNumber,
            data: { basedOn: 'recurrence', originalConfidence: pattern.confidence }
        });
    });
    const cycles = patterns.filter(p => p.category === 'Cycle' && p.confidence >= 60);
    cycles.forEach(pattern => {
        predictions.push({
            type: 'Prédiction Cyclique',
            category: 'Prédiction',
            description: `Chip ${pattern.chipNumber} attendu selon cycle de ${pattern.data.cycleLength} périodes`,
            details: `Cycle détecté avec ${(pattern.data.consistency * 100).toFixed(0)}% de consistance`,
            confidence: pattern.confidence * 0.7,
            chipNumber: pattern.chipNumber,
            data: { basedOn: 'cycle', cycleLength: pattern.data.cycleLength }
        });
    });
    return predictions;
}

function displayPatterns(patterns) {
    const container = document.getElementById('patternsContainer');
    const groupedPatterns = {
        'Récurrence': patterns.filter(p => p.category === 'Récurrence'),
        'Cycle': patterns.filter(p => p.category === 'Cycle'),
        'Séquence': patterns.filter(p => p.category === 'Séquence'),
        'Spatial': patterns.filter(p => p.category === 'Spatial'),
        'Corrélation': patterns.filter(p => p.category === 'Corrélation'),
        'Prédiction': patterns.filter(p => p.category === 'Prédiction')
    };
    let html = '';
    html += `<div class="patterns-summary"><h4>📈 Résumé de l'Analyse</h4><div class="summary-stats"><span class="stat-item">Total: ${patterns.length} patterns</span><span class="stat-item">Confiance élevée: ${patterns.filter(p => p.confidence >= 80).length}</span><span class="stat-item">Prédictions: ${groupedPatterns['Prédiction'].length}</span></div></div>`;
    Object.entries(groupedPatterns).forEach(([category, categoryPatterns]) => {
        if (categoryPatterns.length > 0) {
            html += `<div class="pattern-category">`;
            html += `<h4 class="category-header">${getCategoryIcon(category)} ${category} (${categoryPatterns.length})</h4>`;
            categoryPatterns.forEach((pattern, pIdx) => {
                const confidenceColor = getConfidenceColor(pattern.confidence);
                const confidenceClass = getConfidenceClass(pattern.confidence);
                const patternId = `pattern-${category}-${pIdx}`;

                // Stocker le pattern dans un objet global pour un accès facile au clic
                if (!window._patternRegistry) window._patternRegistry = {};
                window._patternRegistry[patternId] = pattern;

                html += `<div class="pattern-item ${confidenceClass}" id="${patternId}" style="border-left-color: ${confidenceColor};" onclick="handlePatternClick('${patternId}')"><div class="pattern-header"><h5>${pattern.type}</h5><span class="confidence-badge" style="background: ${confidenceColor};">${Math.round(pattern.confidence)}%</span></div><p class="pattern-description"><strong>${pattern.description}</strong></p><p class="pattern-details">${pattern.details}</p>${pattern.chipNumber ? `<div class="chip-highlight">Chip ${pattern.chipNumber}</div>` : ''}</div>`;
            });
            html += `</div>`;
        }
    });
    if (patterns.length === 0) {
        html = '<div class="no-patterns">Aucun pattern significatif détecté. Essayez avec plus de données historiques.</div>';
    }
    container.innerHTML = html;
}

function handlePatternClick(patternId) {
    const pattern = window._patternRegistry ? window._patternRegistry[patternId] : null;
    if (pattern) {
        showPatternDetails(pattern);
    }
}

function getCategoryIcon(category) {
    const icons = { 'Récurrence': '🔄', 'Cycle': '⭕', 'Séquence': '➡️', 'Spatial': '🗺️', 'Corrélation': '🔗', 'Prédiction': '🔮' };
    return icons[category] || '📊';
}

function getConfidenceColor(confidence) {
    if (confidence >= 90) return '#27ae60';
    if (confidence >= 80) return '#2ecc71';
    if (confidence >= 70) return '#f39c12';
    if (confidence >= 60) return '#e67e22';
    if (confidence >= 50) return '#e74c3c';
    return '#95a5a6';
}

function getConfidenceClass(confidence) {
    if (confidence >= 80) return 'high-confidence';
    if (confidence >= 60) return 'medium-confidence';
    return 'low-confidence';
}

function showPatternDetails(pattern) {
    let details = `${pattern.type}\n\n`;
    details += `Catégorie: ${pattern.category}\n`;
    details += `Confiance: ${Math.round(pattern.confidence)}%\n\n`;
    details += `Description: ${pattern.description}\n\n`;
    details += `Détails: ${pattern.details}\n\n`;

    if (pattern.data) {
        details += `Données techniques: \n`;
        Object.entries(pattern.data).forEach(([key, value]) => {
            details += `- ${key}: ${typeof value === 'number' ? value.toFixed(2) : value}\n`;
        });
    }

    if (confirm(details + "\n\nSouhaitez-vous lancer une analyse prédictive sur ce pattern ?")) {
        console.log("Redirection vers Analyse Prédictive pour:", pattern);
        const params = new URLSearchParams({
            universe: currentAnalysisData.universe || 'mundo',
            attribute: pattern.attribute || 'chip',
            value: pattern.data?.value || pattern.chipNumber || pattern.value,
            mode: 'refinement'
        });
        window.location.href = `katula-predictive-analytics.html?${params.toString()}`;
    }
}

function showTableDetails(tableIndex) {
    const tableData = currentAnalysisData.tablesData[tableIndex];
    alert(`Détails ${tableData.year} ${tableData.period}: \n\nOccurrences: ${tableData.occurrences.join(', ')}\nTotal tirages: ${tableData.totalDraws}`);
}

function showTableStats(tableIndex) {
    const tableData = currentAnalysisData.tablesData[tableIndex];
    const coverage = ((tableData.occurrences.length / 48) * 100).toFixed(1);
    alert(`Statistiques ${tableData.year} ${tableData.period}: \n\nCouverture: ${coverage}%\nChips actifs: ${tableData.occurrences.length}/48\nTirages: ${tableData.totalDraws}`);
}

function showChipTemporalDetails(chipNumber, tableTitle, occurrence, event) {
    if (event && event.stopPropagation) event.stopPropagation();
    try {
        console.groupCollapsed(`[showChipTemporalDetails] chip ${chipNumber} - ${tableTitle}`);
        console.log('received occurrence:', occurrence);
        try { console.log('occurrence.details sample:', (occurrence && occurrence.details) ? occurrence.details.slice(0, 5) : null); } catch (e) { console.log('occurrence.details error', e); }
        const aggregated = getAggregatedOccurrence(chipNumber);
        console.log('aggregated occurrence from currentAnalysisData:', aggregated);
        console.log('currentAnalysisData.tablesData count:', currentAnalysisData?.tablesData?.length || 0);
        console.groupEnd();
    } catch (e) { console.warn('Logging error in showChipTemporalDetails', e); }
    const markingType = markingOptions.type;
    // If occurrence has no useful details, prefer aggregated occurrence
    const aggregatedOcc = getAggregatedOccurrence(chipNumber);
    const effectiveOccurrence = (occurrence && (occurrence.details && occurrence.details.length > 0)) ? occurrence : aggregatedOcc;
    const attributeValue = getAttributeValue(chipNumber, markingType, effectiveOccurrence);
    const selectionKey = `${attributeValue}-${tableTitle}-${markingType}`;
    if (selectedChips.has(selectionKey)) {
        selectedChips.delete(selectionKey);
        removeAttributeMarking(attributeValue, markingType, tableTitle);
    } else {
        selectedChips.add(selectionKey);
        addAttributeMarking(attributeValue, markingType, tableTitle, effectiveOccurrence);
        updateCurrentSelection(attributeValue, markingType, tableTitle);
    }
    updateSelectionDisplay();
    showAttributeDetails(chipNumber, attributeValue, markingType, tableTitle, effectiveOccurrence);
}

// Gestionnaire dédié pour les clics dans la légende (dénomination / tiroir)
function showLegendAttribute(chipNumber, attributeValue, markingType, tableTitle, occurrence, event) {
    if (event && event.stopPropagation) event.stopPropagation();
    try {
        console.groupCollapsed(`[showLegendAttribute] chip ${chipNumber} - ${markingType}=${attributeValue}`);
        console.log('received occurrence for legend element:', occurrence);
        try { console.log('occurrence.details sample:', (occurrence && occurrence.details) ? occurrence.details.slice(0, 5) : null); } catch (e) { console.log('occurrence.details error', e); }
        const aggregated = getAggregatedOccurrence(chipNumber);
        console.log('aggregated occurrence from currentAnalysisData:', aggregated);
        console.groupEnd();
    } catch (e) { console.warn('Logging error in showLegendAttribute', e); }
    // Normaliser attributeValue si c'est un nombre ou object
    const attr = attributeValue;
    const selectionKey = `${attr}-${tableTitle}-${markingType}`;

    // Pour la légende, on veut toujours l'occurrence effective (agrégée si besoin)
    const effectiveOccurrence = (occurrence && occurrence.details && occurrence.details.length > 0) ? occurrence : getAggregatedOccurrence(chipNumber);

    if (selectedChips.has(selectionKey)) {
        selectedChips.delete(selectionKey);
        removeAttributeMarking(attr, markingType, tableTitle);
    } else {
        selectedChips.add(selectionKey);
        addAttributeMarking(attr, markingType, tableTitle, effectiveOccurrence);
        updateCurrentSelection(attr, markingType, tableTitle);
    }
    updateSelectionDisplay();
    showAttributeDetails(chipNumber, attr, markingType, tableTitle, effectiveOccurrence);
}

function getAttributeValue(chipNumber, markingType, occurrence) {
    switch (markingType) {
        case 'chip': return chipNumber;
        case 'combination': return occurrence?.combination_id || `combo_${chipNumber}`;
        case 'denomination': return occurrence?.denomination || `denom_${chipNumber}`;
        case 'tome': return occurrence?.tome || `tome${(chipNumber % 4) + 1}`;
        case 'granque': return occurrence?.granque || `Q${(chipNumber % 6) + 1}`;
        case 'forme': return occurrence?.forme || getChipForme(chipNumber);
        case 'parite': return chipNumber % 2 === 0 ? 'pair' : 'impair';
        case 'zone':
        case 'petique':
            const row = Math.ceil(chipNumber / 6);
            const col = ((chipNumber - 1) % 6) + 1;
            if (row <= 4 && col <= 3) return 'q1';
            if (row <= 4 && col > 3) return 'q2';
            if (row > 4 && col <= 3) return 'q3';
            return 'q4';
        case 'ligne': return Math.ceil(chipNumber / 6);
        case 'colonne': return ((chipNumber - 1) % 6) + 1;
        default: return chipNumber;
    }
}

// Agrège les occurrences pour un chip depuis les tables de l'analyse courante
function getAggregatedOccurrence(chipNumber) {
    const aggregated = { count: 0, details: [], attributes: [], totalDraws: 0 };
    if (!currentAnalysisData || !Array.isArray(currentAnalysisData.tablesData)) return aggregated;
    currentAnalysisData.tablesData.forEach(td => {
        const occ = (td.occurrences && (td.occurrences[chipNumber] || td.occurrences[String(chipNumber)] || td.occurrences[`chip${chipNumber}`])) || null;
        if (occ) {
            aggregated.count += (occ.count || 0);
            if (Array.isArray(occ.details)) aggregated.details = aggregated.details.concat(occ.details);
            if (Array.isArray(occ.attributes)) aggregated.attributes = aggregated.attributes.concat(occ.attributes);
            aggregated.totalDraws += (td.totalDraws || 0);
        }
    });
    // Dédupliquer les détails (par timestamp+combinaison+denomination)
    const seen = new Set();
    const uniqueDetails = [];
    aggregated.details.forEach(d => {
        const ts = d.timestamp || d.date || d.last_date || '';
        const combo = d.combination_id || d.combination || d.combo || d.attribute || '';
        const denom = d.denomination || d.denom || d.attribute || '';
        const key = `${ts}|${combo}|${denom}`;
        if (!seen.has(key)) {
            seen.add(key);
            uniqueDetails.push(d);
        }
    });
    aggregated.details = uniqueDetails;
    // Dédupliquer attributs
    aggregated.attributes = Array.from(new Set(aggregated.attributes || []));
    // Si nous avons des détails, aligner le count sur le nombre de détails uniques
    if (aggregated.details.length > 0) aggregated.count = aggregated.details.length;
    return aggregated;
}

function getChipForme(chipNumber) {
    const formes = ['carre', 'triangle', 'cercle', 'rectangle', 'carre-triangle', 'cercle-rectangle'];
    return formes[(chipNumber - 1) % formes.length];
}

function getChipZone(chipNumber) {
    if (chipNumber <= 12) return 'Q1';
    if (chipNumber <= 24) return 'Q2';
    if (chipNumber <= 36) return 'Q3';
    return 'Q4';
}

function updateCurrentSelection(attributeValue, markingType, tableTitle) {
    if (!currentSelection.periods.includes(tableTitle)) currentSelection.periods.push(tableTitle);
    if (!currentSelection[markingType]) currentSelection[markingType] = [];
    if (!currentSelection[markingType].includes(attributeValue)) currentSelection[markingType].push(attributeValue);
    if (markingType === 'chip' && !currentSelection.chips.includes(attributeValue)) currentSelection.chips.push(attributeValue);
}

function updateTablesConfiguration() {
    const count = parseInt(document.getElementById('tablesCountSelect').value);
    initializeTablesConfiguration(count);
    const globalPeriodSelect = document.getElementById('globalPeriodSelect');
    if (globalPeriodSelect && globalPeriodSelect.value) updateAllTablesFromGlobalPeriod(globalPeriodSelect.value);
}

function initializeTablesConfiguration(count) {
    tablesConfiguration = [];
    const currentYear = new Date().getFullYear();
    for (let i = 0; i < count; i++) {
        tablesConfiguration.push({
            id: i + 1,
            title: null, // Allow override by bdData.period_label
            dateStart: `${currentYear - count + i + 1}-01-01`,
            dateEnd: `${currentYear - count + i + 1}-12-31`,
            period: 'ALL',
            type: i === count - 1 ? 'prediction' : 'historical'
        });
    }
}

function showTablesConfiguration() {
    const count = parseInt(document.getElementById('tablesCountSelect').value);
    if (tablesConfiguration.length !== count) initializeTablesConfiguration(count);
    const globalPeriodSelect = document.getElementById('globalPeriodSelect');
    if (globalPeriodSelect && globalPeriodSelect.value) updateAllTablesFromGlobalPeriod(globalPeriodSelect.value);
    displayTablesConfiguration();
    document.getElementById('tablesConfigPanel').style.display = 'block';
}

function hideTablesConfiguration() {
    document.getElementById('tablesConfigPanel').style.display = 'none';
}

// Show marking options panel
function showMarkingOptions() {
    document.getElementById('markingOptionsPanel').style.display = 'block';
}

// Hide marking options panel
function hideMarkingOptions() {
    document.getElementById('markingOptionsPanel').style.display = 'none';
}

// Apply marking options
function applyMarkingOptions() {
    markingOptions.style = document.querySelector('input[name="markingStyle"]:checked')?.value || 'cross';
    markingOptions.colors[1] = document.getElementById('color1')?.value || '#e74c3c';
    markingOptions.colors[2] = document.getElementById('color2')?.value || '#f39c12';
    markingOptions.colors[3] = document.getElementById('color3')?.value || '#8e44ad';
    markingOptions.showCount = document.getElementById('showCount')?.checked ?? true;
    markingOptions.showTooltip = document.getElementById('showTooltip')?.checked ?? true;
    markingOptions.animateMarking = document.getElementById('animateMarking')?.checked ?? false;

    hideMarkingOptions();

    if (currentAnalysisData) {
        displayTemporalTables(currentAnalysisData);
    }
    console.log('✅ Options de marquage appliquées:', markingOptions);
}

function displayTablesConfiguration() {
    const container = document.getElementById('tablesConfigContainer');
    let html = '';
    tablesConfiguration.forEach((config, index) => {
        const typeOptions = `<option value="historical"${config.type === 'historical' ? 'selected' : ''}>Historique</option><option value="prediction"${config.type === 'prediction' ? 'selected' : ''}>Prédiction</option>`;
        let periodOptions = '';
        if (globalAvailablePeriods.length > 0) {
            periodOptions += `<option value="ALL"${config.period === 'ALL' ? 'selected' : ''}>Toute l'année</option>`;
            globalAvailablePeriods.forEach(p => {
                periodOptions += `<option value="${p.id}"${String(p.id) === String(config.period) ? 'selected' : ''}>${p.name}</option>`;
            });
            periodOptions += `<option value="CUSTOM"${config.period === 'CUSTOM' ? 'selected' : ''}>Personnalisée</option>`;
        } else {
            periodOptions = `<option value="ALL"${config.period === 'ALL' ? 'selected' : ''}>Toute l'année</option><option value="P1"${config.period === 'P1' ? 'selected' : ''}>Période 1</option><option value="P2"${config.period === 'P2' ? 'selected' : ''}>Période 2</option><option value="P3"${config.period === 'P3' ? 'selected' : ''}>Période 3</option><option value="P4"${config.period === 'P4' ? 'selected' : ''}>Période 4</option><option value="CUSTOM"${config.period === 'CUSTOM' ? 'selected' : ''}>Personnalisée</option>`;
        }
        html += `<div class="table-config"><h4>Table ${index + 1}</h4><div class="config-row"><label>Titre:</label><input type="text" id="title_${index}" value="${config.title}" onchange="updateTableConfig(${index}, 'title', this.value)"></div><div class="config-row"><label>Type:</label><select id="type_${index}" onchange="updateTableConfig(${index}, 'type', this.value)">${typeOptions}</select></div><div class="config-row"><label>Période:</label><select id="period_${index}" disabled style="background-color: #f0f0f0; cursor: not-allowed;" title="Géré par la Session de Référence globale">${periodOptions}</select><small style="display:block; font-size: 0.7em; color: #7f8c8d; margin-top: 2px;">(Sync Global)</small></div><div class="config-row"><label>Début:</label><input type="date" id="dateStart_${index}" value="${config.dateStart}" onchange="updateTableConfig(${index}, 'dateStart', this.value)"></div><div class="config-row"><label>Fin:</label><input type="date" id="dateEnd_${index}" value="${config.dateEnd}" onchange="updateTableConfig(${index}, 'dateEnd', this.value)"></div></div>`;
    });
    container.innerHTML = html;
}

function updateTableConfig(index, field, value) {
    if (tablesConfiguration[index]) {
        tablesConfiguration[index][field] = value;
    }
}

function applyTablesConfiguration() {
    hideTablesConfiguration();
    const count = tablesConfiguration.length + 1;
    document.getElementById('tablesContainer').className = `tables-grid grid-${count}`;
}

async function generateTemporalAnalysis() {
    const universe = document.getElementById('universeSelect').value;
    if (tablesConfiguration.length === 0) {
        const count = parseInt(document.getElementById('tablesCountSelect').value);
        initializeTablesConfiguration(count);
    }
    const container = document.getElementById('tablesContainer');
    container.innerHTML = '<div class="loading">🔄 Génération de l\'analyse temporelle...</div>';
    container.className = `tables-grid grid-${tablesConfiguration.length + 1}`;
    try {
        const tablesData = await Promise.all(tablesConfiguration.map(config => getTemporalDataFromConfig(universe, config)));
        currentAnalysisData = { universe, tablesConfiguration, tablesData };
        try {
            console.groupCollapsed('[generateTemporalAnalysis] currentAnalysisData summary');
            console.log('universe:', universe);
            console.log('tablesConfiguration.length:', tablesConfiguration.length);
            console.log('tablesData.length:', tablesData.length);
            console.log('tablesData sample:', tablesData.slice(0, 2));
            console.groupEnd();
        } catch (e) { console.warn('Logging error in generateTemporalAnalysis', e); }
        if (!globalReferenceData || globalReferenceData.universe !== universe) {
            globalReferenceData = await fetchReferenceData(universe);
        }
        displayTemporalTables(currentAnalysisData);
        setTimeout(() => { loadRealDrawHistory(); }, 1500);
    } catch (error) {
        console.error('Erreur génération analyse:', error);
        container.innerHTML = '<div class="error">Erreur lors de la génération de l\'analyse temporelle</div>';
    }
}

async function getTemporalDataFromConfig(universe, config) {
    try {
        const markingType = markingOptions.type;
        const sessionId = document.getElementById('globalPeriodSelect')?.value;
        // Correction de l'URL pour pointer vers le bon endpoint backend
        let url = `${API_BASE}/temporal-drawer-data?universe=${universe}&date_start=${config.dateStart}&date_end=${config.dateEnd}&marking_type=${markingType}`;
        if (sessionId) url += `&session_id=${sessionId}`;
        console.log('[getTemporalDataFromConfig] Fetching Real Data:', url);
        const response = await fetch(url);
        if (!response.ok) throw new Error(`Erreur API: ${response.status}`);
        const apiData = await response.json();
        console.log('[getTemporalDataFromConfig] API Response:', apiData);
        const occurrences = {};
        // Backend retourne directement l'objet, pas de wrapper .data
        const bdData = apiData;
        Object.entries(bdData.occurrences || {}).forEach(([chipKey, data]) => {
            occurrences[chipKey] = { count: data.count || 0, attributes: data.attributes || [], details: data.details || [] };
        });
        console.log('[getTemporalDataFromConfig] Occurrences extracted:', Object.keys(occurrences).length, 'chips, keys:', Object.keys(occurrences));

        // Extraire l'année et la période pour l'affichage
        const year = config.dateStart ? config.dateStart.substring(0, 4) : new Date().getFullYear();
        const title = bdData.period_label || config.title || `Table ${config.id}`;

        return {
            ...config,
            universe,
            occurrences,
            markingType,
            totalDraws: bdData.total_draws || 0,
            periodInfo: bdData.period_info || {},
            isRealData: true,
            year: year,
            title: title
        };
    } catch (error) {
        console.warn('[getTemporalDataFromConfig] Error, falling back to simulated data:', error.message);
        return await getSimulatedTemporalData(universe, config);
    }
}

async function getSimulatedTemporalData(universe, config) {
    const markingType = markingOptions.type;
    const occurrences = {};
    const numEvents = Math.floor(Math.random() * 15) + 5;
    for (let i = 0; i < numEvents; i++) {
        const chipNumber = Math.floor(Math.random() * 48) + 1;
        let attributeKey;
        switch (markingType) {
            case 'chip': attributeKey = chipNumber; break;
            case 'combination': attributeKey = `combo_${Math.floor(Math.random() * 100) + 1}`; break;
            case 'denomination': attributeKey = `denom_${Math.floor(Math.random() * 200) + 1}`; break;
            case 'tome': attributeKey = `tome${Math.floor((chipNumber - 1) / 12) + 1}`; break;
            case 'forme': attributeKey = ['carre', 'triangle', 'cercle', 'rectangle'][Math.floor(Math.random() * 4)]; break;
            case 'granque': attributeKey = `Q${Math.floor((chipNumber - 1) / 8) + 1}`; break;
            default: attributeKey = chipNumber;
        }
        if (!occurrences[chipNumber]) occurrences[chipNumber] = { count: 0, attributes: [], details: [] };
        occurrences[chipNumber].count++;
        occurrences[chipNumber].attributes.push(attributeKey);
        occurrences[chipNumber].details.push({
            attribute: attributeKey, type: markingType,
            timestamp: new Date(config.dateStart).getTime() + Math.random() * (new Date(config.dateEnd).getTime() - new Date(config.dateStart).getTime())
        });
    }
    return { ...config, universe, occurrences, markingType, totalDraws: Math.floor(Math.random() * 20) + 10, isRealData: false };
}

function generateMiniKatulaGrid(tableData) {
    const universe = currentAnalysisData?.universe || 'mundo';
    const universeFormes = DRAWER_ORDER[universe] || ['carre', 'triangle', 'cercle', 'rectangle'];
    const markingStyle = markingOptions?.style || 'cross';
    const markingType = markingOptions?.type || 'chip';

    // Condition d'affichage des tiroirs: UNIQUEMENT si type = forme
    const showDrawers = markingType === 'forme';

    // Calcul dynamique de la grille (cols x rows)
    const count = universeFormes.length;
    let cols = 2;
    if (count > 4) cols = 3;
    if (count > 9) cols = 4;
    const rows = Math.ceil(count / cols);
    const gridStyle = `grid-template-columns: repeat(${cols}, 1fr); grid-template-rows: repeat(${rows}, 1fr);`;

    let html = '';

    for (let chipNumber = 1; chipNumber <= 48; chipNumber++) {
        let hasOccurred = false;
        let details = [];
        let occurrence = null;

        // Extraction robuste
        if (Array.isArray(tableData.occurrences)) {
            if (tableData.occurrences.includes(chipNumber)) hasOccurred = true;
        } else if (tableData.occurrences && typeof tableData.occurrences === 'object') {
            occurrence = tableData.occurrences[chipNumber] || tableData.occurrences[String(chipNumber)] || tableData.occurrences[`chip${chipNumber}`];
            if (occurrence && occurrence.count > 0) {
                hasOccurred = true;
                details = occurrence.details || [];
            }
        }

        let content = '';
        let cellClasses = 'mini-chip-cell';
        let tooltip = `Chip ${chipNumber}`;
        let styleAttr = ''; // Correction couleur dynamique

        if (hasOccurred) {
            if (showDrawers) {
                // MODE TIROIRS (Formes)
                let drawersHtml = `<div class="chip-drawer-container" style="${gridStyle}">`;
                universeFormes.forEach((forme, index) => {
                    let isDrawerMarked = false;
                    if (details.length > 0) {
                        isDrawerMarked = details.some(d => {
                            const f = d.forme || d.denomination || d.attribute || '';
                            const fStr = String(f).toLowerCase();
                            const formeStr = String(forme).toLowerCase();
                            return fStr === formeStr || fStr.includes(formeStr);
                        });
                    } else {
                        if (index === (chipNumber % universeFormes.length)) isDrawerMarked = true;
                    }
                    // Pour les tiroirs, on pourrait aussi appliquer la couleur ici si nécessaire
                    const drawerClass = isDrawerMarked ? `occurred marking-${markingStyle}` : '';
                    drawersHtml += `<div class="chip-drawer ${drawerClass}" title="${forme}"></div>`;
                });
                drawersHtml += '</div>';
                content = `<div class="chip-number-overlay">${chipNumber}</div>${drawersHtml}`;
            } else {
                // MODE STANDARD (Chip global)
                cellClasses += ` occurred marking-${markingStyle}`;
                content = `<div class="chip-number-overlay">${chipNumber}</div>`;

                // Calcul couleur selon fréquence
                const countVal = occurrence?.count || 1;
                const mColors = markingOptions.colors || { 1: '#e74c3c', 2: '#f39c12', 3: '#8e44ad' };
                const color = mColors[Math.min(countVal, 3)] || '#e74c3c';
                styleAttr = `style="--marking-color: ${color};"`;

                if (markingOptions.showCount && occurrence && occurrence.count > 1) {
                    content += `<span class="occurrence-counter">${occurrence.count}</span>`;
                }
            }
        } else {
            content = `<div class="chip-number-overlay">${chipNumber}</div>`;
        }

        const countVal = occurrence?.count || 0;
        const dataCountAttr = markingStyle === 'number' ? `data-count="${countVal}"` : '';

        html += `<div class="${cellClasses}" ${styleAttr} ${dataCountAttr} data-chip="${chipNumber}" onclick="showChipTemporalDetails(${chipNumber}, '${tableData.title}', ${JSON.stringify(occurrence || {}).replace(/"/g, '&quot;')}, event)" title="${tooltip}">${content}</div>`;
    }
    return html;
}

function addAttributeMarking(attributeValue, markingType, tableTitle, occurrence) {
    const elements = getElementsForAttribute(attributeValue, markingType, tableTitle);

    // Calcul de la couleur selon la récurrence (Hardi contre les propriétés manquantes)
    const countVal = occurrence?.count || (Array.isArray(occurrence?.details) ? occurrence.details.length : 1);
    const mColors = (markingOptions && markingOptions.colors) || { 1: '#e74c3c', 2: '#f39c12', 3: '#8e44ad' };
    const color = mColors[Math.min(countVal, 3)] || '#e74c3c';

    console.log(`[addAttributeMarking] Attribut: ${attributeValue}, Count: ${countVal}, Color: ${color}`);

    elements.forEach(element => {
        element.classList.add('selection-active');
        // Ajouter aussi le style de marquage actuel pour visibilité
        const currentStyle = markingOptions?.style || 'cross';
        element.classList.add(`marking-${currentStyle}`);

        element.style.setProperty('--marking-color', color);
        element.setAttribute('data-marked-attribute', `${markingType}:${attributeValue}`);

        if (currentStyle === 'number') {
            element.setAttribute('data-count', countVal);
        }
    });
}

function removeAttributeMarking(attributeValue, markingType, tableTitle) {
    const elements = getElementsForAttribute(attributeValue, markingType, tableTitle);
    elements.forEach(element => {
        element.classList.remove('selection-active');
        // Retirer tous les styles de marquage possibles
        element.classList.remove('marking-cross', 'marking-dot', 'marking-square', 'marking-number');

        element.style.removeProperty('--marking-color');
        element.removeAttribute('data-marked-attribute');
        element.removeAttribute('data-count');
    });
}

function getElementsForAttribute(attributeValue, markingType, tableTitle) {
    let elements = [];
    switch (markingType) {
        case 'chip': elements = document.querySelectorAll(`[data-chip="${attributeValue}"]`); break;
        case 'denomination': elements = document.querySelectorAll(`[data-denomination="${attributeValue}"]`); if (elements.length === 0) elements = document.querySelectorAll(`[title*="${attributeValue}"]`); break;
        case 'tome':
            elements = document.querySelectorAll(`[data-tome="${attributeValue}"]`);
            if (elements.length === 0) {
                const tomeNumber = parseInt(attributeValue.replace('tome', ''));
                const startChip = (tomeNumber - 1) * 12 + 1;
                const endChip = tomeNumber * 12;
                for (let chip = startChip; chip <= endChip; chip++) {
                    const chipElements = document.querySelectorAll(`[data-chip="${chip}"]`);
                    elements = [...elements, ...chipElements];
                }
            }
            break;
        case 'granque':
            elements = document.querySelectorAll(`[data-granque="${attributeValue}"]`);
            if (elements.length === 0) {
                const granqueNumber = parseInt(attributeValue.replace('Q', ''));
                const startChipG = (granqueNumber - 1) * 8 + 1;
                const endChipG = granqueNumber * 8;
                for (let chip = startChipG; chip <= endChipG; chip++) {
                    const chipElements = document.querySelectorAll(`[data-chip="${chip}"]`);
                    elements = [...elements, ...chipElements];
                }
            }
            break;
        case 'ligne':
            const lNum = parseInt(attributeValue);
            if (!isNaN(lNum)) {
                const lStart = (lNum - 1) * 6 + 1;
                const lEnd = lNum * 6;
                for (let i = lStart; i <= lEnd; i++) {
                    const els = document.querySelectorAll(`[data-chip="${i}"]`);
                    elements = [...elements, ...els];
                }
            }
            break;
        case 'colonne':
            const cNum = parseInt(attributeValue);
            if (!isNaN(cNum)) {
                for (let r = 0; r < 8; r++) {
                    const chip = r * 6 + cNum;
                    const els = document.querySelectorAll(`[data-chip="${chip}"]`);
                    elements = [...elements, ...els];
                }
            }
            break;
        case 'forme':
            elements = document.querySelectorAll(`[data-forme="${attributeValue}"]`);
            if (elements.length === 0) {
                const allChips = document.querySelectorAll('[data-chip]');
                allChips.forEach(chipElement => {
                    const chipNumber = parseInt(chipElement.dataset.chip);
                    if (getChipForme(chipNumber) === attributeValue) elements.push(chipElement);
                });
            }
            break;
        case 'parite':
            const allChipsP = document.querySelectorAll('[data-chip]');
            allChipsP.forEach(chipElement => {
                const chipNumber = parseInt(chipElement.dataset.chip);
                const chipParite = chipNumber % 2 === 0 ? 'pair' : 'impair';
                if (chipParite === attributeValue) elements.push(chipElement);
            });
            break;
        case 'petique':
        case 'zone':
            // Logique locale robuste pour Quadrants
            const q1 = [1, 2, 3, 7, 8, 9, 13, 14, 15, 19, 20, 21];
            const q2 = [4, 5, 6, 10, 11, 12, 16, 17, 18, 22, 23, 24];
            const q3 = [25, 26, 27, 31, 32, 33, 37, 38, 39, 43, 44, 45];
            const q4 = [28, 29, 30, 34, 35, 36, 40, 41, 42, 46, 47, 48];

            const allChipsZ = document.querySelectorAll('[data-chip]');
            const targetZone = attributeValue.toLowerCase(); // q1, q2...

            allChipsZ.forEach(chipElement => {
                const chipNumber = parseInt(chipElement.dataset.chip);
                let chipZone = 'q4'; // Default
                if (q1.includes(chipNumber)) chipZone = 'q1';
                else if (q2.includes(chipNumber)) chipZone = 'q2';
                else if (q3.includes(chipNumber)) chipZone = 'q3';

                if (chipZone === targetZone) elements.push(chipElement);
            });
            break;
        default: elements = document.querySelectorAll(`[data-chip="${attributeValue}"]`);
    }
    if (tableTitle) {
        elements = Array.from(elements).filter(element => !element.dataset.table || element.dataset.table.includes(tableTitle));
    }
    return Array.from(elements);
}

function showAttributeDetails(chipNumber, attributeValue, markingType, tableTitle, occurrence) {
    const typeLabels = { 'chip': 'Chip', 'denomination': 'Dénomination', 'tome': 'Tome', 'granque': 'Granque', 'forme': 'Forme', 'parite': 'Parité', 'zone': 'Zone Géométrique', 'combination': 'Combinaison' };
    const typeLabel = typeLabels[markingType] || 'Attribut';
    const markedElements = getElementsForAttribute(attributeValue, markingType, tableTitle);

    const detailsArray = Array.isArray(occurrence?.details) ? occurrence.details : [];

    // Construire un mapping par dénomination pour résumer les occurrences
    const denomMap = {};
    detailsArray.forEach(d => {
        const denom = d.denomination || d.denom || d.attribute || (markingType === 'denomination' ? attributeValue : 'N/A');
        const combo = d.combination_id || d.combination || d.combo || null;
        const ts = d.timestamp || d.date || d.last_date || null;
        const dateStr = ts ? (isNaN(Number(ts)) ? new Date(ts).toLocaleString() : new Date(Number(ts)).toLocaleString()) : null;
        const loto = d.lottery || d.loto || d.loto_name || d.source || d.session || d.lotoName || d.loto || null;
        if (!denomMap[denom]) denomMap[denom] = { count: 0, combos: new Set(), dates: [], lotos: new Set() };
        denomMap[denom].count += 1;
        if (combo) denomMap[denom].combos.add(combo);
        if (dateStr) denomMap[denom].dates.push(dateStr);
        if (loto) denomMap[denom].lotos.add(loto);
    });

    const totalOccurrences = occurrence?.count || detailsArray.length || 0;
    let lines = [];
    lines.push(`🎯 ${typeLabel.toUpperCase()}: ${attributeValue} - ${tableTitle}`);
    lines.push(`📊 Occurrences totales: ${totalOccurrences}`);

    if (Object.keys(denomMap).length > 0) {
        lines.push('');
        lines.push('Détails par dénomination:');
        Object.entries(denomMap).forEach(([denom, info]) => {
            const combos = Array.from(info.combos).slice(0, 6).join(', ') || 'N/A';
            const dates = info.dates.slice(-6).reverse().join(' | ') || 'N/A';
            const lotos = Array.from(info.lotos).join(', ') || 'N/A';
            lines.push(`- ${denom}: ${info.count} occurrence(s) — Combos: ${combos} — Dates: ${dates} — Lotos: ${lotos}`);
        });
    } else if (detailsArray.length > 0) {
        // Si aucun denom clef, lister les détails bruts
        lines.push('Détails:');
        detailsArray.slice(-6).reverse().forEach(d => {
            const combo = d.combination_id || d.combination || d.combo || 'N/A';
            const ts = d.timestamp || d.date || d.last_date || null;
            const dateStr = ts ? (isNaN(Number(ts)) ? new Date(ts).toLocaleString() : new Date(Number(ts)).toLocaleString()) : 'N/D';
            const loto = d.lottery || d.loto || d.loto_name || d.source || d.session || d.lotoName || 'N/A';
            const denom = d.denomination || d.denom || d.attribute || 'N/A';
            lines.push(`- ${denom} | combo: ${combo} | date: ${dateStr} | loto: ${loto}`);
        });
    } else {
        lines.push('Aucun détail d\'occurrence disponible pour cet élément');
    }

    if (occurrence?.attributes && occurrence.attributes.length > 0) {
        const attrs = Array.from(new Set(occurrence.attributes)).slice(0, 8);
        lines.push('');
        lines.push(`🔎 Attributs (ex): ${attrs.join(', ')}${occurrence.attributes.length > 8 ? '...' : ''}`);
    }

    lines.push('');
    lines.push(`📍 Éléments marqués: ${markedElements.length}`);
    lines.push(`✅ Ajouté à la sélection pour analyse des tirages`);

    alert(lines.join('\n'));
}

function updateSelectionDisplay() {
    if (selectedChips.size > 0) {
        document.getElementById('resultsPanel').style.display = 'block';
        loadDrawResults();
    } else {
        document.getElementById('resultsPanel').style.display = 'none';
    }
}

async function loadDrawResults() {
    const container = document.getElementById('resultsContainer');
    container.innerHTML = '<div class="loading">🔄 Chargement des résultats de tirages...</div>';
    try {
        const universe = document.getElementById('universeSelect').value;
        const simulatedResults = generateSimulatedDrawResults();
        drawResults = simulatedResults;
        displayDrawResults(simulatedResults);
    } catch (error) {
        console.error('Erreur chargement résultats:', error);
        displayDrawResults(generateSimulatedDrawResults());
    }
}

function displayDrawResults(results) {
    const container = document.getElementById('resultsContainer');
    const markingType = markingOptions.type;
    let html = '';
    if (!results || results.length === 0) {
        html = '<div class="no-results">Aucun résultat trouvé pour la sélection</div>';
    } else {
        const typeLabels = { 'chip': 'chips', 'denomination': 'dénominations', 'tome': 'tomes', 'granque': 'granques', 'forme': 'formes', 'parite': 'parités', 'zone': 'zones', 'combination': 'combinaisons' };
        const typeLabel = typeLabels[markingType] || 'éléments';
        const selectedCount = currentSelection[markingType]?.length || 0;
        html += `<div style="text-align: center; margin-bottom: 15px; font-weight: bold; color: #27ae60;">📊 ${results.length} tirages trouvés avec vos ${typeLabel} sélectionnés <br><small>Type de marquage: ${markingType}</small></div>`;
        results.forEach(result => {
            const highlightedChips = result.chips.filter(chip => currentSelection.chips.includes(parseInt(chip)));
            html += `<div class="result-item"><div class="result-header"><span>🎲 Tirage ${result.id}</span><span class="result-date">${result.date}</span></div><div class="result-info"><strong>Univers:</strong> ${result.universe}<br><strong>Période:</strong> ${result.period}<br><strong>Correspondances ${typeLabel}:</strong> ${highlightedChips.length}/${selectedCount}<br>${highlightedChips.length > 0 ? `<strong>Détails:</strong> ${highlightedChips.join(', ')}` : ''}</div><div class="result-chips">${result.chips.map(chip => {
                const isHighlighted = isChipHighlighted(chip, result, markingType);
                const attributeInfo = getChipAttributeInfo(chip, result, markingType);
                return `<span class="result-chip ${isHighlighted ? 'highlighted' : ''}" title="${attributeInfo}">${chip}</span>`;
            }).join('')}</div></div>`;
        });
    }
    container.innerHTML = html;
}

function isChipHighlighted(chip, result, markingType) {
    const selectedAttributes = currentSelection[markingType] || [];
    if (result.attributes) {
        const chipAttr = result.attributes.find(attr => attr.chip === chip);
        if (chipAttr) return selectedAttributes.includes(chipAttr[markingType]);
    }
    return selectedAttributes.includes(getAttributeValue(chip, markingType, {}));
}

function getChipAttributeInfo(chip, result, markingType) {
    if (result.attributes) {
        const chipAttr = result.attributes.find(attr => attr.chip === chip);
        if (chipAttr) return `Chip ${chip}\n${markingType}: ${chipAttr[markingType]}\nTome: ${chipAttr.tome}\nGranque: ${chipAttr.granque}\nForme: ${chipAttr.forme}`;
    }
    return `Chip ${chip}\n${markingType}: ${getAttributeValue(chip, markingType, {})}`;
}

function generateSimulatedDrawResults() {
    const results = [];
    const universe = 'Multi-univers';
    const markingType = markingOptions.type;
    for (let i = 0; i < 15; i++) {
        const date = new Date();
        date.setDate(date.getDate() - i * 3);
        const chips = [];
        if (currentSelection[markingType] && currentSelection[markingType].length > 0 && Math.random() > 0.3) {
            const selectedAttribute = currentSelection[markingType][Math.floor(Math.random() * currentSelection[markingType].length)];
            const relevantChips = getChipsForAttribute(selectedAttribute, markingType);
            if (relevantChips.length > 0) chips.push(relevantChips[Math.floor(Math.random() * relevantChips.length)]);
        }
        while (chips.length < 6) {
            const randomChip = Math.floor(Math.random() * 48) + 1;
            if (!chips.includes(randomChip)) chips.push(randomChip);
        }
        const chipAttributes = chips.map(chip => ({
            chip: chip,
            denomination: `denom_${chip}_${Math.floor(Math.random() * 10) + 1}`,
            tome: `tome${Math.floor((chip - 1) / 12) + 1}`,
            granque: `Q${Math.floor((chip - 1) / 8) + 1}`,
            forme: getChipForme(chip),
            parite: chip % 2 === 0 ? 'pair' : 'impair',
            zone: getChipZone(chip)
        }));
        results.push({ id: `T${2000 + i}`, date: date.toLocaleDateString('fr-FR'), universe: universe, period: `Période ${i + 1}`, chips: chips.sort((a, b) => a - b), attributes: chipAttributes, markingType: markingType });
    }
    return results;
}

function getChipsForAttribute(attributeValue, markingType) {
    const chips = [];
    switch (markingType) {
        case 'chip': return [parseInt(attributeValue)];
        case 'tome':
            const tNum = parseInt(attributeValue.replace('tome', ''));
            for (let c = (tNum - 1) * 12 + 1; c <= tNum * 12; c++) chips.push(c);
            break;
        case 'granque':
            const gNum = parseInt(attributeValue.replace('Q', ''));
            for (let c = (gNum - 1) * 8 + 1; c <= gNum * 8; c++) chips.push(c);
            break;
        case 'forme':
            for (let c = 1; c <= 48; c++) if (getChipForme(c) === attributeValue) chips.push(c);
            break;
        case 'parite':
            for (let c = 1; c <= 48; c++) if ((c % 2 === 0 ? 'pair' : 'impair') === attributeValue) chips.push(c);
            break;
        case 'zone':
            for (let c = 1; c <= 48; c++) if (getChipZone(c) === attributeValue) chips.push(c);
            break;
        default: return [parseInt(attributeValue)];
    }
    return chips;
}

function exportResults() {
    if (!drawResults || drawResults.length === 0) return alert('Aucun résultat à exporter');
    downloadCSV(generateCSVExport(), `resultats_tirages_${new Date().toISOString().split('T')[0]}.csv`);
}

function showDetailedResults() {
    if (currentSelection.chips.length === 0) return alert('Aucune sélection active');
    alert(`🎯 SÉLECTION ACTIVE\n📊 Chips: ${currentSelection.chips.join(', ')}\n📅 Périodes: ${currentSelection.periods.length}\n🌍 Contexte: Multi-univers\n📈 Résultats: ${drawResults?.length || 0} tirages`);
}

function clearSelection() {
    selectedChips.clear();
    markedZones.clear();
    currentSelection = { chips: [], periods: [], universe: null };
    drawResults = [];
    document.querySelectorAll('.selection-active, .selected-zone, .marked-zone').forEach(el => {
        el.classList.remove('selection-active', 'selected-zone', 'marked-zone');
        el.style.removeProperty('--marking-color');
    });
    document.getElementById('resultsPanel').style.display = 'none';
}

function generateCSVExport() {
    let csv = 'Date,Univers,Periode,Chips,Chips_Selectionnes,Correspondances\n';
    drawResults.forEach(r => {
        const highlighted = r.chips.filter(c => currentSelection.chips.includes(parseInt(c)));
        csv += `${r.date},${r.universe},${r.period},"${r.chips.join(';')}", "${highlighted.join(';')}", ${highlighted.length}\n`;
    });
    return csv;
}

function downloadCSV(content, filename) {
    const blob = new Blob([content], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = filename;
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

function generateCombinations(numbers) {
    const combinations = [];
    for (let i = 0; i < numbers.length; i++) {
        for (let j = i + 1; j < numbers.length; j++) combinations.push([numbers[i], numbers[j]]);
    }
    return combinations;
}


function getAnalyzedDateRange() {
    const configs = (currentAnalysisData && currentAnalysisData.tablesConfiguration)
        ? currentAnalysisData.tablesConfiguration
        : tablesConfiguration;

    const usable = (configs || []).filter(cfg => cfg && cfg.dateStart && cfg.dateEnd);
    if (!usable.length) {
        const today = new Date();
        const date_end = today.toISOString().split('T')[0];
        const startObj = new Date(today);
        startObj.setFullYear(startObj.getFullYear() - 1);
        const date_start = startObj.toISOString().split('T')[0];
        return { date_start, date_end };
    }

    const date_start = usable.reduce((min, cfg) => (String(cfg.dateStart) < min ? String(cfg.dateStart) : min), String(usable[0].dateStart));
    const date_end = usable.reduce((max, cfg) => (String(cfg.dateEnd) > max ? String(cfg.dateEnd) : max), String(usable[0].dateEnd));
    return { date_start, date_end };
}

async function loadRealDrawHistory() {
    const container = document.getElementById('drawHistoryContainer');
    const panel = document.getElementById('drawHistoryPanel');

    if (!container) {
        return;
    }

    if (panel) {
        panel.style.display = 'block';
    }

    container.innerHTML = '<div class="loading">🔄 Chargement de l\'historique des tirages...</div>';

    try {
        const universe = (currentAnalysisData && currentAnalysisData.universe)
            ? currentAnalysisData.universe
            : (document.getElementById('universeSelect')?.value || 'mundo');

        const { date_start, date_end } = getAnalyzedDateRange();
        const sessionId = document.getElementById('globalPeriodSelect')?.value;

        let url = `${window.location.origin}/api/draws/real/${encodeURIComponent(universe)}?date_start=${encodeURIComponent(date_start)}&date_end=${encodeURIComponent(date_end)}`;
        if (sessionId) {
            url += `&session_id=${encodeURIComponent(sessionId)}`;
        }

        const response = await fetch(url);
        if (!response.ok) {
            throw new Error(`Erreur API historique: ${response.status}`);
        }

        const payload = await response.json();
        const rows = payload.draws || [];

        const draws = rows.map(r => {
            const isoDate = r.draw_date ? String(r.draw_date).split('T')[0] : null;
            const numbers = Array.isArray(r.winning_numbers) ? r.winning_numbers : [];
            return {
                id: r.draw_number,
                date: isoDate,
                loto_name: r.lottery_name || (r.draw_number != null ? `Tirage ${r.draw_number}` : 'Tirage'),
                name: r.lottery_name || (r.draw_number != null ? `Tirage ${r.draw_number}` : 'Tirage'),
                winning_numbers: numbers,
                chips: numbers,
                status: (r.is_no_draw || r.no_draw_reason) ? 'no-draw' : (numbers.length ? 'ok' : 'no-hold'),
                is_no_draw: Boolean(r.is_no_draw),
                is_no_hold: !numbers.length,
                no_draw_reason: r.no_draw_reason || null,
                period: 'Période Analysée',
                universe: universe
            };
        });

        displayRealDrawHistory(draws);
    } catch (error) {
        console.error('Erreur chargement historique:', error);
        container.innerHTML = '<div class="no-results">❌ Impossible de charger l\'historique des tirages.<br><small>Vérifiez le backend et les dates sélectionnées.</small></div>';
        window.loadedDraws = [];
    }
}



function displayRealDrawHistory(draws) {
    const container = document.getElementById('drawHistoryContainer');
    let html = '';

    // Helper to parse dates in DD/MM/YYYY or YYYY-MM-DD format
    function parseBestDate(dateString) {
        if (!dateString || typeof dateString !== 'string') return null;

        // Try YYYY-MM-DD first (more standard)
        if (/^\d{4}-\d{2}-\d{2}/.test(dateString)) {
            const date = new Date(dateString);
            if (!isNaN(date)) return date;
        }

        // Then try DD/MM/YYYY
        const parts = dateString.split('/');
        if (parts.length === 3) {
            const [day, month, year] = parts.map(Number);
            // Basic validation
            if (year > 1900 && month > 0 && month <= 12 && day > 0 && day <= 31) {
                return new Date(year, month - 1, day);
            }
        }

        // Fallback for other formats
        const fallbackDate = new Date(dateString);
        if (!isNaN(fallbackDate)) return fallbackDate;

        return null;
    }

    // Filtrer les tirages dont le nom est 'deleted' pour ne pas les afficher.
    const validDraws = draws.filter(draw => {
        const name = draw.loto_name || draw.name || '';
        return name.toLowerCase() !== 'deleted';
    });

    if (validDraws.length === 0) {
        container.innerHTML = '<div class="no-results">❌ Aucun historique de tirage trouvé pour la période sélectionnée.<br><small>Vérifiez que les dates configurées (dans le panneau de configuration des tables) correspondent à une période où des tirages ont eu lieu.</small></div>';
        window.loadedDraws = [];
        return;
    }

    // Group draws by period
    const drawsByPeriod = validDraws.reduce((acc, draw) => {
        const period = draw.period || 'Période Indéfinie';
        if (!acc[period]) {
            acc[period] = [];
        }
        acc[period].push(draw);
        return acc;
    }, {});

    // Get period names and sort them (newest first)
    const sortedPeriods = Object.keys(drawsByPeriod).sort((a, b) => {
        // Find the latest date in each period to sort periods themselves
        const latestDateA = drawsByPeriod[a].map(d => parseBestDate(d.date)).reduce((max, d) => d > max ? d : max, new Date(0));
        const latestDateB = drawsByPeriod[b].map(d => parseBestDate(d.date)).reduce((max, d) => d > max ? d : max, new Date(0));

        if (latestDateB - latestDateA !== 0) {
            return latestDateB - latestDateA;
        }

        // Fallback to period name parsing
        const periodNumA = parseInt(a.replace(/[^0-9]/g, '') || 0);
        const periodNumB = parseInt(b.replace(/[^0-9]/g, '') || 0);
        return periodNumB - periodNumA;
    });

    const finalDrawList = [];

    // Generate HTML
    sortedPeriods.forEach(period => {
        html += `<h4 class="period-header">${period}</h4>`;

        const periodDraws = drawsByPeriod[period];

        // Sort draws within the period (newest first)
        periodDraws.sort((a, b) => {
            const dateA = parseBestDate(a.date);
            const dateB = parseBestDate(b.date);
            if (dateA && dateB && (dateB - dateA !== 0)) {
                return dateB - dateA;
            }
            const nameA = a.name || a.loto_name || '';
            const nameB = b.name || b.loto_name || '';
            const tirageA = parseInt(nameA.replace(/[^0-9]/g, '') || 0);
            const tirageB = parseInt(nameB.replace(/[^0-9]/g, '') || 0);
            return tirageB - tirageA;
        });

        periodDraws.forEach(draw => {
            const drawIndex = finalDrawList.length; // This is the global index
            finalDrawList.push(draw);

            const numbers = draw.winning_numbers || [];
            const chips = draw.chips || [];
            const drawNum = draw.id || draw.draw_number || drawIndex + 1;
            const tirageIdentifier = `Tirage #${drawNum} - ${draw.loto_name || draw.name || ''}`;

            let itemClass = 'draw-item';
            let contentHtml = '';

            if (draw.status === 'no-draw' || draw.is_no_draw) {
                itemClass += ' no-draw';
                contentHtml = `<div class="draw-numbers"><strong>${tirageIdentifier}:</strong> <span class="no-draw-label" style="background: #ff4d4f; color: white; padding: 2px 6px; border-radius: 4px; font-size: 0.85em; margin-left: 5px;">NO DRAW</span></div>`;
            } else if (draw.status === 'no-hold' || numbers.length === 0) {
                itemClass += ' no-hold';
                contentHtml = `<div class="draw-numbers"><strong>${tirageIdentifier}:</strong> <span class="no-hold-label" style="background: #faad14; color: white; padding: 2px 6px; border-radius: 4px; font-size: 0.85em; margin-left: 5px;">NO HOLD</span></div>`;
            } else {
                contentHtml = `
                    <div class="draw-numbers">
                        <strong>Numéros:</strong> ${numbers.map(n => `<span class="draw-number">${n}</span>`).join(' ')}
                    </div>
                    <div class="draw-chips">
                        <strong>Chips:</strong> ${chips.map(c => `<span class="chip-badge" data-chip="${c}">${c}</span>`).join(' ')}
                    </div>
                `;
            }

            const univers = draw.universe || 'Multi-univers';

            html += `
                <div class="${itemClass}" data-draw-index="${drawIndex}" onclick="markDrawInMatrix(${drawIndex})">
                    <div class="draw-header">
                        <span class="draw-date">${draw.date || 'Date N/A'}</span>
                        <span class="draw-name">${tirageIdentifier}</span>
                    </div>
                    <div class="draw-info" style="font-size: 0.8em; color: #555; margin-top: 4px;">
                        <strong>Univers:</strong> ${univers}
                    </div>
                    ${contentHtml}
                </div>
            `;
        });
    });

    container.innerHTML = html;

    // Sauvegarder les tirages pour le marquage. L'index correspondra.
    window.loadedDraws = finalDrawList;
}

function markDrawInMatrix(drawIndex) {
    if (!window.loadedDraws || !window.loadedDraws[drawIndex]) return;
    const draw = window.loadedDraws[drawIndex];
    const chips = draw.chips || [];

    // Réinitialiser les marquages précédents
    document.querySelectorAll('.chip-cell.draw-marked').forEach(el => {
        el.classList.remove('draw-marked');
    });

    // Marquer les chips dans la matrice
    chips.forEach(chipId => {
        // Extraire le numéro du chip (ex: "chip12" -> 12)
        const chipNum = typeof chipId === 'string' ? chipId.replace(/[^0-9]/g, '') : chipId;
        if (chipNum) {
            const cells = document.querySelectorAll(`[data-chip="${chipNum}"], [data-chip="chip${chipNum}"]`);
            cells.forEach(cell => {
                cell.classList.add('draw-marked');
            });
        }
    });

    // Highlight le tirage sélectionné
    document.querySelectorAll('.draw-item.selected').forEach(el => el.classList.remove('selected'));
    document.querySelector(`[data-draw-index="${drawIndex}"]`)?.classList.add('selected');
}

async function loadAvailablePeriods(universe) {
    try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 5000);
        const response = await fetch(`${API_BASE}/temporal-periods/${universe}`, { signal: controller.signal });
        clearTimeout(timeoutId);
        if (response.ok) {
            const data = await response.json();
            if (data.available && data.periods) {
                globalAvailablePeriods = data.periods;
                populateGlobalPeriodSelect(data.periods);
                updateDateRangeInputs(data.earliest_date, data.latest_date);
                showPeriodInfo(data);
            }
            return data;
        }
    } catch (error) {
        console.warn('temporal-periods API not available, trying unified sessions...');
        // Fallback: charger les sessions depuis l'API unifiée
        await loadSessions();
    }
    return null;
}

async function loadSessions() {
    try {
        const API_BASE_SESSION = API_BASE.replace('/analytics', '/unified');
        const response = await fetch(`${API_BASE_SESSION}/session/sessions`);
        if (!response.ok) throw new Error('Erreur API sessions');
        const data = await response.json();
        const sessions = data.sessions || data.value || [];

        if (sessions.length > 0) {
            // Transformer les sessions en format compatible avec le select
            const periods = sessions.map(s => ({
                id: s.id,
                name: s.name,
                start_date: s.start_date ? new Date(s.start_date).toISOString().split('T')[0] : '2024-01-01',
                end_date: s.end_date || new Date().toISOString().split('T')[0],
                dataSource: s.data_source // Ajout de la source de données
            }));
            globalAvailablePeriods = periods;
            populateGlobalPeriodSelect(periods);

            // Déterminer les bornes de dates
            const dates = periods.map(p => p.start_date).filter(d => d);
            if (dates.length > 0) {
                updateDateRangeInputs(dates[dates.length - 1], new Date().toISOString().split('T')[0]);
            }
            showPeriodInfo({ available: true, earliest_date: dates[0] || '2024-01-01', latest_date: new Date().toISOString().split('T')[0], total_days: 365 });
        } else {
            showDefaultPeriodInfo();
        }
    } catch (error) {
        console.error('Erreur chargement sessions:', error);
        showDefaultPeriodInfo();
    }
}

function showDefaultPeriodInfo() {
    const infoDiv = document.getElementById('periodInfo') || createPeriodInfoDiv();
    infoDiv.innerHTML = `<div class="period-info" style="background: #fff3cd; border-color: #ffc107;"><strong>⚠️ Mode dégradé: </strong> API temporelle non disponible <br><small>Redémarrez le backend pour utiliser les vraies données</small></div>`;
}

function updateDateRangeInputs(earliestDate, latestDate) {
    document.querySelectorAll('input[type="date"]').forEach(input => {
        if (earliestDate) input.min = earliestDate;
        if (latestDate) input.max = latestDate;
    });
}

function showPeriodInfo(periodData) {
    const infoDiv = document.getElementById('periodInfo') || createPeriodInfoDiv();
    infoDiv.innerHTML = `<div class="period-info"><strong>📅 Données disponibles:</strong> ${periodData.earliest_date} → ${periodData.latest_date} (${periodData.total_days} jours)</div>`;
}

function createPeriodInfoDiv() {
    const infoDiv = document.createElement('div');
    infoDiv.id = 'periodInfo';
    infoDiv.style.cssText = `background: #e8f4fd; border: 1px solid #3498db; border-radius: 8px; padding: 10px; margin: 10px 0; font-size: 0.9em; color: #2c3e50;`;
    const controls = document.querySelector('.controls');
    controls.parentNode.insertBefore(infoDiv, controls.nextSibling);
    return infoDiv;
}

function onUniverseChange() {
    loadAvailablePeriods(document.getElementById('universeSelect').value);
}

function populateGlobalPeriodSelect(periods) {
    const select = document.getElementById('globalPeriodSelect');
    if (!select) return;
    const defaultOption = select.options[0];
    select.innerHTML = '';
    select.appendChild(defaultOption);
    if (periods && periods.length > 0) {
        periods.forEach(p => {
            const option = document.createElement('option');
            option.value = p.id;
            option.textContent = `${p.name} (${p.start_date} - ${p.end_date})`;
            select.appendChild(option);
        });
    }
}

function updateAllTablesFromGlobalPeriod(periodId) {
    if (!periodId) return;
    const selectedPeriod = globalAvailablePeriods.find(p => String(p.id) === String(periodId));
    if (!selectedPeriod) return;
    tablesConfiguration.forEach((config, index) => {
        config.period = periodId;
        config.dateStart = selectedPeriod.start_date;
        config.dateEnd = selectedPeriod.end_date;
        const ps = document.getElementById(`period_${index}`);
        const ds = document.getElementById(`dateStart_${index}`);
        const de = document.getElementById(`dateEnd_${index}`);
        if (ps) ps.value = periodId;
        if (ds) ds.value = selectedPeriod.start_date;
        if (de) de.value = selectedPeriod.end_date;
    });
}

async function detectPatterns() {
    const universe = document.getElementById('universeSelect').value;
    const panel = document.getElementById('analysisPanel');
    const container = document.getElementById('patternsContainer');

    panel.style.display = 'block';
    container.innerHTML = '<div class="loading">🔍 Analyse des patterns en cours...</div>';

    try {
        const sessionId = document.getElementById('globalPeriodSelect')?.value;
        const response = await fetch(`${API_BASE}/temporal-analysis/${universe}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                tables_config: tablesConfiguration,
                marking_type: markingOptions.type,
                session_id: sessionId
            })
        });

        if (!response.ok) throw new Error('Erreur API');
        const data = await response.json();

        if (data.status === 'success') {
            displayPatterns(data.patterns);
        } else {
            throw new Error(data.message || 'Erreur inconnue');
        }
    } catch (error) {
        console.error('Erreur detection patterns:', error);
        container.innerHTML = '<div class="error">Erreur lors de la détection des patterns réels</div>';
    }
}

document.addEventListener('DOMContentLoaded', () => {
    // Injecter le header universel
    if (typeof UniversalHeader !== 'undefined') {
        UniversalHeader.injectHeader('header-container', 'analysis', {
            showNavigation: true,
            showUserInfo: true
        });
    }

    initializeTablesConfiguration(6);
    const universe = document.getElementById('universeSelect').value;
    loadAvailablePeriods(universe);
    document.getElementById('universeSelect').addEventListener('change', onUniverseChange);
    document.getElementById('markingTypeSelect').addEventListener('change', updateMarkingType);
});


function generateScatterPlotGrid(tableData) {
    let html = '';
    // Grille 6x8 standard
    for (let chipNumber = 1; chipNumber <= 48; chipNumber++) {
        let hasOccurred = false;
        let count = 0;

        if (Array.isArray(tableData.occurrences)) {
            hasOccurred = tableData.occurrences.includes(chipNumber);
            count = hasOccurred ? 1 : 0;
        } else if (tableData.occurrences && typeof tableData.occurrences === 'object') {
            const occurrence = tableData.occurrences[chipNumber] || tableData.occurrences[String(chipNumber)] || tableData.occurrences[`chip${chipNumber}`];
            if (occurrence && occurrence.count > 0) {
                hasOccurred = true;
                count = occurrence.count;
            }
        }

        const row = Math.ceil(chipNumber / 6);
        const col = ((chipNumber - 1) % 6) + 1;

        let cellContent = '';
        if (hasOccurred) {
            const color = markingOptions.colors[Math.min(count, 3)] || '#e74c3c';
            const size = Math.min(6 + count * 2, 14); // Taille selon fréquence
            cellContent = `<div style="width:${size}px; height:${size}px; background-color:${color}; border-radius:50%; box-shadow: 0 0 5px ${color};"></div>`;
        }

        html += `<div class="mini-chip-cell" style="border:none; background:transparent;" title="Chip ${chipNumber}">${cellContent}</div>`;
    }
    return html;
}

function updateViewMode() {
    const select = document.getElementById('viewModeSelect');
    if (select) {
        currentViewMode = select.value;
        if (currentAnalysisData) {
            displayTemporalTables(currentAnalysisData);
        }
    }
}

function updateMarkingType() {
    const select = document.getElementById('markingTypeSelect');
    if (select) {
        markingOptions.type = select.value;
        console.log('🔄 Type de marquage mis à jour :', markingOptions.type);
        if (currentAnalysisData) {
            displayTemporalTables(currentAnalysisData);
        }
    }
}



// ===== DRAW HISTORY MODAL FUNCTIONS =====
// Adapted from advanced-journal.html

function showDrawDetails() {
    // Vérifier que les données sont chargées
    if (!window.loadedDraws || window.loadedDraws.length === 0) {
        alert('❌ Aucun historique chargé.\n\nVeuillez d\'abord :\n1. Configurer et lancer l\'analyse\n2. Attendre le chargement automatique de l\'historique\n\nOu cliquez sur "🔄 Charger Historique Réel" pour forcer le chargement.');
        return;
    }

    // Adapter les données pour le format attendu par displayDrawHistoryModal
    const formattedDraws = window.loadedDraws.map((draw, index) => {
        const nums = draw.winning_numbers || draw.chips || [];
        const n = Array.isArray(nums) ? nums.length : 0;
        const combos = n >= 2 ? (n * (n - 1)) / 2 : 0;

        return {
            date: draw.date || 'N/A',
            draw_number: draw.id || draw.draw_number,
            lottery_name: draw.loto_name || draw.name || `Tirage ${draw.id || index + 1}`,
            winning_numbers: nums,
            combinations_count: combos,
            universe: draw.universe || currentAnalysisData?.universe || 'Multi-univers',
            period: draw.period || 'Période Analysée',
            status: draw.status || 'ok',
            is_no_draw: draw.is_no_draw || false,
            no_draw_reason: draw.no_draw_reason || null
        };
    });

    // Trier par date (plus récent en haut)
    formattedDraws.sort((a, b) => {
        const dateA = new Date(a.date);
        const dateB = new Date(b.date);
        return dateB - dateA;
    });

    // Appeler la fonction de modal
    displayDrawHistoryModal(formattedDraws, 'Analyse Temporelle Katula');
}

function displayDrawHistoryModal(draws, sessionName) {
    const modal = document.createElement('div');
    modal.className = 'draw-history-modal';
    modal.innerHTML = `
        <div class="modal-overlay" onclick="closeDrawHistoryModal()"></div>
        <div class="modal-content" style="position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%); background: white; padding: 20px; border-radius: 12px; box-shadow: 0 10px 40px rgba(0,0,0,0.3); max-width: 800px; max-height: 80vh; overflow-y: auto; z-index: 10000;">
            <div class="modal-header" style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; padding-bottom: 15px; border-bottom: 2px solid #e0e0e0;">
                <h3 style="margin: 0; color: #2c3e50;">📅 Historique des Tirages ${sessionName ? '- ' + sessionName : ''}</h3>
                <button class="modal-close" onclick="closeDrawHistoryModal()" style="background: #e74c3c; color: white; border: none; padding: 8px 12px; border-radius: 6px; cursor: pointer; font-size: 14px;">❌ Fermer</button>
            </div>
            <div class="modal-body">
                <div class="draws-summary" style="background: #f8f9fa; padding: 15px; border-radius: 8px; margin-bottom: 20px;">
                    <div class="summary-item" style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                        <span class="summary-label" style="font-weight: bold;">Nombre de tirages :</span>
                        <span class="summary-value" style="color: #27ae60; font-weight: bold;">${draws.length}</span>
                    </div>
                    <div class="summary-item" style="display: flex; justify-content: space-between;">
                        <span class="summary-label" style="font-weight: bold;">Période :</span>
                        <span class="summary-value">${draws.length > 0 ? draws[draws.length - 1].date : 'N/A'} → ${draws.length > 0 ? draws[0].date : 'N/A'}</span>
                    </div>
                </div>
                <div class="draws-list">
                    ${draws.map(draw => {
        const isMultiUnivers = draw.universe === '5/90';
        const universText = isMultiUnivers ? 'MULTI-UNIVERS' : (draw.universe || 'N/A').toUpperCase();
        const universClass = isMultiUnivers ? 'mundo' : (draw.universe || 'default').toLowerCase();
        const isNoDraw = draw.is_no_draw || draw.status === 'no-draw';
        const statusBadge = isNoDraw ? `<span style="background: #e74c3c; color: white; padding: 2px 8px; border-radius: 4px; font-size: 0.8em;">NO DRAW</span>` : '';

        return `
                        <div class="draw-item" style="border: 1px solid #ddd; border-radius: 8px; padding: 15px; margin-bottom: 12px; background: white; transition: box-shadow 0.2s; cursor: pointer;" onmouseover="this.style.boxShadow='0 4px 12px rgba(0,0,0,0.15)'" onmouseout="this.style.boxShadow='none'">
                            <div class="draw-header" style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                                <div class="draw-date" style="font-weight: bold; color: #3498db;">📅 Tirage <span style="color: #1890ff;">#${draw.draw_number || '?'}</span> - ${draw.date}</div>
                                <div class="draw-period" style="background: #3498db; color: white; padding: 2px 10px; border-radius: 4px; font-size: 0.85em;">${draw.period}</div>
                            </div>
                            <div class="draw-details">
                                <div class="draw-info" style="margin-bottom: 8px;">
                                    <span class="info-label" style="font-weight: 600; color: #555;">Loterie :</span>
                                    <span class="info-value" style="margin-left: 8px;">${draw.lottery_name} ${statusBadge}</span>
                                </div>
                                ${!isNoDraw ? `
                                <div class="draw-info" style="margin-bottom: 8px;">
                                    <span class="info-label" style="font-weight: 600; color: #555;">Numéros :</span>
                                    <span class="info-value winning-numbers" style="margin-left: 8px; font-family: monospace; background: #ecf0f1; padding: 4px 8px; border-radius: 4px;">${draw.winning_numbers.join(' - ')}</span>
                                </div>
                                ` : `
                                <div class="draw-info" style="margin-bottom: 8px;">
                                    <span class="info-label" style="font-weight: 600; color: #e74c3c;">Raison :</span>
                                    <span class="info-value" style="margin-left: 8px; color: #e74c3c;">${draw.no_draw_reason || 'Tirage annulé'}</span>
                                </div>
                                `}
                                <div class="draw-info" style="margin-bottom: 8px;">
                                    <span class="info-label" style="font-weight: 600; color: #555;">Univers :</span>
                                    <span class="info-value universe-${universClass}" style="margin-left: 8px; font-weight: bold; color: #8e44ad;">${universText}</span>
                                </div>
                                ${!isNoDraw ? `
                                <div class="draw-info">
                                    <span class="info-label" style="font-weight: 600; color: #555;">Combinaisons analysées :</span>
                                    <span class="info-value" style="margin-left: 8px; background: #2ecc71; color: white; padding: 2px 8px; border-radius: 4px; font-weight: bold;">${draw.combinations_count}</span>
                                </div>
                                ` : ''}
                            </div>
                        </div>
                    `}).join('')}
                </div>
            </div>
            <div class="modal-footer" style="margin-top: 20px; padding-top: 15px; border-top: 2px solid #e0e0e0; display: flex; justify-content: space-between; gap: 10px;">
                <button class="modal-btn" onclick="exportDrawHistory()" style="background: #27ae60; color: white; border: none; padding: 10px 20px; border-radius: 6px; cursor: pointer; font-weight: 600; flex: 1;">💾 Exporter Historique</button>
                <button class="modal-btn" onclick="closeDrawHistoryModal()" style="background: #95a5a6; color: white; border: none; padding: 10px 20px; border-radius: 6px; cursor: pointer; font-weight: 600; flex: 1;">Fermer</button>
            </div>
        </div>
    `;

    // Ajouter un style pour l'overlay
    const style = document.createElement('style');
    style.textContent = `
        .modal-overlay {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.5);
            z-index: 9999;
        }
    `;
    document.head.appendChild(style);

    document.body.appendChild(modal);

    // Stocker les données pour l'export
    window.currentDrawHistory = draws;
}

function closeDrawHistoryModal() {
    const modal = document.querySelector('.draw-history-modal');
    if (modal) {
        modal.remove();
    }
}

function exportDrawHistory() {
    if (window.currentCombinationsHistory && window.currentCombinationsHistory.length > 0) {
        exportCombinationsHistory();
        return;
    }

    if (!window.currentDrawHistory || window.currentDrawHistory.length === 0) {
        alert('❌ Aucun historique à exporter');
        return;
    }

    const csvContent = [
        ['Date', 'Loterie', 'Numéros Gagnants', 'Univers', 'Période', 'Combinaisons Analysées', 'Statut'],
        ...window.currentDrawHistory.map(draw => [
            draw.date,
            draw.lottery_name,
            (draw.winning_numbers || []).join('-'),
            draw.universe,
            draw.period,
            draw.combinations_count || 0,
            draw.is_no_draw ? 'NO DRAW' : 'OK'
        ])
    ].map(row => row.join(',')).join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `historique_katula_${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
    window.URL.revokeObjectURL(url);

    console.log('✅ Historique exporté avec succès:', window.currentDrawHistory.length, 'tirages');
}

function displayCombinationsModal(combinations, universe) {
    const modal = document.createElement('div');
    modal.className = 'draw-history-modal';

    const groupedByDraw = {};
    combinations.forEach(combo => {
        const key = `${combo.draw_date}_${combo.lottery_name}`;
        if (!groupedByDraw[key]) {
            groupedByDraw[key] = {
                date: combo.draw_date,
                lottery_name: combo.lottery_name,
                period: combo.period,
                combinations: []
            };
        }
        groupedByDraw[key].combinations.push(combo);
    });

    const draws = Object.values(groupedByDraw);

    modal.innerHTML = `
        <div class="modal-overlay" onclick="closeDrawHistoryModal()"></div>
        <div class="modal-content" style="position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%); background: white; padding: 20px; border-radius: 12px; box-shadow: 0 10px 40px rgba(0,0,0,0.3); max-width: 95vw; max-height: 85vh; overflow-y: auto; z-index: 10000;">
            <div class="modal-header" style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; padding-bottom: 15px; border-bottom: 2px solid #e0e0e0;">
                <h3 style="margin: 0; color: #2c3e50;">📊 Combinaisons Détaillées - Univers: ${universe.toUpperCase()}</h3>
                <button class="modal-close" onclick="closeDrawHistoryModal()" style="background: #e74c3c; color: white; border: none; padding: 8px 12px; border-radius: 6px; cursor: pointer; font-size: 14px;">❌ Fermer</button>
            </div>
            <div class="modal-body">
                <div class="draws-summary" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 15px; border-radius: 8px; margin-bottom: 20px;">
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px;">
                        <div style="text-align: center;">
                            <div style="font-size: 0.9em; opacity: 0.9;">Tirages</div>
                            <div style="font-size: 1.8em; font-weight: bold;">${draws.length}</div>
                        </div>
                        <div style="text-align: center;">
                            <div style="font-size: 0.9em; opacity: 0.9;">Combinaisons</div>
                            <div style="font-size: 1.8em; font-weight: bold;">${combinations.length}</div>
                        </div>
                        <div style="text-align: center;">
                            <div style="font-size: 0.9em; opacity: 0.9;">Univers</div>
                            <div style="font-size: 1.8em; font-weight: bold;">${universe.toUpperCase()}</div>
                        </div>
                    </div>
                </div>
                <div class="draws-list">
                    ${draws.map(draw => `
                        <div style="border: 2px solid #3498db; border-radius: 12px; padding: 15px; margin-bottom: 20px; background: linear-gradient(to bottom, #ffffff, #f8f9fa);">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; padding-bottom: 10px; border-bottom: 2px solid #e0e0e0;">
                                <div>
                                    <div style="font-size: 1.2em; font-weight: bold; color: #2c3e50;">📅 ${draw.date}</div>
                                    <div style="color: #7f8c8d; margin-top: 4px;">${draw.lottery_name}</div>
                                </div>
                                <div style="background: #3498db; color: white; padding: 8px 16px; border-radius: 20px; font-weight: bold;">
                                    ${draw.combinations.length} combinaisons
                                </div>
                            </div>
                            <div style="overflow-x: auto;">
                                <table style="width: 100%; border-collapse: collapse; font-size: 0.85em;">
                                    <thead>
                                        <tr style="background: #34495e; color: white;">
                                            <th style="padding: 8px; text-align: left; border: 1px solid #ddd;">Combinaison</th>
                                            <th style="padding: 8px; text-align: left; border: 1px solid #ddd;">Dénomination</th>
                                            <th style="padding: 8px; text-align: left; border: 1px solid #ddd;">Alpha</th>
                                            <th style="padding: 8px; text-align: left; border: 1px solid #ddd;">Chip</th>
                                            <th style="padding: 8px; text-align: left; border: 1px solid #ddd;">Drawer</th>
                                            <th style="padding: 8px; text-align: left; border: 1px solid #ddd;">Tome</th>
                                            <th style="padding: 8px; text-align: left; border: 1px solid #ddd;">Granque</th>
                                            <th style="padding: 8px; text-align: left; border: 1px solid #ddd;">Petique</th>
                                            <th style="padding: 8px; text-align: left; border: 1px solid #ddd;">Ligne</th>
                                            <th style="padding: 8px; text-align: left; border: 1px solid #ddd;">Col</th>
                                            <th style="padding: 8px; text-align: left; border: 1px solid #ddd;">Forme</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        ${draw.combinations.map((combo, idx) => `
                                            <tr style="background: ${idx % 2 === 0 ? '#ffffff' : '#f8f9fa'};">
                                                <td style="padding: 8px; border: 1px solid #ddd; font-weight: bold; color: #3498db;">${combo.combination}</td>
                                                <td style="padding: 8px; border: 1px solid #ddd;">${combo.denomination}</td>
                                                <td style="padding: 8px; border: 1px solid #ddd;">${combo.alpha_ranking}</td>
                                                <td style="padding: 8px; border: 1px solid #ddd; font-weight: bold;">${combo.chip}</td>
                                                <td style="padding: 8px; border: 1px solid #ddd;">${combo.drawer}</td>
                                                <td style="padding: 8px; border: 1px solid #ddd;">${combo.tome}</td>
                                                <td style="padding: 8px; border: 1px solid #ddd;">${combo.granque}</td>
                                                <td style="padding: 8px; border: 1px solid #ddd;">${combo.petique}</td>
                                                <td style="padding: 8px; border: 1px solid #ddd;">${combo.ligne}</td>
                                                <td style="padding: 8px; border: 1px solid #ddd;">${combo.colonne}</td>
                                                <td style="padding: 8px; border: 1px solid #ddd;">${combo.forme}</td>
                                            </tr>
                                        `).join('')}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>
            <div class="modal-footer" style="margin-top: 20px; padding-top: 15px; border-top: 2px solid #e0e0e0; display: flex; justify-content: space-between; gap: 10px;">
                <button class="modal-btn" onclick="exportCombinationsHistory()" style="background: #27ae60; color: white; border: none; padding: 10px 20px; border-radius: 6px; cursor: pointer; font-weight: 600; flex: 1;">💾 Exporter CSV</button>
                <button class="modal-btn" onclick="closeDrawHistoryModal()" style="background: #95a5a6; color: white; border: none; padding: 10px 20px; border-radius: 6px; cursor: pointer; font-weight: 600; flex: 1;">Fermer</button>
            </div>
        </div>
    `;

    document.body.appendChild(modal);
    window.currentCombinationsHistory = combinations;
}

function exportCombinationsHistory() {
    if (!window.currentCombinationsHistory || window.currentCombinationsHistory.length === 0) {
        alert('❌ Aucune combinaison à exporter');
        return;
    }

    const csvContent = [
        ['Date', 'Loterie', 'Période', 'Combinaison', 'Dénomination', 'Alpha Ranking', 'Chip', 'Drawer', 'Tome', 'Granque', 'Petique', 'Ligne', 'Colonne', 'Parité', 'Unidos', 'Forme', 'Engine', 'Beastie', 'Univers'],
        ...window.currentCombinationsHistory.map(combo => [
            combo.draw_date,
            combo.lottery_name,
            combo.period,
            combo.combination,
            combo.denomination,
            combo.alpha_ranking,
            combo.chip,
            combo.drawer,
            combo.tome,
            combo.granque,
            combo.petique,
            combo.ligne,
            combo.colonne,
            combo.parite,
            combo.unidos,
            combo.forme,
            combo.engine,
            combo.beastie,
            combo.univers
        ])
    ].map(row => row.join(',')).join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    const universe = window.currentCombinationsHistory[0]?.univers || 'katula';
    a.download = `combinaisons_${universe}_${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
    window.URL.revokeObjectURL(url);

    console.log('✅ Combinaisons exportées:', window.currentCombinationsHistory.length, 'combinaisons');
}
