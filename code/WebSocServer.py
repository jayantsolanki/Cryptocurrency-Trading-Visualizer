#!/usr/bin/env python
from config.config import *
import logging
import tornado.escape
import tornado.ioloop
import tornado.web
import os.path
import uuid
from WebSocClient import Client
from database.MysqlDriver import MysqlDriver
from tornado.concurrent import Future
from tornado import web, websocket
from tornado.options import define, options, parse_command_line
from threading import Thread
import json

define("port", default=8888, help="run on the given port", type=int)

class HomePage(tornado.web.RequestHandler):
    @web.asynchronous
    def get(self):
        # self.render("index.html")
        self.write("Hello World")
        print("This will be the main page")
        self.finish()


class SendRealTimeUpdates(websocket.WebSocketHandler):
    def check_origin(self, origin):
        return True
    connections = set()
    def open(self):
        # logging.info("A client connected.")
        self.write_message("A client connected.")
        self.connections.add(self)
        # if len(self.connections) == 1:
        # try:
        self.db = MysqlDriver(DATABASE.host,DATABASE.username, DATABASE.password, DATABASE.dbname, DATABASE.tablename, False) # connect to MySql database server
            # self.createDatabase()
        # except:
        #     print("Database connectivity warning")
        print("Active Connections to local Websocket server are  "+str(len(self.connections)))

    def on_close(self):
        logging.info("A client disconnected.")
        self.connections.remove(self)

    def on_message(self, message):
        # logging.info("message: {}".format(message))
        [con.write_message(message) for con in self.connections]
        message = json.loads(message)
        # self.db.insertData(message)

class SendSnapshot(tornado.web.RequestHandler):
    @web.asynchronous
    def set_default_headers(self): # this as safety issues, cors
        origin = self.request.headers.get('Origin')
        if origin:
            self.set_header('Access-Control-Allow-Origin', origin)
        self.set_header('Access-Control-Allow-Credentials', 'true')
    def get(self):
        self.db = MysqlDriver(DATABASE.host,DATABASE.username, DATABASE.password, DATABASE.dbname, DATABASE.tablename, False) # connect to MySql database server
        self.queryResult = self.db.selectData(self.request.arguments, self.get_argument)
        self.write(self.queryResult)
        self.finish()
        # self.write("Your username is %s and password is %s" % (user, passwd))


def main():
    # try:
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
    # except:
    #     print("Server cannot be initialised")


def ConnectBitfinex():
    client = Client("wss://api.bitfinex.com/ws/2", 5, 1)

def ConnectGdax():
    client = Client("wss://ws-feed.gdax.com", 5, 2)

if __name__ == "__main__":
    try:
        dump = MysqlDriver(DATABASE.host,DATABASE.username, DATABASE.password, DATABASE.dbname, DATABASE.tablename, True)# if true, then create database and table
    except:
        print("Database already exists")
    thread = Thread(target = ConnectBitfinex)
    thread2 = Thread(target = ConnectGdax)
    thread3 = Thread(target = main)
    thread.start()
    thread2.start()
    thread3.start()
    thread.join()
    thread2.join()
    thread3.join()
    # main()