import os
import sys
import time
import random
import requests
import csv
from bs4 import BeautifulSoup
from openpyxl import Workbook  # Excel書き出し用

def get_ev_ebitda(stock_code):
    url = f"https://www.kabutec.jp/company/i.php?code={stock_code}"
    headers = {"User-Agent": "Mozilla/5.0"}
    print(f"[INFO] アクセス中: {url}")

    try:
        resp = requests.get(url, headers=headers)
        if resp.status_code != 200:
            print(f"[ERROR] アクセス失敗: {resp.status_code}")
            return "取得失敗"

        soup = BeautifulSoup(resp.text, 'html.parser')
        sections = soup.find_all('section', class_='info_box')

        for section in sections:
            if "EV/EBITDA" in section.text:
                for tr in section.find_all('tr'):
                    th = tr.find('th')
                    td = tr.find('td')
                    if th and 'EV/EBITDA' in th.text and td:
                        return td.text.strip().replace('年', '')
        return "該当なし"
    except Exception as e:
        print(f"[ERROR] 例外発生: {e}")
        return "エラー"

def read_filtered_stocks(filepath):
    stocks = []
    with open(filepath, mode='r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # 分類が「無関係」の銘柄はスキップ
            if row.get("分類", "").strip() == "無関係":
                continue
            stocks.append({
                "銘柄コード": str(row["銘柄コード"]).strip(),
                "銘柄名": row["銘柄名"].strip()
            })
    return stocks

def write_output_excel(data, filepath):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    wb = Workbook()
    ws = wb.active
    ws.title = "EV_EBITDA比較"

    # ヘッダー
    ws.append(["銘柄コード", "銘柄名", "EV/EBITDA"])

    # データ行
    for row in data:
        ws.append([row["銘柄コード"], row["銘柄名"], row["EV/EBITDA"]])

    wb.save(filepath)
    print(f"[INFO] Excel書き込み完了: {filepath}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("使い方: python Select_EV_EBITDA.py <競合判定結果CSV> <出力Excelパス>")
        sys.exit(1)

    input_csv_path = sys.argv[1]
    output_excel_path = sys.argv[2]

    if not output_excel_path.endswith(".xlsx"):
        output_excel_path = os.path.splitext(output_excel_path)[0] + ".xlsx"

    stock_list = read_filtered_stocks(input_csv_path)
    result = []

    for stock in stock_list:
        code = stock["銘柄コード"]
        name = stock["銘柄名"]
        ev_ebitda = get_ev_ebitda(code)
        result.append({
            "銘柄コード": code,
            "銘柄名": name,
            "EV/EBITDA": ev_ebitda
        })

        # 👇 IPブロック対策：1〜3秒のランダム待機
        sleep_time = random.uniform(1, 3)
        print(f"[INFO] 次のリクエストまで {sleep_time:.1f} 秒待機")
        time.sleep(sleep_time)

    write_output_excel(result, output_excel_path)

    try:
        abs_path = os.path.abspath(output_excel_path)
        # print(f"[INFO] Excelを開きます: {abs_path}")
        # os.startfile(abs_path)
    except Exception as e:
        print(f"[WARN] Excel自動起動に失敗: {e}")
