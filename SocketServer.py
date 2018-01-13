# Socket IO server to communicate with the Android Application
# Green / Reset print('\033[1;32;40m XYZ \033[39;49m')

import socketio
import eventlet
from MongoGET import set_Socket,rem_Socket,get_Socket,set_fulfilled,\
                    update_Notification,get_not_reached,get_Notification
from json import loads



sio = socketio.Server()
app = socketio.Middleware(sio)

@sio.on('connect')
def connect(sid, environ):
    queries = [ i.split('=') for i in environ['QUERY_STRING'].split('&') ]
    query_dict = {}
    for i,j in queries:
        query_dict[i]=j
    print(query_dict)

    if not 'uid' in query_dict.keys():
        sio.disconnect(sid)
    else:
        print('Inserted ',sid)
        print(set_Socket(query_dict['uid'],sid))
        # Check if there exists any not_reached notifications
        not_reached = get_not_reached(query_dict['uid'])
        if not_reached is not None:
            for i in not_reached:
                sio.emit('Notification',get_Notification(_all=False,_id = i['_id']),room= \
                    get_Socket(i['UID'])['SID'],callback=set_fulfilled)
        else:
            pass

@sio.on('disconnect')
def disconnect(sid):
    print('removed ',sid)
    rem_Socket(sid)
    print('disconnect ', sid)

@sio.on('NotifyAll')
def NotifyAll(sid,args):
    args = loads(args)
    WID=args['WID']
    pair_name=args['pair_name']
    last_price=args['last_price']
    print("Inside Notify All")
    if WID == "BTFX":
        for i in get_Notification(_all=True,WID="BTFX",Pair=pair_name,Price=last_price):
            print("Attempting to Notify ",i['UID'])
            if get_Socket(i['UID']) is not None:
                print('Sending data ',get_Socket(i['UID']))
                sio.emit('Notification',get_Notification(_all=False,_id = i['_id']),room= \
                        get_Socket(i['UID'])['SID'],callback=set_fulfilled)
                        # set_fulfilled must be called with 0 or 1 from client
                        # If he wants to set or unset the notification
                        # As soon as the client recieves the application will
                        # invoke the callback with the _id sent with the Notification
                        # Which will call set_fulfilled and reset the fulfilled field
            else:
                print("Notification Unsuccessful")
                # The user was not connected at the time of change
                # Update the notification with not_reached as true and set the
                # price_then field to the last_price at that moment
                update_Notification(last_price,i['_id'])
if __name__ == "__main__":
    eventlet.wsgi.server(eventlet.listen(('', 8000)), app)
