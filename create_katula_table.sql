-- Table pour stocker les données Katula
CREATE TABLE IF NOT EXISTS combinations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    univers TEXT NOT NULL,
    forme TEXT NOT NULL,
    chip INTEGER NOT NULL,
    denomination TEXT NOT NULL,
    object_name TEXT,
    num1 INTEGER,
    num2 INTEGER,
    alpha_ranking TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index pour optimiser les requêtes
CREATE INDEX IF NOT EXISTS idx_universe_forme_chip ON combinations(univers, forme, chip);
CREATE INDEX IF NOT EXISTS idx_denomination ON combinations(denomination);

-- Données d'exemple pour l'univers Mundo
 (univers, forme, chip, denomination, object_name, num1, num2, alpha_ranking) VALUES
-- Chip 1
('mundo', 'carre', 1, 'road 1', 'road 1', 12, 34, 'a'),
('mundo', 'carre', 1, 'road 1', 'road 1', 15, 28, 'b'),
('mundo', 'carre', 1, 'road 1', 'road 1', 9, 41, 'c'),
('mundo', 'triangle', 1, 'tree 5', 'tree 5', 22, 45, 'a'),
('mundo', 'triangle', 1, 'tree 5', 'tree 5', 18, 33, 'b'),
('mundo', 'cercle', 1, 'house 3', 'house 3', 7, 29, 'd'),

-- Chip 2  
('mundo', 'carre', 2, 'car 7', 'car 7', 31, 47, 'a'),
('mundo', 'carre', 2, 'car 7', 'car 7', 14, 26, 'c'),
('mundo', 'rectangle', 2, 'star 2', 'star 2', 5, 38, 'b'),
('mundo', 'rectangle', 2, 'star 2', 'star 2', 19, 42, 'd'),

-- Chip 3
('mundo', 'triangle', 3, 'moon 4', 'moon 4', 11, 35, 'a'),
('mundo', 'cercle', 3, 'sun 8', 'sun 8', 23, 46, 'b'),
('mundo', 'cercle', 3, 'sun 8', 'sun 8', 8, 30, 'c'),
('mundo', 'rectangle', 3, 'flower 1', 'flower 1', 16, 39, 'a'),

-- Plus de données pour d'autres chips
('mundo', 'carre', 4, 'road 12', 'road 12', 25, 48, 'a'),
('mundo', 'triangle', 5, 'tree 15', 'tree 15', 13, 37, 'b'),
('mundo', 'cercle', 6, 'house 9', 'house 9', 21, 44, 'c'),
('mundo', 'rectangle', 7, 'car 21', 'car 21', 17, 40, 'd'),
('mundo', 'carre', 8, 'star 6', 'star 6', 10, 32, 'a');