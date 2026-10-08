import json,os,sys,pickle,collections,re
sys.path.insert(0,os.path.dirname(__file__)); from arname import parse,norm
from arnum import birth_year
CERTS,BIOS,IDS,OUT=sys.argv[1:5]
bios=pickle.load(open(BIOS,'rb')); texts=pickle.load(open(BIOS.replace('.pkl','_texts.pkl'),'rb'))
_nt={}
def ntext(cid):
    if cid not in _nt: _nt[cid]=norm(texts[cid])
    return _nt[cid]
ISMS=collections.Counter(b['p']['ism'] for b in bios)
TOP=set(k for k,_ in ISMS.most_common(300))
EXPAND=json.load(open(sys.argv[5])) if len(sys.argv)>5 and os.path.exists(sys.argv[5]) else {}
by_ism=collections.defaultdict(list); by_tok=collections.defaultdict(list)
for i,b in enumerate(bios):
    if b['p']['ism']: by_ism[b['p']['ism']].append(i)
    for w in set(b['nname'].split()): by_tok[w].append(i)
COMMON_NISBA={'الدمشقي','الشافعي','الحنبلي','الحنفي','المالكي','المصري','البغدادي','الانصاري','القرشي','العلامه','المحدث','الصالحي'}
def score(c,b,year,sanad,tkeys):
    P=b['p']; s=0; why=[]
    # date window
    if sanad:
        if not (year-160 <= b['d1'] and b['d0'] <= year): return None
    else:
        if b['d1'] < year or b['d0'] > year+95: return None
    if c['female'] != (b['cat']=='$BIO_WOM$') and b['cat'] in('$BIO_WOM$','$BIO_MAN$'): return None
    if c['ism']:
        if c['ism']!=P['ism']: return None
        s+=2; why.append('ism')
    # nasab alignment
    bn=P['nasab']; mism=0
    for k,a in enumerate(c['nasab']):
        w=[3,2,1.5,1,1][min(k,4)]
        if k<len(bn) and bn[k]==a: s+=w; why.append(f'nasab{k+1}')
        elif a in P['ibn'] or a in P['shuhra'] or ('ابن '+a) in b['nname'] or a in bn: s+=w*0.6; why.append(f'~{a}')
        elif k<len(bn): s-=3*(1 if k==0 else 0.6); mism+=1
    if c['nasab'] and not bn: s-=0.5
    for x in c['laqab']:
        if x in P['laqab'] or x in b['nname']: s+=2; why.append('laqab')
        elif P['laqab']: s-=1.5
    for x in c['kunya']:
        if x in P['kunya'] or x in b['nname']: s+=1.5; why.append('kunya')
        elif P['kunya']: s-=1.5
    for x in c['nisba']:
        if x in P['nisba'] or x in b['nname']: s+=0.5 if x in COMMON_NISBA else 1.5; why.append('nisba')
    if not c['ism']:
        if len(why)<2:
            if not(len(c['nasab'])==1 and not c['kunya'] and not c['laqab'] and ('ابن '+c['nasab'][0]) in b['nname']): return None
            s+=3; why.append('shuhra')
    # mention of the musmi' in the biography (teacher overlap)
    if tkeys and s>=2:
        T=ntext(b['cid'])
        hit=[k for k in tkeys if k in T]
        if hit: s+=2; why.append('teacher:'+hit[0])
    if b['cat']=='$BIO_REP$': s-=0.5
    by=birth_year(ntext(b['cid'])) if s>=3 else None
    if by and not sanad and by>year: return None
    if by: why.append(f'b.{by}')
    return s,why
def cands_for(c):
    if c['ism']: return by_ism.get(c['ism'],[])
    keys=[k for k in list(c['laqab'])+list(c['kunya'])+list(c['nisba'])+c['nasab']]
    pool=set()
    for k in keys:
        L=by_tok.get(k.split()[-1],[])
        if len(L)<5000: pool|=set(L)
    return pool
res=[]
for cid in json.load(open(IDS)):
    d=json.load(open(os.path.join(CERTS,cid+'.json')))
    years=[int(p['attributes']['year'][0]) for p in d['properties'] if p['type']=='date' and (p['attributes'].get('year') or [''])[0].isdigit()]
    year=min(years)
    persons=sorted([p for p in d['properties'] if p['type']=='person'],key=lambda p:p['startIndex'])
    tkeys=set()
    for p in persons:
        if 'musmi' in (p['attributes'].get('role') or []):
            m=parse(EXPAND.get(p['guid'],p['text']))
            if m['ism'] and m['nasab']: tkeys.add(m['ism']+' بن '+m['nasab'][0])
            tkeys|={'ابن '+x for x in m['nasab'] if x not in TOP}
            tkeys|={x for x in m['laqab']}&set() 
    for p in persons:
        roles=p['attributes'].get('role') or []
        src=EXPAND.get(p['guid'],p['text'])
        if src.strip().startswith('و') and not EXPAND.get(p['guid']):
            w=norm(src).split()[0]
            if ISMS.get(w,0)<ISMS.get(w[1:],0): src=src.strip()[1:]
        c=parse(src); sanad='sanad_al_musmi' in roles
        tk=set() if 'musmi' in roles else tkeys
        sc=[]
        for i in cands_for(c):
            r=score(c,bios[i],year,sanad,tk)
            if r and r[0]>=4: sc.append((round(r[0],2),r[1],i))
        sc.sort(key=lambda x:-x[0])
        res.append(dict(cert=cid,year=year,guid=p['guid'],text=p['text'].strip(),expanded=EXPAND.get(p['guid']),roles=roles,parsed={k:(sorted(v) if isinstance(v,set) else v) for k,v in c.items()},
            n_cands=len(sc),cands=[dict(cid=bios[i]['cid'],score=s,why=w,d=[bios[i]['d0'],bios[i]['d1']],name=bios[i]['name'][:150],cat=bios[i]['cat'],snip=texts[bios[i]['cid']][len(bios[i]['name']):][:260]) for s,w,i in sc[:6]]))
json.dump(res,open(OUT,'w'),ensure_ascii=False,indent=1)
print(len(res),'mentions;',sum(1 for r in res if r['cands']),'with candidates;',sum(1 for r in res if r['cands'] and r['cands'][0]['score']>=8),'top>=8')
