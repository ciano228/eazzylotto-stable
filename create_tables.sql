-- Création des tables pour les sessions de travail

-- Table des sessions de travail
CREATE TABLE IF NOT EXISTS work_sessions (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    lottery_type VARCHAR(50),
    numbers_per_draw INTEGER DEFAULT 5,
    total_draws INTEGER DEFAULT 21,
    number_range_min INTEGER DEFAULT 1,
    number_range_max INTEGER DEFAULT 90,
    lottery_schedule JSON,
    start_date DATE,
    is_active BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table des tirages de session
CREATE TABLE IF NOT EXISTS session_draws (
    id SERIAL PRIMARY KEY,
    session_id INTEGER REFERENCES work_sessions(id) ON DELETE CASCADE,
    draw_number INTEGER NOT NULL,
    lottery_name VARCHAR(255),
    draw_date DATE,
    winning_numbers JSON,
    is_completed BOOLEAN DEFAULT false,
    is_no_draw BOOLEAN DEFAULT false,
    no_draw_reason TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(session_id, draw_number)
);

-- Index pour améliorer les performances
CREATE INDEX IF NOT EXISTS idx_work_sessions_active ON work_sessions(is_active);
CREATE INDEX IF NOT EXISTS idx_session_draws_session ON session_draws(session_id);
CREATE INDEX IF NOT EXISTS idx_session_draws_number ON session_draws(session_id, draw_number);