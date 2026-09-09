#!/usr/bin/env python
"""Convert seed JSON files into a single D1 seed SQL file (content portion)."""
import json, pathlib, datetime

D = pathlib.Path(r"C:\Users\Kang\racgp-study-app\seed")
OUT = D / "content.sql"

def esc(s):
    if s is None: return "NULL"
    return "'" + str(s).replace("'", "''") + "'"

def jstr(obj):
    return esc(json.dumps(obj, ensure_ascii=False))

today = datetime.date.today().isoformat()

topics_rows, tid = [], 0
for f in ("presentations.json", "systems.json"):
    for t in json.loads((D / "data" / f).read_text(encoding="utf-8")):
        tid += 1
        topics_rows.append((tid, t))
lines = [
    "-- AUTO-GENERATED from seed/data/*.json - do not edit; edit the JSON and re-run build_seed_sql.py",
    "-- Built " + today,
    "",
    "-- TOPICS",
    "INSERT OR IGNORE INTO topics (id, unit, category, name, priority, must_know, should_know, nice_to_know, status, updated_at) VALUES",
    ",\n".join(
        f"({tid}, {esc(t['unit'])}, {esc(t['category'])}, {esc(t['name'])}, {esc(t['priority'])}, {esc(t.get('must_know',''))}, {esc(t.get('should_know',''))}, {esc(t.get('nice_to_know',''))}, 'not started', '{today}')"
        for tid, t in topics_rows
    ) + ";",
]

qrows, qid = [], 0
for f in ("questions_akt.json", "questions_akt_batch2.json", "questions_akt_batch3.json", "questions_akt_batch4.json", "questions_kfp.json", "questions_kfp_batch2.json"):
    qtype = "AKT" if "akt" in f.lower() else "KFP"
    for q in json.loads((D / "data" / f).read_text(encoding="utf-8")):
        qid += 1
        opts = {"parts": q["parts"]} if qtype == "KFP" else {"options": q["options"]}
        answers = q if qtype == "KFP" else {"answers": q["answers"]}
        qrows.append(f"({qid}, '{qtype}', {esc(q['topic'])}, {esc(q.get('unit',''))}, {esc(q['stem'])}, {jstr(opts)}, {jstr(answers)}, {esc(q.get('explanation',''))}, {esc(q.get('pearl',''))}, {esc(q.get('trap',''))})")
lines += ["", "-- QUESTIONS (chunked)"]
CH = 50
for i in range(0, len(qrows), CH):
    chunk = qrows[i:i+CH]
    lines.append("INSERT OR IGNORE INTO questions (id, type, topic, unit, stem, options, answers, explanation, pearl, trap) VALUES")
    lines.append(",\n".join(chunk) + ";")

crows = []
for i, c in enumerate(json.loads((D / "data" / "cce_cases.json").read_text(encoding="utf-8")), 1):
    crows.append(f"({i}, {esc(c['title'])}, {esc(c['category'])}, {esc(c['testing'])}, {esc(c['must_hits'])}, {esc(c.get('traps',''))}, {esc(c.get('structure',''))}, {esc(c.get('phrases',''))}, {esc(c.get('scoring',''))})")
lines += ["", "-- CCE CASES", "INSERT OR IGNORE INTO cce_cases (id, title, category, testing, must_hits, traps, structure, phrases, scoring) VALUES",
          ",\n".join(crows) + ";"]

grows = []
for i, g in enumerate(json.loads((D / "data" / "guidelines.json").read_text(encoding="utf-8")), 1):
    grows.append(f"({i}, {g['tier']}, {esc(g['title'])}, {esc(g.get('publisher',''))}, {esc(g.get('year',''))}, {esc(g.get('url',''))}, {esc(g.get('key_points',''))}, {esc(g.get('thresholds',''))}, {esc(g.get('exam_relevance',''))})")
lines += ["", "-- GUIDELINES", "INSERT OR IGNORE INTO guidelines (id, tier, title, publisher, year, url, key_points, thresholds, exam_relevance) VALUES",
          ",\n".join(grows) + ";"]

rrows = []
for i, r in enumerate(json.loads((D / "data" / "resources.json").read_text(encoding="utf-8")), 1):
    rrows.append(f"({i}, {esc(r['domain'])}, {esc(r['primary_res'])}, {esc(r.get('secondary_res',''))}, {esc(r.get('rapid_review',''))}, {esc(r.get('url',''))})")
lines += ["", "-- RESOURCES", "INSERT OR IGNORE INTO resources (id, domain, primary_res, secondary_res, rapid_review, url) VALUES",
          ",\n".join(rrows) + ";"]

srows = []
for i, s in enumerate(json.loads((D / "data" / "rapid_sheets.json").read_text(encoding="utf-8")), 1):
    srows.append(f"({i}, {esc(s['title'])}, {esc(s['content'])})")
lines += ["", "-- RAPID SHEETS", "INSERT OR IGNORE INTO rapid_sheets (id, title, content) VALUES",
          ",\n".join(srows) + ";"]

wrows = []
for i, w in enumerate(json.loads((D / "data" / "schedule.json").read_text(encoding="utf-8")), 1):
    wrows.append(f"({i}, {w['week']}, NULL, {esc(w['phase'])}, {esc(w['focus'])}, {esc(w['objectives'])}, {esc(w['activities'])})")
lines += ["", "-- SCHEDULE", "INSERT OR IGNORE INTO schedule (id, week, week_commencing, phase, focus, objectives, activities) VALUES",
          ",\n".join(wrows) + ";"]

vrows = [f"({esc(t['name'])}, 0, '{today}', 0, '{today}')" for _, t in topics_rows]
lines += ["", "-- REVIEWS (spaced repetition, all topics due Day 1)",
          "INSERT OR IGNORE INTO reviews (topic, level, due, streak, updated_at) VALUES",
          ",\n".join(vrows) + ";"]

OUT.write_text("\n".join(lines), encoding="utf-8")
print("Wrote", OUT)
print(f"Topics: {len(topics_rows)} | Questions: {len(qrows)} | CCE: {len(crows)} | Guidelines: {len(grows)} | Resources: {len(rrows)} | Rapid: {len(srows)} | Schedule: {len(wrows)} | Reviews: {len(vrows)}")
