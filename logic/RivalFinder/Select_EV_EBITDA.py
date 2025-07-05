import os
import csv
import sys
import requests
from bs4 import BeautifulSoup

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
                    if th and 'EV/EBITDA' in th.text:
                        return td.text.strip().replace('年', '')
        return "該当なし"
    except Exception as e:
        print(f"[ERROR] 例外発生: {e}")
        return "エラー"

def read_input_csv(filepath):
    stocks = []
    with open(filepath, mode='r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            stocks.append({
                "銘柄コード": str(row["銘柄コード"]).strip(),
                "銘柄名": row["銘柄名"].strip()
            })
    return stocks

def write_output_csv(data, filepath):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, mode='w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=["銘柄コード", "銘柄名", "EV/EBITDA"])
        writer.writeheader()
        writer.writerows(data)
    print(f"[INFO] 書き込み完了: {filepath}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("使い方: python Select_EV_EBITDA.py <入力CSVパス> <出力CSVパス>")
        sys.exit(1)

    input_csv_path = sys.argv[1]
    output_csv_path = sys.argv[2]

    stock_list = read_input_csv(input_csv_path)
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

    write_output_csv(result, output_csv_path)
    try:
        abs_path = os.path.abspath(output_csv_path)
        print(f"[INFO] Excelを開きます: {abs_path}")
        os.startfile(abs_path)
    except Exception as e:
        print(f"[WARN] Excel自動起動に失敗: {e}")