import subprocess
import os
import pandas as pd

# 実行したいスクリプトの順番（相対パス指定）
batch_list = [
    "logic/CompanyAnalysisExcelList/ExcelCreation.py",
    "logic/CompanyAnalysisExcelList/IndexComparisonInsert.py",
    "logic/CompanyAnalysisExcelList/EV_EBITDAInsert.py",
    "logic/CompanyAnalysisExcelList/FullYearPerformanceTrendsInsert.py",
    "logic/DCF/EmbedInDCFExcel.py"
]

for script in batch_list:
    print(f"\n----- {script} 実行開始 -----")
    ret = subprocess.run(["python", script])
    if ret.returncode == 0:
        print(f"----- {script} 実行完了 -----")
    else:
        print(f"× {script} でエラーが発生しました")
        break  # エラーが出たら以降は停止したい場合


output_root = r"data/output/分析"
csv_path = r"data\input\通期業績の推移、指標の取得\競合判定結果.csv"

# 判定CSV読込→企業分析ファイル特定
df_csv = pd.read_csv(csv_path, encoding="utf-8")
row = df_csv.iloc[0]
folder_key = f"{row[0]}_{row[1]}"
target_xlsx = f"{folder_key}_企業分析.xlsx"
folder_path = os.path.join(output_root, folder_key)
target_xlsx_path = os.path.join(folder_path, target_xlsx)

# Excelファイルを開く
if os.path.exists(target_xlsx_path):
    os.startfile(target_xlsx_path)
    print(f"ファイルを開きました: {target_xlsx_path}")
else:
    print(f"ファイルが存在しません: {target_xlsx_path}")
