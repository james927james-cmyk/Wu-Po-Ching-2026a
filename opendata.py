import requests, json

url = "https://newdatacenter.taichung.gov.tw/api/v1/no-auth/resource.download?rid=a1b899c0-511f-4e3d-b22b-814982a97e41"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

try:
    Data = requests.get(url, headers=headers, verify=False)
    
    JsonData = Data.json()
    
    Result = ""
    Road = input("請輸入欲查詢的路名：")
    
    for item in JsonData:
        if Road in item["路口名稱"]:
            Result += f"{item['路口名稱']}：發生 {item['總件數']} 件，主因是 {item['主要肇因']}\n\n"
            
    if Result == "":
        Result = "抱歉，查無相關資料！"
        
    print(Result)

except Exception as e:
    print(f"程式執行發生錯誤：{e}")