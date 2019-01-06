# Cryptocurrency-Trading-Visualizer

## Introduction
***
In this project we will be connecting to two Websocket channels via their APIs: one from Bitfinex and one from Coinbase. These channels relay information about those companies’ Order Books. We will be subscribing to all the avaialable number of pairs(BTCUSD, BTCEUR, etc.). Upon connection, they each send a snapshot of their respective order books and then send any subsequent updates. 
This project is a full-fledged application, with a back-end, a front-end, and a database that will both store and relay this data/updates.

## Features
***
This project has following features:
* **Back-End using Tornado Framework**
    * Multi-threaded Websocket connections to both exchanges’ order books.
    * Provision to create a new consolidated order book that contains information from both exchanges, which is aggregated from the snapshots that come from the Bitfinex/Gdax Websocket APIs as well as the updates they each emit.
      * Upon receiving the snapshot, application parses the data (i.e. find whether the transaction is a bid or ask, find the price, find the count, and find the amount of the transaction, and store it into a MySQL database using SQLAlchemy). Data model has columns for the transaction type (bid or ask), the price, the count (size), the exchange (Bitfinex or Gdax), and the pairname (“USDEUR”, etc.)
      * Same above parsing  are done for each update that is emitted by the 2 APIs. SQLAlchemy is used for creating and updating the models.
    * Websocket Server API that returns the consolidated order book to the subscribed users
      * The user receives the order book on connection.
      * The Websocket server emits any updates that occur to order book (these updates are to be used in the front-end for real-time functionality)
    * A REST endpoint which will return a snapshot of your order book, with the ability to take query parameters for filtering the order book
      * price_greater_than – Return orders where the price is greater than the number specified.
      * exchange – Return orders only from a certain exchange (i.e. exchange=bitfinex).
      * Bonus Points – pair – Return orders for the pair specified (i.e. pair=BTCUSD).

* **Front-End**
    * A small Angular 4 app that connects to the back-end.
    * The app displays the order book that is stored in the data model and update the view in real-time with any updates that come from your Websocket connection.
    * App includes a form (Reactive Form) for filtering the snapshot of the order book (using the parameters defined in the back-end section).
 
## Documentation
***
Report and documentation can be found on this [Documentation](https://github.com/jayantsolanki/Cryptocurrency-Trading-Visualizer-Backend/tree/master/docs)

## Folder Tree
***
* [**docs**](https://github.com/jayantsolanki/Automated-Difficulty-prediction-for-Exam-Questions/tree/master/docs) contains documentation and paper
* [**src**](https://github.com/jayantsolanki/Automated-Difficulty-prediction-for-Exam-Questions/tree/master/src) contains codes
  * 611-Proj-Ques-Eval-Frontend: Contains the Website
  * Python-Web-Server: Provide REST APIs solution for running Machine Learning Algorithm

## Contributors
***
  * [Jayant Solanki](https://github.com/jayantsolanki)
  
## Tech-stack
* Backend
  * Python 3.6
  * Tornado for Rest APIs
  * SQLAlchemy
  * Python WebSocket
  * MySQL
* Frontend
  * Angular 4
  * HTML5/CSS
  * WebSocket

## Acknowledgement
***
* Noble Group (http://www.thisisnoble.com)
