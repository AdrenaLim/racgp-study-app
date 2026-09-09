#!/usr/bin/env python
"""Build v3 curriculum: 42 units in the official RACGP unit format.
Sections per unit (mirroring the RACGP Curriculum and Syllabus structure):
  1. Unit introduction (blurb)
  2. Competencies and learning outcomes (core competency framework, domains 1-5)
  3. Learning strategies (own / supervisor / small group / non-medical - RACGP's four contexts)
  4. Guiding topics and content areas
  5. Learning resources (guidelines + materials, each with source)
  6. Sources (RACGP unit page link)

Also emits UPDATE statements so every topic sits under its official unit
(fixes the v2 bug where the remapped units were never applied to the DB)."""
import json, pathlib

D = pathlib.Path(__file__).parent / "data"
v2 = json.loads((D / "curriculum_v2.json").read_text(encoding="utf-8"))
units_v2 = {u["name"]: u for u in v2["units"]}
topics_v2 = v2["topics"]

# ---- Core competency framework (applies across all 42 units) ----
COMPETENCIES = [
 {"domain":"D1 Communication and the patient-doctor relationship","outcome":"Communicate clearly, respectfully and effectively; use health education and culturally safe communication; provide holistic, patient-centred care."},
 {"domain":"D2 Applied professional knowledge and skills","outcome":"Take a timely history, perform a relevant examination, form differentials, select and interpret investigations, reason clinically, prescribe safely and manage uncertainty."},
 {"domain":"D3 Population health and the context of general practice","outcome":"Apply epidemiology to screening and management, use resources sustainably, manage public health risks, and promote health equity."},
 {"domain":"D4 Professional and ethical role","outcome":"Practise ethically with duty of care, maintain professional conduct and boundaries, care for your own health, and contribute to teaching and quality."},
 {"domain":"D5 Organisational and legal dimensions","outcome":"Maintain accurate records, privacy and consent; work within medico-legal, quality and safety frameworks; manage time, priorities and systems of care."},
]

STRATEGIES = [
 {"context":"On your own","text":"Read this unit's RACGP page and its primary guideline; list the last five patients from your practice who fit this unit and check your management against the guideline."},
 {"context":"With your supervisor","text":"Bring two recent cases from this unit to your tutorial; map your reasoning to the competency framework and ask for specific feedback."},
 {"context":"In a small group","text":"Run a case-based discussion or role-play: one member presents a case from this unit, the group works the differential and management, then compare with the guideline."},
 {"context":"With a non-medical person","text":"Explain one core concept from this unit (e.g., why we screen, how the treatment works) in plain language to a friend or family member - teach-back tests your own understanding."},
]

# ---- Guiding topics and content areas, per official unit ----
GUIDING = {
 "Communication and the patient\u2013doctor relationship": ["Consultation models and structuring the consultation","Open and closed questioning; ICE (ideas, concerns, expectations)","Health literacy and plain-language explaining","Breaking bad news (SPIKES)","Motivational interviewing and behaviour change","Shared decision making and patient-centred care","Difficult consultations: anger, tears, silence","Telehealth consultation skills"],
 "Applied professional knowledge and skills": ["History and examination across presentations","Differential diagnosis and clinical reasoning frameworks","Selecting investigations that change management","Interpreting common results (FBE, UEC, LFT, TFT, imaging)","Safe prescribing: interactions, renal dosing, allergy","Common GP procedures and consent for them","Managing uncertainty and the undifferentiated patient","Evidence-based practice in the consult"],
 "Population health and the context of general practice": ["Principles of screening: sensitivity, lead-time, overdiagnosis","Australian screening programs (cervical, bowel, breast)","Immunisation programs and catch-up","Notifiable diseases and public health responsibilities","Epidemiology basics for GPs","Health promotion and preventive care systems","Social determinants and health equity","Practice audit, recall and reminder systems"],
 "Professional and ethical role": ["Consent (including minors) and capacity","Confidentiality and its limits","Professional boundaries","Conflict of interest","The doctor's own health and help-seeking","Supervision, teaching and giving feedback","Ethical frameworks for everyday dilemmas","Complaints and open disclosure"],
 "Organisational and legal dimensions": ["Medical records and documentation standards","Privacy legislation in practice","MBS item numbers for GP care","Referral letters that work","Results follow-up systems","Mandatory reporting duties","Austroads fitness to drive","Accreditation, quality and clinical governance"],
 "Aboriginal and Torres Strait Islander health": ["Historical and cultural context: colonisation, Stolen Generations, trauma","Cultural safety in practice (vs cultural awareness)","Annual health checks (MBS 715) and follow-up items","Closing the Gap PBS co-payments","Chronic disease priorities: diabetes, CVD risk from 30, kidney disease","Rheumatic heart disease and skin/ear health in high-prevalence settings","Social and emotional wellbeing; suicide prevention","Working with Community Controlled Health Services"],
 "Rural health": ["Extended scope and isolation: what you must be able to do","Telehealth and virtual care models","Retrieval, transfer and pre-hospital decisions","On-call and after-hours sustainability","Occupational and agricultural exposures","Quality care with limited local services"],
 "Abuse and violence": ["Recognising family and domestic violence; asking directly","Safety assessment and safety planning","Sexual assault: first response and forensic options","Child abuse: physical, sexual, emotional, neglect","Elder abuse","Mandatory reporting thresholds (QLD)","Documentation that stands up (verbatim, body maps)","Referral pathways; 1800RESPECT; White Book"],
 "Addiction medicine": ["Alcohol: AUDIT-C, brief intervention, withdrawal (CIWA-Ar, thiamine)","Smoking cessation: Ask-Advise-Help, pharmacotherapy","Opioids: safe prescribing, OAT (buprenorphine/methadone)","Stimulants, cannabis, vaping","Gambling and behavioural addictions","Comorbidity with mental health","Harm minimisation and needle programs"],
 "Cardiovascular health": ["Absolute CVD risk assessment and the Aus CVD Risk Calculator","Hypertension: confirmation, targets, management","Stable angina and the four pillars of management","ACS: recognition, primary care actions, secondary prevention","Heart failure: diagnosis, quadruple therapy","Atrial fibrillation: detection, CHA2DS2-VA, anticoagulation","Other arrhythmias and syncope","Valvular disease and murmur triage","Peripheral arterial disease and aortic disease","VTE prevention and anticoagulation (DOACs, warfarin)","Lipid management and familial hypercholesterolaemia"],
 "Child and youth health": ["Growth, development and surveillance at each age","Feeding, sleep and settling","Common infections: URTI, AOM, bronchiolitis, croup, gastro","Fever assessment and the unwell child (traffic-light)","Eczema, asthma and allergy in children","Behavioural and developmental concerns; ADHD/ASD pathways","Enuresis and constipation","Adolescent consult: HEADSS, confidentiality","Child safeguarding and mandatory reporting"],
 "Dermatological presentations": ["Rash pattern recognition: eczema, psoriasis, urticaria, drug eruptions","Acne management ladder","Skin infections: impetigo, cellulitis, scabies, tinea","Skin cancer: BCC, SCC, melanoma; biopsy rules","Leg ulcers and wound care","Hair and nail presentations","Dermatology referral and phototherapy/systemics overview"],
 "Disability care": ["Health care for people with intellectual disability","Annual health assessments and the Comprehensive Health Assessment Program","Communication: easy-read, augmentative tools, involving support people","Epilepsy and cerebral palsy in GP care","Ageing with disability; preventative care gaps","NDIS: what it funds and the GP's role","Carer health and support"],
 "Disaster health": ["Pandemic preparedness and infection control in the practice","Business continuity for general practice","The GP role in disasters and emergencies","Psychological first aid","Ethical allocation under scarcity"],
 "Doctors' health": ["Burnout, fatigue and mental health in the profession","Substance use among doctors; self-prescribing boundaries","Mandatory notification thresholds and the treating-doctor protection","Confidential care pathways: own GP, doctors' health services","Supporting a colleague: what to say, when to escalate"],
 "Ear, nose, throat and oral health": ["Otitis media: watchful waiting, when to treat, grommets","Otitis externa and ear cleaning","Hearing loss: Rinne/Weber, referral","Epistaxis: first aid and cautery","Sinusitis and nasal steroids","Sore throat: Centor criteria, PEF cultures","Oral lesions, dental emergencies and the non-healing ulcer","Snoring, obstructive sleep apnoea referral","Paediatric ENT: tonsils, adenoids, foreign bodies"],
 "Education in general practice": ["Teaching medical students and registrars in the practice","Feedback that changes practice","Supervision structures and term planning","Assessment basics for learners","Creating a teaching culture in a busy practice"],
 "Emergency medicine": ["Anaphylaxis and IM adrenaline","ACS and stroke: time-critical actions in the community","Sepsis recognition (qSOFA) and transfer","Severe asthma and COPD emergencies","DKA and hyperglycaemic emergencies","Trauma basics and haemorrhage control","Envenomation (snakes, ticks, marine - QLD)","Poisoning: toxicdromes, Poisons Info Centre","Transfer criteria and communicating with retrieval"],
 "Endocrine and metabolic health": ["Type 2 diabetes: diagnosis, annual cycle, agent selection by comorbidity","Type 1 diabetes and insulin basics; DKA","Thyroid: TSH-first interpretation, nodules, pregnancy","Obesity as a chronic disease; pharmacotherapy","PCOS","Osteoporosis and bone health","Adrenal and pituitary problems GPs meet","Steroid-induced hyperglycaemia"],
 "Eye presentations": ["The red eye triage (sight-threatening causes)","Acute vision loss = same day","Trauma and chemical injury (irrigate first)","Diabetic retinopathy screening","Glaucoma: detection and shared care","Lid and lacrimal problems","Flashes, floaters, retinal detachment","Neuro-ophthalmology basics: GCA, pupil changes"],
 "Gastrointestinal health": ["Dyspepsia and GORD; alarm features","IBS (Rome IV) and functional GI","IBD: red flags, extraintestinal, shared care","Coeliac disease: test before diet","Bowel cancer screening and positive iFOBT","Liver: MASLD, viral hepatitis B and C","Pancreatitis and gallstones","Constipation and diarrhoea workup","Anal conditions: haemorrhoids, fissures, pruritus ani"],
 "Haematological presentations": ["Anaemia: micro/macro/normocytic approach","Iron deficiency: find the cause","Anticoagulation: DOACs, warfarin, perioperative","VTE: provoked vs unprovoked, treatment duration","Recognising haematological malignancy (blasts, cytopenias)","Thrombocytosis/penia and eosinophilia","Transfusion basics and iron infusions","Monoclonal protein found incidentally"],
 "Infectious diseases": ["Antimicrobial stewardship and eTG first-line choices","UTI, cellulitis, pneumonia, sore throat, sinusitis, otitis","Zoonoses in QLD: Q fever, leptospirosis, Ross River","Tuberculosis: recognition and notification","HIV: testing, PEP, PrEP, treat-all","Returned traveller with fever","Notifiable diseases and public health duties","Immunisation in practice: errors, catch-ups, AIR","Sepsis: recognition and escalation"],
 "Integrative medicine": ["Common complementary medicines patients take","CAM-drug interactions (St John's wort, fish oils, etc)","Evidenced appraisal of CAM claims","Communicating about CAM without dismissing the patient","Safety concerns: herbals in surgery/pregnancy"],
 "Justice system health": ["Health of prisoners and on release","Opioid therapy and drug courts/prison interfaces","Confidentiality limits in forensic settings","Forensic patients in the community"],
 "Kidney and urinary health": ["CKD: staging (eGFR/ACR), management, referral criteria","AKI: causes, nephrotoxins, sick-day rules","Haematuria and proteinuria workup","UTI: uncomplicated, complicated, recurrence, male","Stones: acute management and prevention","Incontinence and LUTS","Prostate: LUTS, PSA shared decision-making","Erectile dysfunction as CVD marker"],
 "Men's health": ["PSA and prostate cancer: informed choice","Testicular pain: torsion vs others","Erectile dysfunction evaluation","Male mental health and suicide prevention","Alcohol and risk-taking in men","Engaging men in preventive care","Andropause: what's real","Family planning from the male side"],
 "Mental health": ["Depression: stepped care, pharmacotherapy, follow-up","Anxiety disorders: GAD, panic, phobias","Bipolar disorder: recognition, specialist shared care","Psychosis and early intervention pathways","PTSD and trauma-informed care","Eating disorders: recognition, physical monitoring","Perinatal mental health (EPDS)","Suicide risk assessment, safety planning, escalation","Psychological therapies overview; MBS Better Access","Therapeutic alliance and the mental state exam"],
 "Migrant, refugee and asylum seeker health": ["Arrival and post-arrival health assessment","Professional interpreters (TIS National): always, not family","Refugee screening bundle: hepatitis B, HIV, syphilis, TB, parasites","Torture and trauma-informed care","Catch-up immunisation","Vitamin D and nutrition in newly arrived patients","Medicare, visa status and access barriers","Culture, health beliefs and negotiation"],
 "Military and veteran health": ["PTSD and moral injury","Physical injuries: hearing loss, musculoskeletal","DVA health cards and referral pathways","Transition from service and homelessness risk","Families of veterans"],
 "Musculoskeletal presentations": ["Back pain: red flags, acute management, chronic pain transition","Osteoarthritis: non-surgical ladder","Inflammatory arthritis: pattern recognition, early referral","Gout and CPPD","Osteoporosis: fracture prevention","Sports injuries and Ottawa rules","Fibromyalgia and pain sensitisation","Neck pain and whiplash"],
 "Neurological presentations": ["Headache: primary vs secondary; red flags; migraine management","Dizziness: BPPV, vestibular, cardiovascular causes","Stroke and TIA: FAST, same-day pathway","Epilepsy: first seizure, driving, referral","Dementia: workup, reversible causes, disclosures","Parkinson disease: recognition, therapy overview","Neuropathy and mononeuropathies","Functional neurological symptoms"],
 "Occupational and environmental medicine": ["Fitness-for-work certificates done properly","Work-related injury and return-to-work plans","Workers' compensation (QLD): certificates and roles","Occupational asthma and dermatitis","Asbestos and dust diseases","Heat illness (QLD summers)","Doctor's certificates: legal weight"],
 "Older persons' health": ["Comprehensive geriatric assessment (75+ health assessment)","Falls: assessment and multi-factorial prevention","Cognition: dementia vs delirium vs depression","Polypharmacy and deprescribing","Incontinence","RACF medicine: Silver Book, restrictive practices","Elder abuse","Driving and Austroads duties","Aged care system navigation (post-2024 reforms)","End-of-life planning in the community"],
 "Pain management": ["Acute vs persistent pain: different frameworks","Opioids: initiation, tapering, agreements","Adjuvants: gabapentinoids, TCAs, SNRIs","Non-drug: pacing, exercise, CBT, pain programs","Cancer pain basics","Sick-day and overdose safety planning"],
 "Palliative care": ["Symptom control: pain (WHO ladder), nausea, dyspnoea, secretions","Recognising the dying phase","Anticipatory prescribing (subcutaneous set)","Advance care planning and substitute decision-makers (QLD)","Voluntary assisted dying (QLD): eligibility, process","Carer support and bereavement","Paediatric palliative basics","After-hours and crisis planning"],
 "Pregnancy and reproductive health": ["Preconception care","Antenatal schedule and booking tests","Common issues: nausea, GDM, pre-eclampsia red flags","Antenatal complications needing urgent obstetric review","Postnatal care: mother (EPDS), baby, lactation","Contraception: LARC first, UKMEC, emergency","Subfertility: initial GP workup","Medical termination of pregnancy pathways","Medication safety in pregnancy and lactation"],
 "Research in general practice": ["Critical appraisal: quick guides","Clinical audit and quality improvement in your practice","Basic statistics GPs actually need","Consent and ethics in research","Practice-based research networks"],
 "Respiratory health": ["Asthma: diagnosis, AIR/ICS-formoterol, action plans","COPD: spirometry, step-up, pulmonary rehab","Chronic cough: the big three + ACE","Breathlessness workup","Haemoptysis and lung cancer pathways","Obstructive sleep apnoea","Pleural disease and pneumothorax","Spirometry interpretation","Occupational lung disease"],
 "Sexual health and gender diversity": ["STI screening by risk and site (NAAT)","Syphilis: rising incidence, pregnancy, interpretation","HIV: testing, PrEP, PEP, U=U","Chlamydia complications and partner notification","Genital symptoms: sores, discharge, pelvic pain","Cervical screening integration","Sexual dysfunction: taking the history","Gender-diverse care: affirming practice, referral, hormones overview"],
 "Travel medicine": ["Pre-travel consult structure","Vaccine planning including yellow fever certification","Malaria prophylaxis and regions","Travellers' diarrhoea: prevention, self-treatment kit","Returning traveller fever = emergency","Special travellers: pregnant, immunosuppressed, kids","Deep vein thrombosis risk on long flights"],
 "Women's health": ["Cervical screening: HPV, self-collection, result pathways","Heavy menstrual bleeding: PALM-COEIN, treatment ladder","Pelvic pain: endometriosis, PID","Menopause and MHT: timing, risks, non-hormonal","PCOS across the lifespan","Breast symptoms and BreastScreen","Urinary incontinence","Osteoporosis prevention in women","Premenstrual disorders"],
}

# ---- Assemble enriched units ----
units = []
for u in v2["units"]:
    gt = GUIDING.get(u["name"], [])
    if not gt:
        print("WARNING: no guiding topics for", u["name"])
    gl = []
    for g in (u.get("guidelines") or []):
        gl.append({"title": g["title"], "tier": g.get("tier", 2), "url": g["url"],
                   "source": (g["title"].split("(")[0].strip()[:60]) if g["title"] else ""})
    mats = []
    for m in (u.get("materials") or []):
        mats.append({"label": m["label"], "url": m["url"], "kind": m.get("kind", "org"),
                     "source": m["label"]})
    units.append({
        "id": u["id"], "type": u["type"], "number": u["number"], "name": u["name"],
        "racgp_url": u["racgp_url"], "blurb": u["blurb"],
        "rationale": u["blurb"],  # rationale = blurb; v3 schema splits them
        "competencies": COMPETENCIES, "learning_strategies": STRATEGIES,
        "guiding_topics": gt, "case_example": "",  # case examples added later if available
        "guidelines": gl, "materials": mats,
    })

out = {"units": units, "topics": topics_v2}
(D / "curriculum_v3.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
print("curriculum_v3.json:", len(units), "units,", len(topics_v2), "topics")
missing_gt = [u["name"] for u in units if not GUIDING.get(u["name"])]
print("units without guiding topics:", missing_gt)

# ---- Emit curriculum_v3.sql ----
def esc(s):
    if s is None: return "NULL"
    return "'" + str(s).replace("'", "''") + "'"
def jstr(o): return esc(json.dumps(o, ensure_ascii=False))

lines = ["-- AUTO-GENERATED from curriculum_v3.json - do not edit",
         "-- Units in official RACGP unit format + topic-unit realignment fixes",
         "",
         "-- UNITS (chunked to stay under D1 statement limits)"]
rows = []
for u in units:
    rows.append(f"({u['id']}, {esc(u['type'])}, {u['number']}, {esc(u['name'])}, {esc(u['racgp_url'])}, {esc(u['blurb'])}, {esc(u['rationale'])}, {jstr(u['competencies'])}, {jstr(u['learning_strategies'])}, {jstr(u['guiding_topics'])}, {esc(u['case_example'])}, {jstr(u['guidelines'])}, {jstr(u['materials'])})")
CH = 8
for i in range(0, len(rows), CH):
    lines.append("INSERT OR REPLACE INTO units (id, type, number, name, racgp_url, blurb, rationale, competencies, learning_strategies, guiding_topics, case_example, guidelines, materials) VALUES")
    lines.append(",\n".join(rows[i:i+CH]) + ";")

lines.append("\n-- Realign every topic to its official unit (fixes v2 bug where remap was ignored)")
unit_names = set(u["name"] for u in units)
bad = [t["name"] for t in topics_v2 if t["unit"] not in unit_names]
if bad: raise SystemExit("topics pointing at missing units: " + str(bad))
for t in topics_v2:
    lines.append(f"UPDATE topics SET unit = {esc(t['unit'])} WHERE name = {esc(t['name'])};")

(pathlib.Path(__file__).parent / "curriculum_v3.sql").write_text("\n".join(lines), encoding="utf-8")
print("curriculum_v3.sql written with", len(units), "unit rows and", len(topics_v2), "topic updates")
