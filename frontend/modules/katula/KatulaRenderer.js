import { KatulaUniverse } from './KatulaUniverse.js';
import { KatulaChip } from './KatulaChip.js';
import { FormeOrder } from './KatulaTypes.js';

export class KatulaRenderer {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.universe = null;
        this.activeFilters = new Set();
    }

    setUniverse(universeData) {
        this.universe = new KatulaUniverse(universeData);
        this._renderUniverseInfo();
        this._renderFilters();
        this._renderGrid();
    }

    _renderUniverseInfo() {
        const info = document.createElement('div');
        info.className = 'universe-info';
        info.innerHTML = `
            <h2>${this.universe.name.toUpperCase()}</h2>
            <p>Type: ${this.universe.type}</p>
            <p>Total Chips: ${this.universe.totalChips}</p>
            <p>Formes: ${this.universe.getOrderedFormes().join(', ')}</p>
            <p>Petiques: ${this.universe.availablePetiques.join(', ')}</p>
        `;
        this.container.appendChild(info);
    }

    _renderFilters() {
        const filters = document.createElement('div');
        filters.className = 'filters-container';
        
        // Forme filters
        const formeFilters = this._createFilterGroup('Formes', this.universe.getOrderedFormes(), (forme) => {
            return `
                <span class="forme-filter" style="color: ${this.universe.getFormeColor(forme)}">
                    ${this.universe.getFormeSymbol(forme)}
                </span>
            `;
        });
        
        // Petique filters
        const petiqueFilters = this._createFilterGroup('Petiques', this.universe.availablePetiques);
        
        filters.appendChild(formeFilters);
        filters.appendChild(petiqueFilters);
        this.container.appendChild(filters);
    }

    _createFilterGroup(title, items, customLabel = null) {
        const group = document.createElement('div');
        group.className = 'filter-group';
        group.innerHTML = `<h3>${title}</h3>`;

        items.forEach(item => {
            const label = document.createElement('label');
            label.className = 'filter-item';
            
            const checkbox = document.createElement('input');
            checkbox.type = 'checkbox';
            checkbox.value = item;
            checkbox.addEventListener('change', () => this._handleFilterChange());

            label.appendChild(checkbox);
            label.appendChild(document.createTextNode(' '));
            
            if (customLabel) {
                label.insertAdjacentHTML('beforeend', customLabel(item));
            } else {
                label.appendChild(document.createTextNode(item));
            }
            
            group.appendChild(label);
        });

        return group;
    }

    _handleFilterChange() {
        // Implementation of filter logic
    }

    _renderGrid() {
        const grid = document.createElement('div');
        grid.className = 'katula-grid';
        
        // Calculate optimal grid dimensions based on chip count
        const columns = Math.ceil(Math.sqrt(this.universe.totalChips));
        grid.style.gridTemplateColumns = `repeat(${columns}, 1fr)`;
        
        // Create chip cells
        Object.entries(this.universe.chips).forEach(([chipId, chipData]) => {
            const chip = new KatulaChip(chipData, this.universe.type);
            const cell = this._createChipCell(chip);
            grid.appendChild(cell);
        });
        
        this.container.appendChild(grid);
    }

    _createChipCell(chip) {
        const cell = document.createElement('div');
        cell.className = 'chip-cell';
        cell.setAttribute('data-chip-id', chip.id);
        
        // Header with chip ID
        const header = document.createElement('div');
        header.className = 'chip-header';
        header.textContent = `Chip ${chip.id}`;
        cell.appendChild(header);
        
        // Compartments section
        const compartments = document.createElement('div');
        compartments.className = 'chip-compartments';
        
        // Group compartments by forme
        chip.formes.forEach(forme => {
            const compartmentGroup = document.createElement('div');
            compartmentGroup.className = 'compartment-group';
            compartmentGroup.innerHTML = `
                <span class="forme-indicator" style="color: ${this.universe.getFormeColor(forme)}">
                    ${this.universe.getFormeSymbol(forme)}
                </span>
                <span class="denomination-list">
                    ${chip.getDenominationsByForme(forme).join(', ')}
                </span>
            `;
            compartments.appendChild(compartmentGroup);
        });
        
        cell.appendChild(compartments);
        return cell;
    }
}