#!/usr/bin/env python
"""Generate curriculum_v3.sql: full RACGP-format units (7 sections each)."""
import json, pathlib
D = pathlib.Path(__file__).parent
data = json.loads((D / "data" / "curriculum_v3.json").read_text(encoding="utf-8"))
OUT = D / "curriculum_v3.sql"

def esc(s):
    if s is None: return "NULL"
    return "'" + str(s).replace("'", "''") + "'"
def jstr(obj): return esc(json.dumps(obj, ensure_ascii=False))

lines = ["-- AUTO-GENERATED from curriculum_v3.json - full RACGP 7-section format", ""]
lines.append("INSERT INTO units (id, type, number, name, racgp_url, blurb, rationale, competencies, case_example, learning_strategies, guidelines, materials) VALUES")
rows = []
for i, u in enumerate(data["units"], 1):
    rows.append(f"({i}, {esc(u['type'])}, {u['number']}, {esc(u['name'])}, {esc(u['racgp_url'])}, {esc(u.get('blurb',''))}, {esc(u['rationale'])}, {jstr(u['competencies'])}, {esc(u['case_example'])}, {jstr(u['learning_strategies'])}, {jstr(u['guidelines'])}, {jstr(u['materials'])})")
lines.append(",\n".join(rows) + " ON CONFLICT(id) DO UPDATE SET type=excluded.type, number=excluded.number, name=excluded.name, racgp_url=excluded.racgp_url, blurb=excluded.blurb, rationale=excluded.rationale, competencies=excluded.competencies, case_example=excluded.case_example, learning_strategies=excluded.learning_strategies, guidelines=excluded.guidelines, materials=excluded.materials;")
OUT.write_text("\n".join(lines), encoding="utf-8")
print(f"wrote curriculum_v3.sql with {len(rows)} units (full 7-section format)")
