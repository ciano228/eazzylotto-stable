// Service pour gérer les appels à l'API Katula
class KatulaService {
    constructor(baseUrl = 'http://localhost:8000/api/katula') {
        this.baseUrl = baseUrl;
    }

    async getMatrix(universe) {
        try {
            const response = await fetch(`${this.baseUrl}/matrix/${universe}`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return await response.json();
        } catch (error) {
            console.error('Error fetching matrix:', error);
            throw error;
        }
    }

    async getChipDetails(universe, chipNumber) {
        try {
            const response = await fetch(`${this.baseUrl}/chip/${universe}/${chipNumber}`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return await response.json();
        } catch (error) {
            console.error('Error fetching chip details:', error);
            throw error;
        }
    }

    async getFilterOptions(universe) {
        try {
            const response = await fetch(`${this.baseUrl}/filters/${universe}`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return await response.json();
        } catch (error) {
            console.error('Error fetching filter options:', error);
            throw error;
        }
    }
}

// UI Manager pour gérer l'interface utilisateur
class KatulaUI {
    constructor() {
        this.service = new KatulaService();
        this.currentUniverse = 'mundo';
        this.initializeUI();
    }

    async initializeUI() {
        await this.loadFilterOptions();
        await this.loadMatrix();
    }

    async loadFilterOptions() {
        try {
            const options = await this.service.getFilterOptions(this.currentUniverse);
            const filterOptions = options.filter_options;
            
            // Mettre à jour les sélecteurs de filtres
            this.updateFilterSelects(filterOptions);
            
        } catch (error) {
            console.error('Error loading filter options:', error);
        }
    }

    async loadMatrix() {
        try {
            const matrix = await this.service.getMatrix(this.currentUniverse);
            this.renderMatrix(matrix);
        } catch (error) {
            console.error('Error loading matrix:', error);
        }
    }

    updateFilterSelects(filterOptions) {
        // Mettre à jour les sélecteurs avec les options
        const { formes, petiques, tomes, granques } = filterOptions;
        
        // Mise à jour du sélecteur de formes
        this.updateSelect('formeSelect', formes);
        
        // Mise à jour du sélecteur de petiques
        this.updateSelect('petiqueSelect', petiques);
        
        // Mise à jour du sélecteur de tomes
        this.updateSelect('tomeSelect', tomes);
        
        // Mise à jour du sélecteur de granques
        this.updateSelect('granqueSelect', granques);
    }

    updateSelect(selectId, options) {
        const select = document.getElementById(selectId);
        if (!select) return;

        // Vider le sélecteur
        select.innerHTML = '';
        
        // Ajouter l'option par défaut
        const defaultOption = document.createElement('option');
        defaultOption.value = '';
        defaultOption.textContent = `-- Sélectionner --`;
        select.appendChild(defaultOption);
        
        // Ajouter les nouvelles options
        options.forEach(option => {
            const optionElement = document.createElement('option');
            optionElement.value = option;
            optionElement.textContent = option;
            select.appendChild(optionElement);
        });
    }

    renderMatrix(matrixData) {
        const container = document.getElementById('katulaMatrix');
        if (!container) return;

        container.innerHTML = ''; // Clear existing content

        // Create the matrix grid
        const { matrix, dimensions } = matrixData;
        
        // Add row headers (1-8)
        for (let row = 1; row <= dimensions.rows; row++) {
            const rowHeader = document.createElement('div');
            rowHeader.className = 'grid-cell grid-header';
            rowHeader.textContent = `L${row}`;
            container.appendChild(rowHeader);

            // Add cells for each column (1-6)
            for (let col = 1; col <= dimensions.cols; col++) {
                const cell = document.createElement('div');
                cell.className = 'grid-cell';
                const cellData = matrix[row][col];
                
                const cellContent = document.createElement('div');
                cellContent.className = 'cell-content';
                
                // Add chip number
                const chipTitle = document.createElement('div');
                chipTitle.className = 'cell-title';
                chipTitle.textContent = `Chip ${cellData.chip_number}`;
                cellContent.appendChild(chipTitle);
                
                // Add compartments
                const compartmentsList = document.createElement('div');
                compartmentsList.className = 'forme-list';
                cellData.compartments.forEach(comp => {
                    const formeTag = document.createElement('span');
                    formeTag.className = 'forme-tag';
                    formeTag.textContent = `${comp.forme} (${comp.petique})`;
                    compartmentsList.appendChild(formeTag);
                });
                cellContent.appendChild(compartmentsList);
                
                cell.appendChild(cellContent);
                container.appendChild(cell);
            }
        }
    }
}

// Initialiser l'UI quand le document est chargé
document.addEventListener('DOMContentLoaded', () => {
    window.katulaUI = new KatulaUI();
});