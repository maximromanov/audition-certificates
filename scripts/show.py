import json,sys
R=json.load(open(sys.argv[1])); ids=json.load(open(sys.argv[2])); lo,hi=int(sys.argv[3]),int(sys.argv[4])
for n,cid in enumerate(ids[lo:hi],lo):
    print(f'######## C{n} {cid[27:]}')
    for r in [r for r in R if r['cert']==cid]:
        if not r["cands"] or r["cands"][0]["score"]<5: continue
        top=r['cands'][0]['score']
        print(f"-- {r['guid'][:8]} {r['year']} {','.join(r['roles'])} | {r['expanded'] or r['text']}")
        for c in [c for c in r["cands"] if c["score"]>=5][:3]:
            if c['score']<top-2.5: break
            print(f"   [{c['score']}] d.{c['d'][1]} {c['cid'][24:]} {c['name'][:110]} {' '.join(w for w in c['why'] if not w.startswith(('ism','nasab')))}")
            print(f"        {c['snip'][:120]}")
