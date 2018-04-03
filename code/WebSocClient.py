#!/usr/bin/env python
# websocket client for listening to the Trading Webste
from tornado.ioloop import IOLoop, PeriodicCallback
from tornado import gen
from tornado.websocket import websocket_connect
import json
import requests


class Client(object):
    def __init__(self, url, timeout, mode):
        self.url = url
        self.URL = "ws://localhost:8888/noble-markets-realtime-order-book" #local websocket server
        self.timeout = timeout
        self.ioloop = IOLoop()
        self.ws = None
        self.mode = mode#1 for bitfinex, 2 for gdax
        self.channelIdVal = {}
        self.connectLocal()#create connection to local WebSocket Server
        self.connect()
        PeriodicCallback(self.keep_alive, 20000, io_loop=self.ioloop).start()
        self.ioloop.start()


    @gen.coroutine
    def connectLocal(self): # for resuing sma ewebscoket connection, so as to prevent creation of multiple redundant connections
        print ("Establishing connection to Local Websocket server "+self.url)
        try:
            self.WS = yield websocket_connect(self.URL)
        except:
            print ("connection error "+self.URL)
        else:
            pass

    @gen.coroutine
    def connect(self):
        print ("Establishing connection to "+self.url)
        try:
            self.ws = yield websocket_connect(self.url)
        except:
            print ("connection error "+self.url)
        else:
            print ("connected to "+self.url)
            self.run()
            # code for subscribing goes here
            if self.mode==1:
                # self.bitfinexSubscribe()#comment this line for debugging
                pass
            elif self.mode==2:
                self.gdaxSubscribe()
                # pass
            # elif self.mode==0:
            #     print ("you have entered the dungeon, exit now!!!!")
            #     self.ioloop.stop()

            else:
                pass


    @gen.coroutine
    def run(self):
        while True:#look for new messages
            msg = yield self.ws.read_message()
            if msg is None:
                print ("connection closed for "+self.url)
                self.ws = None
                break
            else:
                message = json.loads(msg)#converting the response into json
                if self.mode == 1:# for bitfinex
                    # msgs for bitfinex
                    if 'event' in message:
                        if message['event'] == "subscribed":
                            # print(message)
                            # print(message['chanId'])
                            # print(message['pair'])
                            self.channelIdVal[message['chanId']] = message['pair']
                            # print(self.channelIdVal)
                    else:
                        # print(message)
                        MSG = yield self.WS.read_message()
                        if MSG is None:#can be replaced by while loop
                            print ("connection closed for "+self.URL+ " trying again")
                            self.connectLocal()
                        else:
                            BitfinexData(message, self.channelIdVal, self.WS)
                            # pass #discard that message, badluck
                        # pass
                elif self.mode == 2:#for GDAX
                    print(message)
                    # pass


    def bitfinexSubscribe(self):
        requestArticles = requests.get("https://api.bitfinex.com/v1/symbols")#fetching all the active pairs
        pairs = requestArticles.json()
        # print(pairs)
        for pair in pairs: #subscribing to all active pairs
            print("Subscribing to pair: "+pair)
            request = {}
            request['event'] = 'subscribe'
            request['channel'] = "book"
            request['pair'] = pair
            request['prec'] = "P1"
            request['freq'] = "F1"
            json_request = json.dumps(request)
            # print(json_request)
            self.ws.write_message(json_request)


    def gdaxSubscribe(self):
        # requestArticles = requests.get("https://api.bitfinex.com/v1/symbols")#fetching all the active pairs
        # pairs = requestArticles.json()
        # print(pairs)
        # {
        #     "type": "subscribe",
        #     "product_ids": [
        #         "ETH-USD",
        #         "ETH-EUR"
        #     ],
        #     "channels": [
        #         "level2"
        #     ]
        # }
        # for pair in pairs: #subscribing to all active pairs
        #     print("Subscribing to pair: "+pair)
        request = {}
        request['type'] = 'subscribe'
        request['product_ids'] = ["ETH-USD","ETH-EUR"]
        request['channels'] = ["level2"]
        json_request = json.dumps(request)
        print(json_request)
        self.ws.write_message(json_request)

    def keep_alive(self):#if connection goes down
        if self.ws is None:
            self.connect()
        else:
            pass
            # self.ws.write_message("keep alive")#check this part of the code for heartbeat or use pass


class BitfinexData(object):
    def __init__(self, data, channelIdVal, WS):
        self.data = data
        self.channelIdVal = channelIdVal
        # self.url = "ws://localhost:8888/noble-markets-realtime-order-book"
        self.WS = WS
        self.ioloop = IOLoop()
        # 
        self.parseData()
        # self.ioloop.start()
    @gen.coroutine
    def parseData(self):
        self.payload = {
            'place': "bitfinex",
            'chanId':self.channelIdVal[self.data[0]],
            'data': self.data[1]
        }
        # # print ("Establishing connection to "+self.url)
        # try:
        #     self.ws = yield websocket_connect(self.url)
        # except:
        #     print ("connection error "+self.url)
        # else:
        #     # print ("connected to "+self.url)
        self.WS.write_message(json.dumps(self.payload))
            # self.ws.close()
            # self.ioloop.stop()



# if __name__ == "__main__":
    # client = Client("wss://api.bitfinex.com/ws", 5, 1)
    # client = Client("wss://ws-feed.gdax.com", 5, 2)
