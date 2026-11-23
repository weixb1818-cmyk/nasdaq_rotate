import pandas as pd, numpy as np, requests, json, re, time
H={'User-Agent':'Mozilla/5.0'}
codes=['159501','513100','159941','159696','159659','513870','513300','513390','159660']
px_all={}; nav_all={}
for c in codes:
    sym=('sh' if c.startswith('5') else 'sz')+c
    u=f'https://quotes.sina.cn/cn/api/jsonp_v2.php/var%20_d=/CN_MarketDataService.getKLineData?symbol={sym}&scale=240&ma=no&datalen=1500'
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
        p+=1;time.sleep(.02)
    nav_all[c]=pd.Series(dict(rows)).sort_index()

# 官方溢折率(格隆汇/Wind每日榜单)
official={
'2026-11-06':[23.64,21.31,18.75,19.59,17.52,17.24,16.63,16.66,16.95],
'2026-11-11':[21.79,20.35,19.42,20.01,18.64,17.70,17.68,17.26,17.14],
'2026-11-13':[18.52,17.85,16.45,17.62,16.14,14.80,15.53,14.66,14.66],
'2026-11-20':[18.04,16.98,15.14,17.18,15.74,14.83,14.76,14.22,13.93],
}
print('测试: 价格T日 配 净值T+k日(k为净值FSRQ相对交易日), 比较与官方榜单平均绝对误差')
for k in [-2,-1,0,1,2]:
    errs=[]
    for dt,offs in official.items():
        d=pd.Timestamp(dt)
        calc=[]
        for i,c in enumerate(codes):
            p=px_all[c].get(d,np.nan)
            target=d+pd.Timedelta(days=k)
            navd=nav_all[c].index[nav_all[c].index<=target]
            n=nav_all[c].iloc[-1] if len(navd)==0 else nav_all[c].get(navd[-1])
            calc.append(p/n-1 if n==n and p==p else np.nan)
        errs.extend(np.abs(np.array(calc)-np.array(offs)/100)*100)
    print(f'  k={k:+d}: 平均绝对误差 {np.nanmean(errs):.2f} pct')
