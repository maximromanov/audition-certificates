"""Turn scripts/expansions_raw.tsv (guid prefix -> expanded name, note) into site/data/expansions*.json keyed by full GUID."""
import json,os,sys
CERTS,IDS,OUTDIR=sys.argv[1:4]
guids=[]
for i in json.load(open(IDS)):
    d=json.load(open(os.path.join(CERTS,i+'.json')))
    guids+=[p['guid'] for p in d['properties'] if p['type']=='person']
E={};N={}
for line in open(os.path.join(os.path.dirname(__file__),'expansions_raw.tsv'),encoding='utf-8'):
    if line.startswith('#') or not line.strip(): continue
    g,name,note=line.rstrip('\n').split('\t')
    m=[x for x in guids if x.startswith(g)]; assert len(m)==1,(g,m)
    E[m[0]]=name; N[m[0]]=note
json.dump(E,open(os.path.join(OUTDIR,'expansions.json'),'w'),ensure_ascii=False,indent=1)
json.dump(N,open(os.path.join(OUTDIR,'expansion_notes.json'),'w'),ensure_ascii=False,indent=1)
print(len(E),'expansions')
