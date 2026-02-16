-- This script adds the 'no_draw_reason' column to the 'session_draws' table if it does not already exist.
-- This is intended to fix the API error caused by an outdated database schema.

ALTER TABLE session_draws
ADD COLUMN IF NOT EXISTS no_draw_reason TEXT;
