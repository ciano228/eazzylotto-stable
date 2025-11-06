-- Correction des références des quadrants (petique)
UPDATE table_de_katula
SET petique = CASE 
    WHEN petique = 'q1' THEN 'Q1'
    WHEN petique = 'q2' THEN 'Q2'
    WHEN petique = 'q3' THEN 'Q3'
    WHEN petique = 'q4' THEN 'Q4'
    ELSE petique
END;

-- Extension des tomes jusqu'à tome10
-- D'abord, créer une table temporaire pour stocker la distribution actuelle
CREATE TEMP TABLE tome_distribution AS
SELECT chip_id, forme, denomination, petique, granque_name, COUNT(*) as count
FROM table_de_katula
GROUP BY chip_id, forme, denomination, petique, granque_name;

-- Mettre à jour les tomes avec une distribution uniforme de tome1 à tome10
WITH numbered_rows AS (
    SELECT 
        chip_id,
        forme,
        denomination,
        petique,
        granque_name,
        'Tome' || (ROW_NUMBER() OVER (PARTITION BY chip_id, forme ORDER BY tome) % 10 + 1)::text as new_tome
    FROM table_de_katula
)
UPDATE table_de_katula t
SET tome = n.new_tome
FROM numbered_rows n
WHERE t.chip_id = n.chip_id 
AND t.forme = n.forme 
AND t.denomination = n.denomination
AND t.petique = n.petique
AND t.granque_name = n.granque_name;

-- Vérification des mises à jour
SELECT DISTINCT petique, tome 
FROM table_de_katula 
ORDER BY petique, tome;