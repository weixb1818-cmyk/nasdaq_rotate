import pandas as pd, numpy as np, requests, json, re
df=pd.read_csv('premium_daily.csv',index_col=0,parse_dates=True)
prem=df*100
WIN=120
z=(prem-prem.rolling(WIN,min_periods=60).mean())/prem.rolling(WIN,min_periods=60).std()
H={'User-Agent':'Mozilla/5.0'}
px_all={}
for c in prem.columns:
    sym=('sh' if c.startswith('5') else 'sz')+c
    u=f'https://quotes.sina.cn/cn/api/jsonp_v2.php/var%20_d=/CN_MarketDataService.getKLineData?symbol={sym}&scale=240&ma=no&datalen=1000'
    arr=json.loads(re.search(r'\((\[.*\])\)',requests.get(u,headers=H,timeout=25).text,re.S).group(1))
    px_all[c]=pd.Series({pd.to_datetime(x['day']):float(x['close']) for x in arr}).sort_index()
px=pd.DataFrame(px_all).sort_index()
idx=prem.index.intersection(px.index)
z=z.loc[idx]; px=px.loc[idx]
price_ret=px.pct_change()
strat=pd.Series(index=idx,dtype=float); cur=None; swaps=0
for i,dt in enumerate(idx):
    if i%5==0:
        zz=z.loc[dt].dropna()
        if len(zz)>0:
            pick=zz.idxmin()
            if cur and pick!=cur: swaps+=1
            cur=pick
    if cur: strat.loc[dt]=price_ret.loc[dt,cur]
bench=price_ret.mean(axis=1)
valid=strat.dropna().index
strat=strat.loc[valid]; bench=bench.loc[valid]
yrs=len(strat)/252
cs=(1+strat).prod()-1; cb=(1+bench).prod()-1
print(f"策略累计{cs*100:.1f}% 年化{((1+cs)**(1/yrs)-1)*100:.1f}%")
print(f"等权基准累计{cb*100:.1f}% 年化{((1+cb)**(1/yrs)-1)*100:.1f}%")
excess=strat-bench
print(f"年化超额{excess.mean()*252*100:.2f}% IR={excess.mean()/excess.std()*np.sqrt(252):.2f}")
cost_yr=swaps*0.001/yrs*100
print(f"换仓{swaps}次 成本{cost_yr:.2f}%/年 净超额{excess.mean()*252*100-cost_yr:.2f}%/年")
