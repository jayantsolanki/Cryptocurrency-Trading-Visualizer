#!/usr/bin/env python


import logging
import tornado.escape
import tornado.ioloop
import tornado.web
import os.path
import uuid
from WebSocClient import Client
from tornado.concurrent import Future
from tornado import web, websocket
from tornado.options import define, options, parse_command_line
from threading import Thread

define("port", default=8888, help="run on the given port", type=int)


class HomePage(tornado.web.RequestHandler):
    @web.asynchronous
    def get(self):
        # self.render("index.html")
        print("This will be the main page")


class SendRealTimeUpdates(websocket.WebSocketHandler):
    def check_origin(self, origin):
        return True

    def open(self):
        if self not in cl:
            cl.append(self)

    def on_close(self):
        if self in cl:
            cl.remove(self)


class SendSnapshot(tornado.web.RequestHandler):
    @web.asynchronous
    def get(self):
        print("This is the snapshot data")
        # self.render("Hello World")
        # self.finish()
        # id = self.get_argument("id")
        # value = self.get_argument("value")
        # data = {"id": id, "value" : value}
        # data = json.dumps(data)
        # for c in cl:
        #     c.write_message(data)



def main():
    parse_command_line()
    app = tornado.web.Application(
        [
            (r"/", HomePage),
            (r"/noble-markets-realtime-order-book", SendRealTimeUpdates),#send only realtime updates
            (r"/noble-markets-order-book-snapshot", SendSnapshot),
        ]
    )
    app.listen(options.port)
    print("WebSocker Server Started on localhost port "+str(options.port))
    tornado.ioloop.IOLoop.current().start()

def ConnectBitfinex():
    client = Client("wss://api.bitfinex.com/ws/2", 5, 1)

def ConnectGdax():
    client = Client("wss://ws-feed.gdax.com", 5, 2)

if __name__ == "__main__":
    thread = Thread(target = ConnectBitfinex)
    thread2 = Thread(target = ConnectGdax)
    thread3 = Thread(target = main)
    thread.start()
    thread2.start()
    thread3.start()
    thread.join()
    # main()