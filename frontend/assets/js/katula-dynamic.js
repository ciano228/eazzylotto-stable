const universes = {
    mundo: {
        name: 'Mundo',
        shapes: [
            { name: 'carre', icon: '■' },
            { name: 'triangle', icon: '▲' },
            { name: 'cercle', icon: '●' },
            { name: 'rectangle', icon: '▬' }
        ]
    },
    fruity: {
        name: 'Fruity',
        shapes: [
            { name: 'pomme', icon: '🍎' },
            { name: 'banane', icon: '🍌' },
            { name: 'orange', icon: '🍊' },
            { name: 'fraise', icon: '🍓' }
        ]
    },
    trigga: {
        name: 'Trigga',
        shapes: Array.from({ length: 10 }, (_, i) => ({ name: `forme${i + 1}`, icon: '?' }))
    },
    roaster: {
        name: 'Roaster',
        shapes: Array.from({ length: 12 }, (_, i) => ({ name: `forme${i + 1}`, icon: '?' }))
    },
    sunshine: {
        name: 'Sunshine',
        shapes: Array.from({ length: 16 }, (_, i) => ({ name: `forme${i + 1}`, icon: '?' }))
    }
};

let selectedUniverse = 'mundo'; // Default universe

document.addEventListener('DOMContentLoaded', () => {
    // Initialiser les puces d'univers
    renderUniverseChips();
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

// Couleurs des formes de base
const FORME_COLORS = {
    'carre': '#3498db',      // Bleu
    'triangle': '#27ae60',   // Vert
    'cercle': '#f1c40f',     // Jaune
    'rectangle': '#e74c3c'   // Rouge
};



function renderUniverseChips() {
    const chipsContainer = document.getElementById('universeChipsContainer');
    if (!chipsContainer) return;

    let html = '';
    for (const universeKey in universes) {
        const universe = universes[universeKey];
        html += `
            <div class="chip" id="chip-${universeKey}" onclick="selectUniverse('${universeKey}')">
                <div class="chip-header">${universe.name}</div>
                <div class="chip-drawers">
        `;
        universe.shapes.forEach(shape => {
            html += `<div class="drawer" title="${shape.name}">${shape.icon}</div>`;
        });
        html += `
                </div>
            </div>
        `;
    }
    chipsContainer.innerHTML = html;
}

function selectUniverse(universeKey) {
    selectedUniverse = universeKey;
    // Remove active class from all chips
    document.querySelectorAll('.chip').forEach(chip => chip.classList.remove('active'));
    // Add active class to the selected chip
    const selectedChip = document.getElementById(`chip-${universeKey}`);
    if (selectedChip) {
        selectedChip.classList.add('active');
    }
    loadUniverse();
}

async function loadUniverse() {
    const katulaContainer = document.getElementById('katulaContainer');
    const loadingIndicator = document.getElementById('loadingIndicator');

    if (loadingIndicator) {
        loadingIndicator.style.display = 'block';
    }
    if (katulaContainer) {
        katulaContainer.innerHTML = ''; // Clear previous content
    }

    try {
        // Placeholder for API call
        // We will need to define this API endpoint in the backend
        const response = await fetch(`/api/katula/ui-data/${selectedUniverse}`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        
        renderKatulaTable(data); // Function to render the table
        updateUniverseInfo(selectedUniverse, data); // Function to update universe info
        updateFormesLegend(data); // Function to update formes legend
        updateGranqueTomeButtons(data); // Function to update granque/tome buttons

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
        html += `<div class="header">TABLE KATULA DE L'UNIVERS ${universeName}</div>`;

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

                html += `<div class="chip-cell ${quadrant}" data-row="${r}" data-col="${c}" data-quadrant="${quadrant}" data-forme="${formeName}" onclick="highlightQuadrant('${quadrant}')">`;

                for (let i = 0; i < maxDrawers; i++) {
                    const element = cellData && cellData.elements ? cellData.elements[i] : null;
                    if (element) {
                        if (element.type === 'forme') {
                            const forme_parts = element.content.text.split('-');
                            const icon_html = forme_parts.map(part => `<span style="color: ${FORME_COLORS[part]}">${FORME_ICONS[part]}</span>`).join('');
                            html += `<div class="chip-drawer drawer-forme">${icon_html} ${element.content.text}</div>`;
                        } else { // Assumes denomination
                            const drawerClass = element.denomination ? `drawer-${element.denomination.split(' ')[0].toLowerCase()}` : 'drawer-empty';
                            html += `<div class="chip-drawer ${drawerClass}">${element.denomination || '---'}</div>`;
                        }
                    } else {
                        html += '<div class="chip-drawer drawer-empty">---</div>';
                    }
                }
                html += `</div>`; // Ferme chip-cell
            }
            html += '</div>'; // Ferme ligne-container
        }
        html += '</div>'; // Ferme katula-grid
    } else {
        html += '<p>Aucune donnée de matrice disponible pour cet univers.</p>';
    }

    katulaContainer.innerHTML = html;
}

function getQuadrant(row, col) {
    if (row <= 4) {
        return col <= 3 ? 'q1' : 'q2';
    } else {
        return col <= 3 ? 'q3' : 'q4';
    }
}

// Placeholder functions for filtering (to be implemented later)
function filterByColumn(col) {
    console.log(`Filtering by column: ${col}`);
}

function filterByRow(row) {
    console.log(`Filtering by row: ${row}`);
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
        // Add more detailed info as needed
    }
}

function updateFormesLegend(data) {
    const formesLegendContainer = document.getElementById('formesLegend');
    if (!formesLegendContainer) return;

    let uniqueFormes = new Set();
    if (data && data.matrix) {
        for (let r = 1; r <= 8; r++) {
            for (let c = 1; c <= 6; c++) {
                const cellData = data.matrix[r] ? data.matrix[r][c] : null;
                if (cellData && cellData.elements) {
                    const formeElement = cellData.elements.find(el => el.type === 'forme');
                    if (formeElement) {
                        uniqueFormes.add(formeElement.content.text);
                    }
                }
            }
        }
    }

    let html = '<h4>Légende des formes</h4>';
    if (uniqueFormes.size > 0) {
        html += '<div class="formes-grid">';
        uniqueFormes.forEach(formeName => {
            const forme_parts = formeName.split('-');
            const icon_html = forme_parts.map(part => {
                const icon = FORME_ICONS[part] || '';
                const color = FORME_COLORS[part] || '#000';
                return `<span style="color: ${color}; font-size: 1.5em; font-weight: bold;">${icon}</span>`;
            }).join('');

            html += `<div class="forme-item" onclick="filterByForme('${formeName}')">
                        <div class="forme-legend-icon">${icon_html}</div>
                        <div class="forme-legend-text">${formeName}</div>
                     </div>`;
        });
        html += '</div>';
        html += `<button class="clear-filters-btn" onclick="filterByForme('')" style="margin-top: 10px; display: none;">Réinitialiser le filtre</button>`;
    } else {
        html += '<p>Aucune forme trouvée pour cet univers.</p>';
    }
    formesLegendContainer.innerHTML = html;
}

function filterByForme(selectedForme) {
    const allCells = document.querySelectorAll('.chip-cell');
    const legendItems = document.querySelectorAll('.forme-item');
    const clearButton = document.querySelector('.clear-filters-btn');

    if (!selectedForme || window.lastSelectedForme === selectedForme) {
        allCells.forEach(cell => cell.classList.remove('filtered-out'));
        legendItems.forEach(item => item.classList.remove('selected'));
        window.lastSelectedForme = null;
        if(clearButton) clearButton.style.display = 'none';
        return;
    }

    window.lastSelectedForme = selectedForme;
    if(clearButton) clearButton.style.display = 'block';

    legendItems.forEach(item => {
        if (item.textContent.includes(selectedForme)) {
            item.classList.add('selected');
        } else {
            item.classList.remove('selected');
        }
    });

    allCells.forEach(cell => {
        if (cell.dataset.forme === selectedForme) {
            cell.classList.remove('filtered-out');
        } else {
            cell.classList.add('filtered-out');
        }
    });
}

async function updateGranqueTomeButtons(data) {
    const granqueButtonsContainer = document.getElementById('granqueButtons');
    const tomeButtonsContainer = document.getElementById('tomeButtons');

    if (!granqueButtonsContainer || !tomeButtonsContainer) return;

    granqueButtonsContainer.innerHTML = '';
    tomeButtonsContainer.innerHTML = '';

    try {
        const response = await fetch(`/api/granque-tome/${selectedUniverse}`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const granqueTomeData = await response.json();

        if (granqueTomeData.granque_data) {
            let granqueHtml = '';
            for (const granqueName in granqueTomeData.granque_data) {
                granqueHtml += `<button class="granque-btn" onclick="filterByGranque('${granqueName}')">${granqueName}</button>`;
            }
            granqueButtonsContainer.innerHTML = granqueHtml;
        }

        if (granqueTomeData.tome_data) {
            let tomeHtml = '';
            for (const tomeName in granqueTomeData.tome_data) {
                tomeHtml += `<button class="tome-btn" onclick="filterByTome('${tomeName}')">${tomeName}</button>`;
            }
            tomeButtonsContainer.innerHTML = tomeHtml;
        }

    } catch (error) {
        console.error('Error loading granque and tome data:', error);
        granqueButtonsContainer.innerHTML = '<p>Erreur de chargement des granques.</p>';
        tomeButtonsContainer.innerHTML = '<p>Erreur de chargement des tomes.</p>';
    }
}

// Placeholder functions for filtering (to be implemented later)
function filterByGranque(granque) {
    console.log(`Filtering by granque: ${granque}`);
}

function filterByTome(tome) {
    console.log(`Filtering by tome: ${tome}`);
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