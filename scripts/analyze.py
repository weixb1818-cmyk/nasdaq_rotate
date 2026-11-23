import pandas as pd, numpy as np
pd.set_option('display.width',220)
df=pd.read_csv('premium_daily.csv',index_col=0,parse_dates=True)
prem=df*100
latest=prem.iloc[-1]
print("=== 每只ETF的溢价中枢与当前偏离度(旧口径数据) ===")
for c in prem.columns:
    s=prem[c].dropna()
    med=s.median(); mean=s.mean()
    pct=(s<latest[c]).mean()*100
    z=(latest[c]-mean)/s.std()
    print(f"{c:8s}{mean:9.2f}%{med:7.2f}%{latest[c]:8.2f}%{pct:8.1f}%{z:8.2f}")
WIN=120
mean=prem.rolling(WIN,min_periods=60).mean(); std=prem.rolling(WIN,min_periods=60).std()
z=(prem-mean)/std
for thr in [2.0,2.5]:
    hi=(z>thr)
    print(f" z>{thr} 样本{hi.sum().sum()}")
    for d in [5,20,60]:
        fwd=(z.shift(-d)-z)[hi].stack().dropna()
        print(f"   未来{d}日: 平均{fwd.mean():+.2f} 回落比例{(fwd<0).mean()*100:.0f}%")
pcts=[(prem[c]<latest[c]).mean()*100 for c in prem.columns]
print(f"当前历史分位: {min(pcts):.1f}%~{max(pcts):.1f}%")
corr=prem.corr(); off=corr.values[np.triu_indices_from(corr.values,1)]
print(f"两两相关性: 平均{np.mean(off):.3f} 最低{np.min(off):.3f}")
