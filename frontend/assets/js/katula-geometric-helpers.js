// katula-geometric-helpers.js
// Fonctions helper pour déterminer les valeurs géométriques d'un chip

/**
 * Détermine le petique (quadrant) d'un chip basé sur sa position dans la grille Katula
 * Grille: 8 lignes x 6 colonnes = 48 chips
 * @param {number} chipNumber - Numéro du chip (1-48)
 * @returns {string} - Petique (q1, q2, q3, q4)
 */
function getPetiqueFromChip(chipNumber) {
    // Calculer ligne et colonne (1-indexed)
    const ligne = Math.ceil(chipNumber / 6);
    const colonne = ((chipNumber - 1) % 6) + 1;

    // Déterminer le petique selon la position
    // q1: lignes 1-4, colonnes 1-3 (haut-gauche)
    // q2: lignes 1-4, colonnes 4-6 (haut-droite)
    // q3: lignes 5-8, colonnes 1-3 (bas-gauche)
    // q4: lignes 5-8, colonnes 4-6 (bas-droite)

    if (ligne <= 4) {
        return colonne <= 3 ? 'q1' : 'q2';
    } else {
        return colonne <= 3 ? 'q3' : 'q4';
    }
}

/**
 * Obtient les informations de position d'un chip
 * @param {number} chipNumber - Numéro du chip (1-48)
 * @returns {object} - {ligne, colonne, petique}
 */
function getChipPosition(chipNumber) {
    const ligne = Math.ceil(chipNumber / 6);
    const colonne = ((chipNumber - 1) % 6) + 1;
    const petique = getPetiqueFromChip(chipNumber);

    return {
        ligne: `L${ligne}`,
        colonne: `C${colonne}`,
        petique: petique,
        chipNumber: chipNumber
    };
}

/**
 * Mapping des couleurs par petique pour le marquage visuel
 */
const PETIQUE_COLORS = {
    'q1': '#3498db',  // Bleu - Haut-Gauche
    'q2': '#27ae60',  // Vert - Haut-Droite
    'q3': '#e67e22',  // Orange - Bas-Gauche
    'q4': '#9b59b6'   // Violet - Bas-Droite
};

/**
 * Mapping des labels par petique
 */
const PETIQUE_LABELS = {
    'q1': 'Petique 1 (Haut-Gauche)',
    'q2': 'Petique 2 (Haut-Droite)',
    'q3': 'Petique 3 (Bas-Gauche)',
    'q4': 'Petique 4 (Bas-Droite)'
};

/**
 * Obtient tous les chips d'un petique donné
 * @param {string} petique - Le petique (q1, q2, q3, q4)
 * @returns {array} - Liste des numéros de chips
 */
function getChipsInPetique(petique) {
    const chips = [];
    for (let chip = 1; chip <= 48; chip++) {
        if (getPetiqueFromChip(chip) === petique) {
            chips.push(chip);
        }
    }
    return chips;
}

/**
 * Détermine le tome d'un chip (4 tomes de 12 chips)
 * @param {number} chipNumber - Numéro du chip (1-48)
 * @returns {string} - Tome (tome1, tome2, tome3, tome4)
 */
function getTomeFromChip(chipNumber) {
    if (chipNumber <= 12) return 'tome1';
    if (chipNumber <= 24) return 'tome2';
    if (chipNumber <= 36) return 'tome3';
    return 'tome4';
}

/**
 * Détermine la granque d'un chip (6 granques de 8 chips)
 * @param {number} chipNumber - Numéro du chip (1-48)
 * @returns {string} - Granque (g1-g6)
 */
function getGranqueFromChip(chipNumber) {
    const granqueNum = Math.ceil(chipNumber / 8);
    return `g${granqueNum}`;
}

// Exporter les fonctions pour utilisation globale
if (typeof window !== 'undefined') {
    window.KatulaGeometric = {
        getPetiqueFromChip,
        getChipPosition,
        getChipsInPetique,
        getTomeFromChip,
        getGranqueFromChip,
        PETIQUE_COLORS,
        PETIQUE_LABELS
    };
}
