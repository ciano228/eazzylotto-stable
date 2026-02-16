-- Populate drawers table from distinct values in combinations.drawer
-- Idempotent: will not insert duplicates
BEGIN;

-- Ensure drawers table exists
CREATE TABLE IF NOT EXISTS drawers (
  drawer_id SERIAL PRIMARY KEY,
  drawer VARCHAR(255) UNIQUE NOT NULL,
  drawer_name VARCHAR(255) NOT NULL
);

-- Insert distinct drawer identifiers from combinations into drawers
-- drawer_name is derived:
--  - if value matches 'drawer_<num>_...' -> 'drawer<num>'
--  - if value is purely numeric -> 'drawer<num>'
--  - otherwise keep the text value as drawer_name
INSERT INTO drawers (drawer, drawer_name)
SELECT DISTINCT c.drawer::text AS drawer,
  CASE
    WHEN c.drawer::text ~ '^drawer_(\d+)_' THEN 'drawer' || regexp_replace(c.drawer::text, '^drawer_(\d+)_.*$', '\1')
    WHEN c.drawer::text ~ '^[0-9]+$' THEN 'drawer' || c.drawer::text
    ELSE c.drawer::text
  END AS drawer_name
FROM combinations c
WHERE c.drawer IS NOT NULL
ON CONFLICT (drawer) DO NOTHING;

-- Add drawer_name column to combinations if missing
ALTER TABLE IF EXISTS combinations ADD COLUMN IF NOT EXISTS drawer_name VARCHAR(255);

-- Update combinations.drawer_name from drawers mapping
UPDATE combinations c
SET drawer_name = d.drawer_name
FROM drawers d
WHERE (c.drawer::text = d.drawer OR c.drawer::text = d.drawer_id::text)
  AND (c.drawer_name IS NULL OR c.drawer_name = '');

-- For any remaining NULL drawer_name, synthesize a name
UPDATE combinations
SET drawer_name = 'drawer' || drawer::text
WHERE drawer_name IS NULL AND drawer IS NOT NULL;

-- Create index to speed lookups
CREATE INDEX IF NOT EXISTS ix_combinations_drawer_name ON combinations(drawer_name);

COMMIT;
