import subprocess

# 実行したいスクリプトの順番（相対パス指定）
batch_list = [
    "logic/CompanyAnalysisExcelList/ExcelCreation.py",
    "logic/CompanyAnalysisExcelList/IndexComparisonInsert.py",
    "logic/CompanyAnalysisExcelList/EV_EBITDAInsert.py",
    "logic/CompanyAnalysisExcelList/FullYearPerformanceTrendsInsert.py"
]

for script in batch_list:
    print(f"\n----- {script} 実行開始 -----")
    ret = subprocess.run(["python", script])
    if ret.returncode == 0:
        print(f"----- {script} 実行完了 -----")
    else:
        print(f"× {script} でエラーが発生しました")
        break  # エラーが出たら以降は停止したい場合
