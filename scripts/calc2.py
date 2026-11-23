import numpy as np
js = [23.64,21.79,18.52,18.04]
hx = [16.63,17.68,15.53,14.76]
d  = ["11/06","11/11","11/13","11/20"]
print("=== 分阶段 卖高买低 相对收益 ===")
cum=0
for i in range(3):
    r = (hx[i+1]-hx[i]) - (js[i+1]-js[i])
    cum += r
    print(f"  {d[i]}->{d[i+1]}: 相对{r:+.2f}pct 累计{cum:+.2f}pct")
for i in range(3):
    r=(hx[3]-hx[i])-(js[3]-js[i])
    print(f"  {d[i]}建仓持有到11/20: {r:+.2f} pct")
changes=[-4.64,-5.19,-4.61,-4.66,-4.48,-4.38,-5.64,-5.35,-4.31,-4.87,-4.21,-5.22]
print(f"11/20当日涨跌幅: {min(changes):.2f}%~{max(changes):.2f}%, 均值{np.mean(changes):.2f}%")
