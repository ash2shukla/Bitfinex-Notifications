from websockets import connect
from json import loads,dumps
import asyncio
from socketIO_client import SocketIO
from time import sleep


WID = "BTFX"
template_ticker = {"event":"subscribe","channel":"ticker","pair":""}
# ticker_response = ['channel_id','bid','bid_size','ask','ask_size','daily_change'\
#                    ,'daily_change_perc','last_price','volume','high','low']
pair_map = {}

NotificationSocket = SocketIO('localhost', 8000)

async def get_data(payloads):
    url= "wss://api.bitfinex.com/ws"
    async with connect(url) as websocket:
        for payload in payloads:
            await websocket.send(payload)
        async for message in websocket:
            parse(message)

def parse(msg):
    res = loads(msg)

    # dict response means it's a response for corresponding to a 'send'

    if isinstance(res,dict):
        event = res['event']
        if event == 'info':
            try:
                code = res['code']
                if code == 20051:
                    # Stop/Restart WebSocket Server From Bitfinex
                    init_socketserver()
                elif code == 20060:
                    # Data Refreshing . pause all activity Max Time 10 seconds
                    sleep(10)
                elif code == 20061:
                    init_socketserver()
                    # Restart paused activities preferably resubscribe all

            except KeyError:
                if res['version'] == 1.1:
                    pass
                else:
                    print("API Version Mismatch")
                    return
        elif event == 'subscribed':
            pair_map[res['chanId']] = res['pair']
            print(pair_map)

    # if instance is list then it's a response of subscribed pair
    # Check the channelID for pair name from pair_map to identify response
    elif isinstance(res,list):
        channelID = res[0]
        try:
            pair_name = pair_map[res[0]]
            if res[1] == "hb":
                # HeartBeat for channelID
                print(pair_name, "Alive")
            else:
                # Pass the data to train model

                # res[7] is last_price
                # See ticker_response Template @ line 10
                NotificationSocket.emit('NotifyAll',dumps({"WID":WID,"pair_name":\
                                        pair_name,"last_price":res[7]}))


        except KeyError:
            # A response for a channel that wasn't subscribed
            print("Stray Response")

def init_socketserver():
    # pass the list of required pairs
    pairs = ['tBTCUSD','tBCHBTC']
    payloads = []
    for  i in pairs:
        template_ticker['pair'] = i
        payloads.append(dumps(template_ticker))

    asyncio.get_event_loop().run_until_complete(get_data(payloads))

if __name__ == "__main__":
    init_socketserver()
