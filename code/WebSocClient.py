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
        self.timeout = timeout
        self.ioloop = IOLoop()
        self.ws = None
        self.mode = mode#1 for bitfinex, 2 for gdax
        self.channelIdVal = {}
        self.connect()
        PeriodicCallback(self.keep_alive, 20000, io_loop=self.ioloop).start()
        self.ioloop.start()

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
                self.bitfinexSubscribe()
            elif self.mode==2:
                # self.gdaxSubscribe()
                pass
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
                if self.mode == 1:
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
                        BitfinexData(message, self.channelIdVal)
                        # pass
                elif self.mode == 2:
                    pass


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
        request = {}
        request['event'] = 'subscribe'
        request['channel'] = 'BTCUSD'
        json_request = json.dumps(request)
        print(json_request)
        # self.ws.write_message(json_request)

    def keep_alive(self):#if connection goes down
        if self.ws is None:
            self.connect()
        else:
            pass
            # self.ws.write_message("keep alive")#check this part of the code for heartbeat or use pass


class BitfinexData(object):
    def __init__(self, data, channelIdVal):
        self.data = data
        self.channelIdVal = channelIdVal
        self.url = "ws://localhost:8888/noble-markets-realtime-order-book"
        self.ioloop = IOLoop()
        self.parseData()
        self.ioloop.start()
# self.channelIdVal[self.data[0]]
    @gen.coroutine
    def parseData(self):
        # pass
        self.payload = {
            'place': "bitfinex",
            'chanId':self.channelIdVal[self.data[0]],
            'data': self.data[1]
        }

        print ("Establishing connection to "+self.url)
        try:
            self.ws = yield websocket_connect(self.url)
        except:
            print ("connection error "+self.url)
        else:
            print ("connected to "+self.url)
            self.ws.write_message(json.dumps(self.payload))
            self.ws.close()
            # self.ioloop.stop()

        # # print(jay[1])
        # # data = {
        # #     'payload[]': jay[1],
        # #     'chanId' : jay[0]
        # # }
        # # print(jay[1])
        # payload = {'chanId': jay[1][0] 
        #    # 'favefood': ['raw donuts', 'free donuts']
        # }
        # r = requests.post('http://localhost:8888/noble-markets-order-book-snapshot', data=jay[1][0], contentType= 'application/x-www-form-urlencoded')
        # print(jay[1][0])
        # print ("Sending the data Data.....")
        # print(self.data)
        # client = Client("ws://localhost:8888/noble-markets-realtime-order-book", 5, 0)

        # self.ioloop.stop()



# if __name__ == "__main__":
    # client = Client("wss://api.bitfinex.com/ws", 5, 1)
    # client = Client("wss://ws-feed.gdax.com", 5, 2)
