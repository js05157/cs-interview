"""Snapshot GitHub's public profile calendar. No authentication or third-party service."""
import argparse
from datetime import date,datetime,timezone,timedelta
from html.parser import HTMLParser
import json,re
from pathlib import Path
from urllib.request import Request,urlopen

class Calendar(HTMLParser):
    def __init__(self):
        super().__init__();self.cells=[];self.tips={};self.tip=None
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=='td' and a.get('data-date') and a.get('data-level') is not None:
            self.cells.append((a.get('id'),a['data-date'],int(a['data-level'])))
        if tag=='tool-tip' and a.get('for'):
            self.tip=a['for'];self.tips[self.tip]=''
    def handle_endtag(self,tag):
        if tag=='tool-tip':self.tip=None
    def handle_data(self,value):
        if self.tip:self.tips[self.tip]+=value

def parse_calendar(html,start,end):
    parser=Calendar();parser.feed(html);days={}
    for identifier,day,level in parser.cells:
        if not start<=day<=end:continue
        tip=' '.join(parser.tips.get(identifier,'').split())
        if re.search(r'\bNo contributions\b',tip,re.I):count=0
        else:
            found=re.search(r'([\d,]+) contribution',tip,re.I)
            if not found:raise ValueError('calendar-tooltip-format-changed')
            count=int(found[1].replace(',',''))
        if not 0<=level<=4 or (count==0)!=(level==0):raise ValueError('calendar-level-invalid')
        days[day]={'date':day,'count':count,'level':level}
    expected=(date.fromisoformat(end)-date.fromisoformat(start)).days+1
    if len(days)!=expected:raise ValueError('calendar-incomplete')
    return [days[k] for k in sorted(days)]

def snapshot(user,year,*,html=None,today=None):
    if not re.fullmatch(r'[A-Za-z0-9-]{1,39}',user):raise ValueError('invalid-user')
    today=today or datetime.now(timezone(timedelta(hours=9))).date()
    first=date(year,1,1);last=min(date(year,12,31),today)
    if last<first:raise ValueError('future-calendar-not-available')
    url=f'https://github.com/users/{user}/contributions?from={first}&to={last}'
    if html is None:
        with urlopen(Request(url,headers={'User-Agent':'personal-blog-public-activity-snapshot'}),timeout=25) as response:
            html=response.read(2_000_000).decode('utf-8')
    days=parse_calendar(html,str(first),str(last))
    first_offset=(first.weekday()+1)%7
    cells=[None]*first_offset+days
    weeks=[cells[i:i+7] for i in range(0,len(cells),7)]
    return {'source':'github-public-profile','user':user,'year':year,'from':str(first),'through':str(last),
            'fetched_at':datetime.now(timezone.utc).isoformat(),'source_url':url,
            'profile_url':f'https://github.com/{user}','total':sum(d['count'] for d in days),
            'weeks':weeks,'days':days,
            'description':'GitHub 공개 프로필에 표시된 기여 수입니다. 커밋 수나 블로그 게시 수와 같지 않습니다.'}

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--user',default='js05157')
    parser.add_argument('--year',type=int,default=datetime.now(timezone(timedelta(hours=9))).year)
    parser.add_argument('--output',type=Path,default=Path('blog/_data/activity.json'))
    args=parser.parse_args()
    try:
        result=snapshot(args.user,args.year)
    except (ValueError,OSError):
        print('activity-unavailable: existing snapshot preserved; no fabricated days')
        return 1
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'source':result['source'],'days':len(result['days']),'total':result['total'],'through':result['through']}))
    return 0
if __name__=='__main__':raise SystemExit(main())
