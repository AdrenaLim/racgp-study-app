-- v3: units rebuilt in the official RACGP unit format
-- (drop + recreate is safe: units holds no user data; notes reference by name)
DROP TABLE IF EXISTS units;
CREATE TABLE IF NOT EXISTS units (
  id INTEGER PRIMARY KEY,
  type TEXT NOT NULL,             -- core | contextual
  number INTEGER NOT NULL,        -- official unit number within type
  name TEXT NOT NULL,
  racgp_url TEXT,
  blurb TEXT,                     -- unit introduction
  competencies TEXT,              -- JSON [{domain, outcome}] - core competency framework
  strategies TEXT,                -- JSON [{context, text}] - learning strategies (RACGP format)
  guiding_topics TEXT,            -- JSON [string] - guiding topics and content areas
  guidelines TEXT,                -- JSON [{title, tier, url, source}]
  materials TEXT                 -- JSON [{label, url, kind, source}]
);
