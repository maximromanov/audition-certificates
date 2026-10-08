import json,random,sys,collections
rows=json.load(open(sys.argv[1]))
random.seed(748)
pool=[r for r in rows if 10<=r['n']<=45]
buckets=[(550,600,4),(600,625,5),(625,650,6),(650,675,6),(675,701,4)]
sel=[];venues=collections.Counter();works=set()
for lo,hi,k in buckets:
    c=[r for r in pool if lo<=r['year']<hi]; random.shuffle(c)
    got=0
    for r in c:
        if got>=k: break
        if r['work'] in works or venues[r['venue']]>=7: continue
        sel.append(r);works.add(r['work']);venues[r['venue']]+=1;got+=1
sel.sort(key=lambda r:r['year'])
json.dump([r['id'] for r in sel],open(sys.argv[2],'w'),indent=1)
for r in sel: print(r['year'],r['n'],r['venue'][:22].ljust(22),r['work'][:40],'|',r['id'][27:])
print(len(sel),sum(r['n'] for r in sel),venues)
