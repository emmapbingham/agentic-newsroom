#!/usr/bin/env python3
"""Build the tariff-stance activity table + split summary from the LLM classification.

Reads: db/gain.db, derived/final_map.json (desc_norm -> final label/confidence/source).
Writes: derived/tariff_stance_activities.csv  (one row per Senate TAR activity w/ stance + cohort + canonical flag)
        derived/stance_summary.json           (the splits)
Reference tier: labels are LLM-produced (Haiku+Sonnet, Opus-adjudicated); filter by confidence.
"""
import json, sqlite3, csv, collections, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # case dir
D = os.path.join(ROOT, 'derived')
DB = os.path.join(ROOT, '..', '..', 'db', 'gain.db')

fm = json.load(open(os.path.join(D, 'final_map.json')))
norm2final = {v['desc_norm']: {'label': v['label'], 'confidence': v['confidence'], 'source': v['source']}
              for v in fm.values()}

con = sqlite3.connect(DB)
acts = con.execute("""
 SELECT a.activity_id, a.description, f.filing_uuid, f.registrant_id, f.client_id,
        f.filing_year, f.filing_period, f.dt_posted
 FROM senate_lobbying_activities a JOIN senate_filings f ON f.filing_uuid=a.filing_uuid
 WHERE a.general_issue_code='TAR' AND a.description IS NOT NULL AND LENGTH(TRIM(a.description))>=3
""").fetchall()
first_tar = {r[0]: r[1] for r in con.execute(
    "SELECT registrant_id,MIN(filing_year) FROM derived_registrant_issue_panel WHERE issue_code='TAR' GROUP BY 1")}
trd_pre25 = set(r[0] for r in con.execute(
    "SELECT DISTINCT registrant_id FROM derived_registrant_issue_panel WHERE issue_code='TRD' AND filing_year<2025"))

def cohort(rid):
    fy = first_tar.get(rid)
    if fy is None: return 'unknown'
    if fy < 2025: return 'established'
    if fy == 2025: return 'new2025_incumbent' if rid in trd_pre25 else 'new2025_genuine'
    return 'entrant2026'

rows = []
for aid, desc, uuid, rid, cid, fy, fp, dt in acts:
    fin = norm2final.get((desc or '').strip().lower())
    if not fin: continue
    rows.append(dict(activity_id=aid, filing_uuid=uuid, registrant_id=rid, client_id=cid,
                     filing_year=fy, filing_period=fp, dt_posted=dt or '',
                     stance_label=fin['label'], stance_confidence=fin['confidence'],
                     source=fin['source'], cohort=cohort(rid)))
# canonical = latest dt_posted per (registrant,client,year,period) — dedup amendments/re-files
best = {}
for r in rows:
    k = (r['registrant_id'], r['client_id'], r['filing_year'], r['filing_period'])
    best[k] = max(best.get(k, ''), r['dt_posted'])
for r in rows:
    k = (r['registrant_id'], r['client_id'], r['filing_year'], r['filing_period'])
    r['is_canonical'] = int(r['dt_posted'] == best[k])

with open(os.path.join(D, 'tariff_stance_activities.csv'), 'w', newline='') as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)

def directional(items, minconf=0.0):
    f = [r for r in items if r['stance_confidence'] >= minconf]
    dirn = [r for r in f if r['stance_label'] in ('relief', 'protection', 'mixed')]
    n = len(dirn); c = collections.Counter(r['stance_label'] for r in dirn)
    return {'n_directional': n, 'n_total_kept': len(f),
            'relief': c.get('relief', 0), 'protection': c.get('protection', 0), 'mixed': c.get('mixed', 0),
            'relief_pct': round(c.get('relief', 0)/n, 3) if n else None,
            'protection_pct': round(c.get('protection', 0)/n, 3) if n else None}

canon = [r for r in rows if r['is_canonical']]
summary = {'n_activities_raw': len(rows), 'n_activities_canonical': len(canon),
           'full_dist_canonical_all_years': dict(collections.Counter(r['stance_label'] for r in canon))}
for yr, key in [(None, 'all_years'), (2025, 'y2025')]:
    sel = [r for r in canon if (yr is None or r['filing_year'] == yr)]
    summary[f'split_{key}_allconf'] = directional(sel, 0.0)
    summary[f'split_{key}_conf80'] = directional(sel, 0.8)
s25 = [r for r in canon if r['filing_year'] == 2025]
summary['cohort_2025'] = {}
for coh in ['new2025_genuine', 'new2025_incumbent', 'established']:
    sel = [r for r in s25 if r['cohort'] == coh]
    full = collections.Counter(r['stance_label'] for r in sel)
    summary['cohort_2025'][coh] = {'n_canonical': len(sel), 'directional': directional(sel, 0.0),
                                   'unclear': full.get('unclear', 0), 'monitoring': full.get('monitoring', 0)}
json.dump(summary, open(os.path.join(D, 'stance_summary.json'), 'w'), indent=1)
print(json.dumps(summary, indent=1))
