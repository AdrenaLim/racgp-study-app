#!/usr/bin/env python
"""Build v2 curriculum: 42 official RACGP units (7 core + 35 contextual),
each with RACGP unit URL, tiered guideline links, and study materials.
Remaps all 56 existing topics into official units. Also emits notes seed (empty)."""
import json, pathlib

D = pathlib.Path(r"C:\Users\Kang\racgp-study-app\seed\data")
BASE = "https://www.racgp.org.au/education/education-providers/curriculum/curriculum-and-syllabus/units/"

def U(name, slug): return {"name": name, "racgp_url": BASE + slug}

# ---- Official 42 units (verified 2026-09-09 from racgp.org.au curriculum pages) ----
CORE = [
 dict(number=1, name="Communication and the patient–doctor relationship", slug="1-communication-and-the-patient-doctor-relationship",
  blurb="Domain 1: consulting effectively, health education, cultural safety in communication, holistic patient-centred care.",
  guidelines=[{"title":"RACGP Curriculum unit page","tier":1,"url":BASE+"1-communication-and-the-patient-doctor-relationship"}],
  materials=[{"label":"RACGP patient-centred consulting models (course) gplearning","url":"https://www.racgp.org.au/education/professional-development/online-learning/gplearning","kind":"course"}]),
 dict(number=2, name="Applied professional knowledge and skills", slug="2-applied-professional-knowledge-and-skills",
  blurb="Domain 2: history, examination, differential diagnoses, investigations, clinical reasoning, prescribing, procedures, uncertainty.",
  guidelines=[{"title":"RACGP Curriculum unit page","tier":1,"url":BASE+"2-applied-professional-knowledge-and-skills"}],
  materials=[{"label":"eTG complete (Therapeutic Guidelines)","url":"https://tg.org.au","kind":"reference"},
             {"label":"Australian Medicines Handbook","url":"https://amhonline.amh.net.au","kind":"reference"}]),
 dict(number=3, name="Population health and the context of general practice", slug="3-population-health-and-the-context-of-general-practice",
  blurb="Domain 3: epidemiology, screening, sustainable resource use, public health risks, health promotion, equity.",
  guidelines=[{"title":"RACGP Red Book 10th ed (2024)","tier":1,"url":"https://www.racgp.org.au/clinical-resources/clinical-guidelines/key-racgp-guidelines/view-all-guidelines/red-book"}],
  materials=[{"label":"AIH – Australian Immunisation Handbook","url":"https://immunisationhandbook.health.gov.au/","kind":"reference"}]),
 dict(number=4, name="Professional and ethical role", slug="4-professional-and-ethical-role",
  blurb="Domain 4: ethics, duty of care, professional conduct, doctor's own health, teaching, leadership.",
  guidelines=[{"title":"Medical Board of Australia – Good medical practice","tier":1,"url":"https://www.medicalboard.gov.au/Codes-Guidelines-Policies/Code-of-conduct.aspx"}],
  materials=[{"label":"AHPRA mandatory notification guidelines","url":"https://www.ahpra.gov.au/","kind":"reference"}]),
 dict(number=5, name="Organisational and legal dimensions", slug="5-organisational-and-legal-dimensions",
  blurb="Domain 5: records, consent, privacy, medico-legal, quality and safety, practice systems, time management.",
  guidelines=[{"title":"Austroads – Assessing Fitness to Drive","tier":2,"url":"https://austroads.com.au/drivers-and-vehicles/driver-health/assessing-fitness-to-drive"},
              {"title":"MBS online","tier":2,"url":"http://mbsonline.gov.au"}],
  materials=[{"label":"RACGP practice standards","url":"https://www.racgp.org.au/running-a-practice/practice-standards","kind":"reference"}]),
 dict(number=6, name="Aboriginal and Torres Strait Islander health", slug="6-aboriginal-and-torres-strait-islander-health",
  blurb="Core unit: culturally safe care, health equity, 715 health checks, Closing the Gap, community-controlled services.",
  guidelines=[{"title":"National guide to a preventive health assessment for ATSI people (3rd ed)","tier":1,"url":"https://www.racgp.org.au/clinical-resources/clinical-guidelines/key-racgp-guidelines/view-all-guidelines/national-guide"},
              {"title":"RACGP ATSI health unit page","tier":1,"url":BASE+"6-aboriginal-and-torres-strait-islander-health"}],
  materials=[{"label":"NACCHO","url":"https://www.naccho.org.au","kind":"org"},
             {"label":"AIATSIS map of Indigenous Australia (for local context)","url":"https://aiatsis.gov.au/explore/map-indigenous-australia","kind":"map"}]),
 dict(number=7, name="Rural health", slug="rural-health",
  blurb="Core unit: rural and remote practice, isolation, extended scope, on-call, infrastructure, telehealth.",
  guidelines=[{"title":"RACGP rural health unit page","tier":2,"url":BASE+"rural-health"}],
  materials=[{"label":"Services Australia – telehealth","url":"https://www.servicesaustralia.gov.au","kind":"reference"}]),
]

CTX = [
 (1,"Abuse and violence","abuse-and-violence","FDV recognition, safety assessment, child protection, mandatory reporting. White Book is the reference.",
  [("RACGP White Book (abuse and violence)","https://www.racgp.org.au/clinical-resources/clinical-guidelines/key-racgp-guidelines/view-all-guidelines/white-book",1)],
  [("1800RESPECT","https://www.1800respect.org.au","org")]),
 (2,"Addiction medicine","addiction-medicine","Alcohol, tobacco, other drugs: screening, brief intervention, withdrawal, pharmacotherapy, safe opioid prescribing.",
  [("eTG Psychotropic / Addiction","https://tg.org.au",1),("RACGP smoking cessation guidance","https://www.racgp.org.au/clinical-resources/clinical-guidelines/key-racgp-guidelines/view-all-guidelines/smoking-cessation",2)],
  [("Quitline","https://www.quit.org.au","org"),("Turning Point","https://www.turningpoint.org.au","org")]),
 (3,"Cardiovascular health","cardiovascular-health","CVD risk, HTN, IHD, ACS secondary prevention, AF, heart failure, lipids.",
  [("2023 Australian CVD Risk guideline","https://www.heartfoundation.org.au/for-professionals/clinical-resources/cardiovascular-disease-risk-assessment",1),
   ("Australian AF guideline (2018)","https://www.heartfoundation.org.au/for-professionals/clinical-resources/atrial-fibrillation-resources",1),
   ("Heart Foundation HTN resources","https://www.heartfoundation.org.au/for-professionals/clinical-resources/hypertension",2),
   ("ACS 2025 guideline","https://www.heartfoundation.org.au/for-professionals/clinical-resources/acute-coronary-syndromes",2)],
  [("Aus CVD Risk Calculator","https://www.cvdcheck.org.au","tool"),("Heart Foundation","https://www.heartfoundation.org.au","org")]),
 (4,"Child and youth health","child-and-youth-health","Growth, development, common paediatric presentations, adolescent health, safeguarding.",
  [("RCH Clinical Practice Guidelines","https://www.rch.org.au/clinicalguide/",1),("Red Book (paediatric screening)","https://www.racgp.org.au/clinical-resources/clinical-guidelines/key-racgp-guidelines/view-all-guidelines/red-book",2)],
  [("Raising Children Network","https://raisingchildren.net.au","org")]),
 (5,"Dermatological presentations","dermatological-presentations","Rashes, skin cancer, lesions, wounds, dermatitis, psoriasis, acne.",
  [("Cancer Council melanoma guidelines","https://www.cancer.org.au/clinical-guidelines",1),("eTG Dermatology","https://tg.org.au",2)],
  [("SunSmart","https://www.sunsmart.com.au","org")]),
 (6,"Disability care","disability-care","Patients with intellectual/physical disability, NDIS, communication, health checks, equity.",
  [("RACGP Disability care unit + resources","https://www.racgp.org.au/clinical-resources/clinical-guidelines",2)],
  [("NDIS","https://www.ndis.gov.au","org")]),
 (7,"Disaster health","disaster-health","Pandemics, emergencies, business continuity, public health orders, role of GP.",
  [("AHPPC / DoHAAC pandemic guidance","https://www.health.gov.au",3)],
  [("Australian Disaster Resilience Hub","https://knowledge.aidr.org.au","org")]),
 (8,"Doctors' health","doctors-health","Doctor wellbeing, burnout, impairment, mandatory notification, doctors' health services.",
  [("Doctors' Health Services (converge)","https://www.drs4drs.org.au",1)],
  [("Converge International EAP","https://www.convergeinternational.com.au","org")]),
 (9,"Ear, nose, throat and oral health","ear-nose-throat-and-oral-health","Otitis media, sinusitis, pharyngitis, epistaxis, hearing loss, oral lesions.",
  [("eTG Respiratory (ENT sections)","https://tg.org.au",2)],
  [("Hearing Australia","https://www.hearing.com.au","org")]),
 (10,"Education in general practice","education-in-general-practice","Teaching medical students/registrars, supervision, feedback, assessment.",
  [("RACGP education unit page","https://www.racgp.org.au/education",3)],[]),
 (11,"Emergency medicine","emergency-medicine","Anaphylaxis, sepsis, ACS, stroke, trauma, collapse, urgent transfer criteria.",
  [("eTG Emergency","https://tg.org.au",1)],
  [("ACEM first aid / basic life support","https://resuscitationcouncil.guidelines","org")]),
 (12,"Endocrine and metabolic health","metabolic-and-endocrine-health","Diabetes, thyroid, obesity, lipids, osteoporosis, adrenal, pituitary.",
  [("RACGP/Diabetes Australia T2DM guideline","https://www.racgp.org.au/clinical-resources/clinical-guidelines/key-racgp-guidelines/view-all-guidelines/type-2-diabetes",1),
   ("ADS position statements","https://www.diabetessociety.com.au",2)],
  [("Diabetes Australia","https://www.diabetesaustralia.com.au","org")]),
 (13,"Eye presentations","eye-presentations","Red eye, vision loss, trauma, diabetic retinopathy screening, glaucoma.",
  [("RANZCO / Optometry Australia guidance","https://www.ranzco.edu",2)],
  [("Vision 2020 Australia","https://www.vision2020australia.org.au","org")]),
 (14,"Gastrointestinal health","gastrointestinal-health","Dyspepsia, GORD, IBS, IBD, liver disease, coeliac, bowel cancer screening.",
  [("Australian MASLD consensus","https://www.gesa.org.au",2),("Cancer Council bowel screening","https://www.cancer.org.au",1)],
  [("GESA","https://www.gesa.org.au","org")]),
 (15,"Haematological presentations","haematological-presentations","Anaemia, anticoagulation, thrombosis, haematological malignancy recognition, LFTs and iron studies interpretation.",
  [("eTG Haematology","https://tg.org.au",2),("BloodSafe / NBA","https://www.blood.gov.au",3)],
  []),
 (16,"Infectious diseases","infectious-diseases","Antibiotic choice, notifiable diseases, immunisation, returned traveller, outbreak response.",
  [("Australian Immunisation Handbook","https://immunisationhandbook.health.gov.au/",1),("eTG Antibiotic","https://tg.org.au",1)],
  [("NCIRS","https://www.ncirs.org.au","org")]),
 (17,"Integrative medicine","integrative-medicine","Complementary medicine safety, interactions, evidence, patient communication.",
  [("NPS MedicineWise","https://www.nps.org.au",3)],[]),
 (18,"Justice system health","justice-system-health","Prisoners, forensic patients, legal system interface.",
  [("RACGP justice system unit","https://www.racgp.org.au",3)],[]),
 (19,"Kidney and urinary health","kidney-and-urinary-health","CKD, haematuria, proteinuria, UTI, stones, BPS, mens LUTS.",
  [("Kidney Health Australia CKD in primary care","https://kidney.org.au/health-professionals/chronic-kidney-disease-management-in-primary-care",1)],
  [("Kidney Health Australia","https://kidney.org.au","org")]),
 (20,"Men's health","mens-health","Prostate, testicular, ED, male mental health/suicide, preventive care for men.",
  [("Red Book (men's screening)","https://www.racgp.org.au/clinical-resources/clinical-guidelines/key-racgp-guidelines/view-all-guidelines/red-book",2)],
  [("Andrology Australia","https://www.healthymale.org.au","org")]),
 (21,"Mental health","mental-health","Depression, anxiety, bipolar, psychosis, suicide risk, perinatal mental health.",
  [("RACGP depression guideline / beyondblue guide","https://www.racgp.org.au/clinical-resources/clinical-guidelines/key-racgp-guidelines/view-all-guidelines/depression",1),
   ("LIFE framework (suicide prevention)","https://lifeinmindaustralia.com.au",2)],
  [("beyondblue","https://www.beyondblue.org.au","org"),("QLD Mental Health Line 1300 642 255","tel:1300642255","tel")]),
 (22,"Migrant, refugee and asylum seeker health","migrant-refugee-and-asylum-seeker-health","Arrival screening, interpreters, torture/trauma awareness, Medicare access.",
  [("ASID refugee health guidelines","https://www.asid.net.au",2)],
  [("Foundation House","https://www.foundationhouse.org.au","org")]),
 (23,"Military and veteran health","military-and-veteran-health","Veteran-specific conditions, DVA, PTSD, moral injury.",
  [("DVA health care arrangements","https://www.dva.gov.au",3)],
  [("Open Arms","https://www.openarms.gov.au","org")]),
 (24,"Musculoskeletal presentations","musculoskeletal-presentations","Back pain, joint pain, arthritis, osteoporosis, injuries, gout.",
  [("RACGP OA guideline","https://www.racgp.org.au/clinical-resources/clinical-guidelines/key-racgp-guidelines/view-all-guidelines/osteoarthritis",2),
   ("Healthy Bones Australia","https://healthybonesaustralia.org.au",2)],
  []),
 (25,"Neurological presentations","neurological-presentations","Headache, dizziness, stroke/TIA, epilepsy, dementia, Parkinson disease, neuropathy.",
  [("Stroke Foundation – Clinical Guidelines for Stroke Management","https://www.strokefoundation.org.au",1),("Austroads driving (seizure/dementia)","https://austroads.com.au/drivers-and-vehicles/driver-health/assessing-fitness-to-drive",2)],
  [("Stroke Foundation","https://www.strokefoundation.org.au","org")]),
 (26,"Occupational and environmental medicine","occupational-and-environmental-medicine","Work-related injury, certification, workers comp, Q fever/leptospirosis (QLD), environmental risks.",
  [("Safe Work Australia","https://www.safeworkaustralia.gov.au",3)],[]),
 (27,"Older persons' health","older-persons-health","Comprehensive geriatric assessment, polypharmacy, falls, cognition, RACF care, elder abuse.",
  [("RACGP Silver Book","https://www.racgp.org.au/clinical-resources/clinical-guidelines/key-racgp-guidelines/view-all-guidelines/silver-book",1),
   ("Austroads (dementia driving)","https://austroads.com.au/drivers-and-vehicles/driver-health/assessing-fitness-to-drive",2)],
  []),
 (28,"Pain management","pain-management","Acute vs persistent pain, opioids, non-drug strategies, pain programs.",
  [("eTG Analgesic","https://tg.org.au",1),("Faculty of Pain Medicine guidance","https://www.anzca.edu.au",3)],
  [("ACI pain management network","https://www.aci.health.nsw.gov.au","org")]),
 (29,"Palliative care","palliative-care","Symptom control, dying phase, ACP, VAD (QLD), carer support.",
  [("eTG Palliative Care","https://tg.org.au",1),("CareSearch","https://www.caresearch.com.au",2)],
  [("Palliative Care Australia","https://palliativecareaustralia.org.au","org")]),
 (30,"Pregnancy and reproductive health","pregnancy-and-reproductive-health","Antenatal care, first visit, pregnancy complications, postnatal care, lactation, contraception.",
  [("Dept Health Pregnancy Care Guidelines","https://www.health.gov.au/our-work/clinical-practice-guidelines-pregnancy-care",1),
   ("RANZCOG C-Gen","https://ranzcog.edu.au",2)],
  [("Quit for pregnancy (13QUIT)","https://www.quit.org.au","org")]),
 (31,"Research in general practice","research-in-general-practice","Critical appraisal, audit, research participation.",
  [("RACGP research unit","https://www.racgp.org.au",3)],[]),
 (32,"Respiratory health","respiratory-health","Asthma, COPD, cough, haemoptysis, sleep apnoea, lung cancer.",
  [("Australian Asthma Handbook","https://www.nationalasthma.org.au/australian-asthma-handbook/complete-handbook",1),
   ("COPD-X","https://copdx.org.au/copd-x-plan/",1)],
  [("Asthma Australia","https://asthma.org.au","org"),("Lung Foundation Australia","https://lungfoundation.com.au","org")]),
 (33,"Sexual health and gender diversity","sexual-health-and-gender-diversity","STI screening/treatment, PrEP/PEP, HIV, sexual function, gender diversity care.",
  [("Australian STI Management Guidelines","http://sti.guidelines.org.au/",1)],
  [("ASHM","https://ashm.org.au","org")]),
 (34,"Travel medicine","travel-medicine","Pre-travel risk assessment, vaccines, malaria prophylaxis, returned traveller.",
  [("CDC Yellow Book","https://wwwnc.cdc.gov/travel",2),("WHO travel health","https://www.who.int",3)],
  [("Travelvax","https://www.travelvax.com.au","org")]),
 (35,"Women's health","womens-health","Cervical screening, menopause, PCOS, heavy menstrual bleeding, breast symptoms, contraception.",
  [("NCSP guidelines","https://screening.cancer.org.au/cervical/",1),("Menopause resources (AMS)","https://www.menopause.org.au",2)],
  [("BreastScreen Australia","https://www.breastscreen.org.au","org")]),
]

units = []
uid = 0
for c in CORE:
    uid += 1
    units.append(dict(id=uid, type="core", number=c["number"], name=c["name"],
                      racgp_url=BASE+c["slug"], blurb=c["blurb"],
                      guidelines=c["guidelines"], materials=c["materials"]))
for num, name, slug, blurb, gls, mats in CTX:
    uid += 1
    units.append(dict(id=uid, type="contextual", number=num, name=name,
                      racgp_url=BASE+slug, blurb=blurb,
                      guidelines=[{"title":t,"url":u,"tier":tr} for t,u,tr in gls],
                      materials=[{"label":l,"url":u,"kind":k} for l,u,k in mats]))

# ---- Remap existing 56 topics to official units (by topic name) ----
# Current topic units -> official unit name mapping
OLD_TO_OFFICIAL = {
 # presentations.json topics
 "Chest pain":"Cardiovascular health","Tiredness / fatigue":"Applied professional knowledge and skills",
 "Headache":"Neurological presentations","Dizziness / vertigo":"Neurological presentations",
 "Abdominal pain":"Gastrointestinal health","Dyspnoea":"Respiratory health","Cough":"Respiratory health",
 "Weight loss":"Applied professional knowledge and skills","Fever in adults":"Infectious diseases",
 "Rash":"Dermatological presentations","Joint pain":"Musculoskeletal presentations","Back pain":"Musculoskeletal presentations",
 "Abnormal blood tests":"Applied professional knowledge and skills","Abnormal liver function tests":"Gastrointestinal health",
 "Anaemia":"Haematological presentations","Haematuria":"Kidney and urinary health","Child with fever":"Child and youth health",
 "Pregnancy-related presentations":"Pregnancy and reproductive health","Behavioural concern":"Mental health",
 "Screening consultation":"Population health and the context of general practice",
 # systems.json topics
 "Hypertension":"Cardiovascular health","Ischaemic heart disease and ACS":"Cardiovascular health",
 "Atrial fibrillation":"Cardiovascular health","Heart failure":"Cardiovascular health","Asthma":"Respiratory health",
 "COPD":"Respiratory health","Type 2 diabetes":"Endocrine and metabolic health","Thyroid disease":"Endocrine and metabolic health",
 "Chronic kidney disease":"Kidney and urinary health","Osteoporosis":"Musculoskeletal presentations",
 "Depression and anxiety":"Mental health","Suicide risk assessment":"Mental health","Contraception":"Women's health",
 "Menopause and perimenopause":"Women's health","Skin cancer":"Dermatological presentations",
 "Antimicrobial stewardship and common infections":"Infectious diseases","Immunisation":"Infectious diseases",
 "HIV and sexual health":"Sexual health and gender diversity","Anticoagulation":"Haematological presentations",
 "Stroke and TIA":"Neurological presentations","Headache: migraine":"Neurological presentations",
 "Inflammatory bowel disease and functional GI":"Gastrointestinal health","Liver disease":"Gastrointestinal health",
 "Coeliac disease":"Gastrointestinal health","Obesity":"Endocrine and metabolic health","Lipids":"Cardiovascular health",
 "Prostate and mens health screening":"Men's health","Ophthalmology in general practice":"Eye presentations",
 "ENT and oral health":"Ear, nose, throat and oral health","Child development and behavioural problems":"Child and youth health",
 "Common paediatric conditions":"Child and youth health","Older persons comprehensive care":"Older persons' health",
 "Palliative care":"Palliative care","Alcohol and other drugs":"Addiction medicine",
 "Family and domestic violence":"Abuse and violence","Aboriginal and Torres Strait Islander health":"Aboriginal and Torres Strait Islander health",
}

topics = []
for f in ("presentations.json","systems.json"):
    for t in json.loads((D/f).read_text(encoding="utf-8")):
        topics.append(dict(t))
mapped = 0; unmapped = []
for t in topics:
    official = OLD_TO_OFFICIAL.get(t["name"])
    if official is None:
        unmapped.append(t["name"]); continue
    t["unit"] = official; mapped += 1

print(f"topics mapped: {mapped}/{len(topics)}; unmapped: {unmapped}")
unit_names = [u["name"] for u in units]
bad = [t["name"] for t in topics if t["unit"] not in unit_names]
print("topics pointing at non-existent units:", bad)

# Write outputs
out = {"units": units, "topics": topics}
(D / "curriculum_v2.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
print("wrote curriculum_v2.json with", len(units), "units and", len(topics), "topics")
