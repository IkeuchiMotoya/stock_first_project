import sys
import os
import pandas as pd
import time
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

def fetch_indicators(csv_path, output_path):
    ticker_df = pd.read_csv(csv_path, dtype={"銘柄コード": str})
    ticker_list = ticker_df["銘柄コード"].tolist()
    name_map = dict(zip(ticker_df["銘柄コード"], ticker_df["銘柄名"]))

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

    options = webdriver.ChromeOptions()
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

        results = {"銘柄コード": ticker, "銘柄名": name_map.get(ticker, title)}
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

    df = pd.DataFrame(all_results)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_excel(output_path, index=False)

    if os.path.exists(output_path):
        os.startfile(output_path)
    else:
        print(f"[WARN] ファイル出力に失敗: {output_path}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("使い方: python ExportStockIndicatorsWithArgs.py <銘柄CSVパス> <出力Excelパス>")
        sys.exit(1)

    input_csv = os.path.abspath(sys.argv[1])
    output_excel = os.path.abspath(sys.argv[2])
    fetch_indicators(input_csv, output_excel)
    
    if os.path.exists(output_excel):
        os.startfile(output_excel)
    else:
        print(f"[WARN] 出力ファイルが見つかりませんでした: {output_excel}")
