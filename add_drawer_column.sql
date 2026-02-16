-- Script pour ajouter la colonne drawer à la table combinations
-- À exécuter dans PostgreSQL katooling_main_system

-- 1. Ajouter la colonne
ALTER TABLE combinations ADD COLUMN IF NOT EXISTS drawer INTEGER;

-- 2. Créer un index pour performance
CREATE INDEX IF NOT EXISTS idx_combinations_drawer ON combinations(drawer);

-- 3. Créer un index composite pour requêtes fréquentes
CREATE INDEX IF NOT EXISTS idx_combinations_univers_drawer ON combinations(univers, drawer);

-- 4. Vérifier la création
SELECT column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'combinations' AND column_name = 'drawer';

-- 5. Statistiques avant peuplement
SELECT 
    COUNT(*) as total_rows,
    COUNT(drawer) as rows_with_drawer,
    COUNT(*) - COUNT(drawer) as rows_without_drawer
FROM combinations;

COMMENT ON COLUMN combinations.drawer IS 'Subdivision de chip par forme - identifiant unique du tiroir (drawer) contenant une ou plusieurs dénominations';
