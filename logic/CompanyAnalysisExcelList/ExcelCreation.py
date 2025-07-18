import os
import shutil
import pandas as pd

# パスの定義
csv_path = r"data\input\通期業績の推移、指標の取得\競合判定結果.csv"
source_excel = "data/input/企業分析.xlsx"
output_root = "data/output/分析"

# CSV読み込み
df = pd.read_csv(csv_path, encoding="utf-8")  # 必要に応じて encoding="shift-jis"

# 2行目（0インデックス）の1列目・2列目取得してフォルダ名に
row = df.iloc[0]
folder_name = f"{row[0]}_{row[1]}"
file_name = f"{folder_name}_企業分析.xlsx"  # 新しいファイル名にリネーム

# フォルダ作成
folder_path = os.path.join(output_root, folder_name)
os.makedirs(folder_path, exist_ok=True)

# コピー先の完全パス（リネーム付き）
destination_path = os.path.join(folder_path, file_name)

# Excelファイルをコピー＆リネーム
try:
    shutil.copy2(source_excel, destination_path)
    print(f"コピー成功: {destination_path}")
except Exception as e:
    print(f"コピー失敗: {e}")
