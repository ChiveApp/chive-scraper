from pymongo import MongoClient

from pprint import pprint
client  = MongoClient("mongodb+srv://chive:WxOe3jPwS0oAPx1K@cluster0-ugvid.mongodb.net/test?retryWrites=true")
db = client.admin

serverStatusResult=db.command("serverStatus")
pprint(serverStatusResult)