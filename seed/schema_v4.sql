-- v4 schema additions (idempotent: CREATE TABLE IF NOT EXISTS)
CREATE TABLE IF NOT EXISTS unit_wisdom (
  unit_id INTEGER PRIMARY KEY,
  tips TEXT
);
CREATE TABLE IF NOT EXISTS schedule_focus (
  week INTEGER PRIMARY KEY,
  units TEXT
);
