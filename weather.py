import requests, json
import urllib3 
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

city = input("請輸入縣市：").replace("台", "臺")

token = "rdec-key-123-45678-011121314" 
url = "https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-C0032-001"

params = {
    "Authorization": token,
    "format": "JSON",
    "locationName": city
}

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

try:
    response = requests.get(url, params=params, headers=headers, verify=False)
    
    if response.status_code == 200:
        data = response.json()
        location_data = data["records"]["location"][0]
        
        weather_status = location_data["weatherElement"][0]["time"][0]["parameter"]["parameterName"]
        rain_chance = location_data["weatherElement"][1]["time"][0]["parameter"]["parameterName"]
        
        print(f"--- {city} 的天氣預報 ---")
        print(f"目前天氣狀況：{weather_status}")
        print(f"降雨機率：{rain_chance}%")
    else:
        print(f"連線失敗，狀態碼：{response.status_code}")

except Exception as e:
    print(f"程式執行錯誤：{e}")