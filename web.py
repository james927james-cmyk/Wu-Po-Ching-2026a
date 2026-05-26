import os
import json
import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud.firestore_v1.base_query import FieldFilter
import requests
from bs4 import BeautifulSoup
import urllib3 
from flask import Flask, render_template, request, make_response, jsonify   
from datetime import datetime
from google import genai
import random

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

if os.path.exists('serviceAccountKey.json'):
    cred = credentials.Certificate('serviceAccountKey.json')
else:
    firebase_config = os.getenv('FIREBASE_CONFIG')
    cred_dict = json.loads(firebase_config)
    cred = credentials.Certificate(cred_dict)

if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)

app = Flask(__name__)
client = genai.Client()
#client = genai.Client(api_key=api_key)


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
    link += "<a href=/rate>本週新片進DB</a><hr>"
    link += "<a href=/webhook3>本週分級</a><hr>"
    link += "<a href=/demo>demo</a><hr>"
    link += "<a href=/AI>AI</a><hr>"
    link += "<a href=/ask>ask</a><hr>"
    return link

@app.route("/webhook7", methods=["POST"])
def webhook7():
    # build a request object
    req = request.get_json(force=True)
    # fetch queryResult from json
    action =  req.get("queryResult").get("action")
    #msg =  req.get("queryResult").get("queryText")
    #info = "動作：" + action + "； 查詢內容：" + msg
    if (action == "rateChoice"):
…
    elif (action == "input.unknown"):
        info =  req["queryResult"]["queryText"]
    return make_response(jsonify({"fulfillmentText": info}))


@app.route('/ask', methods=['GET', 'POST']) 
def ask():
    if request.method == "POST":
        user_prompt = request.form.get('prompt', '')
        if not user_prompt:
            return "請輸入內容", 400
        try:
            response = client.models.generate_content(
                model='gemini-3.5-flash',
                contents=user_prompt,
            )
            return response.text
        except Exception as e:
            return f"發生錯誤: {str(e)}", 500

    else:    
        # 當使用者直接打開網頁 (GET) 時，顯示輸入框畫面
        return render_template("ask.html")


@app.route("/AI")
def AI():
    # 每次使用者拜訪該路徑時，直接使用全域的 client 呼叫模型
    response = client.models.generate_content(
        model='gemini-3.5-flash',
        contents='我想查詢靜宜大學資管系的評價？',
    )
    
    # 回傳生成的文字
    return response.text

@app.route("/demo")
def demo():
    return render_template("/demo.html")

@app.route("/webhook", methods=["POST"])
def webhook():
    # build a request object
    req = request.get_json(force=True)
    # fetch queryResult from json
    action =  req.get("queryResult").get("action")
    #msg =  req.get("queryResult").get("queryText")
    #info = "我是吳柏慶設計的電影聊天機器人,  動作：" + action + "； 查詢內容：" + msg
    if (action == "rateChoice"):
        rate =  req["queryResult"]["parameters"]["rate"]
        info = "我是吳柏慶設計的電影聊天機器人, 您選擇的電影分級是：" + rate

    return make_response(jsonify({"fulfillmentText": info}))

@app.route("/webhook2", methods=["POST"])
def webhook2():
    # build a request object
    req = request.get_json(force=True)
    # fetch queryResult from json
    action =  req.get("queryResult").get("action")
    #msg =  req.get("queryResult").get("queryText")
    #info = "動作：" + action + "； 查詢內容：" + msg
    if (action == "rateChoice"):
        rate =  req.get("queryResult").get("parameters").get("rate")
        info = "您選擇的電影分級是：" + rate
    return make_response(jsonify({"fulfillmentText": info}))


@app.route("/rate")
def rate():
    #本週新片
    url = "https://www.atmovies.com.tw/movie/new/"
    Data = requests.get(url)
    Data.encoding = "utf-8"
    sp = BeautifulSoup(Data.text, "html.parser")
    lastUpdate = sp.find(class_="smaller09").text[5:]
    print(lastUpdate)
    print()

    result=sp.select(".filmList")

    for x in result:
        title = x.find("a").text
        introduce = x.find("p").text

        movie_id = x.find("a").get("href").replace("/", "").replace("movie", "")
        hyperlink = "http://www.atmovies.com.tw/movie/" + movie_id
        picture = "https://www.atmovies.com.tw/photo101/" + movie_id + "/pm_" + movie_id + ".jpg"

        r = x.find(class_="runtime").find("img")
        rate = ""
        if r != None:
            rr = r.get("src").replace("/images/cer_", "").replace(".gif", "")
            if rr == "G":
                rate = "普遍級"
            elif rr == "P":
                rate = "保護級"
            elif rr == "F2":
                rate = "輔12級"
            elif rr == "F5":
                rate = "輔15級"
            else:
                rate = "限制級"

        t = x.find(class_="runtime").text

        t1 = t.find("片長")
        t2 = t.find("分")
        showLength = t[t1+3:t2]

        t1 = t.find("上映日期")
        t2 = t.find("上映廳數")
        showDate = t[t1+5:t2-8]

        doc = {
            "title": title,
            "introduce": introduce,
            "picture": picture,
            "hyperlink": hyperlink,
            "showDate": showDate,
            "showLength": int(showLength),
            "rate": rate,
            "lastUpdate": lastUpdate
        }

        db = firestore.client()
        doc_ref = db.collection("本週新片含分級").document(movie_id)
        doc_ref.set(doc)
    return "本週新片已爬蟲及存檔完畢，網站最近更新日期為：" + lastUpdate

@app.route('/weather')
def weather():
    city_input = request.args.get('city')
    if not city_input:
        return HTML_FORM.format(result_content="請在上方輸入框輸入縣市名稱以開始查詢。")

    city = city_input.replace("台", "臺")
    token = "rdec-key-123-45678-011121314" 
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

@app.route("/mis")
def course(): return "<h1>資訊管理導論</h1><a href=/>回到首頁</a>"

@app.route("/today")
def today():
    now = datetime.now()
    formatted_date = now.strftime("%Y年%m月%d日")
    return render_template("today.html", datetime=formatted_date)

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/welcome", methods=["GET"])
def welcome():
    user = request.values.get("nick")
    x = request.values.get("dep")
    return render_template("welcome.html", name=user,dep=x)

@app.route("/account", methods=["GET", "POST"])
def account():
    if request.method == "POST":
        user = request.form["user"]
        pwd = request.form["pwd"]
        result = "您輸入的帳號是：" + user + "; 密碼為：" + pwd 
        return result
    else:
        return render_template("account.html")

@app.route("/math")
def math():
    return render_template("math.html")

@app.route('/cup', methods=["GET"])
def cup():
    # 檢查網址是否有 ?action=toss
    #action = request.args.get('action')
    action = request.values.get("action")
    result = None
    
    if action == 'toss':
        # 0 代表陽面，1 代表陰面
        x1 = random.randint(0, 1)
        x2 = random.randint(0, 1)
        
        # 判斷結果文字
        if x1 != x2:
            msg = "聖筊：表示神明允許、同意，或行事會順利。"
        elif x1 == 0:
            msg = "笑筊：表示神明一笑、不解，或者考慮中，行事狀況不明。"
        else:
            msg = "陰筊：表示神明否定、憤怒，或者不宜行事。"
            
        result = {
            "cup1": "/static/" + str(x1) + ".jpg",
            "cup2": "/static/" + str(x2) + ".jpg",
            "message": msg
        }
        
    return render_template('cup.html', result=result)

@app.route("/read")
def read():
    db = firestore.client()
    
    Result = "" 

    collection_ref = db.collection("靜宜資管")
    docs = collection_ref.order_by("lab", direction=firestore.Query.DESCENDING).limit(4).get()
    
    for doc in docs:
        Result += "{}".format(doc.to_dict()) + "<br>"    
        
    return Result

@app.route("/search", methods=["GET", "POST"])
def search():
    if request.method == "POST":
        keyword = request.form.get("keyword")
        db = firestore.client()
        collection_ref = db.collection("靜宜資管")
        docs = collection_ref.get()
        
        result = f"<h2>關於「{keyword}」的查詢結果：</h2>"
        found = False
        for doc in docs:
            user = doc.to_dict()
            if "name" in user and keyword in user["name"]:
                result += f"<b>{user['name']}</b> 老師的研究室是在 <b>{user['lab']}</b><br><br>"
                found = True
        
        if not found:
            result += "很抱歉，找不到符合條件的老師資料。<br>"
        
        result += "<br><a href=/search>重新查詢</a> | <a href=/>回到首頁</a>"
        return result
    else:
        html = """
        <h1>查詢老師研究室</h1>
        <form action="/search" method="post">
            <input type="text" name="keyword" placeholder="請輸入老師姓名關鍵字" required>
            <button type="submit">開始查詢</button>
        </form>
        <br><a href=/>回到首頁</a>
        """
        return html

@app.route("/webhook3", methods=["POST"])
def webhook3():
    # build a request object
    req = request.get_json(force=True)
    # fetch queryResult from json
    action =  req.get("queryResult").get("action")
    #msg =  req.get("queryResult").get("queryText")
    #info = "動作：" + action + "； 查詢內容：" + msg
    if (action == "rateChoice"):
        rate =  req.get("queryResult").get("parameters").get("rate")
        info = "我是吳柏慶開發的電影聊天機器人,您選擇的電影分級是：" + rate + "，相關電影：\n"
        db = firestore.client()
        collection_ref = db.collection("本週新片含分級")
        docs = collection_ref.get()
        result = ""
        for doc in docs:
            dict = doc.to_dict()
            if rate in dict["rate"]:
                result += "片名：" + dict["title"] + "\n"
                result += "介紹：" + dict["hyperlink"] + "\n\n"
        info += result
    return make_response(jsonify({"fulfillmentText": info}))

    

    




if __name__ == "__main__":
    app.run(debug=True)