#!/usr/bin/env python
"""Generate curriculum_v4.sql + schema_v4.sql from curriculum_v4.json.

Idempotent against existing DBs:
  - UPDATE units (ids 1-42) with real RACGP content for existing TEXT columns
  - new table unit_wisdom (CREATE TABLE IF NOT EXISTS + INSERT OR REPLACE)
  - new table schedule_focus (week -> unit names JSON, for the Today view)
"""
import json, pathlib

D = pathlib.Path(__file__).parent / "data"
v4 = json.loads((D / "curriculum_v4.json").read_text(encoding="utf-8"))["units"]

def sq(s): return "'" + str(s).replace("'", "''") + "'"
def js(o): return sq(json.dumps(o, ensure_ascii=False))

# Week -> unit names (drives the Today view). 18-week plan ending at AKT/KFP 15-16 Jan 2027.
FOCUS_UNITS = {
  1:  ["Cardiovascular health", "Population health and the context of general practice"],
  2:  ["Respiratory health", "Infectious diseases"],
  3:  ["Endocrine and metabolic health", "Kidney and urinary health"],
  4:  ["Mental health", "Addiction medicine"],
  5:  ["Women's health", "Pregnancy and reproductive health"],
  6:  ["Child and youth health", "Ear, nose, throat and oral health"],
  7:  ["Older persons' health", "Palliative care"],
  8:  ["Musculoskeletal presentations", "Dermatological presentations"],
  9:  ["Cardiovascular health", "Respiratory health", "Emergency medicine"],
  10: ["Applied professional knowledge and skills", "Neurological presentations", "Endocrine and metabolic health"],
  11: ["Gastrointestinal health", "Haematological presentations", "Kidney and urinary health"],
  12: ["Dermatological presentations", "Musculoskeletal presentations", "Older persons' health"],
  13: ["Aboriginal and Torres Strait Islander health", "Migrant, refugee and asylum seeker health"],
  14: ["Professional and ethical role", "Organisational and legal dimensions", "Abuse and violence"],
  15: [],  # exam prep: timed blocks + drills (Today view shows weakest topics instead)
  16: [],  # full mock
  17: [],  # weak areas + rapid sheets
  18: [],  # final week
}

lines = ["-- AUTO-GENERATED from curriculum_v4.json (real RACGP unit-page content) - do not edit",
         "-- Idempotent: UPDATEs match on unit id; INSERT OR REPLACE keyed tables.",
         ""]

for u in v4:
    guidelines = [{'title': 'RACGP Curriculum unit page', 'tier': 1, 'url': u['racgp_url'], 'source': 'RACGP Curriculum unit page'}]
    materials = [{'label': r['label'], 'url': r['url'], 'kind': 'reference'} for r in u['learning_resources']]
    lines.append(
        "UPDATE units SET "
        f"blurb = {sq(u['rationale'][:280])}, "
        f"rationale = {js(u['rationale'])}, "
        f"competencies = {js(u['competencies'])}, "
        f"learning_strategies = {js(u['learning_strategies'])}, "
        f"guiding_topics = {js(u['guiding_topics'])}, "
        f"case_example = {js(u['case_example'])}, "
        f"guidelines = {js(guidelines)}, "
        f"materials = {js(materials)} "
        f"WHERE id = {int(u['id'])};"
    )

lines.append("")
lines.append("-- Words of wisdom (new table; separate to avoid non-idempotent ALTER TABLE)")
for u in v4:
    lines.append(f"INSERT OR REPLACE INTO unit_wisdom (unit_id, tips) VALUES ({int(u['id'])}, {js(u['words_of_wisdom'])});")

lines.append("")
lines.append("-- Week -> focus units mapping for the Today view")
lines.append("INSERT OR REPLACE INTO settings (key, value) VALUES ('start_date', '2026-09-14');")
for wk, units in FOCUS_UNITS.items():
    lines.append(f"INSERT OR REPLACE INTO schedule_focus (week, units) VALUES ({wk}, {js(units)});")

out = pathlib.Path(__file__).parent / "curriculum_v4.sql"
out.write_text('\n'.join(lines) + '\n', encoding='utf-8')
print(f"wrote {out}: {len(v4)} unit UPDATEs + wisdom + focus")

sch = pathlib.Path(__file__).parent / "schema_v4.sql"
sch.write_text("""-- v4 schema additions (idempotent: CREATE TABLE IF NOT EXISTS)
CREATE TABLE IF NOT EXISTS unit_wisdom (
  unit_id INTEGER PRIMARY KEY,
  tips TEXT
);
CREATE TABLE IF NOT EXISTS schedule_focus (
  week INTEGER PRIMARY KEY,
  units TEXT
);
""", encoding='utf-8')
print(f"wrote {sch}")
