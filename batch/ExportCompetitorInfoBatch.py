import subprocess

# 対象の銘柄コード（ここを変えればどの銘柄でも一括取得可能）
scode = "3135"

# サイトごとのスクリプトパス
scripts = [
    # ["python", "batch/site1_rivals.py", scode],
    ["python", "logic/sites/NikkeiKeizaiShinbunRivalFinder.py", scode]
    # ["python", "batch/site3_rivals.py", scode]
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
