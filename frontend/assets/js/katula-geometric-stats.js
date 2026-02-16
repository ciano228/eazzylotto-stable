// katula-geometric-stats.js
// Module pour l'analyse géométrique temporelle avec comptage de valeurs géométriques

// Mapping des quadrants (petiques)
const QUADRANT_MAPPING = {
    Q1: { chips: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], color: '#e74c3c', label: 'Quadrant 1' },
    Q2: { chips: [13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24], color: '#3498db', label: 'Quadrant 2' },
    Q3: { chips: [25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36], color: '#2ecc71', label: 'Quadrant 3' },
    Q4: { chips: [37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48], color: '#f39c12', label: 'Quadrant 4' }
};

// Mapping des tomes (4 tomes de 12 chips)
const TOME_MAPPING = {
    Tome1: { chips: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], color: '#9b59b6', label: 'Tome 1' },
    Tome2: { chips: [13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24], color: '#e67e22', label: 'Tome 2' },
    Tome3: { chips: [25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36], color: '#1abc9c', label: 'Tome 3' },
    Tome4: { chips: [37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48], color: '#34495e', label: 'Tome 4' }
};

// Mapping des granques (6 granques de 8 chips)
const GRANQUE_MAPPING = {
    G1: { chips: [1, 2, 3, 4, 5, 6, 7, 8], color: '#e74c3c', label: 'Granque 1' },
    G2: { chips: [9, 10, 11, 12, 13, 14, 15, 16], color: '#3498db', label: 'Granque 2' },
    G3: { chips: [17, 18, 19, 20, 21, 22, 23, 24], color: '#2ecc71', label: 'Granque 3' },
    G4: { chips: [25, 26, 27, 28, 29, 30, 3132, 33, 34, 35, 36, 37, 38, 39, 40], color: '#9b59b6', label: 'Granque 5' },
    G6: { chips: [41, 42, 43, 44, 45, 46, 47, 48], color: '#1abc9c', label: 'Granque 6' }
};

function getQuadrantFromCombination(chip1, chip2) {
    const minChip = Math.min(chip1, chip2);
    for (const [quadrantId, quadrant] of Object.entries(QUADRANT_MAPPING)) {
        if (quadrant.chips.includes(minChip)) return quadrantId;
    }
    return null;
}

function getTomeFromChip(chip) {
    for (const [tomeId, tome] of Object.entries(TOME_MAPPING)) {
        if (tome.chips.includes(chip)) return tomeId;
    }
    return null;
}

function getGranqueFromChip(chip) {
    for (const [granqueId, granque] of Object.entries(GRANQUE_MAPPING)) {
        if (granque.chips.includes(chip)) return granqueId;
    }
    return null;
}

function calculateAttributeStatistics(drawsData, attributeType) {
    const stats = {};
    const mapping = attributeType === 'quadrant' ? QUADRANT_MAPPING :
        attributeType === 'tome' ? TOME_MAPPING : GRANQUE_MAPPING;

    for (const key in mapping) {
        stats[key] = { count: 0, percentage: 0, color: mapping[key].color, label: mapping[key].label };
    }

    let total = 0;
    drawsData.forEach(draw => {
        if (draw.combinations) {
            draw.combinations.forEach(combo => {
                let attributeId = attributeType === 'quadrant' ? getQuadrantFromCombination(combo[0], combo[1]) :
                    attributeType === 'tome' ? getTomeFromChip(combo[0]) :
                        getGranqueFromChip(combo[0]);
                if (attributeId && stats[attributeId]) {
                    stats[attributeId].count++;
                    total++;
                }
            });
        }
    });

    for (const key in stats) {
        stats[key].percentage = total > 0 ? ((stats[key].count / total) * 100).toFixed(1) : 0;
    }
    return stats;
}

function displayAttributeStatistics(stats, attributeType) {
    const statsPanel = document.getElementById('attributeStatsPanel');
    const statsTypeLabel = document.getElementById('statsTypeLabel');
    const statsContent = document.getElementById('statsContent');

    if (!statsPanel || !statsTypeLabel || !statsContent) return;

    const typeLabels = { 'quadrant': 'Quadrants/Petiques', 'tome': 'Tomes', 'granque': 'Granques' };
    statsTypeLabel.textContent = typeLabels[attributeType] || attributeType;

    let html = '<div class="stats-grid">';
    for (const [key, stat] of Object.entries(stats)) {
        html += `<div class="stat-card" style="border-left: 4px solid ${stat.color}">
            <div class="stat-label">${stat.label}</div>
            <div class="stat-value">${stat.count}</div>
            <div class="stat-percentage">${stat.percentage}%</div>
            <div class="stat-bar"><div class="stat-bar-fill" style="width: ${stat.percentage}%; background: ${stat.color}"></div></div>
        </div>`;
    }
    html += '</div>';
    statsContent.innerHTML = html;
    statsPanel.style.display = 'block';
}

function displayMarkingLegend(markingType, stats = null) {
    const indicator = document.getElementById('markingIndicator');
    const typeLabel = document.getElementById('currentMarkingTypeLabel');
    const legendContent = document.getElementById('markingLegendContent');

    if (!indicator || !typeLabel || !legendContent) return;

    const typeLabels = {
        'chip': 'Par Chip', 'combination': 'Par Combinaison', 'denomination': 'Par Dénomination',
        'tome': 'Par Tome', 'forme': 'Par Forme', 'granque': 'Par Granque',
        'parite': 'Par Parité', 'zone': 'Par Zone Géométrique'
    };
    typeLabel.textContent = typeLabels[markingType] || markingType;

    let html = '';
    if (markingType === 'tome' && stats) {
        html += '<div style="color: white; margin-bottom: 10px;">Les tomes sont des zones de 12 chips consécutifs</div>';
        for (const [key, stat] of Object.entries(stats)) {
            html += `<div class="legend-item">
                <div class="legend-color" style="background: ${stat.color}"></div>
                <div class="legend-label">${stat.label}</div>
                <div class="legend-count">${stat.count} occurrences</div>
            </div>`;
        }
    } else if (markingType === 'quadrant' && stats) {
        html += '<div style="color: white; margin-bottom: 10px;">Les quadrants (petiques) divisent la table en 4 zones de 12 chips</div>';
        for (const [key, stat] of Object.entries(stats)) {
            html += `<div class="legend-item">
                <div class="legend-color" style="background: ${stat.color}"></div>
                <div class="legend-label">${stat.label}</div>
                <div class="legend-count">${stat.count} occurrences</div>
            </div>`;
        }
    } else if (markingType === 'granque' && stats) {
        html += '<div style="color: white; margin-bottom: 10px;">Les granques divisent la table en 6 zones de 8 chips</div>';
        for (const [key, stat] of Object.entries(stats)) {
            html += `<div class="legend-item">
                <div class="legend-color" style="background: ${stat.color}"></div>
                <div class="legend-label">${stat.label}</div>
                <div class="legend-count">${stat.count} occurrences</div>
            </div>`;
        }
    } else {
        html = '<div style="color: white;">Sélectionnez "Générer l\'Analyse" pour voir les statistiques</div>';
    }

    legendContent.innerHTML = html;
    indicator.style.display = 'block';
}

function toggleStatsPanel() {
    const statsPanel = document.getElementById('attributeStatsPanel');
    if (statsPanel) statsPanel.style.display = statsPanel.style.display === 'none' ? 'block' : 'none';
}

// Export
window.GeometricStats = {
    getQuadrantFromCombination, getTomeFromChip, getGranqueFromChip,
    calculateAttributeStatistics, displayAttributeStatistics,
    displayMarkingLegend, toggleStatsPanel,
    QUADRANT_MAPPING, TOME_MAPPING, GRANQUE_MAPPING
};
