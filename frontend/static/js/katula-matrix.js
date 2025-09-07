// Fonction pour charger les données de la matrice
async function loadKatulaMatrix(universe) {
    try {
        const response = await fetch(`/api/katula/matrix/${universe}`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Erreur lors du chargement de la matrice:', error);
        throw error;
    }
}

// Fonction pour créer une cellule de tableau
function createTableCell(content) {
    const td = document.createElement('td');
    td.textContent = content || '';
    return td;
}

// Fonction pour générer la table HTML
function generateKatulaTable(matrixData) {
    const container = document.getElementById('katula-matrix-container');
    container.innerHTML = ''; // Clear previous content

    // Créer l'en-tête avec les informations de l'univers
    const header = document.createElement('div');
    header.className = 'matrix-header';
    header.innerHTML = `
        <h2>Matrice Katula - Univers ${matrixData.universe}</h2>
        <p>Total des chips: ${matrixData.total_chips}</p>
        <p>Formes disponibles: ${matrixData.formes.join(', ')}</p>
    `;
    container.appendChild(header);

    // Créer la table
    const table = document.createElement('table');
    table.className = 'katula-table';

    // Créer l'en-tête du tableau
    const thead = document.createElement('thead');
    const headerRow = document.createElement('tr');
    ['Chip', 'Colonne', 'Ligne', 'Pétique', 'Granque', 'Tome', 'Formes', 'Dénominations'].forEach(text => {
        const th = document.createElement('th');
        th.textContent = text;
        headerRow.appendChild(th);
    });
    thead.appendChild(headerRow);
    table.appendChild(thead);

    // Créer le corps du tableau
    const tbody = document.createElement('tbody');
    Object.values(matrixData.chips).forEach(chip => {
        const row = document.createElement('tr');
        
        // Ajouter les cellules de base
        row.appendChild(createTableCell(chip.chip));
        row.appendChild(createTableCell(chip.colonne));
        row.appendChild(createTableCell(chip.ligne));
        row.appendChild(createTableCell(chip.petique));
        row.appendChild(createTableCell(chip.granque));
        row.appendChild(createTableCell(chip.tome));
        
        // Ajouter les formes avec leurs dénominations
        const formesCell = document.createElement('td');
        Object.entries(chip.formes).forEach(([forme, denoms]) => {
            const formeDiv = document.createElement('div');
            formeDiv.className = 'forme-entry';
            formeDiv.innerHTML = `<strong>${forme}:</strong> ${denoms.join(', ')}`;
            formesCell.appendChild(formeDiv);
        });
        row.appendChild(formesCell);
        
        // Ajouter toutes les dénominations
        row.appendChild(createTableCell(chip.denominations.join(', ')));
        
        tbody.appendChild(row);
    });
    table.appendChild(tbody);
    
    container.appendChild(table);
}

// Fonction principale d'initialisation
async function initKatulaMatrix(universe = 'monde') {
    try {
        const matrixData = await loadKatulaMatrix(universe);
        generateKatulaTable(matrixData);
    } catch (error) {
        const container = document.getElementById('katula-matrix-container');
        container.innerHTML = `<div class="error-message">Erreur de chargement de la matrice: ${error.message}</div>`;
    }
}

// Style CSS pour la table
const style = document.createElement('style');
style.textContent = `
.katula-table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 20px;
}

.katula-table th,
.katula-table td {
    border: 1px solid #ddd;
    padding: 8px;
    text-align: left;
}

.katula-table th {
    background-color: #f4f4f4;
    font-weight: bold;
}

.katula-table tr:nth-child(even) {
    background-color: #f9f9f9;
}

.katula-table tr:hover {
    background-color: #f5f5f5;
}

.matrix-header {
    margin-bottom: 20px;
}

.forme-entry {
    margin-bottom: 5px;
}

.error-message {
    color: red;
    padding: 10px;
    border: 1px solid red;
    background-color: #fff3f3;
    margin-top: 20px;
}
`;
document.head.appendChild(style);
