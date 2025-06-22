import subprocess

#競合他社の銘柄コードをcsv出力
#参照サイト
#[日経経済新聞][四季報オンライン][株予報Pro]
# 対象の銘柄コード（ここを変えればどの銘柄でも一括取得可能）
scode = "135A"

# サイトごとのスクリプトパス
scripts = [
    ["python", "logic/sites/NikkeiKeizaiShinbunRivalFinder.py", scode],
    ["python", "logic/sites/ShikihouOnlineRivalFinder.py", scode]
]

# 実行
for cmd in scripts:
    print(f"[RUNNING] {' '.join(cmd)}")
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] 実行失敗: {e}")

# 統合バッチも実行（競合データをまとめる処理）
merge_cmd = ["python", "batch/merge_rivals.py", scode]
print(f"[RUNNING] {' '.join(merge_cmd)}")
try:
    subprocess.run(merge_cmd, check=True)
except subprocess.CalledProcessError as e:
    print(f"[ERROR] 統合処理失敗: {e}")
