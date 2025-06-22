import sys
import os
import csv
import time
import re
import requests
from bs4 import BeautifulSoup

def get_competitor_from_kabuyoho(stock_code):
    url = f"https://kabuyoho.jp/reportAnalyst?bcode={stock_code}"
    print(f"[INFO] アクセス中: {url}")

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    resp = requests.get(url, headers=headers)
    if resp.status_code != 200:
        print(f"[ERROR] アクセス失敗: {resp.status_code}")
        return []

    soup = BeautifulSoup(resp.text, "html.parser")
    section = soup.find("section", class_="analyst brnd_company_comp")
    if not section:
        print("[WARN] 対象のセクションが見つかりませんでした")
        return []

    competitors = []

    for th in section.select("th"):
        href_tag = th.find("a", href=True)
        if not href_tag:
            continue

        match = re.search(r"bcode=([\w]+)", href_tag["href"])
        if not match:
            continue

        code = match.group(1)

        text = th.get_text(separator="\n").strip()
        lines = text.splitlines()

        if len(lines) >= 2:
            name = lines[1].strip()
            competitors.append({"銘柄コード": code, "銘柄名": name})
            print(f"[INFO] 取得: {code} {name}")

    return competitors

def write_to_csv(data, filepath):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, mode='w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=["銘柄コード", "銘柄名"])
        writer.writeheader()
        writer.writerows(data)
    print(f"[INFO] 書き込み完了: {filepath}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("使い方: python site3_rivals_batch_fixed_final.py <銘柄コード>")
        sys.exit(1)

    scode = sys.argv[1]
    rivals = get_competitor_from_kabuyoho(scode)

    output_path = f"data/output/競合他社の銘柄コード取得/株予報Pro_{scode}.csv"
    write_to_csv(rivals, output_path)
