import pyrebase
config = {     
  "apiKey": "AIzaSyAOMX9Qrb-y6DHZG22JqBJNTCh-3AGY2Ug",
  "authDomain": "project-smart-lock.firebaseapp.com",
  "databaseURL": "https://project-smart-lock-default-rtdb.firebaseio.com",
  "storageBucket": "project-smart-lock.appspot.com"
}

firebase = pyrebase.initialize_app(config)
db = firebase.database()
storage = firebase.storage()

users = db.child("users").get()
data = db.child("History").child("xin chao").get()
db.child("History").child("12//2//3").set("xxxxx")
print(data.val())
# print(type(users.val()))
Dict = {}
for user in users.each():
    Dict[user.val()['id']] = [user.val()['idcard'],user.val()['lablename']]
# print(Dict)

# for key, value in Dict.items():
#     print(key, ' : ', value)
id = '320097137727'
index = ""
lists = list(Dict.values())
print(lists)
for x in lists:
    if id in x:
        print("ok")
# if id in Dict.values():
#     Dict
# else:
#     print("àasfasfsaf")
