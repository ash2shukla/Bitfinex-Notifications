# UID(str), WID(Website (Poloniex,Bitfinex)), Pair(BTCUSD,..) ,
# Price (last_price), is_high_low

# UID,WID,pair,price,hl (notifsCOllection)
# UID: SocketID (UIDmap)

from pymongo import MongoClient
from bson.objectid import ObjectId
from bson.json_util import dumps

url = "mongodb://localhost:27017"

client = MongoClient(url)['notifs']
collection_list = ['notifsCollection','UIDMap']
for i in collection_list:
    if i not in client.collection_names():
        client.create_collection(i)

notifsCollection = client['notifsCollection']
UIDMap = client['UIDMap']

def set_Notification(UID,WID,pair,price,hl,msg):
    notif = {'UID':UID,'WID':WID,'pair':pair,'price':price,'hl':hl,'fulfilled':False,\
            'message':msg,'price_then':0.0,'not_reached':False}

    _id = notifsCollection.insert_one(notif).inserted_id
    return _id

def get_Notification(_all=False,_id="",WID="",Pair="",Price=0.0):
    if _all :
        # return all those notifications which are not fulfilled and satisfy the criteria
        try:
            return list(notifsCollection.find({'WID':WID,'pair':Pair,'fulfilled':False,\
                    'not_reached':False,'$where':'('+str(Price)+'>this.price ) == this.hl'}))
        except TypeError:
            return []

    else:
        # Just return the required
        return dumps(notifsCollection.find_one({'_id':_id}))

def get_not_reached(UID=""):
    try:
        return list(notifsCollection.find({'UID':UID,'not_reached':True}))
    except TypeError:
        return None

def set_fulfilled(_id,state):
    # Set not_reached as False as set_fulfilled is also called on_connect
    # on not_reached's delivery
    _id = ObjectId(_id['$oid'])
    notifsCollection.update({'_id':_id},{'$set':{'fulfilled':bool(state),\
    'not_reached':False,'price_then':0.0}})

def set_Socket(UID,SID):
    sock = {'UID':str(UID),'SID':str(SID)}
    obj = UIDMap.find_one_and_delete({'UID':str(UID)})
    _id = UIDMap.insert_one(sock).inserted_id
    return _id

def get_Socket(UID):
    return (UIDMap.find_one({'UID':UID}))

def rem_Socket(SID):
    UIDMap.find_one_and_delete({'SID':str(SID)})

def update_Notification(last_price,_id):
    print("Called Updating for last_price and ID")
    notifsCollection.update({'_id':_id},{'$set':{'not_reached':True,'price_then':last_price}})

if __name__ == "__main__":
    set_Notification(UID='ID1',WID='BTFX',pair='BTCUSD',price=16000,hl=False,\
                    msg="Price is below 16000 let's buy some more.")
    set_Notification(UID='ID1',WID='BTFX',pair='BTCUSD',price=16010,hl=True,\
                    msg="Price is Above 16010 now let's sell it.")
                    # Let the Current price be 16500
    set_Notification(UID='ID1',WID='BTFX',pair='BTCUSD',price=17000,hl=False,\
                    msg="Price is below 17000")
    set_Notification(UID='ID1' ,WID='BTFX',pair='BTCUSD',price=17010,hl=True,\
                    msg="Price is above 17010")
    #print(set_fulfilled(_id=ObjectId("5a483d78f5a7476cd8a8d639"),state=1))
    #pass
