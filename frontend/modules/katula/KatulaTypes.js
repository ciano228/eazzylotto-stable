// Type definitions for Katula system
export const UniverseTypes = {
    BASIC: 'BASIC',       // Simple formes (fruity, mundo)
    COMPOUND: 'COMPOUND', // Compound formes (roaster)
    HYBRID: 'HYBRID'      // Mix of simple and compound (sunshine, trigga)
};

// Forme ordering for consistent display
export const FormeOrder = {
    // Basic formes
    'carre': 1,
    'triangle': 2,
    'cercle': 3,
    'rectangle': 4,
    // Compound formes
    'carre-triangle': 5,
    'carre-cercle': 6,
    'carre-rectangle': 7,
    'triangle-carre': 8,
    'triangle-cercle': 9,
    'triangle-rectangle': 10,
    'cercle-carre': 11,
    'cercle-triangle': 12,
    'cercle-rectangle': 13,
    'rectangle-carre': 14,
    'rectangle-triangle': 15,
    'rectangle-cercle': 16
};

// Visual representation constants
export const FormeSymbols = {
    'carre': '■',
    'triangle': '▲',
    'cercle': '●',
    'rectangle': '▬'
};

export const FormeColors = {
    'carre': '#3498db',     // Blue
    'triangle': '#27ae60',   // Green
    'cercle': '#f1c40f',    // Yellow
    'rectangle': '#e74c3c'   // Red
};