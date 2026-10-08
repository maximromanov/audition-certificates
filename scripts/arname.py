"""Arabic name normalisation and parsing shared by index builder and matcher."""
import re
DIAC=re.compile(r'[ؗ-ًؚ-ْٰـ]')
TITLES=set('''الشيخ الإمام الامام العالم الحافظ الفقيه الأجل الاجل الصدر الرئيس الكبير الأوحد الاوحد العلامة المحدث الزاهد العابد الصالح
القاضي الخطيب المقرئ المقرىء الأمير الامير الحاج الأستاذ الاستاذ السيد الشريف الثقة المسند الأصيل الاصيل الفاضل الورع الأديب الاديب
الجليل الشهيد الأخ الاخ والده ولده ابنه وابنه ابناه وابناه أخوه واخوه وأخوه السادة الأشياخ الاشياخ الشيوخ العدل الكاتب المفيد المحصل
الحاجب الطواشي الأمين الامين المكرم المحترم الأجلاء الاجلاء والشيخ والفقيه والإمام والقاضي والأمير والحاج والأجل والصدر
مولانا سيدنا شيخنا شيخ الشيخة الحرة الست الفقيهة الصالحة العالمة المسندة الأصيلة السابق الفتى الصبي الطفل حاضرا حاضر فتاه مولاه عتيقه'''.split())
DEFECTIVE={'اسحق':'اسحاق','اسمعيل':'اسماعيل','سليمن':'سليمان','الحرث':'الحارث','ابرهيم':'ابراهيم','عثمن':'عثمان','مروان':'مروان','هرون':'هارون','لقمن':'لقمان','عمار':'عمار','ثلثين':'ثلاثين','الرحمن':'الرحمن','سلمن':'سلمان','معوية':'معاويه','معويه':'معاويه'}
def norm(s):
    s=DIAC.sub('',s or '')
    s=re.sub('[أإآٱ]','ا',s).replace('ى','ي').replace('ة','ه').replace('ؤ','و').replace('ئ','ي')
    s=re.sub(r'\[[^\]]*\]',' ',s)
    s=re.sub(r'[^ء-ي ]',' ',s)
    s=re.sub(r'\s+',' ',s).strip()
    s=' '.join(DEFECTIVE.get(w,w) for w in s.split())
    return s
NTITLES={norm(t) for t in TITLES}
KUNYA={'ابو','ابي','ابا','ام'}
AL_ISM=set(norm(x) for x in '''الحسن الحسين القاسم الفضل المبارك المؤيد المظفر المفضل العباس الخضر الربيع الوليد الهيثم المنذر الحارث النعمان الليث المطهر
المعافى المعلى المنجا الموفق الحجاج السري الصلت الأشعث المهلب المسيب المغيرة المحسن الطاهر المسلم المحسن المنتصر الأعز الأسعد الأغر الفتح المختار
الأزهر الحكم المعمر المنتجب المرجى المهذب الأمين الرشيد الخليل اليسع البركات المكرم المسلم'''.split())
def is_nisba(w):
    return w.startswith('ال') and len(w)>3 and w not in AL_ISM
COMPOUND_FIRST={'عبد','ابو','ابي','ابا','ام'}
def tokens(s):
    t=norm(s).split()
    # strip leading conjunction و on first token of name parts (e.g. وعبد) – only if remainder is plausible
    out=[]
    for w in t:
        if w in ('بابن','لابن','وابن','فابن'): w='ابن'
        if w in NTITLES or w in ('المعروف','عرف','يعرف','ويعرف','ثم','وهو','الشهير','المدعو'): continue
        out.append(w)
    return out
def join_compounds(t):
    out=[];i=0
    while i<len(t):
        w=t[i]
        if w in ('عبد','ابو','ابي','ابا','ام') and i+1<len(t) and t[i+1] not in ('بن','ابن','بنت'):
            nxt=t[i+1]
            if w in('ابو','ابي','ابا','ام') and nxt=='عبد' and i+2<len(t):
                out.append(('ابو' if w!='ام' else 'ام')+' عبد '+t[i+2]); i+=3; continue
            out.append(('ابو' if w in('ابي','ابا') else w)+' '+nxt); i+=2; continue
        if i+1<len(t) and t[i+1]=='الله':
            out.append(w+' الله'); i+=2; continue
        if i+1<len(t) and t[i+1] in ('الدين','الدوله','الاسلام','الملك','القضاه','الزمان','الحرمين','الرؤساء','الرءوس'):
            out.append(w+' '+t[i+1]); i+=2; continue
        out.append(w); i+=1
    return out
def parse(s):
    """Return dict(ism, nasab[list], kunya[set], laqab[set], nisba[set], ibn[set]: 'ابن X' shuhra tokens)."""
    t=join_compounds(tokens(s))
    # split into chain segments on بن/ابن/بنت
    segs=[[]]; links=[]
    for w in t:
        if w in('بن','ابن','بنت'):
            segs.append([]); links.append(w)
        else: segs[-1].append(w)
    R=dict(ism=None,nasab=[],kunya=set(),laqab=set(),nisba=set(),ibn=set(),female=('بنت' in links))
    def classify(seg, is_first):
        names=[]
        for w in seg:
            if w.startswith(('ابو ','ام ')): R['kunya'].add(w); 
            elif ' ' in w and w.split()[1] in ('الدين','الدوله','الاسلام','الملك','القضاه','الزمان','الحرمين'): R['laqab'].add(w)
            elif is_nisba(w) and not (is_first and not names and w in AL_ISM): R['nisba'].add(w)
            elif w.startswith('وال') and len(w)>4: R['nisba'].add(w[1:])
            else: names.append(w)
        return names
    first=classify(segs[0],True)
    if first: R['ism']=first[-1]
    for k,seg in enumerate(segs[1:]):
        # a kunya inside a nasab segment ("ابن ابي عمر محمد") -> the kunya names the ancestor
        names=[]; kun=None
        for w in seg:
            if w.startswith(('ابو ','ام ')) and kun is None and not names: kun=w
            elif ' ' in w and w.split()[1] in ('الدين','الدوله','الاسلام','الملك','القضاه','الزمان','الحرمين'): pass
            elif is_nisba(w) and (names or kun): R['nisba'].add(w)
            else: names.append(w)
        anc = names[0] if names else kun
        if anc is None: continue
        R['nasab'].append(anc)
        R['ibn'].add(anc)  # any ancestor can serve as 'ابن X' shuhra
        if kun and names: R['ibn'].add(kun)
    return R
