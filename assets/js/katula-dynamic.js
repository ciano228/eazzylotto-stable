// Global state
let katulaData = [];
let formeIconMap = new Map(); // To store forme -> icon mapping
let activeFilters = {
    petique: new Set(),
    granque: new Set(),
    quadrant: new Set(),
    forme: new Set()
};

// Initialize filters and event listeners
document.addEventListener('DOMContentLoaded', () => {
    initializeFilters();
    loadKatulaData();
});

// Initialize filter checkboxes
async function initializeFilters() {
    // Petique filters
    const petiques = ['q1', 'q2', 'q3', 'q4'];
    const petiqueContainer = document.getElementById('petiqueFilters');
    createFilterCheckboxes(petiques, petiqueContainer, 'petique');

    // Granque filters
    const granques = ['Q1', 'Q2', 'Q3', 'Q4','Q5','Q6'];
    const granqueContainer = document.getElementById('granqueFilters');
    createFilterCheckboxes(granques, granqueContainer, 'granque');

    // Quadrant filters
    const quadrants = ['1', '2', '3', '4'];
    const quadrantContainer = document.getElementById('quadrantFilters');
    createFilterCheckboxes(quadrants, quadrantContainer, 'quadrant');

    // Forme filters (dynamic)
    await loadFormeFilters();
}

async function loadFormeFilters() {
    try {
        const response = await fetch('http://localhost:8001/api/katula/formes');
        if (!response.ok) throw new Error('Failed to fetch formes');
        const data = await response.json();
        const formes = data.formes || [];

        // Populate the icon map
        formes.forEach(forme => {
            formeIconMap.set(forme.name.toLowerCase(), forme.icon);
        });

        const formeContainer = document.getElementById('formeFilters');
        createFilterCheckboxes(formes, formeContainer, 'forme');
    } catch (error) {
        console.error('Error loading forme filters:', error);
    }
}

function createFilterCheckboxes(items, container, filterType) {
    items.forEach(item => {
        const isForme = filterType === 'forme';
        const value = isForme ? item.name : item;
        const icon = isForme ? item.icon : null;

        const div = document.createElement('div');
        const checkbox = document.createElement('input');
        checkbox.type = 'checkbox';
        checkbox.id = `${filterType}-${value}`;
        checkbox.value = value;
        
        const label = document.createElement('label');
        label.htmlFor = `${filterType}-${value}`;
        label.textContent = isForme ? ` ${value}` : value;
        if (icon) {
            const iconSpan = document.createElement('span');
            iconSpan.textContent = icon;
            label.prepend(iconSpan);
        }

        checkbox.addEventListener('change', (e) => {
            if (e.target.checked) {
                activeFilters[filterType].add(value);
            } else {
                activeFilters[filterType].delete(value);
            }
            applyFilters();
        });

        div.appendChild(checkbox);
        div.appendChild(label);
        container.appendChild(div);
    });
}

// Load data from the backend
async function loadKatulaData() {
    const universe = document.getElementById('universeSelect').value;
    try {
        const response = await fetch(`http://localhost:8001/api/katula/ui-data/${universe}`);
        if (!response.ok) throw new Error('Failed to fetch data');
        
        katulaData = await response.json();
        renderKatulaGrid();
    } catch (error) {
        console.error('Error loading data:', error);
        alert('Erreur lors du chargement des données');
    }
}

// Apply filters to the data
function applyFilters() {
    const filteredData = katulaData.filter(chip => {
        // Check if any filters are active
        const hasActiveFilters = Object.values(activeFilters).some(set => set.size > 0);
        if (!hasActiveFilters) return true;

        // Apply petique filter
        if (activeFilters.petique.size > 0) {
            const chipPetiques = new Set(chip.petiques);
            if (!Array.from(activeFilters.petique).some(p => chipPetiques.has(p))) {
                return false;
            }
        }

        // Apply granque filter
        if (activeFilters.granque.size > 0) {
            const chipGranques = new Set(chip.granques);
            if (!Array.from(activeFilters.granque).some(g => chipGranques.has(g))) {
                return false;
            }
        }

        // Apply quadrant filter
        if (activeFilters.quadrant.size > 0) {
            if (!activeFilters.quadrant.has(chip.quadrant.toString())) {
                return false;
            }
        }

        // Apply forme filter
        if (activeFilters.forme.size > 0) {
            if (!activeFilters.forme.has(chip.forme)) {
                return false;
            }
        }

        return true;
    });

    renderKatulaGrid(filteredData);
}

// Render the Katula grid
function renderKatulaGrid(data = katulaData) {
    const grid = document.getElementById('katulaContainer');
    grid.innerHTML = '';

    data.forEach(chip => {
        const chipElement = createChipElement(chip);
        grid.appendChild(chipElement);
    });
}

// Create a chip element
function createChipElement(chip) {
    const chipDiv = document.createElement('div');
    chipDiv.className = 'chip';
    chipDiv.setAttribute('data-quadrant', chip.quadrant);

    // Add chip header with position
    const header = document.createElement('div');
    header.className = 'chip-header';
    header.textContent = `Position ${chip.position}`;
    chipDiv.appendChild(header);

    // Add forme with icon
    const formeDiv = document.createElement('div');
    formeDiv.className = 'compartment';
    formeDiv.innerHTML = `
        <span class="forme-icon">${getFormeIcon(chip.forme)}</span>
        ${chip.forme}
    `;
    chipDiv.appendChild(formeDiv);

    // Add denominations
    const denomDiv = document.createElement('div');
    denomDiv.className = 'compartment';
    denomDiv.innerHTML = `
        <span class="denomination">${chip.denominations.join(' / ')}</span>
    `;
    chipDiv.appendChild(denomDiv);

    // Add petiques
    const petiqueDiv = document.createElement('div');
    petiqueDiv.className = 'compartment';
    petiqueDiv.innerHTML = `
        <span class="petique">${chip.petiques.join(', ')}</span>
    `;
    chipDiv.appendChild(petiqueDiv);

    return chipDiv;
}

// Get icon for forme
function getFormeIcon(forme) {
    return formeIconMap.get(forme.toLowerCase()) || '?';
}