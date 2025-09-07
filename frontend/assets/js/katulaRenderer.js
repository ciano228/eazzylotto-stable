// Module de rendu de l'interface Katula
import { FORME_ICONS, FORME_COLORS } from './katulaConstants.js';
import { getChipFrequency } from './katulaAnalytics.js';
import { getUniverseFormes } from './katulaUtils.js';

export function renderKatulaGrid(universeData, containerId) {
    const container = document.getElementById(containerId);
    if (!container) return;

    let html = '<div class="katula-grid">';
    
    // En-têtes
    html += '<div class="grid-header">Lignes</div>';
    for (let col = 1; col <= 6; col++) {
        html += `<div class="grid-header">C${col}</div>`;
    }
    
    // Générer les 8 lignes × 6 colonnes = 48 chips
    for (let row = 1; row <= 8; row++) {
        html += `<div class="ligne-label">L${row}</div>`;
        for (let col = 1; col <= 6; col++) {
            const chipNumber = ((row - 1) * 6) + col;
            html += createChipHTML(chipNumber, universeData);
        }
    }
    
    html += '</div>';
    container.innerHTML = html;
}

function createChipHTML(chipNumber, universeData) {
    const chipData = universeData.chipDetails[chipNumber];
    const formesData = chipData?.formes_data || {};
    const formes = getUniverseFormes(universeData);
    const freq = getChipFrequency(chipNumber);

    let html = `
        <div class="chip-cell" data-chip="${chipNumber}" onclick="window.showChipDetails(${chipNumber})" title="chip${chipNumber}">
            <div class="chip-header">chip${chipNumber}</div>
            <div class="chip-drawers">
    `;
    
    // Créer les tiroirs selon les formes disponibles
    formes.forEach(forme => {
        const items = formesData[forme] || [];
        const isEmpty = items.length === 0;
        
        // Gérer les dénominations multiples
        let displayText = '---';
        if (items.length > 0) {
            const denominations = [...new Set(items.map(item => item.denomination))];
            displayText = denominations.length === 1 ? denominations[0] : denominations.join('/');
        }
        
        html += `
            <div class="chip-drawer ${isEmpty ? 'empty' : ''}" 
                 data-forme="${forme}" data-chip="${chipNumber}"
                 data-denomination="${displayText}"
                 onclick="window.showDenominationDetails('${displayText}', '${universeData.universe}', event)">
                ${generateFormeIcon(forme)}
                <span class="drawer-text">${displayText}</span>
            </div>
        `;
    });
    
    html += `
            </div>
            <div class="chip-meta">
                <span>📊 Fréquence: ${freq}</span>
            </div>
        </div>
    `;
    
    return html;
}

export function generateFormeIcon(forme) {
    if (forme.includes('-')) {
        const [f1, f2] = forme.split('-');
        const icon1 = FORME_ICONS[f1] || '?';
        const icon2 = FORME_ICONS[f2] || '?';
        const color1 = FORME_COLORS[f1] || '#666';
        const color2 = FORME_COLORS[f2] || '#666';
        
        return `
            <span class="forme-icon-composite">
                <span style="color:${color1}">${icon1}</span><span style="color:${color2}">${icon2}</span>
            </span>
        `;
    } else {
        const icon = FORME_ICONS[forme] || '?';
        const color = FORME_COLORS[forme] || '#666';
        return `<span class="forme-icon" style="color:${color}">${icon}</span>`;
    }
}