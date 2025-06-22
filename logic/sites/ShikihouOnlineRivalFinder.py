import sys
import os
import csv
import re
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

def get_competitor_codes_and_names(stock_code):
    url = f"https://shikiho.toyokeizai.net/stocks/{stock_code}#rivals"
    print(f"[INFO] アクセス中: {url}")

    options = webdriver.ChromeOptions()
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option('excludeSwitches', ['enable-automation'])
    options.add_experimental_option('useAutomationExtension', False)

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get(url)
    time.sleep(3)

    soup = BeautifulSoup(driver.page_source, "html.parser")
    driver.quit()

    results = []

    for a in soup.select("div.company-name-inner a[href^='/stocks/']"):
        href = a["href"]
        name = a.get_text(strip=True)
        match = re.search(r"/stocks/(\d+)", href)
        if match:
            scode = match.group(1)
            results.append({"銘柄コード": scode, "銘柄名": name})
            print(f"[INFO] 取得: {scode} {name}")

    return results

def write_to_csv(data, filepath):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, mode='w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=["銘柄コード", "銘柄名"])
        writer.writeheader()
        writer.writerows(data)
    print(f"[INFO] 書き込み完了: {filepath}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("使い方: python site1_rivals_batch.py <銘柄コード>")
        sys.exit(1)

    stock_code = sys.argv[1]
    rivals = get_competitor_codes_and_names(stock_code)

    output_path = f"data/output/競合他社の銘柄コード取得/四季報オンライン_{stock_code}.csv"
    write_to_csv(rivals, output_path)
