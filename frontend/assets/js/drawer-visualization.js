/**
 * Module pour l'affichage des drawers en liste verticale (empilement naturel)
 * Utilise la vraie structure de la BD (drawer_name, forme, denomination)
 */

// Icônes Unicode pour les formes
const FORME_ICONS = {
    'carre': '□',
    'rectangle': '▭',
    'triangle': '△',
    'cercle': '○',
    'losange': '◇',
    'hexagone': '⬡',
    'etoile': '⭐',
    // Pour d'autres univers
    'pyramide': '▲',
    'cube': '⬛',
    'sphere': '⚪',
    'cone': '🔺',
    'cylindre': '⌭',
    'torus': '⭕'
};

// Cache pour la structure des chips
let chipDrawerStructure = {};
let currentUniverse = null;

/**
 * Charger la structure réelle des drawers depuis l'API
 */
async function loadChipDrawerStructure(universe) {
    if (currentUniverse === universe && Object.keys(chipDrawerStructure).length > 0) {
        console.log(`Structure ${universe} deja en cache`);
        return chipDrawerStructure;
    }

    try {
        console.log(`Chargement structure drawers pour ${universe}...`);

        // 1. Prefer authoritative drawer-structure endpoint
        const primaryUrl = `/api/analytics/chip-drawers-structure?universe=${encodeURIComponent(universe)}`;
        try {
            const pResp = await fetch(primaryUrl);
            if (pResp.ok) {
                const pData = await pResp.json();
                if (pData && pData.chip_structure && Object.keys(pData.chip_structure).length > 0) {
                    chipDrawerStructure = pData.chip_structure;
                    currentUniverse = universe;
                    console.log('Drawer structure loaded from primary endpoint.');
                }
            }
        } catch (e) {
            console.warn('Primary drawer structure endpoint failed, trying next fallback.', e);
        }

        // 2. Fallback to katula matrix endpoint if primary fails or returns no data
        if (!chipDrawerStructure || Object.keys(chipDrawerStructure).length === 0) {
            console.log('Falling back to katula matrix endpoint for drawer structure.');
            const matrixUrl = `/api/analytics/katula/matrix/${encodeURIComponent(universe)}`;
            const response = await fetch(matrixUrl);
            if (!response.ok) {
                throw new Error(`Erreur API (matrix): ${response.status}`);
            }
            const matrixData = await response.json();
            const chips = matrixData.chips || matrixData.result?.chips || {};
            const transformed = {};

            Object.entries(chips).forEach(([chipKey, chipInfo]) => {
                const chipNum = parseInt(chipKey, 10) || chipInfo.chip || Number(chipKey);
                if (!chipNum) return;
                
                const formes = chipInfo.formes || {};
                const drawers = [];

                Object.entries(formes).forEach(([forme, denoms]) => {
                    if (!denoms || denoms.length === 0) {
                        drawers.push({
                            drawer_name: `drawer_${chipNum}_${forme}`,
                            drawer: `drawer_${chipNum}_${forme}`,
                            forme: forme,
                            denomination: null
                        });
                    } else {
                        denoms.forEach((denom, idx) => {
                            drawers.push({
                                drawer_name: `drawer_${chipNum}_${forme}_${idx + 1}`,
                                drawer: `drawer_${chipNum}_${forme}_${idx + 1}`,
                                forme: forme,
                                denomination: denom
                            });
                        });
                    }
                });
                transformed[`chip${chipNum}`] = drawers;
            });

            chipDrawerStructure = transformed;
            currentUniverse = universe;
        }

        // 3. Fallback to local JSON if all APIs fail
        if (!chipDrawerStructure || Object.keys(chipDrawerStructure).length === 0) {
            console.log('Falling back to local JSON file for drawer structure.');
            try {
                const fallbackUrl = `/assets/data/chip_drawers_manual.json`;
                const fResp = await fetch(fallbackUrl);
                if (fResp.ok) {
                    const fallbackData = await fResp.json();
                    // In manual file, structure might be nested under universe key
                    const universeStructure = fallbackData ? (fallbackData[universe] || fallbackData) : {};
                    if (Object.keys(universeStructure).length > 0) {
                       chipDrawerStructure = universeStructure;
                    }
                }
            } catch (e) {
                console.warn('Fallback chip drawers JSON load failed:', e);
            }
        }

        const totalDrawers = Object.values(chipDrawerStructure).reduce((s, arr) => s + (arr?.length || 0), 0);
        console.log(`Structure chargee: ${totalDrawers} drawers pour ${Object.keys(chipDrawerStructure).length} chips`);

        return chipDrawerStructure;
    } catch (error) {
        console.error(`Erreur chargement structure drawers:`, error);
        return {}; // Return empty object on failure
    }
}

/**
 * Générer une mini-grille Katula en mode DRAWER
 * Affiche les drawers en LISTE VERTICALE (empilement naturel)
 */
function generateMiniKatulaGridDrawerMode(tableData) {
    const html = [];

    for (let chipNumber = 1; chipNumber <= 48; chipNumber++) {
        const chipKey = `chip${chipNumber}`;
        const chipDrawers = chipDrawerStructure[chipKey] || [];

        // Les drawers sont déjà uniques (GROUP BY dans la requête BD)
        // Pas besoin de dédupliquer

        // Drawers actifs depuis les données temporelles
        const activeDrawers = tableData.occurrences[chipNumber]?.drawers || [];

        // Créer la liste verticale de drawers
        const drawerItems = chipDrawers.map(realDrawer => {
            // Vérifier si ce drawer est actif
            const activeData = activeDrawers.find(ad => ad.drawer_name === realDrawer.drawer_name);
            const isActive = !!activeData;

            const formeIcon = FORME_ICONS[realDrawer.forme] || realDrawer.forme?.charAt(0).toUpperCase() || '?';
            const drawerShortName = realDrawer.drawer_name.replace('drawer', 'D');

            // Tooltip détaillé
            let tooltip = `${realDrawer.drawer_name}\\n`;
            tooltip += `Forme: ${realDrawer.forme}\\n`;
            tooltip += `Denomination: ${realDrawer.denomination || 'N/A'}`;
            if (isActive) {
                tooltip += `\\n\\nACTIF: ${activeData.count} occurrence(s)`;
            }

            return `
                <div class="drawer-item ${isActive ? 'active' : 'inactive'}"
                     data-drawer="${realDrawer.drawer_name}"
                     data-forme="${realDrawer.forme}"
                     data-denomination="${realDrawer.denomination || ''}"
                     title="${tooltip}">
                    <span class="forme-icon">${formeIcon}</span>
                    <span class="drawer-name">${drawerShortName}</span>
                    ${isActive ? `<span class="count-badge">${activeData.count}</span>` : ''}
                </div>
            `;
        }).join('');

        html.push(`
            <div class="mini-chip-cell drawer-mode vertical-list" 
                 data-chip="${chipNumber}"
                 data-drawer-count="${chipDrawers.length}">
                <div class="chip-number-header">${chipNumber}</div>
                <div class="drawer-list-container">
                    ${drawerItems || '<div class="no-drawers">Aucun drawer</div>'}
                </div>
            </div>
        `);
    }

    return html.join('');
}

/**
 * Générer une mini-grille Katula en mode CHIP classique
 * Affiche le chip globalement (comme avant)
 */
function generateMiniKatulaGridChipMode(tableData) {
    let html = '';

    for (let chipNumber = 1; chipNumber <= 48; chipNumber++) {
        const occurrence = tableData.occurrences[chipNumber];
        const hasOccurred = occurrence && occurrence.count > 0;

        let classes = 'mini-chip-cell chip-mode';
        let styles = '';
        let content = chipNumber;
        let tooltip = `Chip ${chipNumber} - ${tableData.title}`;

        if (hasOccurred) {
            const count = occurrence.count;
            const level = count === 1 ? 1 : count <= 3 ? 2 : 3;

            classes += ` occurred occurred-${level}`;

            // Couleur selon le niveau
            const colors = ['', '#3498db', '#e74c3c', '#8e44ad'];
            styles = `background-color: ${colors[level]} !important; color: white;`;

            // Compteur
            if (count > 1) {
                content += `<span class="occurrence-counter">${count}</span>`;
            }

            // Tooltip
            if (occurrence.attributes && occurrence.attributes.length > 0) {
                const attrs = occurrence.attributes.slice(0, 5).join(', ');
                tooltip = `Chip ${chipNumber} - ${count} occ.\\n${attrs}${occurrence.attributes.length > 5 ? '...' : ''}`;
            }
        }

        html += `
            <div class="${classes}" 
                 style="${styles}"
                 data-chip="${chipNumber}"
                 title="${tooltip}">
                ${content}
            </div>
        `;
    }

    return html;
}

/**
 * Fonction principale : génère la grille selon le mode
 */
function generateMiniKatulaGrid(tableData) {
    if (tableData.markingType === 'drawer') {
        return generateMiniKatulaGridDrawerMode(tableData);
    } else {
        return generateMiniKatulaGridChipMode(tableData);
    }
}

// Export pour utilisation dans katula-temporal-analysis.html
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        loadChipDrawerStructure,
        generateMiniKatulaGrid,
        generateMiniKatulaGridDrawerMode,
        generateMiniKatulaGridChipMode,
        FORME_ICONS
    };
}

