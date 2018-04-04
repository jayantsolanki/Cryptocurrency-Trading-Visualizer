from sqlalchemy import *
import pymysql
# pip install mysqlclient
pymysql.install_as_MySQLdb()

class MysqlDriver(object):
	def __init__(self, host, username, password, database, create):
		self.db = create_engine('mysql://'+username+':'+password+'@'+host,pool_recycle=3600) # connect to server
		self.database = database
		if create == True:#create database
			self.createDatabase()
		else:
			self.useDatabase()

	def createDatabase(self):
		try:
		    self.db.execute("CREATE DATABASE IF NOT EXISTS "+self.database) #create db
		except:
		    print("Database "+self.database+" already exist")
		self.db.execute("USE "+self.database+";") # select Trading for use
		self.metadata = MetaData(self.db)
		#creating the table if not existing
		self.createTable()
		# return self.db

	def useDatabase(self):
		self.db.execute("USE "+self.database+";") # select Trading for use
		self.metadata = MetaData(self.db)
		# return self.db

	def createTable(self):
		if not self.db.dialect.has_table(self.db, 'users'):  # If table don't exist, Create.

		    self.users = Table('order_book', self.metadata,
		        Column('id', Integer, primary_key=True),
		        Column('transactionType', String(4)),
		        Column('price', DECIMAL(10,6)),
		        Column('count', DECIMAL(10,6)),
		        Column('exchange', String(40)),
		        Column('pairname', String(10)),
		        mysql_engine='InnoDB',
		          mysql_charset='utf8'
		    )
		    self.users.create()

	def insertData(self):
		self.db.execute("USE "+self.database+";") # select Trading for use
		tablename=Table('order_book',self.metadata)
		# query = insert('order_book').values({"transactionType": "ask", "price": 6920, "count": 14, "exchange": "Bitfinex", "pairname": "BTCUSD"})
		# self.db.execute(query)
		query = tablename.insert()
		query.execute({"transactionType": "ask", "price": 6920, "count": 14, "exchange": "Bitfinex", "pairname": "BTCUSD"})
		print(query)
		# return self.db