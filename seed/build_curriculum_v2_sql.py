#!/usr/bin/env python
"""Generate curriculum_v2.sql: units table + remapped topics + renumbered question/CCE links.
Run AFTER build_curriculum_v2.py. Idempotent inserts."""
import json, pathlib, datetime

D = pathlib.Path(r"C:\Users\Kang\racgp-study-app\seed")
data = json.loads((D/"data"/"curriculum_v2.json").read_text(encoding="utf-8"))
OUT = D / "curriculum_v2.sql"

def esc(s):
    if s is None: return "NULL"
    return "'" + str(s).replace("'", "''") + "'"
def jstr(obj): return esc(json.dumps(obj, ensure_ascii=False))
today = datetime.date.today().isoformat()

lines = ["-- AUTO-GENERATED from curriculum_v2.json - do not edit","-- Built "+today,""]

lines.append("INSERT OR IGNORE INTO units (id, type, number, name, racgp_url, blurb, guidelines, materials) VALUES")
lines.append(",\n".join(
    f"({u['id']}, {esc(u['type'])}, {u['number']}, {esc(u['name'])}, {esc(u['racgp_url'])}, {esc(u['blurb'])}, {jstr(u['guidelines'])}, {jstr(u['materials'])})"
    for u in data["units"]) + ";")

lines.append("\n-- Topics remapped to official units (categories preserved: Presentation/System/Population kept in 'category')")
lines.append("INSERT OR IGNORE INTO topics (id, unit, category, name, priority, must_know, should_know, nice_to_know, status, updated_at) VALUES")
lines.append(",\n".join(
    f"({i}, {esc(t['unit'])}, {esc(t['category'])}, {esc(t['name'])}, {esc(t['priority'])}, {esc(t.get('must_know',''))}, {esc(t.get('should_know',''))}, {esc(t.get('nice_to_know',''))}, 'not started', '{today}')"
    for i, t in enumerate(data["topics"], 1)) + ";")

# wipe + re-insert reviews to match new topic names (topics unchanged, but keep simple)
lines.append("\n-- Notes: start empty")
OUT.write_text("\n".join(lines), encoding="utf-8")
print("wrote curriculum_v2.sql:", len(data["units"]), "units,", len(data["topics"]), "topics")
