import os
import pandas as pd
import xlwings as xw

# === パス定義 ===
csv_path = r"data\input\通期業績の推移、指標の取得\競合判定結果.csv"
input_excel = r"data/output/競合他社との通期業績比較/ヤフーファイナンス_財務_キャッシュフロー.xlsx"
output_root = r"data/output/分析"

# 判定CSV読込→企業分析ファイル特定
df_csv = pd.read_csv(csv_path, encoding="utf-8")
row = df_csv.iloc[0]
folder_key = f"{row[0]}_{row[1]}"
target_xlsx = f"{folder_key}_企業分析.xlsx"
folder_path = os.path.join(output_root, folder_key)
target_xlsx_path = os.path.join(folder_path, target_xlsx)

print(f"対象Excel: {target_xlsx_path}")

# 入力Excel（ヤフーファイナンス）読込
with pd.ExcelFile(input_excel) as xls:
    df_hakkou = pd.read_excel(xls, sheet_name="発行済株式数")
    df_zaimu = pd.read_excel(xls, sheet_name="財務")
    df_cf = pd.read_excel(xls, sheet_name="キャッシュフロー")

if not os.path.exists(target_xlsx_path):
    print(f"× 指定Excelファイルが存在しません: {target_xlsx_path}")
    exit()

print("→ Excelファイル発見、xlwingsで処理開始...")
app = xw.App(visible=False)
wb = app.books.open(target_xlsx_path)

# 「DCF」シート
if "DCF" in [s.name for s in wb.sheets]:
    sht = wb.sheets["DCF"]
    print("→ 'DCF'シート有。")
else:
    sht = wb.sheets.add("DCF")
    print("→ 'DCF'シート新規作成。")

# ① 発行済株式数（B48～）
sht.range("B48").options(index=False, header=True).value = df_hakkou

# ② 財務（B52～）
sht.range("B52").options(index=False, header=True).value = df_zaimu

# ③ キャッシュフロー（B58～）
sht.range("B58").options(index=False, header=True).value = df_cf

wb.save()
wb.close()
app.quit()
print("→ 書き込み・保存完了。")
