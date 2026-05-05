import os
import json
import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud.firestore_v1.base_query import FieldFilter
import requests
from bs4 import BeautifulSoup
import urllib3 
from flask import Flask, render_template, request
from datetime import datetime
import random

# 禁用 SSL 警告訊息
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# --- Firebase 初始化 ---
if os.path.exists('serviceAccountKey.json'):
    cred = credentials.Certificate('serviceAccountKey.json')
else:
    firebase_config = os.getenv('FIREBASE_CONFIG')
    cred_dict = json.loads(firebase_config)
    cred = credentials.Certificate(cred_dict)

if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)

app = Flask(__name__)

# --- 定義天氣查詢用的 HTML 模板 ---
HTML_FORM = """
<!DOCTYPE html>
<html>
<head><title>天氣查詢</title></head>
<body>
    <h2>縣市天氣查詢系統</h2>
    <form action="/weather" method="get">
        請輸入縣市名稱：<input type="text" name="city" placeholder="例如：臺中市">
        <button type="submit">查詢</button>
    </form>
    <hr>
    {result_content}
    <br><br><a href="/">回到首頁</a>
</body>
</html>
"""

@app.route("/")
def index():
    link = "<h1>歡迎加入地球Online</h1>"
    link += "<a href=/mis>課程</a><hr>"   
    link += "<a href=/today>日期</a><hr>"
    link += "<a href=/about>關於</a><hr>"
    link += "<a href=/welcome?nick=柏慶&dep=靜宜大學>傳送使用者暱稱</a><hr>"
    link += "<a href=/account>post傳值</a><hr>"
    link += "<a href=/math>簡易計算機</a><hr>"
    link += "<a href=/cup>擲茭</a><hr>"
    link += "<a href=/read>讀取Firestore資料</a><hr>"
    link += "<a href=/search>查詢老師研究室</a><hr>"
    link += "<a href=/spider1>爬蟲測試</a><hr>"
    link += "<a href=/movie1>電影上架查詢</a><hr>"
    link += "<a href=/movie2>寫入電影資料到Firestore</a><hr>"
    link += "<a href=/movie3>查詢相關電影資訊</a><hr>"
    link += "<a href=/opendata>113十大肇事路口</a><hr>"
    link += "<a href=/weather>查詢天氣</a><hr>"
    return link

# --- 天氣查詢路由 ---
@app.route('/weather')
def weather():
    city_input = request.args.get('city')
    if not city_input:
        return HTML_FORM.format(result_content="請在上方輸入框輸入縣市名稱以開始查詢。")

    city = city_input.replace("台", "臺")
    token = "rdec-key-123-45678-011121314" # 建議換成你申請的氣象署 Token
    url = "https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-C0032-001"
    
    params = {"Authorization": token, "format": "JSON", "locationName": city}
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        response = requests.get(url, params=params, headers=headers, verify=False)
        if response.status_code == 200:
            data = response.json()
            if data["records"]["location"]:
                location_data = data["records"]["location"][0]
                weather_status = location_data["weatherElement"][0]["time"][0]["parameter"]["parameterName"]
                rain_chance = location_data["weatherElement"][1]["time"][0]["parameter"]["parameterName"]
                res_text = f"<h3>{city} 的查詢結果：</h3>目前天氣：{weather_status}<br>降雨機率：{rain_chance}%"
                return HTML_FORM.format(result_content=res_text)
            else:
                return HTML_FORM.format(result_content=f"找不到『{city}』的資料。")
        return HTML_FORM.format(result_content="連線 API 失敗")
    except Exception as e:
        return HTML_FORM.format(result_content=f"錯誤：{e}")

# --- 十大肇事路口路由 ---
@app.route('/opendata')
def opendata():
    road_query = request.args.get('road', '') 
    url = "https://newdatacenter.taichung.gov.tw/api/v1/no-auth/resource.download?rid=a1b899c0-511f-4e3d-b22b-814982a97e41"
    
    try:
        response = requests.get(url, verify=False)
        json_data = response.json()
        result = "<h2>113年十大肇事路口查詢</h2>"
        result += '<form action="/opendata" method="get"><input type="text" name="road" placeholder="輸入路名"><button>查詢</button></form><hr>'
        
        found_data = ""
        for item in json_data:
            if road_query in item["路口名稱"]:
                found_data += f"<b>{item['路口名稱']}</b>：發生 {item['總件數']} 件，主因：{item['主要肇因']}<br><br>"
        
        result += found_data if found_data else "請輸入路口名稱進行查詢。"
        return result + "<br><a href='/'>回到首頁</a>"
    except Exception as e:
        return f"錯誤：{e}"

# --- 電影相關路由 ---
@app.route("/movie3", methods=["GET", "POST"])
def movie3():
    if request.method == "POST":
        keyword = request.form.get("keyword")
        db = firestore.client()
        docs = db.collection("電影").get()
        
        result = f"<h2>「{keyword}」查詢結果：</h2><ul>"
        found = False
        for doc in docs:
            m = doc.to_dict()
            if keyword in m.get("title", ""):
                result += f"<li><b>{m['title']}</b><br>上映日期：{m.get('showDate')}<br><a href='{m.get('hyperlink')}' target='_blank'>電影介紹</a></li><br>"
                found = True
        result += "</ul>"
        if not found: result += "查無資料。"
        return result + "<br><a href='/movie3'>重新查詢</a> | <a href='/'>首頁</a>"
    
    return '<h1>電影查詢</h1><form method="post"><input name="keyword"><button>查詢</button></form>'

@app.route("/movie2")
def movie2():
    # 爬蟲寫入 Firestore 邏輯 (保持原樣，僅修正 db 呼叫)
    try:
        url = "http://www.atmovies.com.tw/movie/next/"
        res = requests.get(url)
        res.encoding = "utf-8"
        sp = BeautifulSoup(res.text, "html.parser")
        items = sp.select(".filmListAllX li")
        db = firestore.client()
        for item in items:
            title = item.find("div", class_="filmtitle").text
            movie_id = item.find("div", class_="filmtitle").find("a").get("href").replace("/", "").replace("movie", "")
            db.collection("電影").document(movie_id).set({"title": title})
        return "資料已更新"
    except Exception as e:
        return str(e)

# --- 其他基礎路由 (保持原樣) ---
@app.route("/mis")
def course(): return "<h1>資訊管理導論</h1><a href=/>回到首頁</a>"

@app.route("/today")
def today():
    now = datetime.now()
    formatted_date = now.strftime("%Y年%m月%d日")
    return render_template("today.html", datetime=formatted_date)

@app.route("/about")
def about(): return render_template("about.html")

# --- 啟動程式 (放在最後面，且只需一個) ---
if __name__ == "__main__":
    app.run(debug=True)