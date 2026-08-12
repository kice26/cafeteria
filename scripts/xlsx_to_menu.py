import datetime as dt,json,os,re,sys,zipfile
from xml.etree import ElementTree as E
N={'x':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
def read(path):
 with zipfile.ZipFile(path) as z:
  try:s=[''.join(x.itertext()) for x in E.parse(z.open('xl/sharedStrings.xml')).getroot().findall('x:si',N)]
  except KeyError:s=[]
  root=E.parse(z.open('xl/worksheets/sheet1.xml')).getroot()
 out={}
 for c in root.findall('.//x:c',N):
  v=c.find('x:v',N)
  if v is not None:out[c.attrib['r']]=s[int(v.text)] if c.attrib.get('t')=='s' else (v.text or '')
 return out
def vals(c,col,a,b):return [c.get(f'{col}{i}','').strip() for i in range(a,b+1) if c.get(f'{col}{i}','').strip()]
c=read(sys.argv[1]);year=int(os.getenv('MENU_YEAR') or dt.date.today().year);menus={}
for col in 'CDEFG':
 m=re.search(r'(\d{1,2})월\s*(\d{1,2})일',c.get(f'{col}3',''))
 if m:
  mo,day=map(int,m.groups());d=f'{year}-{mo:02d}-{day:02d}'; dinner=vals(c,col,13,18);menus[d]={'day':c.get(f'{col}4',''),'lunch':vals(c,col,5,10),'plus':vals(c,col,11,12),'dinner':None if any('운영하지 않습니다' in x for x in dinner) else dinner}
first=dt.date.fromisoformat(sorted(menus)[0]);payload={'weekLabel':f'{first.year}년 {first.month}월 {(first.day-1)//7+1}주차','menus':menus};encoded=json.dumps(payload,ensure_ascii=False);open(sys.argv[2],'w',encoding='utf-8').write(encoded)
if len(sys.argv)>3: open(sys.argv[3],'w',encoding='utf-8').write('window.menuData='+encoded+';')
