"""静特性解析コード
"""
import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
import DeviceData as dd
from abc import ABC, abstractmethod


# --- グラフ＆解析の共通処理抽象クラス ---
class Base(ABC):
    @abstractmethod
    def graph(self):
        pass
    @abstractmethod
    def data(self):
        pass

#--- ファイルの読み込みクラス ---
class ReadFile:
    def __init__(self, file: str):
        self.file = file

    def read_file(self, abs_mode: bool = False):
        """測定ファイルの読み込み

        Args:
            abs_mode (bool, optional): Trueの場合、IfVfデータの電流と電圧を絶対値に変換する。デフォルトはFalse。

        Raises:
            ValueError: ファイルパスが無効
            IndexError: CSVファイルの列数が不足

        Returns:
            voltage (np.ndarray): 読み込んだ電圧データ\n
            current (np.ndarray): 読み込んだ電流データ\n
            density (np.ndarray): 電流密度（current / device.area * 1e-4）\n
            device_name (str): デバイス名（ファイル名の先頭部分）\n
            data_type (str): データ種類（IdVd, IdVg, IfVf, BV のいずれか）
        """
        df = pd.read_csv(self.file, skiprows=47, header=None)
        file_name = os.path.basename(self.file)
        if not isinstance(self.file, str) or not self.file:
            raise ValueError("ファイルパスが無効です。")
        
        device_name = file_name.split("_")[0]
        device = getattr(dd, device_name)        #DeviceData内からDevice_nameと一致する文字列をもってくる(device.areaを使用するため)

        data_type = file_name.split("_")[1]
        #データが保存されている行
        actions = {"IdVd":[9, 12],
                   "IdVg":[3, 12],
                   "IfVf":[9, 12],
                   "BV"  :[6, 9]
                   }
        try:
            current = df.iloc[:, actions[data_type][0]].values
            voltage = df.iloc[:, actions[data_type][1]].values

            if data_type == "IfVf" and abs_mode:    #IfVfは絶対値モードを追加　引数でモードON,OFFを切り替え
                current = np.abs(current)
                voltage = np.abs(voltage)
        except IndexError:
            raise IndexError("CSVファイルの列数が不足しています。必要な列が見つかりません。")
        
        density = current / device.area *1e-4

        self.voltage = voltage
        self.current = current
        self.density = density
        self.device_name = device_name
        return voltage, current, density, device_name, data_type
        
#--- 共通処理＆設定クラス ---
class Common(ReadFile):
    def __init__(self, file: str, label: str, line_style: str, color: str, abs_mode: bool = False):
        super().__init__(file)
        self.voltage, self.current, self.density, self.device_name, self.data_type = self.read_file(abs_mode=abs_mode)
        self.label = label
        self.line_style = line_style
        self.color = color
        self.abs_mode = abs_mode
        
    def plot(self):
        """グラフ表示
        ラベル・ラインスタイル・線色を設定
        """
        plot_kwargs = {}

        if self.label is not None:
            plot_kwargs['label'] = f"   {self.label}"
        if self.line_style is not None:
            plot_kwargs['linestyle'] = self.line_style
        if self.color is not None:
            plot_kwargs['color'] = self.color

        plt.plot(self.voltage, self.density, **plot_kwargs)

    def graph_scale(self, xlim: int|None = None, ylim: int|None = None):
        """グラフスケール設定

        Args:
            xlim (int or float, optional): x軸の最大値。Noneにすると自動で設定。
            ylim (int or float, optional): y軸の最大値. Noneにすると自動で設定。
        """

        ax = plt.gca()
        if ax.get_yscale() != "log":
            if xlim is None and ylim is None:
                xmax = plt.xlim()[1]
                ymax = plt.ylim()[1]

            if xlim is not None and ylim is not None:
                xmax = xlim
                ymax = ylim

            if xlim is None and ylim is not None:
                xmax = plt.xlim()[1]
                ymax = ylim

            if xlim is not None and ylim is None:
                xmax = xlim
                ymax = plt.ylim()[1]

            plt.ylim(0, ymax)
            plt.xlim(0, xmax)

        if ax.get_yscale() == "log":
            if xlim is None and ylim is None:
                xmax = plt.xlim()[1]
                ymax = plt.ylim()[1]

            if xlim is not None and ylim is not None:
                xmax = xlim
                ymax = ylim

            if xlim is None and ylim is not None:
                xmax = plt.xlim()[1]
                ymax = ylim

            if xlim is not None and ylim is None:
                xmax = xlim
                ymax = plt.ylim()[1]

            plt.ylim(plt.ylim()[0], ymax)
            plt.xlim(plt.xlim()[0], xmax)

    def ifvf_graph_scale(self, xlim: int|float|None = None, ylim: int|float|None = None):
        """ifvf用のグラフスケール設定

        Args:
            xlim (int or float, optional): x軸の最大値。Noneにすると自動で設定。
            ylim (int or float, optional): y軸の最大値。Noneにすると自動で設定。
        """

        if xlim is None and ylim is None:
            xmin = plt.xlim()[0]
            ymin = plt.ylim()[0]

        if xlim is not None and ylim is not None:
            xmin = xlim
            ymin = ylim

        if xlim is None and ylim is not None:
            xmin = plt.xlim()[0]
            ymin = ylim

        if xlim is not None and ylim is None:
            xmin = xlim
            ymin = plt.ylim()[0]

        plt.ylim(ymin, 0)
        plt.xlim(xmin, 0)
    
    @staticmethod
    def set_rcParams():
        """グラフ描画設定。staticmethodになっています。
        """
        plt.rcParams["font.family"] = "Times New Roman"
        plt.rcParams["xtick.direction"] = "in"
        plt.rcParams["ytick.direction"] = "in"
        plt.rcParams["ytick.right"] = True
        plt.rcParams["xtick.top"] = True
        plt.rcParams["xtick.minor.visible"] = True
        plt.rcParams["ytick.minor.visible"] = True
        plt.rcParams["ytick.minor.right"] = True
        plt.rcParams["xtick.minor.top"] = True
        plt.rcParams["xtick.major.width"] = 1.5
        plt.rcParams["ytick.major.width"] = 1.5
        plt.rcParams["xtick.minor.width"] = 1.0
        plt.rcParams["ytick.minor.width"] = 1.0
        plt.rcParams["xtick.major.size"] = 8
        plt.rcParams["ytick.major.size"] = 8
        plt.rcParams["xtick.minor.size"] = 4
        plt.rcParams["ytick.minor.size"] = 4
        plt.rcParams["font.size"] = 18
        plt.rcParams["axes.linewidth"] = 1.5
        plt.rcParams["mathtext.default"] = "default"
        plt.rcParams["mathtext.fontset"] = "stix"
        plt.rcParams["legend.handletextpad"] = -0.5
        plt.rcParams['figure.dpi'] = 300
        plt.rcParams['savefig.dpi'] = 500
    
    def plot_graph(self, xlim: int|float|None = None, ylim: int|float|None = None):
        """グラフ＆プロット＆グラスケール設定まとめ
        整えたグラフを描画
        """
        self.set_rcParams()
        self.plot()
        self.graph_scale(xlim, ylim)

    def ifvf_plot_graph(self, xlim: int|float|None = None, ylim: int|float|None = None):
        """グラフ＆プロット＆グラフスケール設定まとめ
        (abs_modeがFalseの場合の設定)
        整えたグラフを描画
        """
        self.set_rcParams()
        self.plot()
        self.ifvf_graph_scale(xlim, ylim)

    def mask_data(self, mask: np.ndarray):
        """電流、電圧、電流密度のマスク

        Args:
            mask (np.ndarray): マスクをかける範囲

        Returns:
            filtered_current, filtered_voltage, filtered_density (np.ndarray): 範囲選択済みの電流、電圧、電流密度
        """
        filtered_current = self.current[mask]
        sort_idx = np.argsort(filtered_current)
        filtered_current = self.current[sort_idx]
        filtered_voltage = self.voltage[sort_idx]
        filtered_density = self.density[sort_idx]
        return filtered_current, filtered_voltage, filtered_density

# --- 以下、データ処理クラス＆集計用クラス・関数 ---

class IdVd(Base, Common):    #Common経由でReadFileを継承
    def __init__(self, file, label = None, line_style = None, color = None):
        super().__init__(file, label, line_style, color)

    def graph(self, xlim, ylim):
        """オン抵抗グラフ

        Args:
            xlim (int or float, optional): x軸の最大値。Noneにすると自動で設定。
            ylim (int or float, optional): y軸の最大値。Noneにすると自動で設定。
        """
        self.plot_graph(xlim, ylim)
        plt.ylabel("Drain Current Density [A/$cm^2$]")
        plt.xlabel("Drain Voltage [V]")

    def data(self):
        """オン抵抗算出

        Returns:
            Ron (float) : オン抵抗[Ω]
            Ron_sp (float) : 特性オン抵抗[Ω]
        """
        matches = np.where(self.current > 1.2)[0]
        if len(matches) == 0:
            return None, None
        coeffs_sp = np.polyfit(self.voltage[0:matches[0]], self.density[0:matches[0]], 1)    #currentが0~1.2Aの範囲を選択（あんまいらないかも）
        coeffs = np.polyfit(self.voltage[0:matches[0]], self.current[0:matches[0]], 1)

        Ron = 1/coeffs[0]*1e3
        Ron_sp = 1/coeffs_sp[0]*1e3

        label_str = f" ({self.label})" if self.label else ""
        print(f"{self.device_name}{label_str}")
        print(f"オン抵抗:{1/coeffs[0]*1e3:.2f}[mΩ]")
        print(f"特性オン抵抗:{1/coeffs_sp[0]*1e3:.2f}[mΩ]\n")
        
        return Ron, Ron_sp

class IdVg(Base, Common):    #Common経由でBase, ReadFileを継承
    def __init__(self, file, Ith = None, Jth = None, label = None, line_style = None, color = None):
        super().__init__(file, label, line_style, color)
        self.Ith = Ith
        self.Jth = Jth

    def graph(self, xlim, ylim):
        """閾値グラフ

        Args:
            xlim (int or float, optional): x軸の最大値。Noneにすると自動で設定。
            ylim (int or float, optional): y軸の最大値。Noneにすると自動で設定。
        """
        self.plot_graph(xlim, ylim)
        plt.ylabel("Drain Current Density [A/$cm^2$]")
        plt.xlabel("Gate Voltage [V]")

    def data(self):
        """閾値電圧算出

        Returns:
            Vth (float) : 閾値電圧[V]
        """
        mask = self.current > 1e-4    #ノイズ領域をフィルター(このあとnp.interpを使用するため)
        #今は電流値でmaskをかけているけど活性面積が大きく異なるデバイス(DioMOSなど)を使用するときは電流密度を合わせる方が良いかも
        filtered_current, filtered_voltage, filtered_density = self.mask_data(mask)

        if self.Jth is None:
            self.Ith = 20 if self.Ith is None else self.Ith   #未設定時閾値電流は20mAに設定

            Vth = np.interp(self.Ith*1e-3, filtered_current, filtered_voltage)
        
        #電流密度で比較する場合
        else:
            Vth = np.interp(self.Jth, filtered_density, filtered_voltage)

        label_str = f" ({self.label})" if self.label else ""
        print(f"{self.device_name}{label_str}")
        print(f"閾値電圧:{Vth:.2f}[V]   (Ith = {self.Ith}[mA])\n") if self.Jth is None else print(f"閾値電圧:{Vth:.2f}[V]   (Jth = {self.Jth}[A/$cm^2$])\n")
        return Vth

class IfVf(Base, Common):    #Common経由でBase, ReadFileを継承
    def __init__(self, file, Ith = None, Jth = None, label = None, line_style = None, color = None, abs_mode=False):
        super().__init__(file, label, line_style, color, abs_mode=abs_mode)
        self.Ith = Ith
        self.Jth = Jth
        self.abs_mode = abs_mode

    def graph(self, xlim, ylim, abs_mode = None):
        """内蔵ダイオード順方向グラフ

        Args:
            xlim (int or float, optional): x軸の最大値。Noneにすると自動で設定。
            ylim (int or float, optional): y軸の最大値。Noneにすると自動で設定。
            abs_mode (bool, optional): Trueの場合、IfVfデータの電流と電圧を絶対値に変換する。デフォルトはFalse。
        """
        if abs_mode is None:
            abs_mode = self.abs_mode

        if abs_mode:
            self.voltage, self.current, self.density, self.device_name, self.data_type = self.read_file(abs_mode=True)
            self.plot_graph(xlim, ylim)
        else:
            self.ifvf_plot_graph(xlim, ylim)
        plt.ylabel("Forward Current Density [A/$cm^2$]")
        plt.xlabel("Forward Voltage [V]")

    def data(self, abs_mode = None):
        """ダイオード閾値電圧算出

        Returns:
            Vth (float) : ダイオード閾値電圧[V]
        """
        
        if abs_mode is None:
            abs_mode = self.abs_mode

        if abs_mode:
            mask = self.current > 1e-2    #ノイズ領域をフィルター(このあとnp.interpを使用するため)
            #今は電流値でmaskをかけているけど活性面積が大きく異なるデバイス(DioMOSなど)を使用するときは電流密度を合わせる方が良いかも
            filtered_current, filtered_voltage, filtered_density = self.mask_data(mask)

            if self.Jth is None:
                self.Ith = -20 if self.Ith is None else self.Ith   #未設定時閾値電流は-20mAに設定

                Vth = np.interp(-self.Ith*1e-3, filtered_current, filtered_voltage)
            
            #電流密度で比較する場合
            else:
                Vth = np.interp(self.Jth, filtered_density, filtered_voltage)

            label_str = f" ({self.label})" if self.label else ""
            print(f"{self.device_name}{label_str}")
            print(f"ダイオード閾値電圧:{-Vth:.2f}[V]   (Ith = {self.Ith}[mA])\n") if self.Jth is None else print(f"ダイオード閾値電圧:{Vth:.2f}[V]   (Jth = {self.Jth}[A/$cm^2$])\n")
            Vth = -Vth
        else:
            mask = self.current < -1e-2
            filtered_current, filtered_voltage, filtered_density = self.mask_data(mask)

            if self.Jth is None:
                self.Ith = -20 if self.Ith is None else self.Ith   #未設定時閾値電流は-20mAに設定

                Vth = np.interp(self.Ith*1e-3, filtered_current, filtered_voltage)
            
            #電流密度で比較する場合
            else:
                Vth = np.interp(-self.Jth, filtered_density, filtered_voltage)

            label_str = f" ({self.label})" if self.label else ""
            print(f"{self.device_name}{label_str}")
            print(f"ダイオード閾値電圧:{Vth:.2f}[V]   (Ith = {self.Ith}[mA])\n") if self.Jth is None else print(f"ダイオード閾値電圧:{Vth:.2f}[V]   (Jth = {self.Jth}[A/$cm^2$])\n")
            Vth = -Vth
        
        return Vth

class BV(Base, Common):    #Common経由でBase, ReadFileを継承
    def __init__(self, file, Ith = None, Jth = None, label = None, line_style = None, color = None):
        super().__init__(file, label, line_style, color)
        self.Ith = Ith
        self.Jth = Jth

    def graph(self, xlim, ylim):
        """耐圧グラフ

        Args:
            xlim (int or float, optional): x軸の最大値。Noneにすると自動で設定。
            ylim (int or float, optional): y軸の最大値。Noneにすると自動で設定。
        """
        self.plot_graph(xlim, ylim)
        plt.ylabel("Drain Current Density [A/$cm^2$]")
        plt.xlabel("Drain Voltage [V]")

    def data(self):
        """耐圧算出

        Returns:
            Vth (float) : 耐圧[V]
        """
        mask = self.current > 1e-7    #ノイズ領域をフィルター(このあとnp.interpを使用するため)
        #今は電流値でmaskをかけているけど活性面積が大きく異なるデバイス(DioMOSなど)を使用するときは電流密度を合わせる方が良いかも
        filtered_current, filtered_voltage, filtered_density = self.mask_data(mask)

        if self.Jth is None:
            self.Ith = 100 if self.Ith is None else self.Ith   #未設定時閾値電流は100µAに設定

            Vth = np.interp(self.Ith*1e-6, filtered_current, filtered_voltage)
        
        #電流密度で比較する場合
        else:
            Vth = np.interp(self.Jth, filtered_density, filtered_voltage)

        label_str = f" ({self.label})" if self.label else ""
        print(f"{self.device_name}{label_str}")
        print(f"耐圧:{Vth:.0f}[V]   (Id = {self.Ith}[µA])\n") if self.Jth is None else print(f"耐圧:{Vth:.2f}[V]   (Jth = {self.Jth}[A/$cm^2$])\n")
        return Vth

# --- クラス選択関数 ---
def run_class(file, abs_mode = None, **kwargs):
    """ファイルに対応するクラスを選択する

    Args:
        file (str): 測定ファイル
        abs_mode (bool, optional): Trueの場合、IfVfデータの電流と電圧を絶対値に変換する。デフォルトはFalse。
        **kwargs (str): ラベル(label)・ラインスタイル(linestyle)・線色(color)を指定するキーワード変数

    Raises:
        ValueError: 対応クラスが見つからない場合

    Returns:
        obj (str): 測定ファイルに対応するクラス名

    Note:
        IdVdを除いて閾値電流Ithは以下のように設定されていますが、変更したいときは obj = run_class(file, Ith = 〇)としてください
        初期設定 | IdVg: 20[mA], IfVf: -20[mA], BV: 100[µA] |
    """

    reader = ReadFile(file)
    _, _, _, _, data_type = reader.read_file(abs_mode=abs_mode)

    cls = globals().get(data_type)    # data_type に対応するクラスを取得
    if cls is None:
        raise ValueError(f"対応するクラス {data_type} が見つかりません。")
    
    if abs_mode is not None:
        kwargs['abs_mode'] = abs_mode
    
    obj = cls(file, **kwargs)
    return obj

# --- 解析データ集計用クラス ---
class ResultCollector:
    def __init__(self):
        self.results = []

    def call_and_store(self, obj, method_name="data", **kwargs):
        """デバイスと解析データの紐づけ

        Args:
            obj (str): run_classで選択されたクラス名
            method_name (str, optional): 実行メソッド。Defaults to "data".
        """
        method = getattr(obj, method_name)
        result = method(**kwargs)
        device_name = getattr(obj, "device_name", "Unknown")
        class_name = obj.__class__.__name__  # 例: "IdVd", "IdVg", "IfVf", "BV"
        self.results.append((device_name, result, class_name))

    def display_result(self):
        """解析データの集計と表示
        """
        from collections import defaultdict

        grouped_results = defaultdict(list)
        class_names = {}

        for device_name, result, class_name in self.results:
            grouped_results[device_name].append(result)
            class_names[device_name] = class_name  # 1つのデバイスに1種類のデータ前提

        for device, result_list in grouped_results.items():
            class_name = class_names[device]
            n = len(result_list)
            print(f"{device} 集計")

            if class_name == "IdVd":
                rons = [r[0] for r in result_list]
                ron_sps = [r[1] for r in result_list]
                ron_avg = sum(rons) / n
                ron_sp_avg = sum(ron_sps) / n
                print(f"オン抵抗 ({n}素子の平均): {ron_avg:.2f} [mΩ]")
                print(f"特性オン抵抗 ({n}素子の平均): {ron_sp_avg:.2f} [mΩcm²]\n")

            elif class_name == "IdVg":
                vths = result_list
                vth_avg = sum(vths) / n
                print(f"閾値電圧 ({n}素子の平均): {vth_avg * 1e3:.2f} [mV]\n")

            elif class_name == "IfVf":
                vths = result_list
                vth_avg = sum(vths) / n
                print(f"ダイオード閾値電圧 ({n}素子の平均): {vth_avg:.2f} [V]\n")

            elif class_name == "BV":
                bvs = result_list
                bv_avg = sum(bvs) / n
                print(f"耐圧 ({n}素子の平均): {bv_avg:.0f} [V]\n")

            else:
                print(f"未対応のクラス: {class_name}")
            print()

