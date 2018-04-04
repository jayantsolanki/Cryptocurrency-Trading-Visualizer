#!/usr/bin/env python
# websocket client for listening to the Trading Webste
from tornado.ioloop import IOLoop, PeriodicCallback
from tornado import gen
from tornado.websocket import websocket_connect
import json
import requests
import sys


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
                self.bitfinexSubscribe()#comment this line for debugging
                pass
            elif self.mode==2:
                self.gdaxSubscribe()
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
                if self.mode == 1:# for bitfinex
                    # msgs for bitfinex
                    if 'event' in message:
                        if message['event'] == "subscribed":
                            self.channelIdVal[message['chanId']] = message['pair'] # storing the mapping for pair with its channel id
                    else:
                        # print(message)
                        MSG = yield self.WS.read_message()
                        if MSG is None:#can be replaced by while loop
                            print ("connection closed for "+self.URL+ " trying again")
                            self.connectLocal()
                        else:
                            BitfinexData(message, self.channelIdVal, self.WS)
                elif self.mode == 2:#for GDAX
                    # if 'product_id' in message:
                    # MSG = yield self.WS.read_message()
                    # print(message)
                    # if MSG is None:#can be replaced by while loop
                    #     print ("connection closed for "+self.URL+ " trying again")
                    #     print("I m inside")
                    #     self.connectLocal()
                    # else:
                    #     # pass
                    GdaxData(message, self.WS)
                    # print(message)


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
            # break


    def gdaxSubscribe(self):
        requestArticles = requests.get("https://api.gdax.com/products")#fetching all the active product ids from gdax
        pairs = requestArticles.json()
        prodIds = []
        for pair in pairs:# contructing list of the productids to be subscribed
            # print(pair['id'])
            prodIds.append(pair['id'])
            print("Subscribing to productids: "+pair['id'])
            # break
        request = {}
        request['type'] = 'subscribe'
        request['product_ids'] = prodIds
        request['channels'] = ["level2"]
        json_request = json.dumps(request)
        # print(json_request)
        self.ws.write_message(json_request)

    def keep_alive(self):#if connection goes down
        if self.ws is None:
            self.connect()
        else:
            pass
            # self.ws.write_message("keep alive")#check this part of the code for heartbeat or use pass


#### Helper class for passing data to the local websocket server
class BitfinexData(object):
    def __init__(self, data, channelIdVal, WS):
        self.data = data
        self.channelIdVal = channelIdVal#for remapping channel id to pair name
        self.WS = WS
        self.parseData()

    @gen.coroutine
    def parseData(self):
        try: 
            #creating payload for the Bitfine
            self.packet = []
            # print(self.data)
            # print(len(self.data[1]))
            if len(self.data[1]) > 3: #only for snapshots, 3 becoz the list size for update has only three elements
                for item in self.data[1]:
                    payload = {}
                    if item[2] >= 0: #deciding for bid or ask, also if count equlas zero then not storing that msg
                        payload['transactionType'] = 'bid'
                    elif item[2] < 0:
                        payload['transactionType'] = 'ask'
                    payload['price'] = item[0]
                    payload['count'] = item[1]
                    payload['exchange'] = "Bitfinex"
                    payload['pairname'] = self.channelIdVal[self.data[0]]
                    self.packet.append(payload)
                    # print(payload)
            elif len(self.data[1]) == 3: #is updates are coming, excluding heartbeat
                payload = {}
                if self.data[1][2] >= 0:#deciding for bid or ask
                    payload['transactionType'] = 'bid'
                elif self.data[1][2] < 0:
                    payload['transactionType'] = 'ask'
                payload['price'] = self.data[1][0]
                payload['count'] = self.data[1][1]
                payload['exchange'] = "Bitfinex"
                payload['pairname'] = self.channelIdVal[self.data[0]]
                self.packet.append(payload)
                # print(payload)
            #sending the packet to local websocket server
            self.WS.write_message(json.dumps(self.packet))
            # self.ws.close()
        except:
            print("Error happened while sending the bitfinex data to the local websocket server", sys.exc_info()[0])


class GdaxData(object):
    def __init__(self, data, WS):
        self.data = data
        self.WS = WS
        self.parseData()

    @gen.coroutine
    def parseData(self):
        try: 
            #creating payload for the Gdax
            self.packet = []
            if 'type' in self.data:#rejecting other messages if they dont have product ids
                if self.data['type'] == 'snapshot':#snapshot
                    if 'bids' in self.data:#get values in bid
                        for item in self.data['bids']:
                            payload = {
                                'transactionType': 'bid',
                                'price':float(item[0]),
                                'count':float(item[1]),
                                'exchange': "Gdax",
                                'pairname':self.data['product_id'].replace('-', '')
                            }
                            self.packet.append(payload)
                    # print(payload)
                    if 'asks' in self.data:#get values in ask
                        for item in self.data['asks']:
                            if float(item[1])!=0:
                                payload = {
                                    'transactionType': 'ask',
                                    'price':float(item[0]),
                                    'count':float(item[1]),
                                    'exchange': "Gdax",
                                    'pairname':self.data['product_id'].replace('-', '')
                                }
                                self.packet.append(payload)
                elif self.data['type'] == 'l2update':
                    for item in self.data['changes']:
                            if float(item[2])!=0:#bypassing values with count equals zero
                                payload = {}
                                if item[0] == 'sell':
                                    payload['transactionType'] = 'ask'
                                elif item[0] == 'buy':
                                    payload['transactionType'] = 'bid'
                                payload['price'] = float(item[1])
                                payload['count'] = float(item[2])
                                payload['exchange'] = "Gdax"
                                payload['pairname'] = self.data['product_id'].replace('-', '')
                                self.packet.append(payload)
                # print(self.packet)
                self.WS.write_message(json.dumps(self.packet))
            else:
                pass
        except:
            print("Error happend while sending the Gdax data to the local websocket server", sys.exc_info()[0])
