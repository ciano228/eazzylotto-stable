class KatulaChip {
    constructor(data, universeType) {
        this.id = data.chip;
        this.compartments = data.compartment_count;
        this.formes = data.formes;
        this.petiques = data.petiques;
        this.lignes = data.lignes;
        this.colonnes = data.colonnes;
        this.compartmentsData = data.compartments_data;
        this.universeType = universeType;
    }

    getCompartmentsByForme(forme) {
        return this.compartmentsData.filter(comp => comp.forme === forme);
    }

    getCompartmentsByPetique(petique) {
        return this.compartmentsData.filter(comp => comp.petique === petique);
    }

    getDenominationsByForme(forme) {
        return [...new Set(
            this.getCompartmentsByForme(forme)
                .map(comp => comp.denomination)
        )];
    }

    getFormeDistribution() {
        const distribution = {};
        this.formes.forEach(forme => {
            distribution[forme] = this.getCompartmentsByForme(forme).length;
        });
        return distribution;
    }

    getPetiqueDistribution() {
        const distribution = {};
        this.petiques.forEach(petique => {
            distribution[petique] = this.getCompartmentsByPetique(petique).length;
        });
        return distribution;
    }

    getPositions() {
        return this.compartmentsData.map(comp => ({
            ligne: comp.ligne,
            colonne: comp.colonne
        }));
    }
}