import subprocess
import os

#競合他社の銘柄コードをcsv出力し通期業績の推移、指標の取得をする
#競合他社取得の参照サイト
#[日経経済新聞][四季報オンライン][株予報Pro]
# 対象の銘柄コード（ここを変えればどの銘柄でも一括取得可能）
scode = "2975"
name = "スター・マイカ・ホールディングス"
#最初にフォルダのファイルクリーンするためのパス
output_dir = f"data/output/競合他社の銘柄コード取得"

# サイトごとのスクリプトパス
scripts = [
    ["python", "logic/RivalFinder/NikkeiKeizaiShinbunRivalFinder.py", scode],
    ["python", "logic/RivalFinder/ShikihouOnlineRivalFinder.py", scode],
    ["python", "logic/RivalFinder/KabuyohoRivalFinder.py", scode],
    ["python", "logic/RivalFinder/BuffettCodeRivalFinder.py", scode],
]

# === ステップ①: 事前に出力ファイルを全削除 ===
def delete_all_files_in_folder(folder_path):
    if not os.path.exists(folder_path):
        print(f"[WARN] フォルダが存在しません: {folder_path}")
        return

    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        if os.path.isfile(file_path):
            try:
                os.remove(file_path)
                print(f"[INFO] 削除: {file_path}")
            except Exception as e:
                print(f"[ERROR] 削除失敗: {file_path} -> {e}")

#フォルダの中身クリーン
delete_all_files_in_folder(output_dir)


# ===実行
for cmd in scripts:
    print(f"[RUNNING] {' '.join(cmd)}")
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] 実行失敗: {e}")



# === 統合バッチの実行（競合データのマージ） ===
input_dir = f"data/output/競合他社の銘柄コード取得"
output_file = f"data\input\通期業績の推移、指標の取得\検索銘柄.csv"
dedup_cols = ["銘柄コード"]

merge_cmd = ["python", "utils/MergeFilesBatch.py", input_dir, output_file] + dedup_cols

print(f"[RUNNING] {' '.join(merge_cmd)}")
try:
    subprocess.run(merge_cmd, check=True)
except subprocess.CalledProcessError as e:
    print(f"[ERROR] 統合処理失敗: {e}")
#===ファイル統合後比較したい大本の銘柄を先頭に追加する===
try:
    subprocess.run(merge_cmd, check=True)

    # 統合成功後に2行目追加
    insert_row = [scode.strip(), name.strip().splitlines()[0].split(",")[0]]

    with open(output_file, "r", encoding="utf-8-sig") as f:
        lines = f.readlines()

    if len(lines) >= 1:
        header = lines[0]
        rest = lines[1:]
        new_line = ",".join(insert_row) + "\n"
        lines = [header, new_line] + rest

    with open(output_file, "w", encoding="utf-8-sig") as f:
        f.writelines(lines)

    print(f"[DONE] 2行目に {insert_row} を追加しました")

except subprocess.CalledProcessError as e:
    print(f"[ERROR] 統合処理失敗: {e}")



# === 通期の業績推移を取得実行 ===
# パスと引数
input_csv = "data/input/通期業績の推移、指標の取得/検索銘柄.csv"
output_excel = "data/output/競合他社との通期業績比較/通期業績推移.xlsx"
script_path = "logic/sites/KabuPredictor.py"

# コマンド構築
cmd = ["python", script_path, input_csv, output_excel]

# 実行
print(f"[RUNNING] {' '.join(cmd)}")
try:
    subprocess.run(cmd, check=True)
    print("[DONE] KabuPredictor 正常終了")
except subprocess.CalledProcessError as e:
    print(f"[ERROR] KabuPredictor 実行失敗: {e}")


# === 競合他社との指標比較を取得実行 ===
# パスと引数
input_csv = "data/input/通期業績の推移、指標の取得/競合判定結果.csv"
output_excel = "data/output/競合他社との通期業績比較/指標比較.xlsx"
script_path = "logic/sites/Stock_Quotes.py"

# コマンド構築
cmd = ["python", script_path, input_csv, output_excel]

# 実行
print(f"[RUNNING] {' '.join(cmd)}")
try:
    subprocess.run(cmd, check=True)
    print("[DONE] Stock_Quotes 正常終了")
except subprocess.CalledProcessError as e:
    print(f"[ERROR] Stock_Quotes 実行失敗: {e}")


# === 競合他社とのEV/EBITDA取得を実行 ===
import subprocess

# パスと引数
input_csv = "data/input/通期業績の推移、指標の取得/検索銘柄.csv"
output_csv = "data/output/競合他社との通期業績比較/株テク_EV_EBITDA.xlsx"
script_path = "logic/RivalFinder/Select_EV_EBITDA.py"

# コマンド構築
cmd = ["python", script_path, input_csv, output_csv]

# 実行
print(f"[RUNNING] {' '.join(cmd)}")
try:
    subprocess.run(cmd, check=True)
    print("[DONE] Select_EV_EBITDA 正常終了")
except subprocess.CalledProcessError as e:
    print(f"[ERROR] Select_EV_EBITDA 実行失敗: {e}")