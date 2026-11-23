import pandas as pd, numpy as np
pd.set_option('display.width',220)
df=pd.read_csv('premium_daily.csv',index_col=0,parse_dates=True)
prem=df*100
import requests,json,re
H={'User-Agent':'Mozilla/5.0'}
funds=list(prem.columns)
px_all={}
for c in funds:
    sym=('sh' if c.startswith('5') else 'sz')+c
    u=f'https://quotes.sina.cn/cn/api/jsonp_v2.php/var%20_d=/CN_MarketDataService.getKLineData?symbol={sym}&scale=240&ma=no&datalen=1000'
    r=requests.get(u,headers=H,timeout=25)
    arr=json.loads(re.search(r'\((\[.*\])\)',r.text,re.S).group(1))
    px_all[c]=pd.Series({pd.to_datetime(x['day']):float(x['close']) for x in arr}).sort_index()
px=pd.DataFrame(px_all).sort_index()
price_ret=px.pct_change()
WIN=120
z=(prem-prem.rolling(WIN,min_periods=60).mean())/prem.rolling(WIN,min_periods=60).std()
idx=prem.index.intersection(price_ret.index)
z=z.loc[idx]; price_ret=price_ret.loc[idx]
strat_ret=pd.Series(index=idx,dtype=float); bench_ret=price_ret.mean(axis=1)
cur=None; swaps=0
for i,dt in enumerate(idx):
    if i%5==0:
        zz=z.loc[dt].dropna()
        if len(zz)>0:
            pick=zz.idxmin()
            if cur and pick!=cur: swaps+=1
            cur=pick
    if cur: strat_ret.loc[dt]=price_ret.loc[dt,cur]
    else: strat_ret.loc[dt]=np.nan
strat_ret=strat_ret.dropna(); bench_ret=bench_ret.loc[strat_ret.index]
cum_s=(1+strat_ret).prod()-1; cum_b=(1+bench_ret).prod()-1
yrs=len(strat_ret)/252
ann_s=(1+cum_s)**(1/yrs)-1; ann_b=(1+cum_b)**(1/yrs)-1
sharpe_s=strat_ret.mean()/strat_ret.std()*np.sqrt(252)
sharpe_b=bench_ret.mean()/bench_ret.std()*np.sqrt(252)
print(f"策略: 累计{cum_s*100:.1f}% 年化{ann_s*100:.1f}% 夏普{sharpe_s:.2f}")
print(f"基准(等权): 累计{cum_b*100:.1f}% 年化{ann_b*100:.1f}% 夏普{sharpe_b:.2f}")
print(f"累计换仓次数: {swaps}")
