from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time
import os

# ヘッドレスブラウザ設定
options = webdriver.ChromeOptions()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

url = "https://finance.yahoo.co.jp/quote/7649.T/performance"
driver.get(url)
time.sleep(5)

tables = driver.find_elements(By.TAG_NAME, "table")
performance_table = None
for table in tables:
    if "売上高" in table.text and "営業利益" in table.text:
        performance_table = table
        break

data = []
headers = []

if performance_table:
    rows = performance_table.find_elements(By.TAG_NAME, "tr")
    for i, row in enumerate(rows):
        if i == 0:
            headers = [col.text.replace("\n", "") for col in row.find_elements(By.TAG_NAME, "th")][1:]
        else:
            th = row.find_element(By.TAG_NAME, "th")
            fiscal = th.text.replace("\n", "")
            tds = row.find_elements(By.TAG_NAME, "td")
            values = [td.text.replace(",", "").replace("％", "%").replace("\n", "") for td in tds]
            if len(values) == len(headers):
                data.append([fiscal] + values)

    df = pd.DataFrame(data, columns=["決算期"] + headers)

    # 日付変換とソート
    df["財務数値更新日_dt"] = pd.to_datetime(df["財務数値更新日"], errors="coerce")
    df = df.sort_values("財務数値更新日_dt").drop(columns="財務数値更新日_dt").reset_index(drop=True)

    # 直近3年だけ残す（予想含むなら予想+2年、含まないなら3年）
    df = df.tail(3).reset_index(drop=True)

    # 不要列を削除して出力
    df_output = df.drop(columns=["会計方式", "財務数値更新日"])

    file_path = "スギホールディングス_業績_Selenium.xlsx"
    if os.path.exists(file_path):
        os.remove(file_path)

    df_output.to_excel(file_path, index=False)
    print(f"✅ 直近3件の業績をExcelに出力しました: {file_path}")

else:
    print("⚠️ 業績テーブルが見つかりませんでした。")

driver.quit()
