// Module d'analyse des données Katula
export const tirages = {
    "2025-01-15": [12, 27, 33, 5, 19],
    "2025-01-14": [5, 19, 44, 8, 23],
    "2025-01-13": [1, 15, 28, 35, 42],
    "2025-01-12": [7, 14, 21, 29, 36],
    "2025-01-11": [3, 11, 18, 25, 41]
};

export function getChipFrequency(chipNumber) {
    return Object.values(tirages).reduce((count, chips) =>
        chips.includes(chipNumber) ? count + 1 : count, 0);
}

export function getUniverseFormes(universeData) {
    if (universeData?.formes?.formes) {
        return universeData.formes.formes;
    }
    return ['carre', 'triangle', 'cercle', 'rectangle'];
}

export function calculateChipStats(chipData) {
    if (!chipData?.formes_data) return { totalItems: 0, formeCount: 0 };
    
    const totalItems = Object.values(chipData.formes_data)
        .reduce((sum, items) => sum + items.length, 0);
    const formeCount = Object.keys(chipData.formes_data).length;
    
    return { totalItems, formeCount };
}