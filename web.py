import os
import json
import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud.firestore_v1.base_query import FieldFilter


# 判斷是在 Vercel 還是本地
if os.path.exists('serviceAccountKey.json'):
    # 本地環境：讀取檔案
    cred = credentials.Certificate('serviceAccountKey.json')
else:
    # 雲端環境：從環境變數讀取 JSON 字串
    firebase_config = os.getenv('FIREBASE_CONFIG')
    cred_dict = json.loads(firebase_config)
    cred = credentials.Certificate(cred_dict)

firebase_admin.initialize_app(cred)


from flask import Flask, render_template,request
from datetime import datetime
import random

app = Flask(__name__)

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
    link += "<a href=/read>讀取Firestore資料(根據lab遞減排序，取前4)</a><hr>"
    link += "<a href=/search>查詢老師研究室</a><hr>"
    return link

@app.route("/mis")
def course():
    return "<h1>資訊管理導論</h1><a href=/>回到首頁</a>"
    
@app.route("/today")
def today():
    now = datetime.now()
    year = str(now.year)
    month = str(now.month)
    day = str(now.day)
    formatted_date = year + "年" + month + "月" + day + "日"
    return render_template("today.html", datetime = formatted_date)

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

if __name__ == "__main__":
    app.run(debug=True)
