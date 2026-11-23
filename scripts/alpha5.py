import pandas as pd, numpy as np, requests, json, re
df=pd.read_csv('premium_5y_corrected.csv',index_col=0,parse_dates=True)
prem=df*100
WIN=120
mean=prem.rolling(WIN,min_periods=60).mean(); std=prem.rolling(WIN,min_periods=60).std()
z=(prem-mean)/std
H={'User-Agent':'Mozilla/5.0'}
px_all={}
for c in prem.columns:
    sym=('sh' if c.startswith('5') else 'sz')+c
    u=f'https://quotes.sina.cn/cn/api/jsonp_v2.php/var%20_d=/CN_MarketDataService.getKLineData?symbol={sym}&scale=240&ma=no&datalen=1000'
    arr=json.loads(re.search(r'\((\[.*\])\)',requests.get(u,headers=H,timeout=25).text,re.S).group(1))
    px_all[c]=pd.Series({pd.to_datetime(x['day']):float(x['close']) for x in arr}).sort_index()
px=pd.DataFrame(px_all).sort_index()
idx=prem.index.intersection(px.index)
prem=prem.loc[idx]; z=z.loc[idx]; px=px.loc[idx]
price_ret=px.pct_change()
strat=pd.Series(index=idx,dtype=float); cur=None; swaps=0; daily_pick=[]
for i,dt in enumerate(idx):
    if i%5==0:
        zz=z.loc[dt].dropna()
        if len(zz)>0:
            pick=zz.idxmin()
            if cur and pick!=cur: swaps+=1
            cur=pick
    daily_pick.append(cur)
    if cur: strat.loc[dt]=price_ret.loc[dt,cur]
bench=price_ret.mean(axis=1)
valid=strat.dropna().index
strat=strat.loc[valid]; bench=bench.loc[valid]
yrs=len(strat)/252
cs=(1+strat).prod()-1; cb=(1+bench).prod()-1
print("=== 策略 vs 等权基准 (5年校准数据回测) ===")
print(f"策略累计{cs*100:.1f}% 年化{((1+cs)**(1/yrs)-1)*100:.1f}%")
print(f"等权基准累计{cb*100:.1f}% 年化{((1+cb)**(1/yrs)-1)*100:.1f}%")
excess=strat-bench
print(f"年化超额(excess): {excess.mean()*252*100:.2f}%  IR={excess.mean()/excess.std()*np.sqrt(252):.2f}")
cost_yr=swaps*0.001/yrs*100
print(f"换仓{swaps}次, 成本拖累约{cost_yr:.2f}%/年")
print(f">>> 扣成本后净超额约 {excess.mean()*252*100-cost_yr:.2f}%/年")
lastz=z.iloc[-1].sort_values()
print("当前z-score最小(最被低估)的3只:")
for c in lastz.index[:3]:
    print(f"  {c}: z={lastz[c]:+.2f} (仍为正=仍高于自身中枢)")
print(f"当前全部12只z均值{z.iloc[-1].mean():+.2f}, 最小{lastz.min():+.2f}")
