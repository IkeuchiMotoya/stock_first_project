from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time
import os
import sys

def fetch_yahoo_financials(ticker: str, name: str):
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    url = f"https://finance.yahoo.co.jp/quote/{ticker}.T/performance"
    driver.get(url)
    time.sleep(3)

    try:
        tables = driver.find_elements(By.TAG_NAME, "table")
        performance_table = None
        for table in tables:
            if "売上高" in table.text and "営業利益" in table.text:
                performance_table = table
                break

        if not performance_table:
            print(f"⚠️ {ticker}: 業績テーブルが見つかりませんでした")
            return None

        data, headers = [], []
        rows = performance_table.find_elements(By.TAG_NAME, "tr")
        for i, row in enumerate(rows):
            if i == 0:
                headers = [th.text.replace("\n", "") for th in row.find_elements(By.TAG_NAME, "th")][1:]
            else:
                fiscal = row.find_element(By.TAG_NAME, "th").text.replace("\n", "")
                tds = row.find_elements(By.TAG_NAME, "td")
                values = [td.text.replace(",", "").replace("％", "%").replace("\n", "") for td in tds]
                if len(values) == len(headers):
                    data.append([fiscal] + values)

        df = pd.DataFrame(data, columns=["決算期"] + headers)
        df["財務数値更新日_dt"] = pd.to_datetime(df["財務数値更新日"], errors="coerce")
        # 決算期の年でソート
        df["決算期_年"] = df["決算期"].str.extract(r"(\d{4})").astype(int)
        df = df.sort_values("決算期_年").drop(columns="決算期_年").reset_index(drop=True)
        # df = df.sort_values("財務数値更新日_dt").drop(columns="財務数値更新日_dt").reset_index(drop=True)
        df = df.tail(3).reset_index(drop=True)

        df.insert(0, "銘柄コード", ticker)
        df.insert(1, "銘柄名", name)

        for col in ["売上高（百万円）", "売上総利益（百万円）", "営業利益（百万円）", "経常利益（百万円）", "純利益（百万円）"]:
            df[col] = pd.to_numeric(df[col], errors="coerce")

        df["純利益率"] = (df["純利益（百万円）"] / df["売上高（百万円）"] * 100).round(2).astype(str) + "%"
        df["売上高比率"] = df["売上高（百万円）"].pct_change().mul(100).round(2).astype(str).replace("nan%", "") + "%"
        # 営業利益前年比（営業利益比率）
        df["営業利益比率"] = df["営業利益（百万円）"].pct_change().mul(100).round(2).astype(str).replace("nan%", "") + "%"


        df_output = df[[
            "銘柄コード", "銘柄名", "決算期", "売上高（百万円）", "売上高比率",
            "売上総利益（百万円）", "粗利率", "営業利益（百万円）", "営業利益比率",
            "経常利益（百万円）", "経常利益率", "純利益（百万円）", "純利益率"
        ]]
        return df_output

    finally:
        driver.quit()

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("使い方: python financeYahooKabuPredictor.py <入力CSVパス> <出力Excelファイルパス>")
        sys.exit(1)

    input_csv = os.path.abspath(sys.argv[1])
    output_excel = os.path.abspath(sys.argv[2])
    df = pd.read_csv(input_csv, dtype={"銘柄コード": str})

    if "分類" in df.columns:
        df = df[df["分類"] != "無関係"].copy()

    if df.empty:
        print("⚠️ 有効な銘柄が見つかりません")
        sys.exit(1)

    all_data = []
    for _, row in df.iterrows():
        ticker = row["銘柄コード"]
        name = row["銘柄名"] if "銘柄名" in row else ""
        result_df = fetch_yahoo_financials(ticker, name)
        if result_df is not None:
            all_data.append(result_df)

    if all_data:
        final_df = pd.concat(all_data, ignore_index=True)
        os.makedirs(os.path.dirname(output_excel), exist_ok=True)
        final_df.to_excel(output_excel, index=False)
        print(f"[DONE] 出力完了: {output_excel}")
        if os.path.exists(output_excel):
            os.startfile(output_excel)
    else:
        print("❌ すべての銘柄でデータ取得に失敗しました")
