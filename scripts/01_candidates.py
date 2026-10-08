import json,glob,os,sys,collections
D=sys.argv[1]
rows=[]
for f in sorted(glob.glob(os.path.join(D,'*.json'))):
    d=json.load(open(f))
    P=d.get('properties',[])
    locs=[l for p in P if p['type']=='place' for l in p['attributes'].get('location',[])]
    if not any('damascus' in str(l) for l in locs): continue
    if any('damascus' not in str(l) for l in locs): continue  # only-Damascus sessions
    ys=[]
    for p in P:
        if p['type']=='date':
            try: ys.append(int(p['attributes']['year'][0]))
            except: pass
    if not ys: continue
    y=min(ys)
    if not (550<=y<=700): continue
    pers=[p for p in P if p['type']=='person']
    roles=collections.Counter(r for p in pers for r in (p['attributes'].get('role') or []))
    venue='/'.join(locs[0][2:]) if len(locs[0])>2 else ''
    m=d['metadata']
    rows.append(dict(id=os.path.basename(f)[:-5],year=y,n=len(pers),venue=venue,work=(m['context'].get('work_title') or [''])[0].strip(),
        author=(m['context'].get('author_name') or [''])[0], roles=dict(roles), status=(m['edit'].get('status') or [''])[0]))
json.dump(rows,open(sys.argv[2],'w'),ensure_ascii=False,indent=0)
print(len(rows))
import statistics
print(collections.Counter(r['status'] for r in rows)); print(statistics.quantiles([r['n'] for r in rows],n=10))
print(collections.Counter(r['venue'] for r in rows).most_common(12))
