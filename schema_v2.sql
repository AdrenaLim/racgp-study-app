-- v2: official RACGP curriculum structure + notes
CREATE TABLE IF NOT EXISTS units (
  id INTEGER PRIMARY KEY,
  type TEXT NOT NULL,             -- core | contextual
  number INTEGER NOT NULL,        -- official unit number within type
  name TEXT NOT NULL,
  racgp_url TEXT,
  blurb TEXT,
  guidelines TEXT,                -- JSON [{title, tier, url}]
  materials TEXT                 -- JSON [{label, url, kind}]
);

CREATE TABLE IF NOT EXISTS notes (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  unit TEXT,
  topic TEXT,
  content TEXT NOT NULL,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_notes_unit ON notes(unit);
