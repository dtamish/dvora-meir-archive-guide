#!/usr/bin/env python
from pathlib import Path
import argparse,json,collections,re
ap=argparse.ArgumentParser();ap.add_argument('--research',required=True);a=ap.parse_args()
research=json.loads(Path(a.research).read_text(encoding='utf-8'))
required=['title','url','source','rightsOwner','mediaType','mediaGroup','period','category','description','editorialUse','rightsStatus','rightsGroup','verificationNote','nextAction']
public=[]
video_n=0
still_n=0
for n,raw in enumerate(research['items'],1):
    missing=[k for k in required if not str(raw.get(k,'')).strip()]
    if missing: raise SystemExit(f'item {n} missing {missing}')
    x=dict(raw);x['sourceUrl']=x.pop('url');x['driveUrl']='';x['section']=x.pop('category');x.setdefault('subcategory','');x.setdefault('relevanceType','context');x['assetCount']=1
    x['mediaGroup']='video' if 'youtube.com/' in x['sourceUrl'] or 'youtu.be/' in x['sourceUrl'] else 'stills'
    if x['mediaGroup']=='video':
        video_n+=1;x['id']=f'DM-V{video_n:03d}'
    else:
        still_n+=1;x['id']=f'DM-C{still_n:03d}'
    x['rightsGroup']='open' if 'commons.wikimedia.org/' in x['sourceUrl'] else 'permission'
    public.append(x)
# Stable family album request cards; these are not claims that assets exist.
family=[]
for n,b in enumerate(research.get('familyAlbumBlueprints',[]),1):
    family.append({'id':f'DM-F{n:03d}','section':'family_requests','period':'משפחה · נדרש איסוף','title':b['title'],'mediaType':'אלבום תמונות מבוקש','mediaGroup':'stills','assetCount':0,'description':b['description'],'editorialUse':b['editorialUse'],'relevanceType':'character','verificationNote':'Blueprint בלבד: האלבום או התמונות עדיין לא נמסרו ולא נבדקו.','subcategory':b.get('subcategory','אלבום משפחתי'),'source':'משפחת דבורה ומאיר — טרם נמסר','rightsOwner':'המשפחה / הצלם המקורי','date':'לא ידוע','rightsStatus':'משפחתי · נדרש אישור וזיהוי','rightsGroup':'family','nextAction':'לבקש: '+', '.join(b.get('requestedMaterials',[]))+'; '+b.get('safetyNote','לאסוף זיהוי, תאריך וקרדיט.'),'sourceUrl':'','driveUrl':'','clipNames':[]})
items=public+family
assert len({x['id'] for x in items})==len(items)
assert len({x['sourceUrl'] for x in public})==len(public)
counts=collections.Counter(x['section'] for x in items)
sections=[]
for c in research.get('categories',[]):
    if counts[c['id']]:sections.append({'id':c['id'],'label':c['label'],'description':c['description'],'editorialUse':c['editorialUse'],'count':counts[c['id']]})
known={s['id'] for s in sections}
for sid in sorted(set(counts)-known-{'family_requests'}):sections.append({'id':sid,'label':sid.replace('_',' '),'description':'מקורות ארכיוניים שנאספו תחת ציר זה.','editorialUse':'לבדוק כיצד הציר משרת את סיפור דבורה ומאיר.','count':counts[sid]})
if family:sections.append({'id':'family_requests','label':'אלבומי המשפחה שצריך לאסוף','description':'מפת בקשות מסודרת לתמונות ומסמכים שאינם נמצאים עדיין בתיק. כל כרטיס הוא צורך עריכתי, לא נכס קיים.','editorialUse':'להפוך את הסיפור ההיסטורי הכללי לסיפור אישי: פנים, מקומות, מסע, זוגיות ובית.','count':len(family)})
mc=collections.Counter(x['mediaGroup'] for x in items);rc=collections.Counter(x['rightsGroup'] for x in items)
open_count=rc.get('open',0)
meta={'title':'דבורה ומאיר — מדריך חומרי ארכיון לעורך','projectTitle':'דבורה ומאיר','projectSubtitle':'מדריך חומרי ארכיון לעורך','metaDescription':'מפת חומרי ארכיון לסיפור דבורה ומאיר: מה רואים, למה רלוונטי, זכויות ואלבומי משפחה חסרים.','eyebrow':'תיק ארכיון הפקה · 11.8.2026','heroLede':'מקורות היסטוריים ואלבומי משפחה מאורגנים לפי הסיפור: אתיופיה וסודאן, מבצעי העלייה, קליטה בישראל, יהדות צרפת והמפגש בין דבורה למאיר.','heroRule':'מקור היסטורי נותן הקשר; אלבום המשפחה הופך אותו לסיפור אישי.','catalogTitle':'כל חומרי הארכיון','catalogDate':'11.8.2026','total':len(items),'openLicensed':open_count,'metricTotalLabel':'מקורות וכרטיסי איסוף','metricSectionLabel':'קטגוריות סיפור','metricOpenLabel':'פריטים פתוחים בתנאים','metricRouteValue':str(len(family)),'metricRouteLabel':'אלבומי משפחה לבקשה','journeyTitle':'ניווט לפי ציר סיפור','mediaLabels':{'video':'סרטים ותיעוד','stills':'תמונות ואלבומים','web':'עמודים ומאגרים','audio':'אודיו'},'rightsLabels':{'open':'פתוח בתנאים','permission':'נדרש אישור','commercial':'ארכיון מסחרי','family':'אלבום משפחתי חסר','verify':'טעון בדיקה'},'mediaCounts':dict(mc),'rightsCounts':dict(rc),'sections':sections,'startTitle':'אם יש לעורך רק שעה','startIntro':'להתחיל מארבעה צירים שמחברים היסטוריה עם סיפור אישי.','startLeads':[{'title':'המסע מאתיופיה דרך סודאן','description':'רקע חזותי ועדויות למסע של מאיר.','section':'ethiopia_sudan'},{'title':'מבצעי משה ושלמה','description':'המעבר מן ההמתנה אל העלייה לישראל.','section':'operations'},{'title':'יהדות צרפת והעלייה','description':'עולם המוצא והבחירה של דבורה.','section':'france_aliyah'},{'title':'קליטה ובניית חיים בישראל','description':'מהמטוס אל מרכז הקליטה, עבודה ומשפחה.','section':'absorption'},{'title':'אלבומי המשפחה','description':'מה עדיין צריך לבקש כדי להפוך הקשר לדמות.','section':'family_requests'}],'sidebar':{'eyebrow':'מפת שימוש','title':'איך לעבוד עם המקורות','steps':[{'kind':'open','title':'רישיון פתוח','description':'עדיין דורש קרדיט ותנאי רישיון.'},{'kind':'permission','title':'ארכיון רשמי','description':'לבקש master ואישור שידור.'},{'kind':'commercial','title':'שידור/סוכנות','description':'לבקש הצעת רישוי.'},{'kind':'verify','title':'אלבום חסר','description':'אין להניח שהוא קיים; לפנות למשפחה.'}]},'footerDisclaimer':'מדריך מחקר לעורך. אין להשתמש בחומר ללא אימות ורשות; כרטיסי המשפחה הם בקשות ולא נכסים קיימים.','methodology':research.get('meta',{})}
out={'meta':meta,'items':items};Path(__file__).resolve().parents[1].joinpath('data','archive.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print('public',len(public),'family_requests',len(family),'total',len(items),'sections',len(sections))
