# 從全國法規資料庫開放資料抓最新條文，產生 data/laws.json
import json,io,zipfile,subprocess,datetime,os,re
LAWS=[
 # (科目, 法規名稱, 來源: L=法律 O=命令, 重要性)
 ('crim','中華民國刑法','L','核心'),
 ('law','中華民國憲法','L','核心'),
 ('law','中華民國憲法增修條文','L','核心'),
 ('law','中央法規標準法','L','法學緒論常考'),
 ('law','憲法訴訟法','L','補充'),
 ('pol','警察法','L','命題範圍'),
 ('pol','警察法施行細則','O','命題範圍相關'),
 ('pol','行政執行法','L','命題範圍'),
 ('pol','社會秩序維護法','L','命題範圍'),
 ('pol','違反社會秩序維護法案件處理辦法','O','補充'),
 ('pol','警械使用條例','L','命題範圍'),
 ('pol','集會遊行法','L','命題範圍'),
 ('pol','警察職權行使法','L','命題範圍'),
 ('pol','行政程序法','L','命題範圍'),
 ('pol','公務人員行政中立法','L','命題範圍'),
 ('pol','公務人員行政中立法施行細則','O','補充'),
 ('pol','警察人員人事條例','L','歷屆有考'),
 ('pol','警察勤務條例','L','歷屆有考'),
 ('pol','公務人員考績法','L','歷屆有考'),
 ('pol','公務員懲戒法','L','補充'),
 ('pol','公務員服務法','L','補充'),
 ('pol','行政罰法','L','補充'),
 ('pol','提審法','L','補充'),
 ('pol','個人資料保護法','L','補充'),
 ('pol','國家賠償法','L','補充'),
]
def get(kind):
    url='https://law.moj.gov.tw/api/Ch/%s/JSON'%('Law' if kind=='L' else 'Order')
    local=os.environ.get('LAW_ZIP' if kind=='L' else 'ORDER_ZIP')
    raw=open(local,'rb').read() if local else subprocess.run(['curl','-sSL','--retry','3','--max-time','300',url],capture_output=True,check=True).stdout
    z=zipfile.ZipFile(io.BytesIO(raw))
    name=[n for n in z.namelist() if n.endswith('.json')][0]
    d=json.loads(z.read(name).decode('utf-8-sig'))
    return d['UpdateDate'],{l['LawName']:l for l in d['Laws']}
def main(out):
    srcs={}
    for k in ('L','O'): srcs[k]=get(k)
    laws=[]
    for subj,name,k,imp in LAWS:
        l=srcs[k][1].get(name)
        if not l: print('缺少',name);continue
        arts=[]
        for a in l['LawArticles']:
            if a['ArticleType']=='C': arts.append({'h':re.sub(r'\s+',' ',a['ArticleContent']).strip()})
            else:
                no=re.sub(r'\s+','',a['ArticleNo']).replace('第','').replace('條','')
                arts.append({'n':no,'t':a['ArticleContent'].strip()})
        laws.append({'subj':subj,'name':name,'imp':imp,'url':l['LawURL'],'mod':l['LawModifiedDate'],'abandon':l.get('LawAbandonNote',''),'arts':arts})
    old=None
    try: old=json.load(open(out,encoding='utf-8'))
    except Exception: pass
    if old and old.get('laws')==laws:
        print('法條沒有變動');return
    data={'updated':datetime.date.today().isoformat(),'source':'全國法規資料庫開放資料 '+srcs['L'][0],'laws':laws}
    json.dump(data,open(out,'w',encoding='utf-8'),ensure_ascii=False,separators=(',',':'))
    print('OK',len(laws),'部',sum(len([a for a in l['arts'] if 'n' in a]) for l in laws),'條')
if __name__=='__main__':
    main(os.path.join(os.path.dirname(os.path.abspath(__file__)),'laws.json'))
