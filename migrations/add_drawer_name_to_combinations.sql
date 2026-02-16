-- Migration: add drawer_name column to combinations and populate it
-- Idempotent: will not fail if the column already exists

ALTER TABLE IF EXISTS combinations
ADD COLUMN IF NOT EXISTS drawer_name VARCHAR(255);

-- If a 'drawers' lookup table exists, prefer it to populate drawer_name.
-- Otherwise, synthesize a simple name like 'drawer{n}' where 'drawer' column is numeric.

-- Populate from drawers table when possible
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'drawers') THEN
        UPDATE combinations c
        SET drawer_name = d.drawer_name
        FROM drawers d
        WHERE d.drawer IS NOT NULL
          AND (c.drawer::text = d.drawer OR c.drawer::text = d.drawer_id::text);
    END IF;
END$$;

-- For any rows still without drawer_name, synthesize a name using the drawer integer
UPDATE combinations
SET drawer_name = 'drawer' || drawer::text
WHERE drawer_name IS NULL AND drawer IS NOT NULL;

-- For safety: set empty strings to NULL
UPDATE combinations SET drawer_name = NULL WHERE drawer_name = '';

-- Add an index to speed lookups
CREATE INDEX IF NOT EXISTS ix_combinations_drawer_name ON combinations(drawer_name);
