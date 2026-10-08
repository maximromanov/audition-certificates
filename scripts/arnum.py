import re
U={'احدي':1,'احد':1,'واحد':1,'اثنتين':2,'اثنين':2,'اثنتي':2,'ثنتين':2,'ثلاث':3,'ثلث':3,'اربع':4,'خمس':5,'ست':6,'سبع':7,'ثمان':8,'ثماني':8,'تسع':9,'عشر':10}
T={'عشرين':20,'ثلاثين':30,'ثلثين':30,'اربعين':40,'خمسين':50,'ستين':60,'سبعين':70,'ثمانين':80,'تسعين':90}
H={'مايه':100,'مايتين':200,'مئتين':200,'ثلاثمايه':300,'ثلثمايه':300,'اربعمايه':400,'خمسمايه':500,'ستمايه':600,'سبعمايه':700,'ماييه':100,'ميه':100,'مئه':100,'ستميه':600,'ستمئه':600,'خمسميه':500,'خمسمئه':500,'اربعمئه':400,'سبعمئه':700}
def words_to_year(ws):
    tot=0; i=0; seen=False
    while i<len(ws):
        w=ws[i]
        if w.startswith('و') and w[1:] and (w[1:] in U or w[1:] in T or w[1:] in H or w[1:] in('مايه','ستمايه')): w=w[1:]
        if w in H: tot+=H[w]; seen=True
        elif w in U and i+1<len(ws) and ws[i+1] in('مايه','ميه','مئه','ماييه'): tot+=U[w]*100; i+=1; seen=True
        elif w in U and i+1<len(ws) and ws[i+1]=='عشره': tot+=U[w]+10; i+=1; seen=True
        elif w in U: tot+=U[w]; seen=True
        elif w in T: tot+=T[w]; seen=True
        elif w in ('عشره',): tot+=10; seen=True
        else: break
        i+=1
    return tot if seen and 300<tot<800 else None
def birth_year(ntext):
    m=re.search(r'(?:مولده|ولد|مولدها|ولدت)(?:[^.]{0,40}?)سنه ((?:\S+ ?){1,6})',ntext)
    if not m: return None
    ws=m.group(1).split()
    if ws and ws[0].isdigit(): return int(ws[0])
    return words_to_year(ws)
