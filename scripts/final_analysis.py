import pandas as pd, numpy as np
pd.set_option('display.width',220)
df=pd.read_csv('premium_5y_corrected.csv',index_col=0,parse_dates=True)
prem=df*100
latest=prem.iloc[-1]

print("=== A. 5年中枢与当前偏离度(校准后数据) ===")
print(f"{'代码':8s}{'均值中枢':>9s}{'中位数':>8s}{'当前':>8s}{'超出均值':>9s}{'历史分位':>9s}{'Z-score':>8s}{'数据起点':>12s}")
res=[]
for c in prem.columns:
    s=prem[c].dropna()
    pct=(s<latest[c]).mean()*100
    z=(latest[c]-s.mean())/s.std()
    start=s.index.min().date()
    res.append((c,s.mean(),s.median(),latest[c],latest[c]-s.mean(),pct,z,str(start)))
    print(f"{c:8s}{s.mean():8.2f}%{s.median():7.2f}%{latest[c]:7.2f}%{latest[c]-s.mean():8.2f}pct{pct:8.1f}%{z:7.2f}  {start}")

print("\n=== B. 年度平均溢价(%) ===")
yr=prem.groupby(prem.index.year).mean().mean(axis=1)
print({int(k):round(v,2) for k,v in yr.items()})

print("\n=== C. 偏离度均值回归检验(120日滚动Z) ===")
WIN=120
zall=(prem-prem.rolling(WIN,min_periods=60).mean())/prem.rolling(WIN,min_periods=60).std()
for thr in [2.0,2.5,3.0]:
    hi=zall>thr
    print(f"\n z>{thr}: 样本{int(hi.sum().sum())}")
    for d in [20,60]:
        fwd=(zall.shift(-d)-zall)[hi].stack().dropna()
        print(f"   未来{d}日: 平均变化{fwd.mean():+.2f}, 回落比例{(fwd<0).mean()*100:.0f}%")

print("\n=== D. 当前Z-score分布(全12只) ===")
lastz=zall.iloc[-1].dropna().sort_values()
print("最被低估3只:",[(c,round(v,2)) for c,v in lastz.head(3).items()])
print("最被高估3只:",[(c,round(v,2)) for c,v in lastz.tail(3).items()])
print(f"当前Z均值{lastz.mean():.2f}, 最小{lastz.min():.2f}, 全部为正? {(lastz>0).all()}")

print("\n=== E. 溢价两两相关性 ===")
corr=prem.corr().values
off=corr[np.triu_indices_from(corr,1)]
print(f"平均{np.nanmean(off):.3f} 最低{np.nanmin(off):.3f}")
