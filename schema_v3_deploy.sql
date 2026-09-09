DROP TABLE IF EXISTS units;
CREATE TABLE IF NOT EXISTS units (
  id INTEGER PRIMARY KEY,
  type TEXT NOT NULL,
  number INTEGER NOT NULL,
  name TEXT NOT NULL,
  racgp_url TEXT,
  blurb TEXT,
  rationale TEXT,
  competencies TEXT,
  learning_strategies TEXT,
  guiding_topics TEXT,
  case_example TEXT,
  guidelines TEXT,
  materials TEXT
);
