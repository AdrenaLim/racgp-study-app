-- RACGP Study System - D1 schema (idempotent: safe to re-run on deploy)
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS exam_meta (
  key TEXT PRIMARY KEY,
  value TEXT NOT NULL,
  source_url TEXT,
  checked_date TEXT
);

CREATE TABLE IF NOT EXISTS topics (
  id INTEGER PRIMARY KEY,
  unit TEXT NOT NULL,            -- RACGP 2022 curriculum contextual unit
  category TEXT NOT NULL,        -- grouping: Presentation / System / Population / Practice
  name TEXT NOT NULL,
  priority TEXT NOT NULL,        -- VH (very high yield), H, M, L
  must_know TEXT,
  should_know TEXT,
  nice_to_know TEXT,
  status TEXT DEFAULT 'not started',  -- not started / learning / solid / exam ready
  updated_at TEXT
);

CREATE TABLE IF NOT EXISTS questions (
  id INTEGER PRIMARY KEY,
  type TEXT NOT NULL,            -- AKT | KFP
  topic TEXT NOT NULL,
  unit TEXT,
  stem TEXT NOT NULL,
  options TEXT NOT NULL,          -- JSON array (AKT) or array of arrays per part (KFP)
  answers TEXT NOT NULL,          -- JSON: index (AKT) or array per part (KFP)
  explanation TEXT,
  pearl TEXT,                     -- exam pearl
  trap TEXT                       -- common trap
);

CREATE TABLE IF NOT EXISTS attempts (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  question_id INTEGER NOT NULL REFERENCES questions(id),
  user_answer TEXT,
  correct INTEGER NOT NULL,
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS cce_cases (
  id INTEGER PRIMARY KEY,
  title TEXT NOT NULL,
  category TEXT NOT NULL,
  testing TEXT NOT NULL,          -- what the examiner is assessing
  must_hits TEXT NOT NULL,        -- must-hit points
  traps TEXT,
  structure TEXT,                 -- ideal consultation structure
  phrases TEXT,                   -- example phrases
  scoring TEXT                    -- where marks are gained
);

CREATE TABLE IF NOT EXISTS mistakes (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  created_at TEXT NOT NULL,
  exam TEXT NOT NULL,             -- AKT | KFP | CCE
  topic TEXT NOT NULL,
  question_ref TEXT,
  my_error TEXT,
  correct_principle TEXT,
  why_missed TEXT,                -- error category
  review_date TEXT,
  status TEXT DEFAULT 'open'      -- open / reviewed
);

CREATE TABLE IF NOT EXISTS guidelines (
  id INTEGER PRIMARY KEY,
  tier INTEGER NOT NULL,          -- 1 = must know cold, 2 = working knowledge, 3 = know where to look
  title TEXT NOT NULL,
  publisher TEXT,
  year TEXT,
  url TEXT,
  key_points TEXT,
  thresholds TEXT,                -- numbers / intervals worth memorising
  exam_relevance TEXT
);

CREATE TABLE IF NOT EXISTS resources (
  id INTEGER PRIMARY KEY,
  domain TEXT NOT NULL,
  primary_res TEXT NOT NULL,
  secondary_res TEXT,
  rapid_review TEXT,
  url TEXT
);

CREATE TABLE IF NOT EXISTS rapid_sheets (
  id INTEGER PRIMARY KEY,
  title TEXT NOT NULL,
  content TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS schedule (
  id INTEGER PRIMARY KEY,
  week INTEGER NOT NULL,
  week_commencing TEXT,
  phase TEXT NOT NULL,
  focus TEXT NOT NULL,
  objectives TEXT,
  activities TEXT
);

CREATE TABLE IF NOT EXISTS reviews (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  topic TEXT NOT NULL UNIQUE,
  level INTEGER DEFAULT 0,        -- spaced repetition box 0..5
  due TEXT NOT NULL,
  streak INTEGER DEFAULT 0,
  updated_at TEXT
);

CREATE TABLE IF NOT EXISTS settings (
  key TEXT PRIMARY KEY,
  value TEXT
);

CREATE INDEX IF NOT EXISTS idx_topics_unit ON topics(unit);
CREATE INDEX IF NOT EXISTS idx_questions_type ON questions(type);
CREATE INDEX IF NOT EXISTS idx_attempts_q ON attempts(question_id);
CREATE INDEX IF NOT EXISTS idx_mistakes_topic ON mistakes(topic);
