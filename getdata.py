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

Dict = {}
for user in users.each():
    Dict[user.val()['id']] = user.val()['idcard']
print(Dict)


id = '506174ư384351'

if id in Dict.values():
    print("OKOKOKOKOK")
else:
    print("àasfasfsaf")