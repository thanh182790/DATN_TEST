import pyrebase
config = {     
  "apiKey": "AIzaSyBL9p5Gp7hkprcNy_Bj9TGZFQnJW8YaM3Y",
  "authDomain": "finalproject-db669.firebaseapp.com",
  "databaseURL": "https://finalproject-db669-default-rtdb.firebaseio.com",
  "storageBucket": "finalproject-db669.appspot.com"
}
firebase = pyrebase.initialize_app(config)
db = firebase.database()
storage = firebase.storage()
db.child("Global_variable").child("face").child("canceladdface").set("False")
# users = db.child("users").get()
# data = db.child("History").child("xin chao").get()
# db.child("History").child("12//2//3").set("xxxxx")
# print(data.val())
# # print(type(users.val()))
# Dict = {}
# for user in users.each():
#     Dict[user.val()['id']] = [user.val()['idcard'],user.val()['lablename']]
# # print(Dict)

# # for key, value in Dict.items():
# #     print(key, ' : ', value)
# id = '320097137727'
# index = ""
# lists = list(Dict.values())
# print(lists)
# for x in lists:
#     if id in x:
#         print("ok")
# # if id in Dict.values():
# #     Dict
# # else:
# #     print("àasfasfsaf")

""" code get url của 1 file trên firebase
 url = storage.child("acv")
localpath = "/home/pi/Desktop/a.jpg"
cloud = "image/pi.jpg"
# firebase.storage().child(cloud).put(localpath)
print(type(storage.child("PicAvt/CJjR87lyjdOvnxMObDvuqtzyeXx2.jpg").get_url(None))) """


"""  Code get tất cả các giá trị rfid, lable, active của các user cho vào 1 dictionary
RefUsers = db.child("users").get()
DictValAuthUser = {}
for user in RefUsers.each():
    DictValAuthUser[user.val()['id']] = [user.val()['idcard'],user.val()['lablename'], user.val()['active']]

print(DictValAuthUser) """

""" code xóa lablename trong file đã mã hóa 
ls = []
for index, val in enumerate(encoded_data['names']):
	if val == "thanh":
		ls.append(index)
print(ls)
if len(ls):
	del encoded_data['encodings'][ls[0]:ls[-1]+1]
	del encoded_data['names'][ls[0]:ls[-1]+1]

with open("Mahoa.pickle", 'wb') as file:
	file.write(pickle.dumps(encoded_data)) """
