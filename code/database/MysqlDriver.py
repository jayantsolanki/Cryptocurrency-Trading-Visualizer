from config.config import *
from sqlalchemy import *
import pymysql
import json
# pip install mysqlclient
pymysql.install_as_MySQLdb()

# I could have used ORM, but due to lack of time I settled on classical approach
# insertion is not able to handle bulk inserts in thousands
class MysqlDriver(object):
	def __init__(self, host, username, password, database, tablename, create):
		self.db = create_engine('mysql://'+username+':'+password+'@'+host,pool_recycle=3600) # connect to server
		self.database = database
		self.tablename = tablename
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
		self.orderBook=Table(self.tablename, self.metadata, autoload=True)
		# return self.db

	def createTable(self):
		if not self.db.dialect.has_table(self.db, 'users'):  # If table don't exist, Create.

		    self.users = Table(self.tablename, self.metadata,
		        Column('id', Integer, primary_key=True),
		        Column('transactionType', String(4)),
		        Column('price', DECIMAL(64,10)),
		        Column('count', DECIMAL(64,10)),
		        Column('exchange', String(40)),
		        Column('pairname', String(10)),
		        mysql_engine='InnoDB',
		          mysql_charset='utf8'
		    )
		    self.users.create()

	def insertData(self, data):
		if len(data) > 0:
			try:
				query = self.orderBook.insert()
				query.execute(data)
				# print("Row insertion success")
			except:
				print("OMG!!! I failed at inserting data into the table")
		else:
			pass