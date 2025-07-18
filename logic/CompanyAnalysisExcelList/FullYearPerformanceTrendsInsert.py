import os
import pandas as pd
import xlwings as xw

# === パス定義 ===
csv_path = r"data\input\通期業績の推移、指標の取得\競合判定結果.csv"
input_excel = r"data/output/競合他社との通期業績比較/通期業績推移.xlsx"
output_root = r"data/output/分析"

print(f"判定CSV読込: {csv_path}")
df_csv = pd.read_csv(csv_path, encoding="utf-8")

print(f"業績推移Excel読込: {input_excel}")
df_input = pd.read_excel(input_excel, header=0)
headers = df_input.columns.tolist()
data_rows = df_input.values.tolist()  # 全データ行

# 1行目でフォルダ・ファイル特定
row = df_csv.iloc[0]
folder_key = f"{row[0]}_{row[1]}"
target_xlsx = f"{folder_key}_企業分析.xlsx"
folder_path = os.path.join(output_root, folder_key)
target_xlsx_path = os.path.join(folder_path, target_xlsx)

print(f"\n対象フォルダ: {folder_path}")
print(f"対象Excel: {target_xlsx_path}")

if os.path.exists(target_xlsx_path):
    print("→ Excelファイル発見、xlwingsで処理開始...")
    app = xw.App(visible=False)
    wb = app.books.open(target_xlsx_path)

    # 他社比較シート取得
    if "他社比較" in [s.name for s in wb.sheets]:
        sht = wb.sheets["他社比較"]
        print("→ '他社比較'シート有。")
    else:
        sht = wb.sheets.add("他社比較")
        print("→ '他社比較'シート新規作成。")

    start_col = 2  # B列
    start_row = 37 # 37行目

    # ヘッダー埋め込み（B37, C37, ... 横展開）
    sht.range((start_row, start_col)).options(expand='right').value = headers

    # データ埋め込み（B38, C38, ... → 1行目データ、B39, ... → 2行目データ）
    for row_idx, data_row in enumerate(data_rows):
        sht.range((start_row + 1 + row_idx, start_col)).options(expand='right').value = data_row

    wb.save()
    wb.close()
    app.quit()
    print("→ 書き込み・保存完了。")
else:
    print(f"× 指定Excelファイルが存在しません: {target_xlsx_path}")

print("\n処理終了")
