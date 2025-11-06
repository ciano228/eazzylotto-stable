/**
 * Gestionnaire de disposition des tables Katula conforme à la BD
 */
class KatulaTableLayout {
    constructor(containerId, universe = 'mundo') {
        this.container = document.getElementById(containerId);
        this.universe = universe;
        this.layout = null;
        this.apiBase = 'http://localhost:8000/api/katula/layout';
    }

    async loadLayout() {
        try {
            const response = await fetch(`${this.apiBase}/${this.universe}`);
            this.layout = await response.json();
            this.renderTable();
        } catch (error) {
            console.error('Erreur chargement layout:', error);
            this.renderError();
        }
    }

    renderTable() {
        if (!this.layout || !this.layout.tableStructure) {
            this.renderError();
            return;
        }

        const table = document.createElement('table');
        table.className = 'katula-table';
        
        // En-tête avec colonnes
        const thead = document.createElement('thead');
        const headerRow = document.createElement('tr');
        headerRow.innerHTML = '<th>Ligne</th>';
        
        // Déterminer les colonnes disponibles
        const columns = new Set();
        Object.values(this.layout.tableStructure).forEach(ligne => {
            Object.keys(ligne).forEach(col => columns.add(col));
        });
        
        Array.from(columns).sort().forEach(col => {
            headerRow.innerHTML += `<th>${col}</th>`;
        });
        thead.appendChild(headerRow);
        table.appendChild(thead);

        // Corps de la table
        const tbody = document.createElement('tbody');
        
        Object.keys(this.layout.tableStructure).sort().forEach(ligne => {
            const row = document.createElement('tr');
            row.innerHTML = `<td class="ligne-header">${ligne}</td>`;
            
            Array.from(columns).sort().forEach(col => {
                const cell = document.createElement('td');
                const compartiments = this.layout.tableStructure[ligne][col] || [];
                
                if (compartiments.length > 0) {
                    cell.className = 'compartiment-cell';
                    compartiments.forEach(comp => {
                        const div = document.createElement('div');
                        div.className = `compartiment ${comp.forme} ${comp.petique}`;
                        div.innerHTML = `
                            <span class="chip">Chip ${comp.chip}</span>
                            <span class="denomination">${comp.denomination}</span>
                            <span class="forme">${comp.forme}</span>
                        `;
                        cell.appendChild(div);
                    });
                } else {
                    cell.className = 'empty-cell';
                    cell.innerHTML = '-';
                }
                
                row.appendChild(cell);
            });
            
            tbody.appendChild(row);
        });
        
        table.appendChild(tbody);
        
        // Ajouter les informations de l'univers
        const info = document.createElement('div');
        info.className = 'universe-info';
        info.innerHTML = `
            <h3>Univers: ${this.universe.toUpperCase()}</h3>
            <p>Formes disponibles: ${this.layout.availableFormes.join(', ')}</p>
            <p>Petiques disponibles: ${this.layout.availablePetiques.join(', ')}</p>
        `;
        
        this.container.innerHTML = '';
        this.container.appendChild(info);
        this.container.appendChild(table);
    }

    renderError() {
        this.container.innerHTML = `
            <div class="error-message">
                <h3>Erreur de chargement</h3>
                <p>Impossible de charger la disposition pour l'univers ${this.universe}</p>
            </div>
        `;
    }

    async switchUniverse(newUniverse) {
        this.universe = newUniverse;
        await this.loadLayout();
    }
}

// CSS pour la table
const style = document.createElement('style');
style.textContent = `
.katula-table {
    width: 100%;
    border-collapse: collapse;
    margin: 20px 0;
}

.katula-table th,
.katula-table td {
    border: 1px solid #ddd;
    padding: 8px;
    text-align: center;
}

.katula-table th {
    background-color: #f2f2f2;
    font-weight: bold;
}

.ligne-header {
    background-color: #e8f4f8;
    font-weight: bold;
}

.compartiment-cell {
    padding: 4px;
}

.compartiment {
    margin: 2px;
    padding: 4px;
    border-radius: 4px;
    font-size: 0.8em;
}

.compartiment.carre {
    background-color: #ffeb3b;
}

.compartiment.cercle {
    background-color: #4caf50;
    border-radius: 50%;
}

.compartiment.triangle {
    background-color: #ff9800;
}

.compartiment.rectangle {
    background-color: #2196f3;
}

.compartiment.q1 {
    border-left: 3px solid #red;
}

.compartiment.q2 {
    border-left: 3px solid #blue;
}

.compartiment.q3 {
    border-left: 3px solid #green;
}

.compartiment.q4 {
    border-left: 3px solid #orange;
}

.chip {
    display: block;
    font-weight: bold;
}

.denomination {
    display: block;
    font-style: italic;
}

.forme {
    display: block;
    font-size: 0.7em;
    color: #666;
}

.empty-cell {
    background-color: #f9f9f9;
    color: #ccc;
}

.universe-info {
    background-color: #f0f0f0;
    padding: 10px;
    border-radius: 4px;
    margin-bottom: 10px;
}

.error-message {
    background-color: #ffebee;
    color: #c62828;
    padding: 20px;
    border-radius: 4px;
    text-align: center;
}
`;
document.head.appendChild(style);