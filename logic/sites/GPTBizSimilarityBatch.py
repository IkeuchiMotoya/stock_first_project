import pandas as pd
import sys
import json
import openai
import io
import os

# ==== 設定 ====
CSV_PATH = "data/input/通期業績の推移、指標の取得/検索銘柄.csv"
RAW_RESPONSE_PATH = "data/output/競合判定結果.csv"
MODEL = "gpt-4o"
SECRETS_PATH = "secrets.json"

# ==== 引数チェック ====
if len(sys.argv) != 3:
    print("使い方: python GPTBizSimilarityBatch.py <基準銘柄コード> <基準銘柄名>")
    sys.exit(1)

base_code = sys.argv[1]
base_name = sys.argv[2]

# ==== APIキー読み込み ====
if not os.path.exists(SECRETS_PATH):
    print(f"[エラー] {SECRETS_PATH} が見つかりません")
    sys.exit(1)

with open(SECRETS_PATH, "r", encoding="utf-8") as f:
    secrets = json.load(f)

if "openai_api_key" not in secrets:
    print("[エラー] secrets.json に 'openai_api_key' が含まれていません")
    sys.exit(1)

openai.api_key = secrets["openai_api_key"]

# ==== CSV読み込み ====
df = pd.read_csv(CSV_PATH, dtype=str)
if "銘柄コード" not in df.columns or "銘柄名" not in df.columns:
    print("CSVには '銘柄コード' と '銘柄名' カラムが必要です")
    sys.exit(1)

compare_targets = [
    f"{row['銘柄名']}（{row['銘柄コード']}）"
    for _, row in df.iterrows()
    if row["銘柄コード"] != base_code
]

content = f"""あなたは業界分析の専門家です。
以下の【基準銘柄】と【比較銘柄リスト】について、業種・事業内容・市場の観点から、
それぞれ『競合』『類似』『無関係』のいずれかで分類し、理由と業種カテゴリを添えてください。

【出力形式（必ず守ってください）】
CSV形式で出力してください。先頭行は次のカラム構成です：

銘柄コード, 銘柄名, 分類, 理由


【基準銘柄】：{base_name}（{base_code}）

【比較銘柄リスト】：
{', '.join(compare_targets)}

【分類基準】
- 「競合」：同一市場または類似のビジネスモデルで、顧客・シェアを争う可能性がある。
- 「類似」：事業モデルや業種は近いが直接の競合ではない。
- 「無関係」：業種や事業モデルが異なり、直接的な関係がない。

【理由について】
- 各理由は100文字以上で具体的に書いてください。
- 「SaaSによる物件管理」「サブリース型の住宅提供」など、特徴的なキーワードを盛り込んでください。
"""



# ==== OpenAI API呼び出し ====
response = openai.chat.completions.create(
    model=MODEL,
    messages=[
        {"role": "system", "content": "あなたは業界分析の専門家です。"},
        {"role": "user", "content": content}
    ],
    temperature=0.3,
)

result_text = response.choices[0].message.content

# ==== 不要な行削除 ====
cleaned_lines = []
start_found = False
for line in result_text.splitlines():
    # ヘッダー行が見つかるまではスキップ
    if not start_found:
        if "銘柄コード" in line and "分類" in line:
            start_found = True
            cleaned_lines.append(line)
        continue
    # ヘッダー以降の処理
    if line.strip() == "" or line.strip().startswith("※") or "---" in line or line.strip().startswith("```"):
        continue
    cleaned_lines.append(line)

cleaned_csv_text = "\n".join(cleaned_lines)

# ==== CSVファイルとして保存 ====
try:
    df_result = pd.read_csv(io.StringIO(cleaned_csv_text))
    df_result.to_csv(RAW_RESPONSE_PATH, index=False, encoding="utf-8-sig")
    print(f"[完了] 結果を {RAW_RESPONSE_PATH} に出力しました。")
except Exception as e:
    print("[エラー] 出力CSVの保存に失敗しました")
    print(e)
