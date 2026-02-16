-- Migration: create drawers table
-- Idempotent: will not fail if table exists

CREATE TABLE IF NOT EXISTS drawers (
    drawer_id SERIAL PRIMARY KEY,
    drawer VARCHAR(255) UNIQUE NOT NULL,
    drawer_name VARCHAR(255) NOT NULL
);

-- Example seed data (adjust to your real names):
INSERT INTO drawers (drawer, drawer_name)
VALUES
  ('drawer_1_carre', 'drawer1'),
  ('drawer_2_triangle', 'drawer2'),
  ('drawer_3_cercle', 'drawer3')
ON CONFLICT (drawer) DO NOTHING;
