import sys
import os
import pandas as pd
import time
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

#指標を取得する
def fetch_indicators(input_csv, output_excel):
    # CSV読み込み（全角スペース除去）
    df = pd.read_csv(input_csv, dtype=str)
    df.columns = df.columns.str.strip()

    # 無関係な行をスキップ
    df = df[df["分類"] != "無関係"].copy()
    if df.empty:
        print("[WARN] 有効な行がありません（分類≠無関係）")
        return

    ticker_list = df["銘柄コード"].tolist()
    name_map = dict(zip(df["銘柄コード"], df["銘柄名"]))
    classify_map = dict(zip(df["銘柄コード"], df["分類"]))
    reason_map = dict(zip(df["銘柄コード"], df["理由"]))

    items = {
        "PER（予）": r"PER（(連|個)）.*予",
        "EPS（予）": r"EPS（(連|個)）.*予",
        "EPS": r"EPS（(連|個)）(?!.*予)",
        "PBR": r"PBR（(連|個)）",
        "ROE（予）": r"ROE（(連|個)）.*予",
        "ROA（予）": r"ROA（(連|個)）.*予",
        "配当利回り（予）": r"配当利回り.*予",
        "時価総額": r"時価総額",
        "発行済み株式総数": r"発行済み株式総数"
    }

    # Selenium起動
    options = webdriver.ChromeOptions()
    # options.add_argument('--headless')
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    all_results = []

    for ticker in ticker_list:
        print(f"\n=== 処理中: {ticker} ===")
        base_url = f"https://irbank.net/{ticker}"
        driver.get(base_url)
        time.sleep(3)
        soup = BeautifulSoup(driver.page_source, "html.parser")
        e_href_tag = soup.find("a", href=re.compile(r"^/E\d+"))

        if not e_href_tag:
            print(f"❌ Eコード取得失敗: {ticker}")
            continue

        e_code = e_href_tag["href"].strip("/")
        driver.get(f"https://irbank.net/{e_code}")
        time.sleep(3)
        soup = BeautifulSoup(driver.page_source, "html.parser")
        title = soup.title.text.strip() if soup.title else ""

        results = {
            "銘柄コード": ticker,
            "銘柄名": name_map.get(ticker, title),
            "分類": classify_map.get(ticker, ""),
            "理由": reason_map.get(ticker, "")
        }

        dl_elements = soup.find_all("dl")
        for dl in dl_elements:
            for dt, dd in zip(dl.find_all("dt"), dl.find_all("dd")):
                key = dt.text.strip().replace(" ", "")
                val = dd.text.strip()
                for label, pattern in items.items():
                    if re.search(pattern, key):
                        results[label] = val

        all_results.append(results)

    driver.quit()

    if not all_results:
        print("[WARN] 出力対象がありません")
        return

    df_out = pd.DataFrame(all_results)
    os.makedirs(os.path.dirname(output_excel), exist_ok=True)
    df_out.to_excel(output_excel, index=False)

    print(f"[DONE] 出力完了: {output_excel}")
    # if os.path.exists(output_excel):
    #     os.startfile(output_excel)
    # else:
    #     print(f"[ERROR] 出力ファイルが見つかりません: {output_excel}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("使い方: python Stock_Quotes.py <銘柄CSVパス> <出力Excelパス>")
        sys.exit(1)

    input_csv = os.path.abspath(sys.argv[1])
    output_excel = os.path.abspath(sys.argv[2])
    fetch_indicators(input_csv, output_excel)
