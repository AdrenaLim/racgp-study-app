#!/usr/bin/env python
"""Scrape all 42 official RACGP curriculum unit pages into structured JSON.
Extracts the RACGP's own 7-section format per unit, plus related units and PDF link.
Polite: sequential fetches with delay. Output: seed/data/units_full.json"""
import re, json, time, pathlib, urllib.request, html as H

D = pathlib.Path(__file__).parent / "data"
D.mkdir(parents=True, exist_ok=True)
CACHE = pathlib.Path(__file__).parent / "scrape"
CACHE.mkdir(exist_ok=True)

BASE = "https://www.racgp.org.au/education/education-providers/curriculum/curriculum-and-syllabus/units/"

UNITS = [
 ("core",1,"Domain 1 Communication skills and the patient-doctor relationship","domain-1"),
 ("core",2,"Domain 2 Applied professional knowledge and skills","domain-2"),
 ("core",3,"Domain 3 Population health and the context of general practice","domain-3"),
 ("core",4,"Domain 4 Professional and ethical role","domain-4"),
 ("core",5,"Domain 5 Organisational and legal dimensions","domain-5"),
 ("core",6,"Aboriginal and Torres Strait Islander health","aboriginal-and-torres-strait-islander-health"),
 ("core",7,"Rural health","rural-health"),
 ("contextual",1,"Abuse and violence","abuse-and-violence"),
 ("contextual",2,"Addiction medicine","addiction-medicine"),
 ("contextual",3,"Cardiovascular health","cardiovascular-health"),
 ("contextual",4,"Child and youth health","child-and-youth-health"),
 ("contextual",5,"Dermatological presentations","dermatological-presentations"),
 ("contextual",6,"Disability care","disability-care"),
 ("contextual",7,"Disaster health","disaster-health"),
 ("contextual",8,"Doctors' health","doctors-health"),
 ("contextual",9,"Ear, nose, throat and oral health","ear-nose-throat-and-oral-health"),
 ("contextual",10,"Education in general practice","education-in-general-practice"),
 ("contextual",11,"Emergency medicine","emergency-medicine"),
 ("contextual",12,"Endocrine and metabolic health","metabolic-and-endocrine-health"),
 ("contextual",13,"Eye presentations","eye-presentations"),
 ("contextual",14,"Gastrointestinal health","gastrointestinal-health"),
 ("contextual",15,"Haematological presentations","haematological-presentations"),
 ("contextual",16,"Infectious diseases","infectious-diseases"),
 ("contextual",17,"Integrative medicine","integrative-medicine"),
 ("contextual",18,"Justice system health","justice-system-health"),
 ("contextual",19,"Kidney and urinary health","kidney-and-urinary-health"),
 ("contextual",20,"Men's health","mens-health"),
 ("contextual",21,"Mental health","mental-health"),
 ("contextual",22,"Migrant, refugee and asylum seeker health","migrant-refugee-and-asylum-seeker-health"),
 ("contextual",23,"Military and veteran health","military-and-veteran-health"),
 ("contextual",24,"Musculoskeletal presentations","musculoskeletal-presentations"),
 ("contextual",25,"Neurological presentations","neurological-presentations"),
 ("contextual",26,"Occupational and environmental medicine","occupational-and-environmental-medicine"),
 ("contextual",27,"Older persons' health","older-person-s-health"),
 ("contextual",28,"Pain management","pain-management"),
 ("contextual",29,"Palliative care","palliative-care"),
 ("contextual",30,"Pregnancy and reproductive health","pregnancy-and-reproductive-health"),
 ("contextual",31,"Research in general practice","research-in-general-practice"),
 ("contextual",32,"Respiratory health","respiratory-health"),
 ("contextual",33,"Sexual health and gender diversity","sexual-health-and-gender-diversity"),
 ("contextual",34,"Travel medicine","travel-medicine"),
 ("contextual",35,"Women's health","womens-health"),
]

def fetch(url, slug):
    f = CACHE / f"{slug}.html"
    if f.exists() and f.stat().st_size > 50000:
        return f.read_text(encoding="utf-8", errors="replace")
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"})
    with urllib.request.urlopen(req, timeout=45) as r:
        text = r.read().decode("utf-8", errors="replace")
    f.write_text(text, encoding="utf-8")
    return text

def clean(t):
    t = re.sub(r'<[^>]+>', ' ', t)
    t = H.unescape(t)
    t = re.sub(r'\s+', ' ', t)
    return t.strip()

def extract_panels(html_text):
    """RACGP syllabus panels: <div class='syllabus-panel'><div id='parent-X'>...<div id='X' class='panel-collapse collapse'>content</div></div>"""
    panels = {}
    # panel blocks
    for m in re.finditer(r'<div class="syllabus-panel">\s*<div class="panel-heading" id="parent-([^"]+)"', html_text):
        pid = m.group(1)
        # content div starts after this; find the matching content div with same id (without parent-)
        cid = pid.replace("parent-", "")
        cm = re.search(r'id="' + re.escape(cid) + r'"[^>]*class="panel-collapse collapse[^"]*"[^>]*>(.*?)(?=<div class="syllabus-panel">|<div class="panel-heading" id="parent-)', html_text[m.start():], re.S)
        if not cm:
            cm = re.search(r'class="panel-collapse collapse[^"]*"[^>]*id="' + re.escape(cid) + r'"[^>]*>(.*?)(?=<div class="syllabus-panel">|<div class="panel-heading" id="parent-)', html_text[m.start():], re.S)
        if cm:
            panels[cid] = cm.group(1)
    return panels

def parse_unit(html_text, url, slug):
    panels = extract_panels(html_text)
    out = {"url": url, "slug": slug}
    # Rationale: from Rationale panel - strip the Instructions box
    rat = panels.get("Rationale", "")
    # remove instructions sub-block
    rat = re.sub(r'### Instructions.*?(?=<|$)', '', rat, flags=re.S)
    # take text
    out["rationale"] = clean(rat)[:4000]
    # References within rationale panel
    refs = re.findall(r'<h5[^>]*>References</h5>(.*?)(?=</div>|$)', rat, re.S)
    if refs:
        out["references"] = [clean(r)[:400] for r in re.findall(r'<li[^>]*>(.*?)</li>', refs[0], re.S)][:12]
    else:
        out["references"] = []
    # Competencies: keep as structured text list
    comp = panels.get("Competencies-and-learning-outcomes", "")
    out["competencies_raw"] = clean(comp)[:6000]
    # words of wisdom
    wow = panels.get("Words-of-wisdom", "")
    wows = re.findall(r'<li[^>]*>(.*?)</li>', wow, re.S)
    if not wows:
        wows = re.findall(r'<p[^>]*>(.*?)</p>', wow, re.S)
    out["words_of_wisdom"] = [clean(w)[:500] for w in wows if clean(w)][:10]
    # learning strategies
    ls = panels.get("Learning-strategies", "")
    lss = re.findall(r'<li[^>]*>(.*?)</li>', ls, re.S)
    if not lss: lss = re.findall(r'<p[^>]*>(.*?)</p>', ls, re.S)
    out["learning_strategies"] = [clean(x)[:500] for x in lss if clean(x)][:10]
    # guiding topics
    gt = panels.get("Guiding-topics", "")
    gts = re.findall(r'<li[^>]*>(.*?)</li>', gt, re.S)
    if not gts: gts = re.findall(r'<p[^>]*>(.*?)</p>', gt, re.S)
    out["guiding_topics"] = [clean(x)[:300] for x in gts if clean(x)][:30]
    # learning resources: links!
    lr = panels.get("Learning-resources", "")
    links = re.findall(r'<a[^>]*href="([^"]+)"[^>]*>(.*?)</a>', lr, re.S)
    seen = set(); res = []
    for href, label in links:
        label = clean(label)[:200]
        if href.startswith("/"): href = "https://www.racgp.org.au" + href
        k = (href, label)
        if k in seen or not label: continue
        seen.add(k); res.append({"label": label, "url": href})
    # also plain text resources
    lr_text = clean(lr)
    out["learning_resources"] = res[:25]
    out["learning_resources_text"] = lr_text[:1500]
    # case examples (some units)
    ce = panels.get("Case-examples", "") or panels.get("Case-examples-and-discussion", "")
    out["case_examples"] = clean(ce)[:2000]
    # related units
    rel = re.search(r'this contextual unit relates to the other unit/s of:(.*?)(?=Back to units|$)', html_text, re.S|re.I)
    if rel:
        out["related_units"] = [clean(x)[:120] for x in re.findall(r'<a[^>]*>(.*?)</a>', rel.group(1), re.S)][:8]
    else:
        out["related_units"] = []
    # PDF link
    pdf = re.search(r'href="([^"]*getattachment[^"]*)"[^>]*>\s*Download PDF', html_text)
    out["pdf_url"] = ("https://www.racgp.org.au" + pdf.group(1)) if pdf and pdf.group(1).startswith("/") else (pdf.group(1) if pdf else None)
    return out

units = []
fails = []
for i, (typ, num, name, slug) in enumerate(UNITS, 1):
    url = BASE + slug
    try:
        html_text = fetch(url, slug)
        u = parse_unit(html_text, url, slug)
        u.update(type=typ, number=num, name=name)
        units.append(u)
        got = sum(bool(u.get(k)) for k in ["rationale","competencies_raw","words_of_wisdom","learning_strategies","guiding_topics","learning_resources"])
        print(f"{i:2d}/42 {slug:45s} sections:{got}/6 wow:{len(u['words_of_wisdom'])} topics:{len(u['guiding_topics'])} res:{len(u['learning_resources'])}")
    except Exception as e:
        fails.append(slug); print(f"{i:2d}/42 {slug} FAILED: {e}")
    if i % 8 == 0 and i < len(UNITS):
        time.sleep(3)

(D / "units_full.json").write_text(json.dumps({"units": units, "failed": fails}, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"\nDONE: {len(units)} units scraped, {len(fails)} failures -> units_full.json")
if fails: print("failed:", fails)
