import pandas as pd, numpy as np, requests, json, re, time
H={'User-Agent':'Mozilla/5.0'}
funds={"159501":"sz159501","159696":"sz159696","513100":"sh513100","159659":"sz159659",
 "159941":"sz159941","513870":"sh513870","513300":"sh513300","513390":"sh513390",
 "159660":"sz159660","159632":"sz159632","513110":"sh513110","159513":"sz159513"}
allp={}
for code,sym in funds.items():
    u=f'https://quotes.sina.cn/cn/api/jsonp_v2.php/var%20_d=/CN_MarketDataService.getKLineData?symbol={sym}&scale=240&ma=no&datalen=1600'
    arr=json.loads(re.search(r'\((\[.*\])\)',requests.get(u,headers=H,timeout=30).text,re.S).group(1))
    px=pd.Series({pd.to_datetime(x['day']):float(x['close']) for x in arr}).sort_index()
    rows=[];p=1
    while True:
        j=requests.get('https://api.fund.eastmoney.com/f10/lsjz',params={'fundCode':code,'pageIndex':p,'pageSize':20},headers={**H,'Referer':'https://fund.eastmoney.com/'},timeout=25).json()
        lst=(j.get('Data') or {}).get('LSJZList',[])
        if not lst:break
        for x in lst:
            if x['DWJZ']:rows.append((pd.to_datetime(x['FSRQ']),float(x['DWJZ'])))
        if p*20>=j.get('TotalCount',0):break
        p+=1;time.sleep(.02)
    nav=pd.Series(dict(rows)).sort_index()
    # 关键修正: T日价格配 T-1日净值 (k=-1)
    nav_shift=nav.copy(); nav_shift.index=nav_shift.index+pd.Timedelta(days=1)
    j=pd.DataFrame({'px':px,'nav':nav_shift}).dropna()
    j['prem']=j['px']/j['nav']-1
    allp[code]=j['prem']
    print(f"{code}: {len(j)}交易日 {j.index.min().date()}~{j.index.max().date()} 最新{j['prem'].iloc[-1]*100:.2f}%")
out=pd.DataFrame(allp).sort_index()
out.to_csv('premium_5y_corrected.csv')
print('\n形状',out.shape,'区间',out.index.min().date(),out.index.max().date())
# 验证最新值与官方对比
print('最新一日溢价:',out.iloc[-1].mul(100).round(2).to_dict())
