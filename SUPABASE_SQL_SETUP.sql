-- Create teams table
CREATE TABLE teams (
    id SERIAL PRIMARY KEY,
    team_name VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    is_admin BOOLEAN DEFAULT FALSE,
    status VARCHAR(50) DEFAULT 'active',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Insert admin user
INSERT INTO teams (team_name, password, is_admin, status) 
VALUES ('admin', 'admin', TRUE, 'active');

-- Create matches table
CREATE TABLE matches (
    id SERIAL PRIMARY KEY,
    team1_id INTEGER REFERENCES teams(id),
    team2_id INTEGER REFERENCES teams(id),
    winner_id INTEGER REFERENCES teams(id),
    score VARCHAR(50),
    status VARCHAR(50) DEFAULT 'pending',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create challenges table
CREATE TABLE challenges (
    id SERIAL PRIMARY KEY,
    challenger_id INTEGER REFERENCES teams(id),
    challenged_id INTEGER REFERENCES teams(id),
    status VARCHAR(50) DEFAULT 'pending',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Enable Row Level Security (RLS)
ALTER TABLE teams ENABLE ROW LEVEL SECURITY;
ALTER TABLE matches ENABLE ROW LEVEL SECURITY;
ALTER TABLE challenges ENABLE ROW LEVEL SECURITY;

-- Create policies for public read access
CREATE POLICY "Allow public read access to teams" ON teams
    FOR SELECT USING (true);

CREATE POLICY "Allow public read access to matches" ON matches
    FOR SELECT USING (true);

CREATE POLICY "Allow public read access to challenges" ON challenges
    FOR SELECT USING (true);

-- Create policies for authenticated insert/update
CREATE POLICY "Allow authenticated insert to teams" ON teams
    FOR INSERT WITH CHECK (true);

CREATE POLICY "Allow authenticated insert to matches" ON matches
    FOR INSERT WITH CHECK (true);

CREATE POLICY "Allow authenticated insert to challenges" ON challenges
    FOR INSERT WITH CHECK (true); 