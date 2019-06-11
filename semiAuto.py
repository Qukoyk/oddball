# import文
import numpy as np
import matplotlib.pyplot as plt
import time
import csv,os
from scipy import signal


# 定数宣言
waveMax = 500
waveMin = -500

# 変数宣言
fileName = 'LE029_0514.m00'
position = 0
positionList = []
os.chdir('C:/Users/Qukoyk/Desktop/download/')


# トリガーのチャンネルを宣言
std = 8
tgt = 9

# 番号入力
answer = input("分析したいチャンネルの番号を入力ください：\n")

print('\n'+"チャンネルデータ読み込み中……")

# 分析するチャンネルを読み込んでからフィルターをかけて行列変換をする
#          トレンド除去                  ファイル名       行頭抜き   分析する列の番号   行列変換をする
chList = signal.detrend(np.loadtxt(fileName, skiprows=2, usecols=int(answer)-1).T)        # トレンド除去フィルターで波形を整形

# バンドパス Chebyshev Ⅰ型　リップル1db（第一種チェビシェフフィルタ）
# フィルターパラメータ設定
dt = 0.001     # サンプリング間隔
fn = 1/(2*dt)  # ナイキスト周波数
fp = 2         # 通過域端周波数[Hz]
fs = 3         # 阻止域端周波数[Hz]
gPass = 1      # 通過域最大損失量[dB]
gStop = 40     # 阻止域最小減衰量[dB]
# 正規化
Wp = fp/fn
Ws = fs/fn
N, Wn = signal.cheb1ord(Wp, Ws, gPass, gStop)
b, a = signal.cheby1(N, gPass, Wn, "low")
#chList = signal.filtfilt(b, a, chList)

# トリガー抽出関数
def triggerExtract(trigger):
    # 関数内変数を宣言
    counter = 0
    continuous = False
    position = 0
    tempPosition = 0
    triggerList = []
    tempList = np.loadtxt(fileName,skiprows=2, usecols=trigger-1)
    maxValue = max(tempList)
    # 抽出開始
    for i in tempList:

        if i == 0:
            continuous = False
            pass
            
        if i == maxValue and continuous == False:
            if position - tempPosition > 1200:
                counter = counter + 1
                triggerList.append(position)
                continuous = True
                tempPosition = position
                pass
            pass
        # 累進
        position = position + 1
        pass

    print(counter,"個検出された")
    return triggerList

# 外れ値検出関数
def triggerCheck(listName):
    # 局所変数設定
    position = 0
    badList = []
    tempList = []
    trialList = []
    sessionList = []
    # 検出開始

    for i in listName:                     # i はトリガーの時点

        for j in range(i-200,i+1001):      # j はトリガーの時点前200ms~後1000msの時点
            k = chList[j]                  # k はj時点の脳波の値
            if k>waveMax or k<waveMin:
                tempList.append(position)  # k値は過大か過小ならこのトリガーを除外
                pass
            trialList.append(k)            # trialListは波形のもの
            pass
            
        # トライアルリストのデータ（1トリガー前後1200ms間のデータ）をセッションリストに導入
        sessionList.append(trialList)
        # トライアルリストを初期化
        trialList = []
        # ポジションのカウンターを累進
        position = position + 1
        pass

    # 重複要素を削除
    tempList = list(set(tempList))
    # ソーティング
    tempList.sort()
    # 「012345」から「123456」に変換
    for i in tempList:
        i = i + 1
        badList.append(i)
        pass
    print('\n'+"外れるトリガーは",'\n',badList)
    return sessionList


# メインプログラム
# Standard
# トリガー抽出
print('\n'+"Standard トリガー抽出開始……")
stdList = triggerExtract(std)
# 外れ値検出 & データ行列化
stdArray = np.array(triggerCheck(stdList))

# Target
# トリガー抽出
print('\n'+"Target トリガー抽出開始……")
tgtList = triggerExtract(tgt)
# 外れ値検出 & データ行列化
tgtArray = np.array(triggerCheck(tgtList))


# 保存
np.savetxt(str(answer)+'std.csv',stdArray,delimiter=',')
np.savetxt(str(answer)+'tgt.csv',tgtArray,delimiter=',')

#print(stdArray.shape)
#print(tgtArray.shape)
#print(stdArray)
#np.savetxt('stdFed.csv',stdArray,delimiter=',')
#np.savetxt('tgtFed.csv',tgtArray,delimiter=',')