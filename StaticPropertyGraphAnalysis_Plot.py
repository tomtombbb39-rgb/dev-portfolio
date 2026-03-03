#%% --- コードの説明＆実行上の注意 ---
"""
--- 関数について ---
run_classはファイル名にあった処理クラスを選択する関数です。
処理クラスにはIdVd,IdVg,IfVf,BVの4種類があります。
それぞれのクラスにはdata()とgraph()という名前の関数があり、data()は解析データ表示、graph()はグラフ作成を担当しています。
初期状態ではどちらの関数も記述していますがデータ表示だけさせたければobj.graph()をコメントアウト、
グラフ表示だけさせたければobj.data()をコメントアウトなどして対応してください。

IdVdを除いて閾値電流Ithは以下のように設定されていますが、変更したいときは obj = run_class(file, Ith = 〇)としてください
初期設定 | IdVg:20[mA], IfVf:-20[mA], BV:100[µA] |

IfVfは第三象限にプロットされるため、そのままだと片対数プロットにできません。片対数プロットにしたい場合は
obj.graph(xlim, ylim, abs_mode = True)とし、plt.yscale("log")のコメントアウトを解除してください。
こうするとvoltage, currentの絶対値をとります。書いていない場合はFalseで処理されます。
-------------------

--- グラフ設定を追加する場合 ---
run_classにキーワード引数を追加するとグラフ設定ができます
凡例：label = "ラベル名"
プロット線：line_style = "(線の種類)"   ←   破線："--", 点線：":", 一点鎖点："-."
線色：color = "(色)"   ←   "red", "blue" など
------------------------------

--- ファイルの命名規則は以下のようになっています。 ---
デバイス名_測定内容_測定条件.csv
測定内容：IdVd, IdVg, IfVf, BV
例）Wolfspeed_IfVf_Vgs-4V_1.csv
--------------------------------------------------

[注意]
解析＆グラフのコードの記述順序はなるべく変更しないでください。正しく動作しなくなる可能性があります。
特にplt.yscale("log")はobj.graphよりも先に実行すること。
(obj.graphは軸の種類によって軸の範囲を選択する関数を引き継いでいるので、先に軸スケールは設定しておく必要がある)
引数の型などはdocstringを参照
"""


#%% --- 一つのファイル実行 ---
import matplotlib.pyplot as plt
from STClass import run_class
from STClass import Common

# --- ファイルを指定 ---
file = "file_path.csv"    #ファイルのパスを指定してください

# --- グラフ軸範囲 ---
#(Noneにすると自動設定)
xlim = None   #横軸最大値[V]
ylim = None   #縦軸最大値[A/cm2]

# --- 解析＆グラフ ---
obj = run_class(file)
Common.set_rcParams()
obj.data()
#plt.yscale("log")
obj.graph(xlim, ylim, abs_mode = True)    #IfVfでは[,abs_mode=True]追加
#plt.title("IfVf")    #グラフのタイトル
plt.show()



# %% --- 測定デバイスをまとめて解析 ---
import os
import glob
import matplotlib.pyplot as plt
from STClass import run_class
from STClass import ResultCollector
import DeviceData as dd
# --- ファイルのあるディレクトリを指定 ---
file_dir = "file_directory_path"    #ファイルのあるディレクトリを指定してください

#--- ファイル指定 ---
for device in dd.devices:
    collector = ResultCollector()

    for num in dd.nums:
        pattern = os.path.join(file_dir, f"{device}_IdVd_{num}.csv")
        matched_files = glob.glob(pattern)

        for file in matched_files:
            obj = run_class(file, label = f"device{num}")    #ラベルなどはここで
            collector.call_and_store(obj)

    collector.display_result()




#%%  --- 測定デバイスをまとめてプロット ---
import os
import glob
import matplotlib.pyplot as plt
import itertools
from STClass import run_class
from STClass import Common
import DeviceDataPydantic as dd
# --- ファイルのあるディレクトリを指定 ---
file_dir = "file_directory_path"    #ファイルのあるディレクトリを指定してください

# --- グラフ軸範囲 ---
#(Noneにすると自動設定)
xlim = None   #横軸最大値[V]
ylim = None   #縦軸最大値[A/cm2]

color_cycle = plt.rcParams['axes.prop_cycle'].by_key()['color']
color_iter = itertools.cycle(color_cycle)
device_color_map = {}
Common.set_rcParams()

for device in dd.devices:
    if device not in device_color_map:
        device_color_map[device] = next(color_iter)

    label = f"{device}"
    pattern = os.path.join(file_dir, f"{device}_IfVf_1.csv")
    matched_files = glob.glob(pattern)

    for file in matched_files:
        color = device_color_map[device]
        obj = run_class(file, label=label, color=color,abs_mode=True, Jth = 400)    #IfVfでは[,abs_mode=True]追加
        #plt.yscale("log")
        obj.graph(xlim, ylim)
        obj.data()
plt.legend(frameon=False)    #判例が入らないときは[, bbox_to_anchor=(1.05, 0.8)]をplt.legendに追加
#plt.title("IfVf")    #グラフのタイトル
#plt.savefig("graph.svg", bbox_inches='tight')    #svgにしたいとき用
plt.show()




# %% --- 温度振りグラフ＆解析データ ---
import os
import glob
import matplotlib.pyplot as plt
import itertools
from STClass import run_class
from STClass import Common
import DeviceData as dd

# --- ファイルのあるディレクトリを指定 ---
file_dir = "file_directory_path"    #ファイルのあるディレクトリを指定してください

# --- グラフ軸範囲 ---
#(Noneにすると自動設定)
xlim = None   #横軸最大値[V]
ylim = None   #縦軸最大値[A/cm2]

color_cycle = plt.rcParams['axes.prop_cycle'].by_key()['color']
color_iter = itertools.cycle(color_cycle)
device_color_map = {}

for device in dd.devices:
    if device not in device_color_map:
        device_color_map[device] = next(color_iter)

    for temp in dd.temps:
        label = f"{device}:RT" if temp == '' else f"{device}:175℃"    #ファイルの命名則変更したらこちらも変更
        line_style = "-" if temp == "" else "--"
        pattern = os.path.join(file_dir, f"{device}_IdVg_{temp}_1.csv")
        matched_files = glob.glob(pattern)

        for file in matched_files:
            color = device_color_map[device]
            obj = run_class(file, label=label, line_style=line_style, color=color)    #IfVfでは[,abs_mode=True]追加
            plt.yscale("log")
            obj.graph(xlim, ylim)
            obj.data()
plt.legend(frameon=False)    #判例が入らないときは[, bbox_to_anchor=(1.05, 0.8)]をplt.legendに追加
#plt.title("")    #グラフのタイトル
#plt.savefig("graph.svg", bbox_inches='tight')    #svgにしたいとき用
plt.show()




# %%
