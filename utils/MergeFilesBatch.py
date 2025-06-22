import sys
import os
import pandas as pd

def merge_csv_files(input_dir, output_path, dedup_columns=None):
    import pandas as pd
    import os

    if not os.path.exists(input_dir):
        print(f"[ERROR] 入力ディレクトリが存在しません: {input_dir}")
        return

    merged_df = pd.DataFrame()
    count = 0

    for filename in os.listdir(input_dir):
        filepath = os.path.join(input_dir, filename)
        if os.path.isfile(filepath) and filename.lower().endswith(".csv"):
            try:
                df = pd.read_csv(filepath, dtype=str)
                merged_df = pd.concat([merged_df, df], ignore_index=True)
                print(f"[INFO] 読み込み成功: {filename}")
                count += 1
            except Exception as e:
                print(f"[WARN] 読み込み失敗: {filename} -> {e}")

    if count == 0:
        print("[WARN] CSVファイルが見つかりませんでした。処理終了。")
        return

    # ✅ 一般化された重複排除
    if dedup_columns:
        merged_df.drop_duplicates(subset=dedup_columns, inplace=True)
        print(f"[INFO] 重複排除済み: {dedup_columns}")

    # 保存
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    merged_df.to_csv(output_path, index=False, encoding='utf-8-sig')
    print(f"[DONE] 統合ファイルを出力しました: {output_path}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("使い方: python merge_rivals_batch.py <入力フォルダ> <出力ファイルパス> [重複排除カラム1 カラム2 ...]")
        sys.exit(1)

    input_dir = sys.argv[1]
    output_file = sys.argv[2]
    dedup_columns = sys.argv[3:] if len(sys.argv) > 3 else None

    merge_csv_files(input_dir, output_file, dedup_columns)


