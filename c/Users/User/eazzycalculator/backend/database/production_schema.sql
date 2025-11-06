-- EazzyLotto Production Database Schema
-- Version MVP 1.0

-- Users table for authentication
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    subscription_type VARCHAR(50) DEFAULT 'free',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    is_active BOOLEAN DEFAULT true
);

-- Real lottery draws data
CREATE TABLE lottery_draws (
    id SERIAL PRIMARY KEY,
    draw_date DATE NOT NULL,
    numbers INTEGER[] NOT NULL,
    bonus_number INTEGER,
    lottery_type VARCHAR(50) DEFAULT 'loto',
    jackpot_amount DECIMAL(15,2),
    winners_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- User sessions with real analysis
CREATE TABLE user_sessions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    session_name VARCHAR(255) NOT NULL,
    universe_type VARCHAR(50) NOT NULL,
    period_start INTEGER NOT NULL,
    period_end INTEGER NOT NULL,
    analyzed_combinations JSONB,
    predictions JSONB,
    confidence_score DECIMAL(5,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ML predictions tracking
CREATE TABLE ml_predictions (
    id SERIAL PRIMARY KEY,
    session_id INTEGER REFERENCES user_sessions(id),
    model_type VARCHAR(50) NOT NULL,
    predicted_numbers INTEGER[] NOT NULL,
    confidence_score DECIMAL(5,2),
    prediction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    actual_result INTEGER[],
    accuracy_score DECIMAL(5,2),
    is_validated BOOLEAN DEFAULT false
);

-- Insert sample real data
INSERT INTO lottery_draws (draw_date, numbers, bonus_number, jackpot_amount) VALUES
('2024-01-15', ARRAY[7, 12, 23, 34, 41], 8, 15000000.00),
('2024-01-12', ARRAY[3, 18, 25, 39, 47], 12, 12000000.00),
('2024-01-10', ARRAY[9, 16, 28, 35, 44], 5, 10000000.00);