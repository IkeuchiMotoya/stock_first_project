import xlwings as xw
import pandas as pd
import os

# === パス定義 ===
csv_path = r"data\input\通期業績の推移、指標の取得\競合判定結果.csv"
input_excel = r"data/output/競合他社との通期業績比較/株テク_EV_EBITDA.xlsx"
output_root = r"data/output/分析"

# CSV読み込み
df_csv = pd.read_csv(csv_path, encoding="utf-8")

# インプットExcel C列取得（1行目から）
df_input = pd.read_excel(input_excel, header=None)
c_values = df_input.iloc[:, 2].tolist()

# 対象ファイルの特定
row = df_csv.iloc[0]
folder_key = f"{row[0]}_{row[1]}"
target_xlsx = f"{folder_key}_企業分析.xlsx"
folder_path = os.path.join(output_root, folder_key)
target_xlsx_path = os.path.join(folder_path, target_xlsx)

print(f"編集対象: {target_xlsx_path}")

# xlwingsでExcelファイルを開く
app = xw.App(visible=False)
wb = app.books.open(target_xlsx_path)

# シート取得
if "他社比較" in [s.name for s in wb.sheets]:
    sht = wb.sheets["他社比較"]
else:
    sht = wb.sheets.add("他社比較")

# O4から縦に値を書き込む
for i, value in enumerate(c_values):
    sht.range(f"O{4+i}").value = value

wb.save()
wb.close()
app.quit()

print("グラフや色を壊さずに値のみ書き換え完了。")
