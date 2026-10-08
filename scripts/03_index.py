import json,glob,os,re,sys,pickle
sys.path.insert(0,os.path.dirname(__file__)); from arname import parse,norm
D=sys.argv[1]; out=[]; texts={}
DRE=re.compile(r'\[\s*الوفاة\s*:\s*([0-9]+)(?:\s*-\s*([0-9]+))?')
for f in sorted(glob.glob(os.path.join(D,'*.json'))):
    for r in json.load(open(f)):
        y=r['yml']; cat=y.get('category','')
        if not cat.startswith('$BIO'): continue
        t=r['text']; m=DRE.search(t)
        if m:
            namepart=t[:m.start()]; d0=int(m.group(1)); d1=int(m.group(2) or m.group(1))
        else:
            namepart=re.split(r'[.:]',t,1)[0][:200]; d0=y.get('min_date'); d1=y.get('max_date')
        if d1 is None: continue
        P=parse(namepart.replace('،',' '))
        o=y.get('onomastics') or {}
        if not P['ism'] and o.get('ism'): P['ism']=norm(o['ism'][0])
        P['kunya']|={norm(k).replace('ابي ','ابو ') for k in o.get('kun',[])}
        P['laqab']|={norm(k) for k in o.get('lqb',[])}
        P['nisba']|={norm(k) for k in o.get('nsb',[])}
        P['shuhra']={norm(k) for k in o.get('shr',[])}
        nm=norm(namepart)
        texts[r['CID']]=t
        out.append(dict(cid=r['CID'],cat=cat,d0=d0,d1=d1,name=namepart.strip(' ،.'),nname=nm,p=P,h1=y.get('headings',{}).get('h1',''),ntok=y.get('number_of_tokens')))
pickle.dump(out,open(sys.argv[2],'wb')); pickle.dump(texts,open(sys.argv[2].replace('.pkl','_texts.pkl'),'wb'))
print(len(out), sum(1 for b in out if not b['p']['ism']), sum(1 for b in out if b['d1']<=700))
