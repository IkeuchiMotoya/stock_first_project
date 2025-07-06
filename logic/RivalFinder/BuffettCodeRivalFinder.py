import sys
import os
import csv
import re
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

# 引数チェック
if len(sys.argv) != 2:
    print("使い方: python buffett_code_rival_batch.py <銘柄コード>")
    sys.exit(1)

target_code = sys.argv[1]

def get_competitors_from_buffett_code(stock_code):
    url = f"https://www.buffett-code.com/company/{stock_code}/"
    print(f"[INFO] アクセス中: {url}")

    options = webdriver.ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get(url)
    time.sleep(3)

    soup = BeautifulSoup(driver.page_source, "html.parser")
    driver.quit()

    results = []
    tables = soup.select("table.custom-table.table-hover")
    for table in tables:
        rows = table.select("tbody tr")
        for row in rows:
            tds = row.select("td")
            if len(tds) < 2:
                continue
            code_tag = tds[0].find("a", href=True)
            name_tag = tds[1].find("a")
            if code_tag and name_tag:
                code = code_tag.get_text(strip=True)
                name = name_tag.get_text(strip=True)
                results.append({"銘柄コード": code, "銘柄名": name})
                print(f"[INFO] 取得: {code} {name}")
    return results

def write_to_csv(data, filepath):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, mode='w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=["銘柄コード", "銘柄名"])
        writer.writeheader()
        writer.writerows(data)
    print(f"[INFO] 書き込み完了: {filepath}")

# 実行
if __name__ == "__main__":
    rivals = get_competitors_from_buffett_code(target_code)
    output_path = f"data/output/競合他社の銘柄コード取得/バフェットコード_{target_code}.csv"
    write_to_csv(rivals, output_path)
