import firebase_admin
from firebase_admin import credentials, firestore

cred = credentials.Certificate("../serviceAccountKey.json")
if not firebase_admin._apps: 
    firebase_admin.initialize_app(cred)

db = firestore.client()

collection_ref = db.collection("靜宜資管")
docs = collection_ref.get()

keyword = input("請輸入老師姓名關鍵字：") 

found = False
for doc in docs:
    user = doc.to_dict()
    if "name" in user and keyword in user["name"]:
        print(f"{user['name']} 老師的研究室是在 {user['lab']}")
        found = True

if not found:
    print(f"找不到姓名包含 '{keyword}' 的老師。")