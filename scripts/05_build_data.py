"""Assemble site/data.js: certificates, persons with reviewed matches and alternatives, and the biographies they point to."""
import json,os,sys,pickle,re
CERTS,BIOS,SITE=sys.argv[1:4]
bios=pickle.load(open(BIOS,'rb')); texts=pickle.load(open(BIOS.replace('.pkl','_texts.pkl'),'rb'))
B={b['cid']:b for b in bios}
ids=json.load(open(os.path.join(SITE,'data','sample_ids.json')))
cands={r['guid']:r for r in json.load(open(os.path.join(SITE,'data','candidates.json')))}
exp=json.load(open(os.path.join(SITE,'data','expansions.json'))); expn=json.load(open(os.path.join(SITE,'data','expansion_notes.json')))
dec={}
for l in open(os.path.join(os.path.dirname(__file__),'review_decisions.tsv')):
    if l.startswith('#') or not l.strip(): continue
    g,uid,conf,note=l.rstrip('\n').split('\t'); dec[g]=dict(uid=None if uid=='-' else uid,conf=conf,note=note)
PFX='0748Dhahabi.TarikhIslam.'
need=set(); out=[]
def first(v): return (v or [''])[0] if isinstance(v,list) else (v or '')
for cid in ids:
    d=json.load(open(os.path.join(CERTS,cid+'.json'))); m=d['metadata']
    anns=[]; persons=[]
    for p in sorted(d['properties'],key=lambda p:p['startIndex']):
        a=p.get('attributes',{})
        A=dict(id=p['guid'],type=p['type'],s=p['startIndex'],e=p['endIndex']+1)  # ACP endIndex is inclusive
        assert d['text'][A['s']:A['e']]==p['text'], (cid,p['guid'])
        if p['type']=='person':
            g=p['guid']; r=cands.get(g,{}); dd=dec.get(g[:8])
            cl=[dict(uid=c['cid'][len(PFX):],score=c['score']) for c in r.get('cands',[])[:6] if c['score']>=4]
            if dd and dd['uid'] and dd['uid'] not in [c['uid'] for c in cl]: cl.insert(0,dict(uid=dd['uid'],score=None))
            for c in cl: need.add(c['uid'])
            persons.append(dict(id=g,text=p['text'].strip(),roles=a.get('role') or [],expanded=exp.get(g),expNote=expn.get(g),
                proposal=(dict(uid=dd['uid'],conf=dd['conf'],note=dd['note']) if dd else None),cands=cl))
        elif p['type']=='place': A['loc']=a.get('location')
        elif p['type']=='date': A['date']=[first(a.get('year')),first(a.get('month')),first(a.get('day'))]
        anns.append(A)
    years=[int(x['date'][0]) for x in anns if x['type']=='date' and str(x['date'][0]).isdigit()]
    o=m['object']
    out.append(dict(id=cid,library=first(o.get('library')).strip(),classmark=first(o.get('classmark')).strip(),folio=first(o.get('folio_number')).strip(),
        link=first(o.get('manuscript_link')) or first(o.get('link_to_manuscript')) or '',
        work=first(m['context'].get('work_title')).strip(),author=first(m['context'].get('author_name')).strip(),
        type=m['characteristics'].get('type') or [],year=min(years) if years else None,text=d['text'],anns=anns,persons=persons))
bio={}
for uid in sorted(need):
    b=B[PFX+uid]
    bio[uid]=dict(name=b['name'],d=[b['d0'],b['d1']],cat=b['cat'],h1=re.sub(r'\s*(Beg|End)?V\d+P\d+.*','',b['h1']).strip(' -'),text=texts[PFX+uid])
DATA=dict(generated='2026-10-08',uriPrefix=PFX,certs=out,bios=bio)
open(os.path.join(SITE,'data.js'),'w').write('window.ACP_DATA='+json.dumps(DATA,ensure_ascii=False)+';\n')
# flat table of proposals for inspection outside the interface
import csv,shutil
with open(os.path.join(SITE,'data','proposals.csv'),'w',newline='',encoding='utf-8') as fh:
    w=csv.writer(fh); w.writerow(['certificate_id','session_year_ah','person_guid','person_name','resolved_name','roles','ti_uri','ti_name','ti_death_ah','confidence','justification'])
    for c in out:
        for p in c['persons']:
            pr=p['proposal']
            if not pr: continue
            b=bio.get(pr['uid']) if pr['uid'] else None
            w.writerow([c['id'],c['year'],p['id'],p['text'],p['expanded'] or '','|'.join(p['roles']),PFX+pr['uid'] if pr['uid'] else '',b['name'] if b else '',b['d'][1] if b else '',pr['conf'],pr['note']])
for f in ('review_decisions.tsv','expansions_raw.tsv'):
    shutil.copy(os.path.join(os.path.dirname(__file__),f),os.path.join(SITE,'data',f))
np=sum(len(c['persons']) for c in out)
print(len(out),'certs',np,'persons',len(bio),'bios', round(os.path.getsize(os.path.join(SITE,'data.js'))/1e6,2),'MB')
print('proposals:',sum(1 for c in out for p in c['persons'] if p['proposal'] and p['proposal']['uid']))
