import requests, json, re, time, pandas as pd
funds = {"159501":"sz159501","159696":"sz159696","513100":"sh513100","159659":"sz159659","159941":"sz159941","513870":"sh513870","513300":"sh513300","513390":"sh513390","159660":"sz159660","159632":"sz159632","513110":"sh513110","159513":"sz159513"}
H={'User-Agent':'Mozilla/5.0'}
def get_kline(sym):
    u=f'https://quotes.sina.cn/cn/api/jsonp_v2.php/var%20_d=/CN_MarketDataService.getKLineData?symbol={sym}&scale=240&ma=no&datalen=1000'
    r=requests.get(u,headers=H,timeout=25)
    arr=json.loads(re.search(r'\((\[.*\])\)',r.text,re.S).group(1))
    df=pd.DataFrame(arr); df['date']=pd.to_datetime(df['day']); df['close']=pd.to_numeric(df['close'])
    return df[['date','close']].set_index('date')
def get_nav(code):
    rows=[]; p=1
    while True:
        r=requests.get('https://api.fund.eastmoney.com/f10/lsjz',params={'fundCode':code,'pageIndex':p,'pageSize':20},headers={**H,'Referer':'https://fund.eastmoney.com/'},timeout=25)
        j=r.json(); d=j.get('Data') or {}
        lst=d.get('LSJZList',[])
        if not lst: break
        for x in lst:
            if x['DWJZ']: rows.append((x['FSRQ'], float(x['DWJZ'])))
        if p*20>=j.get('TotalCount',0): break
        p+=1; time.sleep(0.03)
    df=pd.DataFrame(rows,columns=['date','nav']); df['date']=pd.to_datetime(df['date'])
    return df.drop_duplicates('date').set_index('date')
allp={}
for code,sym in funds.items():
    try:
        px=get_kline(sym); nav=get_nav(code)
        j=px.join(nav,how='inner').dropna(); j['prem']=j['close']/j['nav']-1
        allp[code]=j
        print(f"{code}: K线{len(px)} 净值{len(nav)} 对齐{len(j)} {j.index.min().date()}~{j.index.max().date()}")
    except Exception as e: print(code,'失败',repr(e)[:100])
out=pd.DataFrame({c:d['prem'] for c,d in allp.items()}).sort_index()
out.to_csv('premium_daily.csv')
print('形状',out.shape,'起止',out.index.min().date(),out.index.max().date())
