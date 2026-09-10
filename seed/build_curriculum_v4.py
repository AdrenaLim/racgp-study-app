#!/usr/bin/env python
"""Build curriculum_v4: REAL per-unit content parsed from the scraped official
RACGP Curriculum and Syllabus unit pages (seed/scrape/*.html).

Per unit this extracts:
  1. rationale                - official rationale text (minus instructions)
  2. competencies            - [{domain, outcomes:[{text, codes}]}] per RACGP domain
  3. words_of_wisdom          - GP tips list
  4. case_example             - {narrative, questions:[{q, area, domains}]}
  5. learning_strategies      - [{context, items:[...]}] (own/supervisor/small group/non-medical)
  6. guiding_topics          - official list
  7. learning_resources      - [{label, url}] from the unit's resource table
  8. words_of_wisdom          - tips from experienced GPs
Output: seed/data/curriculum_v4.json + units_full_v2.json for inspection.
"""
import json, re, html as H, pathlib

SC = pathlib.Path(__file__).parent / "scrape"
OUT = pathlib.Path(__file__).parent / "data"
BASE = "https://www.racgp.org.au"
PANELS = ['Rationale','Competencies-and-learning-outcomes','Words-of-wisdom','Case-consultation-example','Learning-strategies','Guiding-topics-and-content-areas','Learning-resources']

def unesc(s): return H.unescape(s)

def text_of(fragment):
    t = re.sub(r'<style[\s\S]*?</style>', '', fragment)
    t = re.sub(r'<[^>]+>', '\n', t)
    t = unesc(t)
    t = t.replace('\xa0', ' ').replace('–','—').replace('\u2011','-')
    lines = [re.sub(r'\s+', ' ', l).strip() for l in t.split('\n')]
    return [l for l in lines if l]

def absolute(url):
    url = url.strip()
    if url.startswith('#') or url.startswith('javascript'): return None
    if url.startswith('http'): return url
    if url.startswith('/'): return BASE + url
    return BASE + '/' + url

def get_panel(html, pid):
    i = html.find(f'id="{pid}"')
    if i < 0: return ''
    ends = [html.find(f'id="{p}"', i+10) for p in PANELS if p != pid]
    ends = [e for e in ends if e > 0]
    end = min(ends) if ends else len(html)
    f = html.find('<footer', i)
    if f > 0: end = min(end, f)
    return html[i:end]

def strip_instructions(panel):
    # remove the instructions div and 'Show instructions' links
    p = re.sub(r'<div class="d-flex flex-row justify-content-end">[\s\S]*?</div>\s*</div>\s*</div>\s*</div>', '', panel, count=1)
    p = re.sub(r'<div class="collapse" id="collapse\d+">[\s\S]*?</div>\s*</div>\s*</div>', '', p, count=1)
    return p

def parse_rationale(panel):
    # rationale: paragraphs after the instructions block; skip References
    txt = re.sub(r'<style[\s\S]*?</style>', '', panel)
    # cut before References section if present
    m = re.search(r'<h3[^>]*>\s*References\s*</h3>', txt)
    if not m:
        m = re.search(r'\bReferences\b', txt)
    if m: txt = txt[:m.start()]
    paras = re.findall(r'<p[^>]*>([\s\S]*?)</p>', txt)
    out = []
    for p in paras:
        t = ' '.join(text_of('<p>'+p+'</p>'))
        if not t or t.startswith('This section provides'): continue
        out.append(t)
    return ' '.join(out)

def parse_competencies(panel):
    # tables: header th = domain; rows: outcome | codes
    comps = []
    for tbl in re.findall(r'<table[\s\S]*?</table>', panel):
        rows = re.findall(r'<tr[^>]*>([\s\S]*?)</tr>', tbl)
        domain = None
        cur = None
        for r in rows:
            th = re.search(r'<th[^>]*>([\s\S]*?)</th>', r)
            if th and th.group(1).strip() and not re.search(r'^\s*$', th.group(1)):
                t = ' '.join(text_of('<th>'+th.group(1)+'</th>'))
                if t and t not in ('Learning outcomes','Related core competency outcomes'):
                    domain = t
                    cur = {'domain': domain, 'outcomes': []}
                    comps.append(cur)
            tds = re.findall(r'<td[^>]*>([\s\S]*?)</td>', r)
            if len(tds) >= 2 and cur is not None:
                outcome = ' '.join(text_of('<td>'+tds[0]+'</td>'))
                codes = ' '.join(text_of('<td>'+tds[1]+'</td>'))
                skip = ('Learning outcomes', 'Related core competency outcomes')
                if outcome and outcome not in skip and not outcome.startswith('The GP is able') and codes not in skip:
                    cur['outcomes'].append({'text': outcome, 'codes': codes})
    return comps

def parse_wisdom(panel):
    items = re.findall(r'<li[^>]*>([\s\S]*?)</li>', panel)
    out = []
    for it in items:
        t = ' '.join(text_of('<li>'+it+'</li>'))
        if t and 'Extension exercise' not in t and 'instructions' not in t.lower():
            out.append(t)
    return out

def parse_case(panel):
    div = re.search(r'<div class="mb-5 p-3 syllabus-case">([\s\S]*?)</div>', panel)
    narrative = ' '.join(text_of('<div>'+ (div.group(1) if div else '') +'</div>')) if div else ''
    narrative = re.sub(r'^Cardiovascular health\s*', '', narrative)
    questions = []
    for tbl in re.findall(r'<table[\s\S]*?</table>', panel):
        for r in re.findall(r'<tr[^>]*>([\s\S]*?)</tr>', tbl):
            tds = re.findall(r'<td[^>]*>([\s\S]*?)</td>', r)
            if len(tds) == 3:
                qs = [t for t in text_of('<td>'+tds[0]+'</td>')]
                area = ' '.join(text_of('<td>'+tds[1]+'</td>'))
                doms = ' '.join(text_of('<td>'+tds[2]+'</td>'))
                q = ' '.join(qs)
                if q and 'Questions for you' not in q:
                    questions.append({'q': q, 'area': area, 'domains': doms})
    return {'narrative': narrative.strip(), 'questions': questions}

def parse_strategies(panel):
    # context headers: grey divs with an icon + <h6 class="font-weight-bold">Label</h6>
    p = strip_instructions(panel)
    ctxs = []
    for m in re.finditer(r'<div class="p-3 mb-5"[^>]*>[\s\S]{0,800}?<h6 class="font-weight-bold">\s*([^<]+?)\s*</h6>', p):
        ctxs.append((m.start(), unesc(m.group(1)).strip()))
    out = []
    for idx, (pos, label) in enumerate(ctxs):
        end = ctxs[idx+1][0] if idx+1 < len(ctxs) else len(p)
        chunk = p[pos:end]
        items = []
        for para in re.findall(r'<p[^>]*>([\s\S]*?)</p>', chunk):
            t = ' '.join(text_of('<p>'+para+'</p>'))
            if t and not t.startswith('This section') and 'self-evaluate' not in t:
                items.append(t)
        for li in re.findall(r'<li[^>]*>([\s\S]*?)</li>', chunk):
            t = ' '.join(text_of('<li>'+li+'</li>'))
            if t and t not in items: items.append(t)
        out.append({'context': label, 'items': items})
    return out

def top_level_lis(fragment):
    """Depth-aware scan: return top-level <li> contents with nested lists inline."""
    out = []
    depth = 0
    cur = None
    token_re = re.compile(r'<ul[^>]*>|</ul>|<li[^>]*>|</li>')
    for m in token_re.finditer(fragment):
        tok = m.group(0)
        if tok.startswith('<ul'):
            depth += 1
        elif tok.startswith('</ul'):
            depth -= 1
        elif tok.startswith('<li') and cur is None:
            cur = m.end()
        elif tok.startswith('</li') and cur is not None and depth <= 1:
            out.append(fragment[cur:m.start()])
            cur = None
    return out

def parse_guiding(panel):
    p = strip_instructions(panel)
    out = []
    for li in top_level_lis(p):
        lines = text_of(li)
        if not lines: continue
        if len(lines) == 1:
            out.append(lines[0])
        else:
            # first line = the competency statement; nested lines = examples/sub-areas
            out.append(lines[0].rstrip(':. ') + ': ' + '; '.join(lines[1:]))
    if not out:
        out = [t for t in text_of(p) if len(t) > 3 and not t.startswith('These are examples')]
    return out

def parse_resources(panel):
    p = strip_instructions(panel)
    res = []
    for m in re.finditer(r'<a[^>]+href="([^"]+)"[^>]*>([\s\S]*?)</a>', p):
        url = absolute(m.group(1))
        label = ' '.join(text_of('<a>'+m.group(2)+'</a>'))
        if not url or not label or label.lower().startswith('show instructions'): continue
        # skip footer/org nav links: only keep links that appear before the related-units section
        res.append({'label': label, 'url': url})
    return res

def parse_unit_file(path, meta):
    html = path.read_text(encoding='utf-8')
    u = dict(meta)
    u['rationale'] = parse_rationale(get_panel(html, 'Rationale'))
    u['competencies'] = parse_competencies(get_panel(html, 'Competencies-and-learning-outcomes'))
    u['words_of_wisdom'] = parse_wisdom(get_panel(html, 'Words-of-wisdom'))
    u['case_example'] = parse_case(get_panel(html, 'Case-consultation-example'))
    u['learning_strategies'] = parse_strategies(get_panel(html, 'Learning-strategies'))
    u['guiding_topics'] = parse_guiding(get_panel(html, 'Guiding-topics-and-content-areas'))
    u['learning_resources'] = parse_resources(get_panel(html, 'Learning-resources'))
    return u

# ---- unit metadata from current DB units (id, type, number, name, racgp_url) ----
db_units = json.load(open(OUT / 'units_current.json', encoding='utf-8'))

def slug_to_file(slug):
    # DB racgp_url slugs for core units 1-5 have numeric prefixes; files use domain-N or short names
    cands = [slug, slug.split('-',1)[1] if '-' in slug else None]
    for c in cands:
        if not c: continue
        f = SC / f"{c}.html"
        if f.exists(): return f
    # manual mapping for the 6 core units and mens-health
    MANUAL = {
      'Communication and the patient–doctor relationship': 'domain-1.html',
      'Applied professional knowledge and skills': 'domain-2.html',
      'Population health and the context of general practice': 'domain-3.html',
      'Professional and ethical role': 'domain-4.html',
      'Organisational and legal dimensions': 'domain-5.html',
      "Men's health": 'mens-health.html',
      "Older persons' health": 'older-person-s-health.html',
    }
    name = db_units_name(slug)
    if name in MANUAL:
        f = SC / MANUAL[name]
        if f.exists(): return f
    return None

def db_units_name(slug):
    slug_noprefix = slug.split('-',1)[1] if slug and slug[0].isdigit() and '-' in slug else slug
    for u in db_units:
        if u['racgp_url'].rstrip('/').split('/')[-1] in (slug, slug_noprefix): return u['name']
    return None

units = []
fails = []
for u in db_units:
    slug = u['racgp_url'].rstrip('/').split('/')[-1]
    f = slug_to_file(slug)
    if f is None:
        fails.append(u['name']); continue
    units.append(parse_unit_file(f, {k: u[k] for k in ('id','type','number','name','racgp_url')}))

print(f"parsed {len(units)} units, {len(fails)} failed: {fails}")
# fill-rate report
for field in ['rationale','competencies','words_of_wisdom','case_example','learning_strategies','guiding_topics','learning_resources']:
    n = sum(1 for u in units if u.get(field) and (not isinstance(u[field], (list,dict)) or len(u[field])>0) and (not isinstance(u.get(field), dict) or u[field].get('narrative')))
    print(f"  {field:20s} {n}/{len(units)}")

(OUT / 'curriculum_v4.json').write_text(json.dumps({'units': units}, ensure_ascii=False, indent=1), encoding='utf-8')
print("wrote", OUT / 'curriculum_v4.json')
