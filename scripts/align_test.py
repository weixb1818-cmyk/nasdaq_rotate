import pandas as pd, numpy as np, requests, json, re
H={'User-Agent':'Mozilla/5.0'}
codes=['159501','513100','159941','159696','159659']
px_all={}; nav_all={}
for c in codes:
    sym=('sh' if c.startswith('5') else 'sz')+c
    u=f'https://quotes.sina.cn/cn/api/jsonp_v2.php/var%20_d=/CN_MarketDataService.getKLineData?symbol={sym}&scale=240&ma=no&datalen=1000'
    arr=json.loads(re.search(r'\((\[.*\])\)',requests.get(u,headers=H,timeout=25).text,re.S).group(1))
    px_all[c]=pd.Series({pd.to_datetime(x['day']):float(x['close']) for x in arr}).sort_index()
    rows=[];p=1
    while True:
        j=requests.get('https://api.fund.eastmoney.com/f10/lsjz',params={'fundCode':c,'pageIndex':p,'pageSize':20},headers={**H,'Referer':'https://fund.eastmoney.com/'},timeout=25).json()
        lst=(j.get('Data') or {}).get('LSJZList',[])
        if not lst:break
        for x in lst:
            if x['DWJZ']:rows.append((pd.to_datetime(x['FSRQ']),float(x['DWJZ'])))
        if p*20>=j.get('TotalCount',0):break
        p+=1
    nav_all[c]=pd.Series(dict(rows)).sort_index()
pub={'2026-11-06':21.99,'2026-11-11':19.04,'2026-11-13':20.02}
for shift in [-2,-1,0,1,2]:
    print(f'净值前移{shift}日:')
    for dt,pv in pub.items():
        d=pd.Timestamp(dt); vals=[]
        for c in codes:
            p=px_all[c].get(d,np.nan)
            nd=d+pd.Timedelta(days=shift)
            navd=nav_all[c].index[nav_all[c].index<=nd]
            n=nav_all[c].get(navd[-1],np.nan) if len(navd) else np.nan
            vals.append(p/n-1 if n==n else np.nan)
        print(f'  {dt}: 均值{np.nanmean(vals)*100:.2f}%')
