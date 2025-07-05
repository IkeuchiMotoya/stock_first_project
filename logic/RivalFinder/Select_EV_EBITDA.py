import os
import csv
import requests
from bs4 import BeautifulSoup

def get_ev_ebitda(stock_code):
    url = f"https://www.kabutec.jp/company/i.php?code={stock_code}"
    print(f"[INFO] アクセス中: {url}")

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    try:
        resp = requests.get(url, headers=headers)
        if resp.status_code != 200:
            print(f"[ERROR] アクセス失敗: {resp.status_code}")
            return "取得失敗"

        soup = BeautifulSoup(resp.text, 'html.parser')
        sections = soup.find_all('section', class_='info_box')

        for section in sections:
            if "EV/EBITDA" in section.text:
                rows = section.find_all('tr')
                for tr in rows:
                    th = tr.find('th')
                    td = tr.find('td')
                    if th and 'EV/EBITDA' in th.text:
                        value = td.text.strip().replace('年', '')
                        print(f"[INFO] 取得成功: {stock_code} → {value}")
                        return value
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
    input_csv_path = "data/input/通期業績の推移、指標の取得/検索銘柄.csv"
    output_csv_path = "data/output/競合他社の銘柄コード取得/株テク_EV_EBITDA.csv"

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
