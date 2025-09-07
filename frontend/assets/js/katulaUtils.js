// Utilitaires pour Katula
export function getUniverseFormes(universeData) {
    if (universeData?.formes?.formes) {
        return universeData.formes.formes;
    }
    return ['carre', 'triangle', 'cercle', 'rectangle'];
}

export function formatDenomination(items) {
    if (!items || items.length === 0) return '---';
    
    const denominations = [...new Set(items.map(item => item.denomination))];
    return denominations.length === 1 ? denominations[0] : denominations.join('/');
}

export function validateUniverse(universe) {
    const validUniverses = ['mundo', 'fruity', 'trigga', 'roaster', 'sunshine'];
    return validUniverses.includes(universe.toLowerCase());
}