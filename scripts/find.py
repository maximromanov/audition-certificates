import pickle,sys,os
sys.path.insert(0,os.path.dirname(__file__)); from arname import norm
b=pickle.load(open(sys.argv[1],'rb'))
for q in sys.argv[2:]:
    terms,_,rng=q.partition('@'); lo,hi=(int(x) for x in rng.split('-')) if rng else (0,800)
    ts=[norm(t) for t in terms.split('+')]
    hits=[x for x in b if all(t in x['nname'] for t in ts) and lo<=x['d1']<=hi]
    print('##',q,len(hits))
    for x in hits[:5]: print('  ',x['cid'][24:],x['d1'],x['cat'],x['name'][:120])
