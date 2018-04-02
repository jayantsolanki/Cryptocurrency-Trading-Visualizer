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
            else:
                pass


    @gen.coroutine
    def run(self):
        while True:#look for new messages
            msg = yield self.ws.read_message()
            message = json.loads(msg)
            if msg is None:
                print ("connection closed for "+self.url)
                self.ws = None
                break
            else:
                if self.mode == 1:
                    # msgs for bitfinex
                    if 'event' in message:
                        # self.channelIdVal[message['chaId']] = message['pair']
                        print(message)
                        # print(message['chaId'])
                        # print(message['pair'])
                    else:
                        print(message)
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
            print(json_request)
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

# if __name__ == "__main__":
    # client = Client("wss://api.bitfinex.com/ws", 5, 1)
    # client = Client("wss://ws-feed.gdax.com", 5, 2)