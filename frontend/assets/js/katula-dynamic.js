// Configuration des univers - sera mise à jour dynamiquement avec les vraies données
const universes = {
    mundo: { name: 'Mundo', shapes: [] },
    fruity: { name: 'Fruity', shapes: [] },
    trigga: { name: 'Trigga', shapes: [] },
    roaster: { name: 'Roaster', shapes: [] },
    sunshine: { name: 'Sunshine', shapes: [] }
};

// Vraies données des univers selon le service backend - DONNÉES EXACTES
const REAL_UNIVERSE_DATA = {
    mundo: {
        type: 'BASIC',
        formes: ['carre', 'triangle', 'cercle', 'rectangle']  // 4 formes
    },
    fruity: {
        type: 'BASIC',
        formes: ['carre', 'triangle', 'cercle', 'rectangle']  // 4 formes
    },
    trigga: {
        type: 'HYBRID',
        formes: ['carre', 'triangle', 'cercle', 'rectangle', 'triangle-cercle', 'triangle-rectangle', 'cercle-rectangle', 'cercle-triangle', 'rectangle-cercle', 'rectangle-triangle']  // 10 formes
    },
    roaster: {
        type: 'COMPOUND',
        formes: ['carre-triangle', 'carre-cercle', 'carre-rectangle', 'triangle-carre', 'triangle-cercle', 'triangle-rectangle', 'cercle-carre', 'cercle-triangle', 'cercle-rectangle', 'rectangle-carre', 'rectangle-triangle', 'rectangle-cercle']  // 12 formes
    },
    sunshine: {
        type: 'HYBRID',
        formes: ['carre', 'triangle', 'cercle', 'rectangle', 'carre-triangle', 'carre-cercle', 'carre-rectangle', 'triangle-carre', 'triangle-cercle', 'triangle-rectangle', 'cercle-carre', 'cercle-triangle', 'cercle-rectangle', 'rectangle-carre', 'rectangle-triangle', 'rectangle-cercle']  // 16 formes
    }
};

let selectedUniverse = 'mundo'; // Default universe
let currentFilter = null; // État du filtre actuel pour désélection

document.addEventListener('DOMContentLoaded', async () => {
    console.log('=== DOM CONTENT LOADED ===');

    // Test immédiat du container
    const container = document.getElementById('universeChipsContainer');
    console.log('Container universeChipsContainer:', container);

    if (container) {
        container.innerHTML = '<div style="background: red; color: white; padding: 10px; margin: 10px;">TEST CONTAINER FONCTIONNE</div>';
    }

    // Charger les vraies formes
    console.log('Chargement des formes...');
    await loadRealUniverseFormes();
    console.log('Formes chargées');

    // Initialiser les puces d'univers avec les vraies données
    console.log('Rendu des chips univers...');
    renderUniverseChips();
    showUniverseBanner(selectedUniverse);
    console.log('Chips rendus');

    // Sélectionner l'univers par défaut
    selectUniverse(selectedUniverse);
    // Charger les données de l'univers
    loadUniverse();
});

const FORME_ICONS = {
    'carre': '■',        // Bleu
    'triangle': '▲',     // Vert
    'cercle': '●',       // Jaune
    'rectangle': '▬',    // Rouge
    'carre-triangle': '■▲',
    'carre-cercle': '■●',
    'carre-rectangle': '■▬',
    'triangle-carre': '▲■',
    'triangle-cercle': '▲●',
    'triangle-rectangle': '▲▬',
    'cercle-carre': '●■',
    'cercle-triangle': '●▲',
    'cercle-rectangle': '●▬',
    'rectangle-carre': '▬■',
    'rectangle-triangle': '▬▲',
    'rectangle-cercle': '▬●'
};

// Couleurs des formes de base - ordre métier strict
const FORME_COLORS = {
    'carre': '#3498db',      // Bleu
    'triangle': '#2ecc71',   // Vert  
    'cercle': '#f1c40f',     // Jaune
    'rectangle': '#e74c3c'   // Rouge
};

// Fonction pour obtenir la couleur d'une forme (simple ou composée)
function getFormeColor(forme) {
    if (FORME_COLORS[forme]) {
        return FORME_COLORS[forme];
    }
    // Pour les formes composées, utiliser la couleur de la première forme
    if (forme.includes('-')) {
        const [forme1] = forme.split('-');
        return FORME_COLORS[forme1] || '#95a5a6';
    }
    return '#95a5a6';
}

// Fonction pour générer l'icône d'une forme composée avec les bonnes couleurs
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



async function loadRealUniverseFormes() {
    // Utiliser les vraies données du service backend
    for (const universeKey in REAL_UNIVERSE_DATA) {
        const realData = REAL_UNIVERSE_DATA[universeKey];

        // Mettre à jour avec les vraies formes
        universes[universeKey].type = realData.type;
        universes[universeKey].realFormes = realData.formes;

        // Créer les shapes avec les vraies formes et couleurs correctes
        universes[universeKey].shapes = realData.formes.map(forme => ({
            name: forme,
            icon: FORME_ICONS[forme] || '?',
            color: getFormeColor(forme),
            compositeIcon: generateCompositeIcon(forme)
        }));

        console.log(`Univers ${universeKey}: ${realData.formes.length} formes chargees`);
    }
}

function renderUniverseChips() {
    console.log('=== DEBUT renderUniverseChips ===');
    const chipsContainer = document.getElementById('universeChipsContainer');
    if (!chipsContainer) {
        console.error('ERREUR: universeChipsContainer non trouvé');
        return;
    }
    console.log('Container trouvé:', chipsContainer);

    let html = '';
    for (const universeKey in universes) {
        const universe = universes[universeKey];
        const totalFormes = universe.shapes ? universe.shapes.length : 0;
        const isSelected = universeKey === selectedUniverse;
        const chipStyle = isSelected ? 'border:4px solid #3498db;box-shadow:0 0 20px rgba(52,152,219,0.6);transform:scale(1.05)' : 'opacity:0.6';

        html += `
            <div class="chip" id="chip-${universeKey}" onclick="selectUniverse('${universeKey}')" style="${chipStyle}">
                <div class="chip-header">${universe.name} (${totalFormes})</div>
                <div class="chip-drawers" style="display: flex; flex-wrap: wrap; gap: 2px; padding: 5px;">
        `;

        if (universe.shapes && universe.shapes.length > 0) {
            if (universe.shapes.length <= 4) {
                // Afficher toutes les formes + compléter avec tiroirs vides
                universe.shapes.forEach(shape => {
                    html += `<div class="drawer clickable-forme forme-${shape.name}" 
                                onclick="filterByFormeFromChip('${shape.name}')" 
                                title="Filtrer par ${shape.name} dans ${universe.name}" 
                                style="font-weight: bold; font-size: 1.1em; cursor: pointer; transition: all 0.2s ease; min-width: 30px; text-align: center; padding: 4px; z-index: 1000; position: relative; background: rgba(255,255,255,0.8); border: 2px solid #007bff; border-radius: 4px; margin: 2px;">
                                ${shape.compositeIcon}
                             </div>`;
                });

                // Compléter avec tiroirs vides
                const emptySlots = 4 - universe.shapes.length;
                for (let i = 0; i < emptySlots; i++) {
                    html += `<div class="drawer" style="color: #ecf0f1; min-width: 30px; text-align: center; padding: 4px;">-</div>`;
                }
            } else {
                // Afficher 3 premières formes + bouton +n
                const shapesToShow = universe.shapes.slice(0, 3);
                const remainingCount = universe.shapes.length - 3;

                shapesToShow.forEach(shape => {
                    html += `<div class="drawer clickable-forme forme-${shape.name}" 
                                onclick="filterByFormeFromChip('${shape.name}')" 
                                title="Filtrer par ${shape.name} dans ${universe.name}" 
                                style="font-weight: bold; font-size: 1.1em; cursor: pointer; transition: all 0.2s ease; min-width: 30px; text-align: center; padding: 4px; z-index: 1000; position: relative; background: rgba(255,255,255,0.8); border: 2px solid #007bff; border-radius: 4px; margin: 2px;">
                                ${shape.compositeIcon}
                             </div>`;
                });

                // Bouton +n cliquable
                html += `<div class="drawer plus-button" 
                            title="Voir toutes les ${universe.shapes.length} formes de ${universe.name}" 
                            onclick="event.stopPropagation(); showUniverseFormesBubble('${universeKey}')" 
                            style="color: #3498db; font-size: 0.9em; cursor: pointer; font-weight: bold; min-width: 30px; text-align: center; padding: 4px; border: 2px dashed #3498db; background: #e8f4fd;">
                            +${remainingCount}
                         </div>`;
            }
        } else {
            // Placeholder si pas de données
            for (let i = 0; i < 4; i++) {
                html += `<div class="drawer" style="color: #bdc3c7;">...</div>`;
            }
        }

        html += `
                </div>
            </div>
        `;
    }
    console.log('HTML généré:', html.length, 'caractères');

    // SOLUTION DE CONTOURNEMENT - BOUTONS DE FILTRAGE PAR FORME ADAPTATIFS
    html += generateFormeFilterButtons(selectedUniverse);

    chipsContainer.innerHTML = html;
    console.log('HTML injecté dans le container');

    console.log('=== FIN renderUniverseChips - ONCLICK INLINE UTILISE ===');
}

// Générer les boutons de filtrage par forme selon l'univers
function generateFormeFilterButtons(universeKey) {
    const universe = universes[universeKey];
    if (!universe || !universe.shapes) {
        console.log(`Pas de formes pour l'univers ${universeKey}`);
        return '';
    }

    let html = `<div style="margin: 10px 0; padding: 15px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border-radius: 8px; box-shadow: 0 4px 15px rgba(0,0,0,0.2);">
        <h4 style="margin: 0 0 10px 0; text-align: center;">🎯 FILTRAGE PAR FORME - ${universe.name.toUpperCase()} (${universe.shapes.length})</h4>
        <div style="display: flex; flex-wrap: wrap; gap: 6px; justify-content: center; max-height: 120px; overflow-y: auto;">`;

    // Couleurs pour les formes
    const formeColors = {
        'carre': '#3498db',
        'triangle': '#2ecc71',
        'cercle': '#f1c40f',
        'rectangle': '#e74c3c',
        'carre-triangle': '#9b59b6',
        'carre-cercle': '#e67e22',
        'carre-rectangle': '#1abc9c',
        'triangle-carre': '#34495e',
        'triangle-cercle': '#16a085',
        'triangle-rectangle': '#27ae60',
        'cercle-carre': '#2980b9',
        'cercle-triangle': '#8e44ad',
        'cercle-rectangle': '#d35400',
        'rectangle-carre': '#c0392b',
        'rectangle-triangle': '#7f8c8d',
        'rectangle-cercle': '#2c3e50'
    };

    // Utiliser l'ordre métier des formes
    const ordreMetier = DRAWER_ORDER[universeKey] || universe.shapes.map(s => s.name);

    // Générer un bouton pour chaque forme dans l'ordre métier
    ordreMetier.forEach(formeName => {
        const shape = universe.shapes.find(s => s.name === formeName);
        if (!shape) return;

        const color = formeColors[shape.name] || '#95a5a6';
        const icon = shape.compositeIcon || shape.icon || '?';

        html += `<button id="forme-btn-${shape.name}" onclick="toggleFormeFilter('${shape.name}')" 
                    style="padding: 6px 10px; background: ${color}; color: white; border: 2px solid transparent; border-radius: 4px; cursor: pointer; font-weight: bold; transition: all 0.2s; font-size: 0.85em; min-width: 80px;" 
                    onmouseover="this.style.transform='scale(1.05)'; this.style.boxShadow='0 4px 8px rgba(0,0,0,0.3)';" 
                    onmouseout="this.style.transform='scale(1)'; this.style.boxShadow='none';" 
                    title="Filtrer par ${shape.name}">
                    ${icon} ${shape.name.toUpperCase()}
                 </button>`;
    });

    // Bouton d'effacement
    html += `<button onclick="clearAllFilters()" 
                style="padding: 6px 10px; background: #95a5a6; color: white; border: none; border-radius: 4px; cursor: pointer; font-weight: bold; transition: all 0.2s; font-size: 0.85em; min-width: 80px;" 
                onmouseover="this.style.transform='scale(1.05)'; this.style.boxShadow='0 4px 8px rgba(0,0,0,0.3)';" 
                onmouseout="this.style.transform='scale(1)'; this.style.boxShadow='none';" 
                title="Effacer tous les filtres">
                ✕ EFFACER
             </button>`;

    html += `</div></div>`;
    return html;
}

function selectUniverse(universeKey) {
    selectedUniverse = universeKey;
    clearAllFilters();
    hideFilterMessage();

    // Mettre en surbrillance le chip d'univers sélectionné
    document.querySelectorAll('.chip').forEach(chip => chip.classList.remove('active'));
    const selectedChip = document.getElementById(`chip-${universeKey}`);
    if (selectedChip) {
        selectedChip.classList.add('active');
    }

    // Regénérer les boutons de filtrage et mettre en surbrillance le dropdown
    renderUniverseChips();
    showUniverseBanner(universeKey);
    
    // Mettre en surbrillance le dropdown de formes de l'univers sélectionné
    setTimeout(() => {
        const formeDropdowns = document.querySelectorAll('[id^="forme-btn-"]');
        formeDropdowns.forEach(btn => {
            btn.style.boxShadow = '0 0 15px rgba(52, 152, 219, 0.8)';
            btn.style.transform = 'scale(1.05)';
        });
        
        // Animation de pulsation pour attirer l'attention
        setTimeout(() => {
            formeDropdowns.forEach(btn => {
                btn.style.transform = 'scale(1)';
            });
        }, 500);
    }, 100);

    loadUniverse();
}

async function loadUniverse() {
    const katulaContainer = document.getElementById('katulaContainer');
    const loadingIndicator = document.getElementById('loadingIndicator');

    if (loadingIndicator) {
        loadingIndicator.style.display = 'block';
    }
    if (katulaContainer) {
        katulaContainer.innerHTML = '';
    }

    try {
        const matrixData = await loadRealMatrixData();

        renderKatulaTable(matrixData);
        updateUniverseInfo(selectedUniverse, matrixData);
        updateFormesLegend(matrixData);
        updateGranqueTomeButtons();

    } catch (error) {
        console.error('Error loading universe data:', error);
        if (katulaContainer) {
            katulaContainer.innerHTML = `<p class="error-message">Erreur lors du chargement des données pour l'univers ${selectedUniverse}. Veuillez réessayer.</p>`;
        }
    } finally {
        if (loadingIndicator) {
            loadingIndicator.style.display = 'none';
        }
    }
}

function renderKatulaTable(data) {
    const katulaContainer = document.getElementById('katulaContainer');
    if (!katulaContainer) return;

    let html = '';

    if (data && data.matrix) {
        let maxDrawers = 4;
        if (data.matrix) {
            for (let r = 1; r <= 8; r++) {
                for (let c = 1; c <= 6; c++) {
                    const cellData = data.matrix[r] ? data.matrix[r][c] : null;
                    if (cellData && cellData.elements) {
                        maxDrawers = Math.max(maxDrawers, cellData.elements.length);
                    }
                }
            }
        }

        // Utiliser le nom de l'univers sélectionné depuis l'objet universes
        const universeName = universes[selectedUniverse]?.name || selectedUniverse.toUpperCase();
        const universeIcon = getUniverseIcon(selectedUniverse);
        const totalFormes = universes[selectedUniverse]?.shapes?.length || 0;
        html += `<div class="header" style="background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);color:white;padding:20px;border-radius:10px;margin-bottom:20px;box-shadow:0 4px 15px rgba(0,0,0,0.2);display:flex;align-items:center;justify-content:center;gap:15px"><span style="font-size:2em">${universeIcon}</span><span style="font-size:1.3em">TABLE KATULA</span><span style="background:rgba(255,255,255,0.2);padding:8px 20px;border-radius:20px;font-size:1.4em">${universeName}</span><span style="background:rgba(255,255,255,0.15);padding:4px 12px;border-radius:15px;font-size:1em">${totalFormes} formes</span></div>`;

        html += '<div class="column-headers">';
        for (let c = 1; c <= 6; c++) {
            html += `<div class="column-header clickable-header" onclick="filterByColumn(${c})">Colonne ${c}</div>`;
        }
        html += '</div>';

        html += '<div class="katula-grid">';

        for (let r = 1; r <= 8; r++) {
            html += '<div class="ligne-container">';
            html += `<div class="ligne-label clickable-header" onclick="filterByRow(${r})">LIGNE ${r}</div>`;

            for (let c = 1; c <= 6; c++) {
                const cellData = data.matrix[r] ? data.matrix[r][c] : null;
                const quadrant = getQuadrant(r, c);

                const formeElement = cellData && cellData.elements ? cellData.elements.find(el => el.type === 'forme') : null;
                const formeName = formeElement ? formeElement.content.text : '';

                const chipNumber = (r - 1) * 6 + c;
                // Debug complet: Vérifier les calculs
                console.log(`Chip ${chipNumber}: Ligne ${r}, Colonne ${c}, Quadrant ${quadrant}`);

                // Diagnostic ciblé pour vérification des dénominations multiples (ex: fruity chip44)
                if (selectedUniverse === 'fruity' && (chipNumber === 38 || chipNumber === 39 || chipNumber === 44)) {
                    console.log(`[DIAG] chip${chipNumber} data (fruity):`, cellData);
                    if (cellData && cellData.elements) {
                        console.log(`  -> ${cellData.elements.length} elements:`);
                        cellData.elements.forEach((el, idx) => {
                            console.log(`     [${idx}] forme=${el.forme}, denom="${el.denomination}", hasSlash=${el.denomination ? el.denomination.includes('/') : false}`);
                        });
                    } else {
                        console.log('  -> NO ELEMENTS');
                    }
                }

                // Couleur de fond selon le quadrant pour vérification visuelle
                const debugColors = {
                    'q1': 'rgba(52, 152, 219, 0.1)',  // Bleu léger
                    'q2': 'rgba(46, 204, 113, 0.1)',  // Vert léger
                    'q3': 'rgba(243, 156, 18, 0.1)',  // Orange léger
                    'q4': 'rgba(155, 89, 182, 0.1)'   // Violet léger
                };

                html += `<div class="chip-cell ${quadrant}" data-row="${r}" data-col="${c}" data-quadrant="${quadrant}" data-forme="${formeName}" data-chip="${chipNumber}" style="background-color: ${debugColors[quadrant]}; position: relative; padding-top: 30px;">
                    <div class="chip-name clickable-chip-header" onclick="event.stopPropagation(); showChipDetails(${chipNumber});" style="position: absolute; top: 2px; left: 50%; transform: translateX(-50%); background: rgba(44,62,80,0.9); color: white; padding: 2px 6px; border-radius: 8px; font-size: 0.65em; font-weight: bold; z-index: 15; cursor: pointer; transition: all 0.2s ease; border: 1px solid #34495e; white-space: nowrap; max-width: 90%;" onmouseover="this.style.background='rgba(52,152,219,0.9)'; this.style.transform='translateX(-50%) scale(1.05)';" onmouseout="this.style.background='rgba(44,62,80,0.9)'; this.style.transform='translateX(-50%) scale(1)';">chip${chipNumber}</div>
                    <div class="debug-info" style="position: absolute; bottom: 2px; right: 2px; background: rgba(255,255,255,0.9); padding: 1px 3px; border-radius: 2px; font-size: 0.6em; color: #333; font-weight: bold;">L${r}C${c}-${quadrant}</div>`;

                // Nombre de tiroirs selon l'univers
                const maxDrawers = universes[selectedUniverse]?.shapes?.length || 4;

                // RÈGLE MÉTIER: Afficher seulement les formes existantes dans l'univers
                const universeFormes = DRAWER_ORDER[selectedUniverse] || ['carre', 'triangle', 'cercle', 'rectangle'];
                const elementsMap = {};

                // Mapper les éléments par forme
                if (cellData && cellData.elements) {
                    cellData.elements.forEach(element => {
                        elementsMap[element.forme] = element;
                    });
                }

                // Afficher dans l'ordre métier seulement les formes de l'univers
                universeFormes.forEach(forme => {
                    const element = elementsMap[forme];

                    if (element) {
                        // Forme avec données
                        const drawerClass = `drawer-${element.forme}`;
                        const icon = generateCompositeIcon(element.forme);
                        // Toutes les données viennent de PostgreSQL katooling_main_system
                        const sourceIcon = '✓';
                        const sourceColor = '#27ae60';
                        const sourceTitle = 'Données PostgreSQL';

                        // Gérer l'affichage des dénominations multiples (2, 3, 4+ dénominations)
                        let denominationDisplay = element.denomination;
                        let denominationClickHandler = '';

                        if (element.denomination && element.denomination.includes('/')) {
                            const parts = element.denomination.split('/').map(p => p.trim());
                            // Afficher toutes les dénominations l'une au-dessus de l'autre
                            if (parts.length === 2) {
                                // 2 dénominations: première normale, deuxième plus petite
                                denominationDisplay = `<div style="line-height: 1.0;">${parts[0]}<br/><span style="font-size: 0.85em;">${parts[1]}</span></div>`;
                            } else if (parts.length === 3) {
                                // 3 dénominations: tailles décroissantes
                                denominationDisplay = `<div style="line-height: 0.95;">${parts[0]}<br/><span style="font-size: 0.80em;">${parts[1]}</span><br/><span style="font-size: 0.75em;">${parts[2]}</span></div>`;
                            } else if (parts.length >= 4) {
                                // 4+ dénominations: tailles encore plus petites
                                denominationDisplay = `<div style="line-height: 0.9;">`;
                                parts.forEach((part, idx) => {
                                    const fontSize = Math.max(0.65, 0.85 - (idx * 0.08)); // Décroissance progressive, min 0.65em
                                    denominationDisplay += `${idx > 0 ? '<br/>' : ''}<span style="font-size: ${fontSize}em;">${part}</span>`;
                                });
                                denominationDisplay += `</div>`;
                            }
                            // Échapper les quotes ET les slashes pour injection sûre dans l'onclick inline
                            const safeDenom = (element.denomination || '').replace(/\\/g, '\\\\').replace(/'/g, "\\'").replace(/\//g, '\\/');
                            denominationClickHandler = `showMultipleDenominationDetails('${selectedUniverse}', '${safeDenom}', event)`;
                        } else {
                            const safeDenom = (element.denomination || '').replace(/\\/g, '\\\\').replace(/'/g, "\\'");
                            denominationClickHandler = `showDenominationDetails('${selectedUniverse}', '${safeDenom}', event)`;
                        }

                        const drawerId = `drawer-${chipNumber}-${element.forme}`;
                        html += `<div class="chip-drawer ${drawerClass}" id="${drawerId}" onclick="toggleDrawerSelection('${drawerId}', ${chipNumber}, '${element.forme}', '${element.denomination}')" title="Forme: ${element.forme} - Dénomination: ${element.denomination} (${sourceTitle}) - Cliquer pour sélectionner" style="cursor: pointer; transition: all 0.2s ease; margin: 1px 0; padding: 2px 4px; border-radius: 3px;">
                            <span style="font-size: 1.0em; margin-right: 3px;">${icon}</span>
                            <span class="denomination-clickable" onclick="event.stopPropagation(); ${denominationClickHandler}" style="font-weight: bold; cursor: pointer; text-decoration: underline; color: #2980b9; font-size: 0.85em;" title="Cliquer pour voir les combinations">${denominationDisplay}</span>
                            <span style="color: ${sourceColor}; font-size: 0.65em; margin-left: 2px; font-weight: bold;" title="${sourceTitle}">${sourceIcon}</span>
                        </div>`;
                    } else {
                        // Forme existante dans l'univers mais sans données sur ce chip
                        const icon = generateCompositeIcon(forme);
                        const drawerId = `drawer-${chipNumber}-${forme}-empty`;
                        html += `<div class="chip-drawer drawer-empty" id="${drawerId}" title="Forme: ${forme} - Pas de données" style="margin: 1px 0; padding: 2px 4px;">
                            <span style="font-size: 1.0em; margin-right: 3px; opacity: 0.3;">${icon}</span>
                            <span style="font-weight: bold; color: #bdc3c7; font-size: 0.85em;">---</span>
                        </div>`;
                    }
                });
                html += `</div>`; // Ferme chip-cell
            }
            html += '</div>'; // Ferme ligne-container
        }
        html += '</div>'; // Ferme katula-grid

        // Les zones petiques seront ajoutées après le rendu
        generatePetiquesOverlay(selectedUniverse);
    } else {
        html += '<p>Aucune donnée de matrice disponible pour cet univers.</p>';
    }

    katulaContainer.innerHTML = html;
}

// Règles métier pour l'ordre des tiroirs par univers (ordre métier appliqué)
const DRAWER_ORDER = {
    mundo: ['carre', 'triangle', 'cercle', 'rectangle'],
    fruity: ['carre', 'triangle', 'cercle', 'rectangle'],
    trigga: ['carre', 'triangle', 'cercle', 'rectangle', 'triangle-cercle', 'triangle-rectangle', 'cercle-rectangle', 'cercle-triangle', 'rectangle-cercle', 'rectangle-triangle'],
    roaster: ['carre-triangle', 'carre-cercle', 'carre-rectangle', 'triangle-carre', 'triangle-cercle', 'triangle-rectangle', 'cercle-carre', 'cercle-triangle', 'cercle-rectangle', 'rectangle-carre', 'rectangle-triangle', 'rectangle-cercle'],
    sunshine: ['carre', 'triangle', 'cercle', 'rectangle', 'carre-triangle', 'carre-cercle', 'carre-rectangle', 'triangle-carre', 'triangle-cercle', 'triangle-rectangle', 'cercle-carre', 'cercle-triangle', 'cercle-rectangle', 'rectangle-carre', 'rectangle-triangle', 'rectangle-cercle']
};

// Charger les vraies données de la matrice depuis PostgreSQL
async function loadRealMatrixData() {
    const matrix = {};

    try {
        // Charger les données en une seule requête pour éviter la surcharge de connexions
        const response = await fetch(`/api/formes/real/${selectedUniverse}/all`);

        if (!response.ok) {
            throw new Error(`Erreur HTTP: ${response.status}`);
        }

        const bulkData = await response.json();
        console.log('[DEBUG] Données globales reçues:', bulkData);

        // Nouveau format: bulkData.chips contient les données par chip
        if (bulkData && bulkData.status === 'success' && bulkData.chips) {
            for (let r = 1; r <= 8; r++) {
                matrix[r] = {};
                for (let c = 1; c <= 6; c++) {
                    const chipNumber = (r - 1) * 6 + c;
                    const chipKey = `chip${chipNumber}`;
                    const chipData = bulkData.chips[chipKey];

                    const elements = [];
                    const formeOrder = DRAWER_ORDER[selectedUniverse] || ['carre', 'triangle', 'cercle', 'rectangle'];

                    if (chipData && chipData.formes_data) {
                        formeOrder.forEach(forme => {
                            const formeData = chipData.formes_data[forme];
                            if (formeData && formeData.length > 0) {
                                formeData.forEach(item => {
                                    if (item.denomination && item.denomination !== "---") {
                                        if (selectedUniverse === 'fruity' && (chipNumber === 38 || chipNumber === 39 || chipNumber === 44) && item.denomination.includes('/')) {
                                            console.log(`[LOAD] chip${chipNumber} ${forme}: "${item.denomination}" (multiple=${item.multiple})`);
                                        }
                                        elements.push({
                                            type: 'real_data',
                                            forme: forme,
                                            denomination: item.denomination,
                                            frequency: item.frequency || 1,
                                            multiple: item.multiple || false
                                        });
                                    }
                                });
                            }
                        });
                    }

                    matrix[r][c] = {
                        elements: elements,
                        chipNumber: chipNumber,
                        totalItems: elements.length,
                        source: 'database'
                    };
                }
            }
        } else {
            throw new Error("Format de réponse invalide ou statut non success");
        }

        return { matrix };

    } catch (error) {
        console.error('Erreur lors du chargement des données réelles:', error);
        console.log('Impossible de charger les données de la BD');
        // Retourner une matrice vide avec message d\'erreur
        const matrix = {};
        for (let r = 1; r <= 8; r++) {
            matrix[r] = {};
            for (let c = 1; c <= 6; c++) {
                const chipNumber = (r - 1) * 6 + c;
                matrix[r][c] = {
                    elements: [],
                    chipNumber,
                    totalItems: 0,
                    error: 'Connexion BD échouée'
                };
            }
        }
        return { matrix };
    }
}

// Créer des données par défaut pour un chip (fallback seulement)
function createDefaultChipData(chipNumber) {
    console.log(`Utilisation de données par défaut pour chip ${chipNumber} - BD non accessible`);
    return {
        elements: [],
        chipNumber,
        totalItems: 0,
        error: 'BD non accessible'
    };
}

// Créer une matrice simulée en cas d'erreur
function createSimulatedMatrix() {
    const matrix = {};

    for (let r = 1; r <= 8; r++) {
        matrix[r] = {};
        for (let c = 1; c <= 6; c++) {
            const chipNumber = (r - 1) * 6 + c;
            matrix[r][c] = createDefaultChipData(chipNumber);
        }
    }

    return matrix;
}



function getQuadrant(row, col) {
    // Calcul du numéro de chip basé sur la position
    const chipNumber = (row - 1) * 6 + col;

    // Définition des quadrants par chips selon votre logique
    const q1Chips = [1, 2, 3, 7, 8, 9, 13, 14, 15, 19, 20, 21];
    const q2Chips = [4, 5, 6, 10, 11, 12, 16, 17, 18, 22, 23, 24];
    const q3Chips = [25, 26, 27, 31, 32, 33, 37, 38, 39, 43, 44, 45];
    const q4Chips = [28, 29, 30, 34, 35, 36, 40, 41, 42, 46, 47, 48];

    if (q1Chips.includes(chipNumber)) return 'q1';
    if (q2Chips.includes(chipNumber)) return 'q2';
    if (q3Chips.includes(chipNumber)) return 'q3';
    if (q4Chips.includes(chipNumber)) return 'q4';

    // Fallback (ne devrait pas arriver)
    return 'q1';
}

// Fonction pour obtenir le petique (quadrant) d'un chip
function getPetique(row, col) {
    return getQuadrant(row, col); // petique = quadrant
}

// Générer les zones petiques en utilisant directement les positions des chips DOM
function generatePetiquesOverlay(universe) {
    // Attendre que le DOM soit rendu
    setTimeout(() => {
        const quadrantDefinitions = {
            q1: [1, 2, 3, 7, 8, 9, 13, 14, 15, 19, 20, 21],
            q2: [4, 5, 6, 10, 11, 12, 16, 17, 18, 22, 23, 24],
            q3: [25, 26, 27, 31, 32, 33, 37, 38, 39, 43, 44, 45],
            q4: [28, 29, 30, 34, 35, 36, 40, 41, 42, 46, 47, 48]
        };

        const colors = {
            q1: '#3498db', q2: '#2ecc71', q3: '#f39c12', q4: '#9b59b6'
        };

        // Supprimer les anciens cadres
        const existingOverlay = document.querySelector('.petiques-overlay');
        if (existingOverlay) existingOverlay.remove();

        const overlay = document.createElement('div');
        overlay.className = 'petiques-overlay';
        overlay.style.cssText = 'position: absolute; top: 0; left: 0; right: 0; bottom: 0; pointer-events: none; z-index: 5;';

        Object.keys(quadrantDefinitions).forEach(quadrant => {
            const chipNumbers = quadrantDefinitions[quadrant];
            const chipElements = chipNumbers.map(num =>
                document.querySelector(`[data-chip="${num}"]`)
            ).filter(el => el !== null);

            if (chipElements.length === 0) return;

            // Calculer les limites basées sur les positions réelles des éléments
            const rects = chipElements.map(el => el.getBoundingClientRect());
            const containerRect = document.querySelector('.katula-grid').getBoundingClientRect();

            const minLeft = Math.min(...rects.map(r => r.left)) - containerRect.left;
            const minTop = Math.min(...rects.map(r => r.top)) - containerRect.top;
            const maxRight = Math.max(...rects.map(r => r.right)) - containerRect.left;
            const maxBottom = Math.max(...rects.map(r => r.bottom)) - containerRect.top;

            const frame = document.createElement('div');
            frame.className = `petique-zone ${quadrant}`;
            // Cadre visuel sans onclick (juste délimitation)
            frame.title = `Quadrant ${quadrant}: chips ${chipNumbers.join(',')}`;
            frame.style.cssText = `
                position: absolute;
                left: ${minLeft}px;
                top: ${minTop}px;
                width: ${maxRight - minLeft}px;
                height: ${maxBottom - minTop}px;
                border: 3px solid ${colors[quadrant]};
                border-radius: 8px;
                background: rgba(255, 255, 255, 0.05);
                pointer-events: none;
                transition: all 0.3s ease;
            `;

            // Bouton de sélection positionné selon le quadrant
            const button = document.createElement('button');
            button.className = `quadrant-selector-btn ${quadrant}`;
            button.textContent = quadrant;
            button.style.pointerEvents = 'auto';

            // Utiliser addEventListener au lieu de onclick
            button.addEventListener('click', function (e) {
                e.preventDefault();
                e.stopPropagation();
                console.log(`=== CLIC BOUTON ${quadrant} ===`);
                toggleQuadrantFilter(quadrant);
            });

            // Position du bouton selon le quadrant
            let buttonTop, buttonLeft;
            if (quadrant === 'q1' || quadrant === 'q2') {
                // Au-dessus pour q1 et q2
                buttonTop = minTop - 35;
            } else {
                // En dessous pour q3 et q4
                buttonTop = maxBottom + 10;
            }
            buttonLeft = minLeft + (maxRight - minLeft) / 2 - 20;

            button.style.cssText = `
                position: absolute;
                left: ${buttonLeft}px;
                top: ${buttonTop}px;
                width: 40px;
                height: 25px;
                background: #2c3e50;
                color: white;
                border: 2px solid ${colors[quadrant]};
                border-radius: 12px;
                font-weight: bold;
                font-size: 0.8em;
                cursor: pointer;
                transition: all 0.3s ease;
                z-index: 100;
                opacity: 1;
                pointer-events: auto;
                box-shadow: 0 2px 8px rgba(0,0,0,0.3);
            `;

            // Bulle d'info petique
            const petiqueNames = {
                'q1': 'petique q1 Nord-Ouest',
                'q2': 'petique q2 Nord-Est',
                'q3': 'petique q3 Sud-Ouest',
                'q4': 'petique q4 Sud-Est'
            };

            button.title = `${petiqueNames[quadrant]} - Cliquer pour filtrer`;

            button.onmouseover = () => {
                button.style.transform = 'scale(1.1)';
                button.style.background = colors[quadrant];
                button.style.boxShadow = `0 4px 12px ${colors[quadrant]}60`;

                // Afficher bulle petique
                showPetiqueBubble(quadrant, petiqueNames[quadrant], button);
            };
            button.onmouseout = () => {
                button.style.transform = 'scale(1)';
                button.style.background = activeQuadrants.has(quadrant) ? colors[quadrant] : '#2c3e50';
                button.style.boxShadow = '0 2px 8px rgba(0,0,0,0.3)';

                // Masquer bulle petique
                hidePetiqueBubble();
            };

            overlay.appendChild(frame);
            overlay.appendChild(button);
        });

        document.querySelector('.katula-grid').appendChild(overlay);

        // Test des boutons créés
        setTimeout(() => {
            console.log('=== TEST BOUTONS QUADRANTS ===');
            const buttons = document.querySelectorAll('.quadrant-selector-btn');
            console.log(`Nombre de boutons créés: ${buttons.length}`);
            buttons.forEach(btn => {
                console.log(`Bouton: ${btn.textContent}, classes: ${btn.className}`);
            });
        }, 200);
    }, 100);

    return ''; // Retourner vide car on crée les éléments directement
}

// Fonction de test pour vérifier la logique des quadrants basée sur les chips
function testQuadrantLogic() {
    console.log('\n=== TEST DE LA LOGIQUE BASÉE SUR LES CHIPS ===');

    // Définir les quadrants attendus selon votre logique
    const expectedQuadrants = {
        // Q1: chips 1,2,3,7,8,9,13,14,15,19,20,21
        1: 'q1', 2: 'q1', 3: 'q1', 7: 'q1', 8: 'q1', 9: 'q1',
        13: 'q1', 14: 'q1', 15: 'q1', 19: 'q1', 20: 'q1', 21: 'q1',

        // Q2: chips 4,5,6,10,11,12,16,17,18,22,23,24
        4: 'q2', 5: 'q2', 6: 'q2', 10: 'q2', 11: 'q2', 12: 'q2',
        16: 'q2', 17: 'q2', 18: 'q2', 22: 'q2', 23: 'q2', 24: 'q2',

        // Q3: chips 25,26,27,31,32,33,37,38,39,43,44,45
        25: 'q3', 26: 'q3', 27: 'q3', 31: 'q3', 32: 'q3', 33: 'q3',
        37: 'q3', 38: 'q3', 39: 'q3', 43: 'q3', 44: 'q3', 45: 'q3',

        // Q4: chips 28,29,30,34,35,36,40,41,42,46,47,48
        28: 'q4', 29: 'q4', 30: 'q4', 34: 'q4', 35: 'q4', 36: 'q4',
        40: 'q4', 41: 'q4', 42: 'q4', 46: 'q4', 47: 'q4', 48: 'q4'
    };

    // Tester tous les chips
    let correctCount = 0;
    let totalCount = 0;

    for (let chip = 1; chip <= 48; chip++) {
        const row = Math.floor((chip - 1) / 6) + 1;
        const col = ((chip - 1) % 6) + 1;
        const actualQuadrant = getQuadrant(row, col);
        const expectedQuadrant = expectedQuadrants[chip];

        const isCorrect = actualQuadrant === expectedQuadrant;
        const status = isCorrect ? '✅' : '❌';

        if (isCorrect) correctCount++;
        totalCount++;

        // Afficher seulement les erreurs et quelques exemples
        if (!isCorrect || [1, 3, 4, 6, 21, 22, 25, 27, 28, 30, 45, 48].includes(chip)) {
            console.log(`${status} Chip ${chip}: L${row}C${col} → ${actualQuadrant} (attendu: ${expectedQuadrant})`);
        }
    }

    console.log(`\n📊 RÉSULTAT: ${correctCount}/${totalCount} chips correctement assignés`);
    console.log('=== FIN DU TEST ===\n');
}

// Filtrage par colonne avec désélection et stats
function filterByColumn(col) {
    const universeName = universes[selectedUniverse]?.name || selectedUniverse.toUpperCase();

    // Désélection si déjà actif
    if (currentFilter && currentFilter.type === 'column' && currentFilter.value === col) {
        clearAllFilters();
        closeFilterStats();
        return;
    }

    clearAllFilters();
    currentFilter = { type: 'column', value: col };

    const allCells = document.querySelectorAll('.chip-cell');
    let visibleCount = 0;

    allCells.forEach(cell => {
        const cellCol = parseInt(cell.dataset.col);
        if (cellCol === col) {
            cell.classList.add('filtered-in');
            cell.style.opacity = '1';
            cell.style.border = '3px solid #e74c3c';
            cell.style.backgroundColor = '#fdf2f2';
            cell.style.transform = 'scale(1.02)';
            visibleCount++;
        } else {
            cell.classList.add('filtered-out');
            cell.style.opacity = '0.15';
            cell.style.filter = 'grayscale(100%)';
            cell.style.transform = 'scale(0.95)';
        }
    });

    showFilterMessage(`COLONNE ${col} active de ${universeName} (${visibleCount} chips)`);

    // Charger les statistiques
    showFilterStats('colonne', col);
}

// Filtrage par ligne avec désélection
function filterByRow(row) {
    const universeName = universes[selectedUniverse]?.name || selectedUniverse.toUpperCase();

    // Désélection si déjà actif
    if (currentFilter && currentFilter.type === 'row' && currentFilter.value === row) {
        clearAllFilters();
        closeFilterStats();
        return;
    }

    clearAllFilters();
    currentFilter = { type: 'row', value: row };

    const allCells = document.querySelectorAll('.chip-cell');
    let visibleCount = 0;

    allCells.forEach(cell => {
        const cellRow = parseInt(cell.dataset.row);
        if (cellRow === row) {
            cell.classList.add('filtered-in');
            cell.style.opacity = '1';
            cell.style.border = '3px solid #27ae60';
            cell.style.backgroundColor = '#f0f9f4';
            cell.style.transform = 'scale(1.02)';
            visibleCount++;
        } else {
            cell.classList.add('filtered-out');
            cell.style.opacity = '0.15';
            cell.style.filter = 'grayscale(100%)';
            cell.style.transform = 'scale(0.95)';
        }
    });

    showFilterMessage(`LIGNE ${row} active de ${universeName} (${visibleCount} chips)`);
    showFilterStats('ligne', row);
}

// Variable pour suivre les quadrants actifs
let activeQuadrants = new Set();

// Toggle du filtre quadrant avec gestion multi-sélection
function toggleQuadrantFilter(quadrant) {
    console.log(`=== TOGGLE QUADRANT ${quadrant} ===`);
    const universeName = universes[selectedUniverse]?.name || selectedUniverse.toUpperCase();
    const button = document.querySelector(`.quadrant-selector-btn.${quadrant}`);

    if (!button) {
        console.error(`Bouton ${quadrant} non trouvé`);
        console.log('Boutons disponibles:', document.querySelectorAll('.quadrant-selector-btn'));
        return;
    }

    console.log(`Bouton ${quadrant} trouvé, état actuel:`, activeQuadrants.has(quadrant));

    if (activeQuadrants.has(quadrant)) {
        // Désélectionner
        activeQuadrants.delete(quadrant);
        button.style.opacity = '0.6';
        button.style.background = '#95a5a6';
        console.log(`Désélection ${quadrant}`);
        if (activeQuadrants.size === 0) closeFilterStats();
    } else {
        // Sélectionner
        activeQuadrants.add(quadrant);
        const colors = { q1: '#3498db', q2: '#2ecc71', q3: '#f39c12', q4: '#9b59b6' };
        button.style.opacity = '1';
        button.style.background = colors[quadrant];
        console.log(`Sélection ${quadrant}`);
    }

    console.log('Quadrants actifs:', Array.from(activeQuadrants));

    // Appliquer le filtre
    applyQuadrantFilters();
}

// Appliquer les filtres de quadrants actifs
function applyQuadrantFilters() {
    console.log('=== APPLY QUADRANT FILTERS ===');
    const allCells = document.querySelectorAll('.chip-cell');
    const universeName = universes[selectedUniverse]?.name || selectedUniverse.toUpperCase();

    console.log(`Nombre de cellules trouvées: ${allCells.length}`);
    console.log('Quadrants actifs:', Array.from(activeQuadrants));

    if (activeQuadrants.size === 0) {
        console.log('Aucun quadrant actif - affichage normal');
        allCells.forEach(cell => {
            cell.classList.remove('filtered-out', 'filtered-in');
            cell.style.opacity = '1';
            cell.style.border = '';
            cell.style.backgroundColor = '';
            cell.style.transform = '';
            cell.style.filter = '';
        });
        hideFilterMessage();
        return;
    }

    let visibleCount = 0;
    const colors = { q1: '#3498db', q2: '#2ecc71', q3: '#f39c12', q4: '#9b59b6' };

    allCells.forEach(cell => {
        const cellQuadrant = cell.dataset.quadrant;
        console.log(`Cellule quadrant: ${cellQuadrant}, actif: ${activeQuadrants.has(cellQuadrant)}`);

        if (activeQuadrants.has(cellQuadrant)) {
            cell.classList.add('filtered-in');
            cell.classList.remove('filtered-out');
            cell.style.opacity = '1';
            cell.style.border = `3px solid ${colors[cellQuadrant]}`;
            cell.style.backgroundColor = `${colors[cellQuadrant]}15`;
            cell.style.transform = 'scale(1.02)';
            cell.style.filter = '';
            visibleCount++;
        } else {
            cell.classList.add('filtered-out');
            cell.classList.remove('filtered-in');
            cell.style.opacity = '0.15';
            cell.style.filter = 'grayscale(100%)';
            cell.style.transform = 'scale(0.95)';
        }
    });

    console.log(`Cellules visibles: ${visibleCount}`);
    const quadrantsList = Array.from(activeQuadrants).join(', ');
    showFilterMessage(`QUADRANTS ${quadrantsList} actifs de ${universeName} (${visibleCount} chips)`);
    if (activeQuadrants.size === 1) {
        showFilterStats('quadrant', Array.from(activeQuadrants)[0]);
    }
}

function updateUniverseInfo(universe, data) {
    const universeInfo = document.getElementById('universeInfo');
    if (universeInfo) {
        let totalElements = 0;
        if (data && data.matrix) {
            for (let r = 1; r <= 8; r++) {
                for (let c = 1; c <= 6; c++) {
                    const cell = data.matrix[r] ? data.matrix[r][c] : null;
                    if (cell && cell.elements) {
                        totalElements += cell.elements.length;
                    }
                }
            }
        }
        universeInfo.innerHTML = `<h3>Informations sur l'univers: ${universe}</h3>
                                  <p>Nombre d'éléments: ${totalElements}</p>`;
    }
}

function updateFormesLegend(data) {
    const formesLegendContainer = document.getElementById('formesLegend');
    if (!formesLegendContainer) return;

    // Ordre métier strict pour tous les univers
    const ordreMetier = ['carre', 'triangle', 'cercle', 'rectangle'];

    let html = '<h4>🎨 Légende des Formes - Ordre Métier</h4>';
    html += '<div class="formes-grid">';

    ordreMetier.forEach((formeName, index) => {
        const position = index + 1;
        const icon = FORME_ICONS[formeName] || '?';
        const color = FORME_COLORS[formeName] || '#000';

        html += `<div class="forme-item" onclick="filterByForme('${formeName}')" style="border-left: 4px solid ${color}">
                    <div class="forme-legend-icon">
                        <span style="color: ${color}; font-size: 1.5em; font-weight: bold;">${icon}</span>
                    </div>
                    <div class="forme-legend-text">
                        <strong>Tiroir ${position}: ${formeName.toUpperCase()}</strong>
                    </div>
                    <div style="color: ${color}; font-size: 0.8em; margin-top: 4px;">
                        Position ${position}
                    </div>
                 </div>`;
    });

    html += '</div>';
    html += `<button class="clear-filters-btn" onclick="filterByForme('')" style="margin-top: 10px; display: none;">Réinitialiser le filtre</button>`;

    formesLegendContainer.innerHTML = html;
}

// Variable pour suivre la forme active
let activeFormeFilter = null;

// Toggle du filtre par forme avec désélection
function toggleFormeFilter(selectedForme) {
    // Désélection si déjà actif
    if (activeFormeFilter === selectedForme) {
        clearAllFilters();
        resetFormeButtons();
        activeFormeFilter = null;
        return;
    }

    // Nouvelle sélection
    activeFormeFilter = selectedForme;
    updateFormeButtonStyles(selectedForme);
    filterByFormeFromChip(selectedForme);
}

// Mettre à jour les styles des boutons de forme
function updateFormeButtonStyles(selectedForme) {
    // Réinitialiser tous les boutons
    document.querySelectorAll('[id^="forme-btn-"]').forEach(btn => {
        btn.style.border = '2px solid transparent';
        btn.style.boxShadow = 'none';
    });

    // Surligner le bouton sélectionné
    const selectedBtn = document.getElementById(`forme-btn-${selectedForme}`);
    if (selectedBtn) {
        selectedBtn.style.border = '2px solid #fff';
        selectedBtn.style.boxShadow = '0 0 10px rgba(255,255,255,0.8), inset 0 0 10px rgba(255,255,255,0.3)';
    }
}

// Réinitialiser les styles des boutons
function resetFormeButtons() {
    document.querySelectorAll('[id^="forme-btn-"]').forEach(btn => {
        btn.style.border = '2px solid transparent';
        btn.style.boxShadow = 'none';
    });
}

// Filtrage par forme - VERSION FONCTIONNELLE
function filterByFormeFromChip(selectedForme) {
    console.log(`=== FILTRAGE FORME: ${selectedForme} ===`);
    console.log(`Univers actuel: ${selectedUniverse}`);

    try {
        clearAllFilters();

        const allCells = document.querySelectorAll('.chip-cell');
        const allDrawers = document.querySelectorAll('.chip-drawer');
        let visibleCount = 0;
        let drawerCount = 0;

        // Couleurs optimisées pour le contraste
        const colors = {
            'carre': '#2980b9',
            'triangle': '#27ae60',
            'cercle': '#f39c12',
            'rectangle': '#c0392b'
        };
        const color = colors[selectedForme] || '#007bff';

        // Réinitialiser tous les tiroirs
        allDrawers.forEach(drawer => {
            drawer.style.background = '';
            drawer.style.border = '';
            drawer.style.transform = '';
            drawer.style.boxShadow = '';
            drawer.style.opacity = '1';
            drawer.style.color = '';
            drawer.style.fontWeight = '';
            drawer.style.textShadow = '';
            drawer.style.borderRadius = '';
            drawer.style.filter = '';
        });

        allCells.forEach(cell => {
            let hasMatchingForme = false;

            // Vérifier les tiroirs de ce chip
            const drawers = cell.querySelectorAll('.chip-drawer');
            drawers.forEach(drawer => {
                const drawerClasses = drawer.className;
                // Correspondance exacte : drawer-FORME suivi d'un espace ou fin de chaîne
                const pattern = `drawer-${selectedForme}`;
                const exactMatch = drawerClasses.split(' ').some(cls => cls === pattern);
                if (exactMatch) {
                    hasMatchingForme = true;
                    drawerCount++;
                    // Surligner le tiroir correspondant avec meilleur contraste
                    drawer.style.background = `linear-gradient(135deg, ${color}20, ${color}40)`;
                    drawer.style.border = `3px solid ${color}`;
                    drawer.style.transform = 'scale(1.05)';
                    drawer.style.boxShadow = `0 0 15px ${color}80, inset 0 0 10px rgba(255,255,255,0.3)`;
                    drawer.style.color = '#000';
                    drawer.style.fontWeight = 'bold';
                    drawer.style.textShadow = '1px 1px 2px rgba(255,255,255,0.8)';
                    drawer.style.borderRadius = '6px';
                } else if (!drawer.className.includes('drawer-empty')) {
                    drawer.style.opacity = '0.3';
                    drawer.style.filter = 'grayscale(80%)';
                }
            });

            if (hasMatchingForme) {
                cell.classList.add('filtered-in');
                cell.style.opacity = '1';
                cell.style.border = `3px solid ${color}`;
                cell.style.backgroundColor = `${color}15`;
                cell.style.transform = 'scale(1.02)';
                visibleCount++;
            } else {
                cell.classList.add('filtered-out');
                cell.style.opacity = '0.15';
                cell.style.filter = 'grayscale(100%)';
                cell.style.transform = 'scale(0.95)';
            }
        });

        console.log(`Résultats: ${visibleCount} chips, ${drawerCount} tiroirs pour forme ${selectedForme}`);

        const universeName = universes[selectedUniverse]?.name || selectedUniverse.toUpperCase();
        showFilterMessage(`FORME ${selectedForme.toUpperCase()} active de ${universeName} (${visibleCount} chips, ${drawerCount} tiroirs)`);

        // Mettre à jour le filtre actuel
        currentFilter = { type: 'forme', value: selectedForme };

        // Debug si aucun résultat
        if (drawerCount === 0) {
            console.log('=== DEBUG: Aucun tiroir trouvé ===');
            const matchingDrawers = document.querySelectorAll(`.drawer-${selectedForme}`);
            console.log(`Tiroirs avec classe .drawer-${selectedForme}: ${matchingDrawers.length}`);

            // Lister toutes les classes de tiroirs pour debug
            const allDrawers = document.querySelectorAll('.chip-drawer');
            console.log(`Total tiroirs: ${allDrawers.length}`);
            const drawerClasses = [];
            allDrawers.forEach((drawer, i) => {
                if (i < 20) { // Limiter à 20 pour éviter le spam
                    drawerClasses.push(drawer.className);
                }
            });
            console.log('Classes de tiroirs (20 premiers):', drawerClasses);
        }

    } catch (error) {
        console.error('ERREUR dans filterByFormeFromChip:', error);
    }
}

// FONCTIONS DE TEST DEBUG
function testFormeClick(forme) {
    console.log(`=== TEST FORCE FORME: ${forme} ===`);
    alert(`Test forcé: ${forme}`);
    filterByFormeFromChip(forme);
}

function showDebugInfo() {
    console.log('=== DEBUG INFO ===');
    const clickableElements = document.querySelectorAll('.clickable-forme');
    console.log(`Éléments .clickable-forme trouvés: ${clickableElements.length}`);

    clickableElements.forEach((el, i) => {
        console.log(`Élément ${i}:`, {
            element: el,
            classes: el.className,
            dataForme: el.dataset.forme,
            dataUniverse: el.dataset.universe,
            visible: el.offsetParent !== null,
            style: el.style.cssText
        });

        // Test de clic programmatique
        console.log(`Test clic programmatique sur élément ${i}`);
        el.click();
    });

    const container = document.getElementById('universeChipsContainer');
    console.log('Container:', container);
    console.log('Container HTML:', container ? container.innerHTML.substring(0, 500) : 'NON TROUVÉ');

    alert(`Debug: ${clickableElements.length} éléments clickables trouvés - Test de clic programmatique effectué`);
}

// Afficher bulle interactive avec toutes les formes
function showUniverseFormesBubble(universeKey) {
    const universe = universes[universeKey];
    if (!universe || !universe.shapes) return;

    const bubble = document.createElement('div');
    bubble.id = 'formesBubble';
    bubble.style.cssText = `
        position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%);
        background: white; border: 3px solid #3498db; border-radius: 15px;
        padding: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.3); z-index: 2000;
        max-width: 500px; max-height: 400px; overflow-y: auto;
    `;

    let html = `<h3 style="margin: 0 0 15px 0; color: #2c3e50; text-align: center;">Formes de ${universe.name} (${universe.shapes.length})</h3>`;
    html += `<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(80px, 1fr)); gap: 10px;">`;

    universe.shapes.forEach(shape => {
        html += `<div onclick="filterByFormeFromBubble('${shape.name}'); closeBubble();" 
                    style="background: #f8f9fa; border: 2px solid #dee2e6; border-radius: 8px; padding: 10px; text-align: center; cursor: pointer; transition: all 0.2s ease;" 
                    onmouseover="this.style.background='#e3f2fd'; this.style.borderColor='#2196f3'; this.style.transform='scale(1.05)';" 
                    onmouseout="this.style.background='#f8f9fa'; this.style.borderColor='#dee2e6'; this.style.transform='scale(1)';">
                    <div style="font-size: 1.5em; margin-bottom: 5px;">${shape.compositeIcon}</div>
                    <div style="font-size: 0.8em; font-weight: bold; color: #2c3e50;">${shape.name}</div>
                 </div>`;
    });

    html += `</div><button onclick="closeBubble()" style="margin-top: 15px; width: 100%; padding: 10px; background: #e74c3c; color: white; border: none; border-radius: 8px; cursor: pointer; font-weight: bold;">Fermer</button>`;
    bubble.innerHTML = html;

    const overlay = document.createElement('div');
    overlay.id = 'bubbleOverlay';
    overlay.style.cssText = `position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); z-index: 1999;`;
    overlay.onclick = closeBubble;

    document.body.appendChild(overlay);
    document.body.appendChild(bubble);
}

function closeBubble() {
    const bubble = document.getElementById('formesBubble');
    const overlay = document.getElementById('bubbleOverlay');
    if (bubble) bubble.remove();
    if (overlay) overlay.remove();
}

// Variables pour suivre les sélections
let selectedChipNumber = null;
let selectedDrawers = new Set(); // Ensemble des tiroirs sélectionnés

// Afficher les détails d'un chip spécifique
async function showChipDetails(chipNumber) {
    console.log(`Affichage détails chip ${chipNumber}`);

    try {
        // Charger les données du chip
        const response = await fetch(`/api/formes/real/${selectedUniverse}/chip/chip${chipNumber}`);
        const data = await response.json();

        const universeName = universes[selectedUniverse]?.name || selectedUniverse.toUpperCase();

        // Créer la bulle de détails
        const bubble = document.createElement('div');
        bubble.id = 'chipDetailsBubble';
        bubble.style.cssText = `
            position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%);
            background: white; border: 3px solid #2c3e50; border-radius: 15px;
            padding: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.3); z-index: 2000;
            max-width: 500px; max-height: 400px; overflow-y: auto;
        `;

        let html = `<h3 style="margin: 0 0 15px 0; color: #2c3e50; text-align: center;">CHIP ${chipNumber} - ${universeName}</h3>`;

        if (data.status === 'success' && data.formes_data) {
            html += `<div style="margin-bottom: 15px; padding: 10px; background: #e8f5e8; border-radius: 8px; text-align: center;">
                        <strong>✓ Données BD disponibles (${data.total_items} éléments)</strong>
                     </div>`;

            html += `<div style="display: grid; gap: 10px;">`;

            Object.entries(data.formes_data).forEach(([forme, denominations]) => {
                const icon = generateCompositeIcon(forme);
                const color = getFormeColor(forme);

                html += `<div style="border: 2px solid ${color}; border-radius: 8px; padding: 10px; background: ${color}10;">
                            <div style="display: flex; align-items: center; margin-bottom: 8px;">
                                <span style="font-size: 1.2em; margin-right: 8px;">${icon}</span>
                                <strong style="color: ${color}; text-transform: uppercase;">${forme}</strong>
                            </div>
                            <div style="margin-left: 20px;">`;

                denominations.forEach(denom => {
                    html += `<div style="margin: 4px 0; padding: 4px 8px; background: white; border-radius: 4px; font-weight: bold;">
                                ${denom.denomination}
                             </div>`;
                });

                html += `</div></div>`;
            });

            html += `</div>`;
        } else {
            html += `<div style="margin-bottom: 15px; padding: 10px; background: #ffebee; border-radius: 8px; text-align: center; color: #c62828;">
                        <strong>❌ Données BD non disponibles</strong>
                     </div>`;
        }

        // Informations de position
        const row = Math.floor((chipNumber - 1) / 6) + 1;
        const col = ((chipNumber - 1) % 6) + 1;
        const quadrant = getQuadrant(row, col);

        html += `<div style="margin-top: 15px; padding: 10px; background: #f8f9fa; border-radius: 8px;">
                    <h4 style="margin: 0 0 8px 0; color: #2c3e50;">Position</h4>
                    <div><strong>Ligne:</strong> ${row}</div>
                    <div><strong>Colonne:</strong> ${col}</div>
                    <div><strong>Quadrant:</strong> ${quadrant.toUpperCase()}</div>
                 </div>`;

        html += `<div style="display: flex; gap: 10px; margin-top: 15px;">
                    <button onclick="filterByChip(${chipNumber})" style="flex: 1; padding: 10px; background: #3498db; color: white; border: none; border-radius: 8px; cursor: pointer; font-weight: bold;">Filtrer ce chip</button>
                    <button onclick="clearChipSelection(); closeChipDetails();" style="flex: 1; padding: 10px; background: #95a5a6; color: white; border: none; border-radius: 8px; cursor: pointer; font-weight: bold;">Désélectionner</button>
                    <button onclick="closeChipDetails()" style="flex: 1; padding: 10px; background: #e74c3c; color: white; border: none; border-radius: 8px; cursor: pointer; font-weight: bold;">Fermer</button>
                 </div>`;

        bubble.innerHTML = html;

        // Overlay
        const overlay = document.createElement('div');
        overlay.id = 'chipDetailsOverlay';
        overlay.style.cssText = `position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); z-index: 1999;`;
        overlay.onclick = closeChipDetails;

        document.body.appendChild(overlay);
        document.body.appendChild(bubble);

    } catch (error) {
        console.error('Erreur chargement détails chip:', error);
        alert(`Erreur lors du chargement des détails du chip ${chipNumber}`);
    }
}

// Fermer la bulle de détails du chip
function closeChipDetails() {
    const bubble = document.getElementById('chipDetailsBubble');
    const overlay = document.getElementById('chipDetailsOverlay');
    if (bubble) bubble.remove();
    if (overlay) overlay.remove();
}

// Fermer bulle avec Escape
document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') {
        closeChipDetails();
        closeBubble();
    }
});

// Filtrer pour afficher uniquement un chip spécifique
function filterByChip(chipNumber) {
    const universeName = universes[selectedUniverse]?.name || selectedUniverse.toUpperCase();

    clearAllFilters();

    const allCells = document.querySelectorAll('.chip-cell');

    allCells.forEach(cell => {
        const cellChipNumber = parseInt(cell.dataset.chip);

        if (cellChipNumber === chipNumber) {
            cell.classList.add('filtered-in');
            cell.style.opacity = '1';
            cell.style.border = '4px solid #2c3e50';
            cell.style.backgroundColor = '#ecf0f1';
            cell.style.transform = 'scale(1.1)';
            cell.style.zIndex = '10';
        } else {
            cell.classList.add('filtered-out');
            cell.style.opacity = '0.1';
            cell.style.filter = 'grayscale(100%)';
            cell.style.transform = 'scale(0.9)';
        }
    });

    showFilterMessage(`CHIP ${chipNumber} sélectionné de ${universeName}`);
    showFilterStats('chip', `chip${chipNumber}`);
    closeChipDetails();
}

// Toggle sélection du chip avec désélection
function toggleChipSelection(chipNumber) {
    if (selectedChipNumber === chipNumber) {
        // Désélectionner si déjà sélectionné
        clearChipSelection();
        closeFilterStats();
        hideFilterMessage();
    } else {
        // Sélectionner nouveau chip
        highlightSelectedChip(chipNumber);
        showChipDetails(chipNumber);
    }
}

// Surligner le chip sélectionné
function highlightSelectedChip(chipNumber) {
    clearChipSelection();

    selectedChipNumber = chipNumber;
    const chipCell = document.querySelector(`[data-chip="${chipNumber}"]`);

    if (chipCell) {
        chipCell.classList.add('chip-selected');
        chipCell.style.border = '4px solid #e74c3c';
        chipCell.style.background = 'linear-gradient(135deg, #fff5f5, #ffebee)';
        chipCell.style.transform = 'scale(1.08)';
        chipCell.style.zIndex = '20';
        chipCell.style.boxShadow = '0 8px 25px rgba(231, 76, 60, 0.4)';

        const chipHeader = chipCell.querySelector('.chip-name');
        if (chipHeader) {
            chipHeader.style.background = 'rgba(231, 76, 60, 0.9)';
            chipHeader.style.transform = 'translateX(-50%) scale(1.2)';
        }

        const universeName = universes[selectedUniverse]?.name || selectedUniverse.toUpperCase();
        showFilterMessage(`CHIP ${chipNumber} sélectionné de ${universeName} - Cliquer à nouveau pour désélectionner`);
    }
}

// Effacer la sélection de chip
function clearChipSelection() {
    if (selectedChipNumber) {
        const prevChip = document.querySelector(`[data-chip="${selectedChipNumber}"]`);
        if (prevChip) {
            prevChip.classList.remove('chip-selected');
            prevChip.style.border = '';
            prevChip.style.background = '';
            prevChip.style.transform = '';
            prevChip.style.zIndex = '';
            prevChip.style.boxShadow = '';

            const prevHeader = prevChip.querySelector('.chip-name');
            if (prevHeader) {
                prevHeader.style.background = 'rgba(44, 62, 80, 0.9)';
                prevHeader.style.transform = 'translateX(-50%)';
            }
        }
    }
    selectedChipNumber = null;
}

function filterByFormeFromBubble(selectedForme) {
    const universeName = universes[selectedUniverse]?.name || selectedUniverse.toUpperCase();
    clearAllFilters();
    filterByForme(selectedForme);
    showFilterMessage(`${selectedForme.toUpperCase()} actif de ${universeName}`);
}

// Fonction de filtrage améliorée avec données réelles
function filterByForme(selectedForme) {
    console.log(`Filtrage par forme: ${selectedForme}`);

    if (!selectedForme || window.lastSelectedForme === selectedForme) {
        clearAllFilters();
        return;
    }

    window.lastSelectedForme = selectedForme;
    clearAllFilters();

    const allCells = document.querySelectorAll('.chip-cell');
    const universeName = universes[selectedUniverse]?.name || selectedUniverse.toUpperCase();
    let visibleCount = 0;

    allCells.forEach(cell => {
        const chipNumber = parseInt(cell.dataset.chip);
        let hasMatchingForme = false;

        // Vérifier dans les tiroirs de ce chip
        const drawers = cell.querySelectorAll('.chip-drawer');
        drawers.forEach(drawer => {
            if (drawer.className.includes(`drawer-${selectedForme}`)) {
                hasMatchingForme = true;
            }
        });

        if (hasMatchingForme) {
            cell.classList.add('filtered-in');
            cell.style.opacity = '1';
            cell.style.border = '3px solid #3498db';
            cell.style.backgroundColor = '#e8f4fd';
            cell.style.transform = 'scale(1.02)';
            visibleCount++;
        } else {
            cell.classList.add('filtered-out');
            cell.style.opacity = '0.15';
            cell.style.filter = 'grayscale(100%)';
            cell.style.transform = 'scale(0.95)';
        }
    });

    showFilterMessage(`FORME ${selectedForme.toUpperCase()} active de ${universeName} (${visibleCount} chips)`);
}

// Effacer tous les filtres et restaurer l'apparence normale
function clearAllFilters() {
    const allCells = document.querySelectorAll('.chip-cell');
    const allDrawers = document.querySelectorAll('.chip-drawer');
    const legendItems = document.querySelectorAll('.forme-item');
    const clearButton = document.querySelector('.clear-filters-btn');
    const quadrantButtons = document.querySelectorAll('.quadrant-selector-btn');
    const granqueSlots = document.querySelectorAll('.granque-slot');
    const tomeSlots = document.querySelectorAll('.tome-slot');

    allCells.forEach(cell => {
        cell.classList.remove('filtered-out', 'filtered-in');
        cell.style.opacity = '1';
        cell.style.border = '';
        cell.style.backgroundColor = '';
        cell.style.transform = '';
        cell.style.filter = '';
        cell.style.zIndex = '';
    });

    // Réinitialiser tous les tiroirs
    allDrawers.forEach(drawer => {
        drawer.style.background = '';
        drawer.style.color = '';
        drawer.style.fontWeight = '';
        drawer.style.transform = '';
        drawer.style.opacity = '1';
    });

    legendItems.forEach(item => {
        item.classList.remove('selected');
    });

    // Réinitialiser les boutons de quadrants
    activeQuadrants.clear();
    quadrantButtons.forEach(btn => {
        btn.style.opacity = '0.6';
        btn.style.background = '#95a5a6';
    });

    // Réinitialiser les granques et tomes
    activeGranque = null;
    activeTome = null;
    granqueSlots.forEach(slot => {
        slot.style.transform = 'scale(1)';
        slot.style.boxShadow = 'none';
    });
    tomeSlots.forEach(slot => {
        slot.style.transform = 'scale(1)';
        slot.style.boxShadow = 'none';
    });

    // Réinitialiser les formes
    activeFormeFilter = null;
    resetFormeButtons();

    window.lastSelectedForme = null;
    currentFilter = null;
    if (clearButton) clearButton.style.display = 'none';

    // Effacer la sélection de chip
    clearChipSelection();

    // Effacer les sélections de tiroirs
    clearDrawerSelections();

    // Fermer le popup de stats
    closeFilterStats();

    hideFilterMessage();
}

// Afficher un message de filtre avec bouton de réinitialisation
function showFilterMessage(message) {
    let filterMsg = document.getElementById('filterMessage');
    if (!filterMsg) {
        filterMsg = document.createElement('div');
        filterMsg.id = 'filterMessage';
        filterMsg.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: #3498db;
            color: white;
            padding: 10px 15px;
            border-radius: 5px;
            z-index: 1000;
            font-weight: bold;
            box-shadow: 0 2px 10px rgba(0,0,0,0.2);
            display: flex;
            align-items: center;
            gap: 10px;
        `;
        document.body.appendChild(filterMsg);
    }

    filterMsg.innerHTML = `
        <span>${message}</span>
        <button onclick="clearAllFilters()" style="
            background: rgba(255,255,255,0.2);
            border: 1px solid rgba(255,255,255,0.5);
            color: white;
            padding: 4px 8px;
            border-radius: 3px;
            cursor: pointer;
            font-size: 0.8em;
            font-weight: bold;
        ">✕ Réinitialiser</button>
    `;
    filterMsg.style.display = 'flex';
}

// Masquer le message de filtre
function hideFilterMessage() {
    const filterMsg = document.getElementById('filterMessage');
    if (filterMsg) {
        filterMsg.style.display = 'none';
    }
}

async function updateGranqueTomeButtons() {
    try {
        // Charger les granques
        const granqueResponse = await fetch(`/api/granques/${selectedUniverse}`);
        const granqueData = await granqueResponse.json();
        console.log('Réponse granques:', granqueData);

        // Charger les tomes
        const tomeResponse = await fetch(`/api/tomes/${selectedUniverse}`);
        const tomeData = await tomeResponse.json();
        console.log('Réponse tomes:', tomeData);

        // Mettre à jour les boutons granques avec vraies données
        const granqueContainer = document.getElementById('granqueFilters');
        if (granqueContainer && granqueData.status === 'success') {
            let html = `<h5>Granques (${granqueData.total_granques})</h5>`;
            html += '<div class="granque-visual-grid">';

            if (granqueData.granques && granqueData.granques.length > 0) {
                granqueData.granques.forEach(granque => {
                    html += `<div class="granque-slot active" onclick="filterByGranque('${granque.name}')" title="${granque.count} combinations">
                        <div class="granque-label">${granque.name || 'N/A'}</div>
                        <div class="granque-count">${granque.count || 0}</div>
                    </div>`;
                });
            } else {
                html += '<div style="color: #666; padding: 10px;">Aucune granque trouvée</div>';
            }

            html += '</div>';
            granqueContainer.innerHTML = html;
        }

        // Mettre à jour les boutons tomes avec vraies données
        const tomeContainer = document.getElementById('tomeButtons');
        if (tomeContainer && tomeData.status === 'success') {
            let html = `<h5>Tomes (${tomeData.total_tomes})</h5>`;
            html += '<div class="tome-visual-grid">';

            if (tomeData.tomes && tomeData.tomes.length > 0) {
                tomeData.tomes.forEach(tome => {
                    html += `<div class="tome-slot active" onclick="filterByTome('${tome.name}')" title="${tome.count} combinations">
                        <div class="tome-label">${tome.name || 'N/A'}</div>
                        <div class="tome-count">${tome.count || 0}</div>
                    </div>`;
                });
            } else {
                html += '<div style="color: #666; padding: 10px;">Aucun tome trouvé</div>';
            }

            html += '</div>';
            tomeContainer.innerHTML = html;
        }

    } catch (error) {
        console.error('Erreur chargement granques/tomes:', error);
        console.log('Données granques reçues:', granqueData);
        console.log('Données tomes reçues:', tomeData);
    }
}

// Variables pour suivre les filtres actifs
let activeGranque = null;
let activeTome = null;

// Filtrage par granque avec désélection
function filterByGranque(granque) {
    const universeName = universes[selectedUniverse]?.name || selectedUniverse.toUpperCase();

    // Désélection si déjà actif
    if (activeGranque === granque) {
        clearAllFilters();
        closeFilterStats();
        return;
    }

    clearAllFilters();
    activeGranque = granque;

    // Mettre à jour l'apparence du bouton
    document.querySelectorAll('.granque-slot').forEach(slot => {
        const label = slot.querySelector('.granque-label');
        if (label && label.textContent === granque) {
            slot.style.transform = 'scale(1.05)';
            slot.style.boxShadow = '0 4px 12px rgba(230, 126, 34, 0.4)';
            slot.style.background = '#e67e22';
            slot.style.color = 'white';
        } else {
            slot.style.transform = 'scale(1)';
            slot.style.boxShadow = 'none';
            slot.style.background = '';
            slot.style.color = '';
        }
    });

    // Utiliser l'API pour filtrer par granque (tiroirs spécifiques)
    fetch(`/api/stats/${selectedUniverse}/granque/${encodeURIComponent(granque)}`)
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                const allCells = document.querySelectorAll('.chip-cell');
                const allDrawers = document.querySelectorAll('.chip-drawer');
                let visibleCount = 0;
                let drawerCount = 0;  // Compter manuellement les tiroirs comme le filtre par forme

                // Réinitialiser tous les tiroirs
                allDrawers.forEach(drawer => {
                    drawer.style.background = '';
                    drawer.style.transform = '';
                    drawer.style.boxShadow = '';
                });

                // Mettre en évidence les chips et tiroirs spécifiques
                allCells.forEach(cell => {
                    const chipNumber = parseInt(cell.dataset.chip);
                    const chipName = `chip${chipNumber}`;
                    let hasGranqueDrawer = false;

                    if (data.filtered_chips.includes(chipName)) {
                        // Mettre en évidence les tiroirs spécifiques de cette granque
                        const drawers = cell.querySelectorAll('.chip-drawer');
                        drawers.forEach(drawer => {
                            const drawerForme = drawer.className.match(/drawer-([a-z-]+)/)?.[1];
                            const denominationSpan = drawer.querySelector('.denomination-clickable');

                            if (denominationSpan && drawerForme) {
                                const denomination = denominationSpan.textContent.trim();

                                // Vérifier si ce tiroir correspond à la granque
                                const matchingDetail = data.granque_details.find(detail =>
                                    detail.chip === chipName &&
                                    detail.forme === drawerForme &&
                                    detail.denomination.includes(denomination)
                                );

                                if (matchingDetail) {
                                    drawer.style.background = 'linear-gradient(135deg, #e67e22, #d35400)';
                                    drawer.style.transform = 'scale(1.05)';
                                    drawer.style.boxShadow = '0 4px 12px rgba(230, 126, 34, 0.4)';
                                    hasGranqueDrawer = true;
                                    drawerCount++;  // Compter manuellement comme le filtre par forme
                                }
                            }
                        });

                        if (hasGranqueDrawer) {
                            cell.classList.add('filtered-in');
                            cell.style.opacity = '1';
                            cell.style.border = '2px solid #e67e22';
                            cell.style.backgroundColor = '#fdf6f0';
                            visibleCount++;
                        } else {
                            cell.classList.add('filtered-out');
                            cell.style.opacity = '0.3';
                        }
                    } else {
                        cell.classList.add('filtered-out');
                        cell.style.opacity = '0.15';
                        cell.style.filter = 'grayscale(100%)';
                        cell.style.transform = 'scale(0.95)';
                    }
                });

                // Utiliser le compteur manuel au lieu de data.stats.total_drawers
                showFilterMessage(`GRANQUE ${granque} actif de ${universeName} (${visibleCount} chips, ${drawerCount} tiroirs)`);

                // Passer les données spécifiques à la granque pour les stats
                showFilterStatsWithData('granque', granque, data);
            }
        })
        .catch(error => console.error('Erreur filtrage granque:', error));
}

// Filtrage par tome avec désélection
function filterByTome(tome) {
    const universeName = universes[selectedUniverse]?.name || selectedUniverse.toUpperCase();

    // Désélection si déjà actif
    if (activeTome === tome) {
        clearAllFilters();
        closeFilterStats();
        return;
    }

    clearAllFilters();
    activeTome = tome;

    // Mettre à jour l'apparence du bouton
    document.querySelectorAll('.tome-slot').forEach(slot => {
        const label = slot.querySelector('.tome-label');
        if (label && label.textContent === tome) {
            slot.style.transform = 'scale(1.05)';
            slot.style.boxShadow = '0 4px 12px rgba(142, 68, 173, 0.4)';
            slot.style.background = '#8e44ad';
            slot.style.color = 'white';
        } else {
            slot.style.transform = 'scale(1)';
            slot.style.boxShadow = 'none';
            slot.style.background = '';
            slot.style.color = '';
        }
    });

    // Utiliser l'API pour filtrer par tome
    fetch(`/api/stats/${selectedUniverse}/tome/${encodeURIComponent(tome)}`)
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                const allCells = document.querySelectorAll('.chip-cell');
                let visibleCount = 0;

                allCells.forEach(cell => {
                    const chipNumber = parseInt(cell.dataset.chip);
                    const chipName = `chip${chipNumber}`;

                    if (data.filtered_chips.includes(chipName)) {
                        cell.classList.add('filtered-in');
                        cell.style.opacity = '1';
                        cell.style.border = '3px solid #8e44ad';
                        cell.style.backgroundColor = '#f8f5fb';
                        cell.style.transform = 'scale(1.02)';
                        visibleCount++;
                    } else {
                        cell.classList.add('filtered-out');
                        cell.style.opacity = '0.15';
                        cell.style.filter = 'grayscale(100%)';
                        cell.style.transform = 'scale(0.95)';
                    }
                });

                showFilterMessage(`TOME ${tome} actif de ${universeName} (${visibleCount} chips)`);
                showFilterStats('tome', tome);
            }
        })
        .catch(error => console.error('Erreur filtrage tome:', error));
}

// Fonction utilitaire pour surligner les chips filtrés
function highlightFilteredChips(filteredChips, color) {
    const allCells = document.querySelectorAll('.chip-cell');

    allCells.forEach(cell => {
        const chipNumber = (parseInt(cell.dataset.row) - 1) * 6 + parseInt(cell.dataset.col);

        if (filteredChips[chipNumber]) {
            cell.classList.add('filtered-in');
            cell.style.opacity = '1';
            cell.style.border = `3px solid ${color}`;
            cell.style.backgroundColor = `${color}15`;
            cell.style.transform = 'scale(1.02)';
        } else {
            cell.classList.add('filtered-out');
            cell.style.opacity = '0.15';
            cell.style.filter = 'grayscale(100%)';
            cell.style.transform = 'scale(0.95)';
        }
    });
}

// Placeholder functions for other UI interactions
function showAllTableDetails() {
    alert('Voir tout le tableau - Fonctionnalité à implémenter');
}

function toggleSidePanel() {
    const sidePanel = document.getElementById('sidePanel');
    if (sidePanel) {
        sidePanel.classList.toggle('open');
    }
}

function showUpdatePanel() {
    const updatePanel = document.getElementById('updatePanel');
    if (updatePanel) {
        updatePanel.style.display = 'block';
    }
}

function hideUpdatePanel() {
    const updatePanel = document.getElementById('updatePanel');
    if (updatePanel) {
        updatePanel.style.display = 'none';
    }
}

function checkForUpdates() {
    alert('Vérifier les mises à jour - Fonctionnalité à implémenter');
}

function applyUpdate() {
    alert('Appliquer la mise à jour - Fonctionnalité à implémenter');
}

// Afficher les détails d'une dénomination avec ses combinations
async function showDenominationDetails(universe, denomination, event) {
    try {
        if (event && event.stopPropagation) event.stopPropagation();
        closeDenominationDetails();
        // Nettoyer la dénomination des entités HTML
        const cleanDenomination = denomination
            .replace(/&#39;/g, "'")
            .replace(/&quot;/g, '"')
            .replace(/&amp;/g, '&')
            .replace(/&lt;/g, '<')
            .replace(/&gt;/g, '>');

        console.log(`Requête dénomination: "${cleanDenomination}" dans ${universe}`);

        const response = await fetch(`/api/denomination/${universe}/${encodeURIComponent(cleanDenomination)}`);
        const data = await response.json();

        console.log('Réponse API:', data);

        if (data.status !== 'success') {
            alert('Erreur lors du chargement des détails de la dénomination');
            return;
        }

        const bubble = document.createElement('div');
        bubble.id = 'denominationDetailsBubble';
        bubble.style.cssText = `
            position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%);
            background: white; border: 3px solid #2980b9; border-radius: 15px;
            padding: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.3); z-index: 2000;
            max-width: 700px; max-height: 600px; overflow: visible;
            font-family: Arial, sans-serif;
        `;

        let html = `<h3 style="margin: 0 0 15px 0; color: #2c3e50; text-align: center;">DÉNOMINATION: ${cleanDenomination}</h3>`;
        html += `<p style="text-align: center; color: #7f8c8d; margin-bottom: 20px;">${universe.toUpperCase()} - ${data.total_combinations} combinations (ordre alpha-ranking)</p>`;

        if (data.combinations && data.combinations.length > 0) {
            html += `<div style="max-height: 350px; overflow-y: auto; border: 1px solid #ddd; border-radius: 8px; padding: 10px; background: #fafafa;">`;
            html += `<table style="width: 100%; border-collapse: collapse; font-size: 0.9em;">`;
            html += `<thead><tr style="background: #2c3e50; color: white; font-weight: bold;">
                        <th style="padding: 8px; border: 1px solid #34495e; text-align: left; color: white;">Forme</th>
                        <th style="padding: 8px; border: 1px solid #34495e; text-align: left; color: white;">Chip</th>
                        <th style="padding: 8px; border: 1px solid #34495e; text-align: center; color: white;">Combination</th>
                        <th style="padding: 8px; border: 1px solid #34495e; text-align: center; color: white;">α-Rank</th>
                        <th style="padding: 8px; border: 1px solid #34495e; text-align: left; color: white;">Détails</th>
                     </tr></thead>`;
            html += `<tbody>`;

            data.combinations.forEach((combo, index) => {
                const icon = generateCompositeIcon(combo.forme);
                const color = getFormeColor(combo.forme);
                const rowBg = index % 2 === 0 ? '#ffffff' : '#f8f9fa';

                html += `<tr style="background: ${rowBg}; border-bottom: 1px solid #dee2e6;">
                    <td style="padding: 8px; border: 1px solid #dee2e6; vertical-align: middle;">
                        <span style="font-size: 1.1em; margin-right: 6px;">${icon}</span>
                        <strong style="color: ${color};">${combo.forme}</strong>
                    </td>
                    <td style="padding: 8px; border: 1px solid #dee2e6; vertical-align: middle;">
                        <strong style="color: #2c3e50; font-size: 1em;">${combo.chip}</strong>
                    </td>
                    <td style="padding: 8px; border: 1px solid #dee2e6; text-align: center; vertical-align: middle;">
                        <span style="background: #e74c3c; color: white; padding: 4px 8px; border-radius: 6px; font-weight: bold; font-size: 1.1em;">${combo.combination || 'N/A'}</span>
                    </td>
                    <td style="padding: 8px; border: 1px solid #dee2e6; text-align: center; vertical-align: middle;">
                        <span style="background: #3498db; color: white; padding: 2px 6px; border-radius: 4px; font-weight: bold;">${combo.alpha_ranking}</span>
                    </td>
                    <td style="padding: 8px; border: 1px solid #dee2e6; vertical-align: middle; font-size: 0.85em; color: #495057;">
                        ${combo.petique} | ${combo.tome}<br/>
                        <span style="color: #6c757d;">${combo.granque_name}</span>
                    </td>
                </tr>`;
            });

            html += `</tbody></table></div>`;
        } else {
            html += `<div style="text-align: center; padding: 20px; color: #6c757d; background: #f8f9fa; border-radius: 8px; border: 1px solid #dee2e6;">
                        <p style="margin: 0; font-size: 1.1em;">❌ Aucune combination trouvée</p>
                     </div>`;
        }

        html += `<button onclick="closeDenominationDetails()" style="margin-top: 15px; width: 100%; padding: 10px; background: #e74c3c; color: white; border: none; border-radius: 8px; cursor: pointer; font-weight: bold;">Fermer</button>`;

        bubble.innerHTML = html;

        const overlay = document.createElement('div');
        overlay.id = 'denominationDetailsOverlay';
        overlay.style.cssText = `position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); z-index: 1999;`;
        overlay.onclick = closeDenominationDetails;

        document.body.appendChild(overlay);
        document.body.appendChild(bubble);

    } catch (error) {
        console.error('Erreur chargement détails dénomination:', error);
        alert('Erreur lors du chargement des détails');
    }
}

// Fermer la bulle de détails de dénomination
function closeDenominationDetails() {
    const bubble = document.getElementById('denominationDetailsBubble');
    const overlay = document.getElementById('denominationDetailsOverlay');
    if (bubble) bubble.remove();
    if (overlay) overlay.remove();
}

// Afficher les détails de dénominations multiples
async function showMultipleDenominationDetails(universe, multipleDenomination, event) {
    try {
        // Stopper propagation et fermer toute bulle existante
        if (event && event.stopPropagation) event.stopPropagation();
        closeDenominationDetails();
        // Séparer les dénominations
        const denominations = multipleDenomination.split('/').map(d => d.trim());

        const bubble = document.createElement('div');
        bubble.id = 'denominationDetailsBubble';
        bubble.style.cssText = `
            position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%);
            background: white; border: 3px solid #2980b9; border-radius: 15px;
            padding: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.3); z-index: 2000;
            max-width: 700px; max-height: 600px; overflow: visible;
            font-family: Arial, sans-serif;
        `;

        let html = `<h3 style="margin: 0 0 15px 0; color: #2c3e50; text-align: center;">DÉNOMINATIONS MULTIPLES</h3>`;
        html += `<p style="text-align: center; color: #7f8c8d; margin-bottom: 20px;">${universe.toUpperCase()} - ${denominations.length} dénominations</p>`;

        // Charger les détails pour chaque dénomination
        const promises = denominations.map(async (denomination) => {
            try {
                const response = await fetch(`/api/denomination/${universe}/${encodeURIComponent(denomination)}`);
                return await response.json();
            } catch (error) {
                return { status: 'error', denomination: denomination, error: error.message };
            }
        });

        const results = await Promise.all(promises);

        console.groupCollapsed('[DIAG] showMultipleDenominationDetails fetched results');
        console.log('denominations:', denominations);
        try { console.log('results sample:', results.slice(0,3)); } catch (e) { console.log('results log err', e); }
        console.groupEnd();

        // Afficher chaque section
        results.forEach((data, index) => {
            const denomination = denominations[index];

            html += `<div style="margin-bottom: 20px; border: 2px solid #3498db; border-radius: 8px; padding: 15px; background: #f8f9fa;">`;
            html += `<h4 style="margin: 0 0 10px 0; color: #2980b9; border-bottom: 1px solid #bdc3c7; padding-bottom: 5px;">${denomination}</h4>`;

            if (data.status === 'success' && data.combinations && data.combinations.length > 0) {
                html += `<div style="max-height: 200px; overflow-y: auto;">`;
                html += `<table style="width: 100%; border-collapse: collapse; font-size: 0.85em;">`;
                html += `<thead><tr style="background: #2c3e50; color: white; font-weight: bold;">
                            <th style="padding: 6px; border: 1px solid #34495e; color: white;">Forme</th>
                            <th style="padding: 6px; border: 1px solid #34495e; color: white;">Chip</th>
                            <th style="padding: 6px; border: 1px solid #34495e; color: white;">Combination</th>
                            <th style="padding: 6px; border: 1px solid #34495e; color: white;">α-Rank</th>
                         </tr></thead>`;
                html += `<tbody>`;

                data.combinations.forEach((combo, idx) => {
                    const icon = generateCompositeIcon(combo.forme);
                    const color = getFormeColor(combo.forme);
                    const rowBg = idx % 2 === 0 ? '#ffffff' : '#f8f9fa';

                    html += `<tr style="background: ${rowBg};">
                        <td style="padding: 6px; border: 1px solid #dee2e6;">
                            <span style="margin-right: 4px;">${icon}</span>
                            <strong style="color: ${color};">${combo.forme}</strong>
                        </td>
                        <td style="padding: 6px; border: 1px solid #dee2e6;">
                            <strong>${combo.chip}</strong>
                        </td>
                        <td style="padding: 6px; border: 1px solid #dee2e6; text-align: center;">
                            <span style="background: #e74c3c; color: white; padding: 2px 6px; border-radius: 4px;">${combo.combination || 'N/A'}</span>
                        </td>
                        <td style="padding: 6px; border: 1px solid #dee2e6; text-align: center;">
                            <span style="background: #3498db; color: white; padding: 2px 6px; border-radius: 4px;">${combo.alpha_ranking}</span>
                        </td>
                    </tr>`;
                });

                html += `</tbody></table></div>`;
                html += `<p style="margin: 8px 0 0 0; font-size: 0.8em; color: #6c757d; text-align: right;">${data.total_combinations} combinations</p>`;
            } else {
                html += `<p style="color: #6c757d; font-style: italic; margin: 0;">Aucune combination trouvée</p>`;
            }

            html += `</div>`;
        });

        html += `<button onclick="closeDenominationDetails()" style="width: 100%; padding: 10px; background: #e74c3c; color: white; border: none; border-radius: 8px; cursor: pointer; font-weight: bold; margin-top: 10px;">Fermer</button>`;

        bubble.innerHTML = html;

        const overlay = document.createElement('div');
        overlay.id = 'denominationDetailsOverlay';
        overlay.style.cssText = `position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); z-index: 1999;`;
        overlay.onclick = closeDenominationDetails;

        document.body.appendChild(overlay);
        document.body.appendChild(bubble);

    } catch (error) {
        console.error('Erreur chargement détails multiples:', error);
        alert('Erreur lors du chargement des détails');
    }
}

// Afficher les statistiques d'un filtre
async function showFilterStats(filterType, filterValue) {
    try {
        const response = await fetch(`/api/stats/${selectedUniverse}/${filterType}/${encodeURIComponent(filterValue)}`);
        const data = await response.json();

        if (data.status !== 'success') return;

        showFilterStatsWithData(filterType, filterValue, data);

    } catch (error) {
        console.error('Erreur stats:', error);
    }
}

// Afficher les statistiques avec des données spécifiques
function showFilterStatsWithData(filterType, filterValue, data) {
    const bubble = document.createElement('div');
    bubble.id = 'filterStatsBubble';
    bubble.style.cssText = `position: fixed; top: 80px; left: 50%; transform: translateX(-50%); background: #2c3e50; color: white; border: 2px solid #3498db; border-radius: 8px; padding: 12px; box-shadow: 0 4px 15px rgba(52,152,219,0.4); z-index: 1500; max-width: 280px; font-weight: bold;`;

    let html = `<h4 style="margin: 0 0 8px 0; color: #3498db; text-align: center;">${filterType.toUpperCase()} ${filterValue}</h4>`;
    html += `<div style="background: rgba(255,255,255,0.1); padding: 8px; border-radius: 4px; line-height: 1.4;">`;

    // Affichage adapté selon le type de filtre
    if (filterType === 'granque') {
        const combinations = data.granque_details ? data.granque_details.length : 0;
        const chips = data.filtered_chips ? data.filtered_chips.length : 0;
        const drawers = data.stats ? data.stats.total_drawers : 0;

        html += `<div style="color: #ecf0f1;">📊 <strong>Combinations:</strong> <span style="color: #f39c12;">${combinations}</span></div>`;
        html += `<div style="color: #ecf0f1;">🎯 <strong>Chips:</strong> <span style="color: #e74c3c;">${chips}</span></div>`;
        html += `<div style="color: #ecf0f1;">🏷️ <strong>Tiroirs:</strong> <span style="color: #2ecc71;">${drawers}</span></div>`;
    } else {
        html += `<div style="color: #ecf0f1;">📊 <strong>Combinations:</strong> <span style="color: #f39c12;">${data.stats ? data.stats.total_combinations : 0}</span></div>`;
        html += `<div style="color: #ecf0f1;">🎯 <strong>Chips:</strong> <span style="color: #e74c3c;">${data.stats ? data.stats.total_chips : 0}</span></div>`;
        html += `<div style="color: #ecf0f1;">🏷️ <strong>Tiroirs:</strong> <span style="color: #2ecc71;">${data.stats ? data.stats.total_drawers : 0}</span></div>`;
        html += `<div style="color: #ecf0f1;">📇 <strong>Dénominations:</strong> <span style="color: #9b59b6;">${data.stats ? data.stats.total_denominations : 0}</span></div>`;
    }

    html += `</div>`;
    html += `<button onclick="closeFilterStats()" style="width: 100%; padding: 6px; background: #e74c3c; color: white; border: none; border-radius: 4px; cursor: pointer; margin-top: 8px; font-weight: bold;">✕ Fermer</button>`;

    bubble.innerHTML = html;

    // Supprimer l'ancienne bulle s'il y en a une
    closeFilterStats();
    document.body.appendChild(bubble);
}

function closeFilterStats() {
    const bubble = document.getElementById('filterStatsBubble');
    if (bubble) bubble.remove();
}

// Sélection/désélection des tiroirs
function toggleDrawerSelection(drawerId, chipNumber, forme, denomination) {
    const drawer = document.getElementById(drawerId);
    if (!drawer || denomination === '---') return;

    const universeName = universes[selectedUniverse]?.name || selectedUniverse.toUpperCase();

    if (selectedDrawers.has(drawerId)) {
        // Désélectionner
        selectedDrawers.delete(drawerId);
        drawer.classList.remove('drawer-selected');
        drawer.style.background = '';
        drawer.style.transform = '';
        drawer.style.boxShadow = '';
        drawer.style.border = '';

        if (selectedDrawers.size === 0) {
            hideFilterMessage();
            closeFilterStats();
        } else {
            updateDrawerSelectionMessage();
        }
    } else {
        // Sélectionner
        selectedDrawers.add(drawerId);
        drawer.classList.add('drawer-selected');
        drawer.style.background = 'linear-gradient(135deg, #3498db, #2980b9)';
        drawer.style.transform = 'scale(1.08)';
        drawer.style.boxShadow = '0 4px 15px rgba(52, 152, 219, 0.4)';
        drawer.style.border = '2px solid #2980b9';
        drawer.style.color = 'white';
        drawer.style.fontWeight = 'bold';

        updateDrawerSelectionMessage();
        showDrawerStats(drawerId, chipNumber, forme, denomination);
    }
}

// Mettre à jour le message de sélection des tiroirs
function updateDrawerSelectionMessage() {
    const count = selectedDrawers.size;
    const universeName = universes[selectedUniverse]?.name || selectedUniverse.toUpperCase();

    if (count === 1) {
        showFilterMessage(`1 tiroir sélectionné dans ${universeName}`);
    } else {
        showFilterMessage(`${count} tiroirs sélectionnés dans ${universeName}`);
    }
}

// Afficher les stats d'un tiroir sélectionné
function showDrawerStats(drawerId, chipNumber, forme, denomination) {
    const bubble = document.createElement('div');
    bubble.id = 'drawerStatsBubble';
    bubble.style.cssText = `
        position: fixed; top: 80px; left: 50%; transform: translateX(-50%);
        background: #34495e; color: white; border: 2px solid #3498db; border-radius: 8px;
        padding: 12px; box-shadow: 0 4px 15px rgba(52,152,219,0.4); z-index: 1500;
        max-width: 280px; font-weight: bold;
    `;

    const icon = generateCompositeIcon(forme);
    const color = getFormeColor(forme);

    let html = `<h4 style="margin: 0 0 8px 0; color: #3498db; text-align: center;">TIROIR SÉLECTIONNÉ</h4>`;
    html += `<div style="background: rgba(255,255,255,0.1); padding: 8px; border-radius: 4px; line-height: 1.4;">`;
    html += `<div style="color: #ecf0f1;">🎯 <strong>Chip:</strong> <span style="color: #f39c12;">${chipNumber}</span></div>`;
    html += `<div style="color: #ecf0f1;">🔶 <strong>Forme:</strong> <span style="color: ${color};">${icon} ${forme}</span></div>`;
    html += `<div style="color: #ecf0f1;">🏷️ <strong>Dénomination:</strong> <span style="color: #2ecc71;">${denomination}</span></div>`;
    html += `</div>`;
    html += `<button onclick="closeDrawerStats()" style="width: 100%; padding: 6px; background: #e74c3c; color: white; border: none; border-radius: 4px; cursor: pointer; margin-top: 8px; font-weight: bold;">✕ Fermer</button>`;

    bubble.innerHTML = html;

    // Supprimer l'ancien popup s'il existe
    closeDrawerStats();
    document.body.appendChild(bubble);
}

// Fermer les stats de tiroir
function closeDrawerStats() {
    const bubble = document.getElementById('drawerStatsBubble');
    if (bubble) bubble.remove();
}

// Afficher bulle d'information pétique
function showPetiqueBubble(quadrant, petiqueName, buttonElement) {
    hidePetiqueBubble();

    const bubble = document.createElement('div');
    bubble.id = 'petiqueBubble';
    bubble.style.cssText = `
        position: fixed;
        background: #34495e;
        color: white;
        padding: 8px 12px;
        border-radius: 6px;
        font-size: 0.8em;
        font-weight: bold;
        z-index: 2000;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        border: 2px solid #3498db;
        white-space: nowrap;
        pointer-events: none;
    `;

    const rect = buttonElement.getBoundingClientRect();
    const bubbleLeft = rect.left + rect.width / 2;
    const bubbleTop = rect.top - 40;

    bubble.style.left = bubbleLeft + 'px';
    bubble.style.top = bubbleTop + 'px';
    bubble.style.transform = 'translateX(-50%)';

    bubble.innerHTML = `
        <div style="text-align: center;">
            <div style="color: #3498db; font-size: 0.9em;">${quadrant.toUpperCase()}</div>
            <div style="margin-top: 2px;">${petiqueName}</div>
        </div>
    `;

    document.body.appendChild(bubble);
}

// Masquer bulle d'information pétique
function hidePetiqueBubble() {
    const bubble = document.getElementById('petiqueBubble');
    if (bubble) bubble.remove();
}

// Effacer toutes les sélections de tiroirs
function clearDrawerSelections() {
    selectedDrawers.forEach(drawerId => {
        const drawer = document.getElementById(drawerId);
        if (drawer) {
            drawer.classList.remove('drawer-selected');
            drawer.style.background = '';
            drawer.style.transform = '';
            drawer.style.boxShadow = '';
            drawer.style.border = '';
            drawer.style.color = '';
            drawer.style.fontWeight = '';
        }
    });
    selectedDrawers.clear();
    closeDrawerStats();
}

function highlightQuadrant(quadrant) {
    const currentlySelected = document.querySelector(`.chip-cell.${quadrant}.selected-quadrant`);

    // D'abord, enlever le surlignage de partout
    document.querySelectorAll('.chip-cell').forEach(cell => {
        cell.classList.remove('selected-quadrant');
    });

    // Si le quadrant sur lequel on a cliqué n'était pas déjà sélectionné, on le surligne
    if (!currentlySelected) {
        document.querySelectorAll(`.chip-cell.${quadrant}`).forEach(cell => {
            cell.classList.add('selected-quadrant');
        });
    }
}


function showUniverseBanner(universeKey) {
    const banner = document.getElementById('universeBanner');
    if (banner) banner.remove();
}

function getUniverseIcon(universeKey) {
    const icons = {
        mundo: '🌍',
        fruity: '🍓',
        trigga: '⚡',
        roaster: '🔥',
        sunshine: '☀️'
    };
    return icons[universeKey] || '🌍';
}
