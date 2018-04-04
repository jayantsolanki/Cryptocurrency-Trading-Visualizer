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

		    self.table = Table(self.tablename, self.metadata,
		        Column('id', Integer, primary_key=True),
		        Column('transactionType', String(4)),
		        Column('price', DECIMAL(64,10)),
		        Column('count', DECIMAL(64,10)),
		        Column('exchange', String(40)),
		        Column('pairname', String(10)),
		        mysql_engine='InnoDB',
		          mysql_charset='utf8'
		    )
		    self.table.create()

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

	def selectData(self, params, arguments):
		# chanId = arguments("exchange")
		request = json.dumps({ k: arguments(k) for k in params })
		request = json.loads(request)
		query = self.orderBook.select()
		numRows = 50 #default number of rows to be fetched unless specified
		if 'price_greater_than' in request:
			query = query.where(self.orderBook.c.price > float(request['price_greater_than']))
			# print(query)

		elif 'pair' in request:
			query = query.where(self.orderBook.c.pairname == request['pair'])
			# print(query)
		elif 'exchange' in request:
			query = query.where(self.orderBook.c.exchange == request['exchange'])
			
		if 'numRows' in request:
			numRows = int(request['numRows'])
		query = query.order_by(desc(self.orderBook.c.id)) # for snapshot, recent rows
		query = query.limit(numRows)
		result = self.db.execute(query)
		packet = []
		for row in result:
			payload = {
				'transactionType': row.transactionType,
				'price' : float(row.price),
				'count' : float(row.count),
				'exchange' : row.exchange,
				'pairname' : row.pairname
			}
			packet.append(payload)
		return (json.dumps(packet))
