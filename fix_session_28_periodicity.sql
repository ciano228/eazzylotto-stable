-- Fix Session 28 periodicity from 7 to 5
UPDATE work_sessions 
SET cycle_length = 5 
WHERE id = 28;

-- Verify the change
SELECT id, name, cycle_length, total_draws 
FROM work_sessions 
WHERE id = 28;
