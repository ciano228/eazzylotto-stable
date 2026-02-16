-- Agrandir la colonne denomination pour supporter les dénominations multiples
ALTER TABLE combinations ALTER COLUMN denomination TYPE VARCHAR(100);

-- Vérifier
SELECT column_name, data_type, character_maximum_length
FROM information_schema.columns
WHERE table_name = 'combinations' AND column_name = 'denomination';
