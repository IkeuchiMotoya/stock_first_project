import yfinance as yf
import pandas as pd
import csv
import os
from datetime import datetime

#場中決算発表反応銘柄
# 📥 CSVパス
import_path = r'data/input/決算発表後の反応/決算発表予定_2025-05-14.csv'

# 決算日取得（1行目の値）
with open(import_path, 'r', encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)
    rows = list(reader)
    if not rows:
        raise ValueError("CSVが空です")
    date_str = rows[0]['決算日']
    target_date = datetime.strptime(date_str, "%Y-%m-%d")

# 銘柄一覧作成
tickers = [row['銘柄コード'].strip() + '.T' for row in rows]
results = []

for ticker in tickers:
    try:
        print(f"\n=== {ticker} のデータ取得開始 ===")
        data = yf.download(
            ticker,
            start=target_date.strftime("%Y-%m-%d"),
            end=(target_date + pd.Timedelta(days=1)).strftime("%Y-%m-%d"),
            auto_adjust=False,
            progress=False
        )

        print(f"{ticker} 取得データ:\n{data}")
        print(f"{ticker} data.empty: {data.empty}")
        print(f"{ticker} columns: {data.columns}")
        print(f"{ticker} index: {data.index}")

        # マルチカラム（Tickerが列にある）場合の処理
        if isinstance(data.columns, pd.MultiIndex):
            data = data.xs(ticker, axis=1, level=1)

        if data.empty or 'Open' not in data.columns or 'Close' not in data.columns:
            print(f"{ticker} の当日データが存在しないためスキップ")
            continue

        open_price = data['Open'].iloc[0]
        close_price = data['Close'].iloc[0]
        print(f"{ticker} Open: {open_price}, Close: {close_price}")

        if pd.isna(open_price) or pd.isna(close_price):
            print(f"{ticker} の始値または終値がNaNでした")
            continue

        change = (close_price - open_price) / open_price * 100
        print(f"{ticker} 変化率: {round(change, 2)}%")

        if change >= 5:
            results.append({
                '銘柄コード': ticker.replace('.T', ''),
                '決算日': date_str,
                '始値': round(open_price, 2),
                '終値': round(close_price, 2),
                '変化率(%)': round(change, 2)
            })

    except Exception as e:
        print(f"{ticker} の処理中にエラー: {e}")
        continue

# 保存処理
if results:
    df = pd.DataFrame(results)
    output_path = fr'data/output/決算発表後反応銘柄/場中決算反応銘柄{date_str}.csv'
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False, encoding='utf-8-sig')
    print(f"✅ 出力完了: {output_path}")
else:
    print("⚠ 条件を満たす銘柄はありませんでした。")
