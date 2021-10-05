import pyupbit
import numpy as np
import pandas as pd
import time
import pandas as pd
import matplotlib.pyplot as plt

#판다스 경고 무시
pd.set_option('mode.chained_assignment',  None)

def get_hpr(k):

    dfs = []
    df= pyupbit.get_ohlcv("KRW-ETH",interval="day", count=60)
    dfs.append(df)

    df['range'] = (df['high']-df['low'])*k
    #target(매수가), range 컬럼을 한칸씩 밑으로 내림(.shift(1))
    df['target_price'] = round(df['open'] + df['range'].shift(1),-3)
    #다음날 시가
    df['tomorrow_open'] = df['open'].shift(-1)

    #10일 이평선
    df['ma10'] = df['close'].rolling(10).mean()
    #null 삭제 하기
    df=df[df['ma10'].notnull()]

    #조건 만족했는지 확인
    cond = ((df['high']>df['target_price']) & (df['high']>df['ma10']))
    #수익률
    df['ror'] = df.loc[cond,'tomorrow_open']/df.loc[cond,'target_price']
    #누적 수익률
    df['hpr'] = df['ror'].cumprod()
    df=df[df['hpr'].notnull()]
    df.loc[cond].to_excel("backtesting_k=%.1f.xlsx" %(k))
    result = df.iloc[-1]['hpr']
    return result
def find_best_k():
    ks = []
    k_list = [0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9]
    for k in k_list:
        hpr = get_hpr(k)
        ks.append(hpr)
    hpr = pd.DataFrame({"hpr": ks})
    k_data = pd.DataFrame({"k": k_list})
    sum = pd.concat([k_data, hpr], axis =1)
    final=sum.sort_values(by = "hpr", ascending=False)
    best_k = final.iloc[:10]['k'].values.tolist()[0]
    return best_k
print(find_best_k())
