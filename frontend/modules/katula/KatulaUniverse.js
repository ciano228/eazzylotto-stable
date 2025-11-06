import { UniverseTypes, FormeOrder, FormeSymbols, FormeColors } from './KatulaTypes.js';

class KatulaUniverse {
    constructor(data) {
        this.name = data.universe;
        this.totalChips = data.total_chips;
        this.availableFormes = data.available_formes;
        this.availablePetiques = data.available_petiques;
        this.denominationCount = data.denomination_count;
        this.chips = data.chips;
        this.type = this._determineUniverseType();
    }

    _determineUniverseType() {
        const hasBasicFormes = this.availableFormes.some(forme => !forme.includes('-'));
        const hasCompoundFormes = this.availableFormes.some(forme => forme.includes('-'));

        if (hasBasicFormes && !hasCompoundFormes) return UniverseTypes.BASIC;
        if (!hasBasicFormes && hasCompoundFormes) return UniverseTypes.COMPOUND;
        return UniverseTypes.HYBRID;
    }

    getOrderedFormes() {
        return [...this.availableFormes].sort((a, b) => {
            return (FormeOrder[a] || 99) - (FormeOrder[b] || 99);
        });
    }

    getChipById(chipId) {
        return this.chips[chipId];
    }

    getFormeSymbol(forme) {
        if (forme.includes('-')) {
            const [f1, f2] = forme.split('-');
            return FormeSymbols[f1] + FormeSymbols[f2];
        }
        return FormeSymbols[forme];
    }

    getFormeColor(forme) {
        if (forme.includes('-')) {
            const [f1] = forme.split('-');
            return FormeColors[f1];
        }
        return FormeColors[forme];
    }

    getChipsWithForme(forme) {
        return Object.entries(this.chips)
            .filter(([_, chip]) => chip.formes.includes(forme))
            .map(([chipId]) => chipId);
    }

    getChipsWithPetique(petique) {
        return Object.entries(this.chips)
            .filter(([_, chip]) => chip.petiques.includes(petique))
            .map(([chipId]) => chipId);
    }
}