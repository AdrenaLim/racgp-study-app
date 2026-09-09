-- v3: full RACGP 7-section curriculum format
ALTER TABLE units ADD COLUMN rationale TEXT;
ALTER TABLE units ADD COLUMN competencies TEXT;      -- JSON array
ALTER TABLE units ADD COLUMN case_example TEXT;
ALTER TABLE units ADD COLUMN learning_strategies TEXT; -- JSON array
-- materials already exists (JSON); guidelines already exists (JSON)
