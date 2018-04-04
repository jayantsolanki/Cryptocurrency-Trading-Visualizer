from sqlalchemy import *
import pymysql
# pip install mysqlclient
pymysql.install_as_MySQLdb()

self.db = create_engine('mysql://root:jayant123@localhost',pool_recycle=3600) # connect to server


self.db.echo = False  # Try changing this to True and see what happens


def createDatabase(self):
	try:
		self.db.execute("CREATE DATABASE IF NOT EXISTS Trading;") #create db
	except:
		print("Database Trading already exist")
	self.db.execute("USE Trading") # select Trading for use
	self.metadata = MetaData(db)

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
print(db.dialect.has_table(db, 'users'))

if not engine.dialect.has_table(engine, Variable_tableName):  # If table don't exist, Create.
    metadata = MetaData(engine)
    # Create a table with the appropriate Columns
    Table(Variable_tableName, metadata,
          Column('Id', Integer, primary_key=True, nullable=False), 
          Column('Date', Date), Column('Country', String),
          Column('Brand', String), Column('Price', Float),
    # Implement the creation
    metadata.create_all()

i = users.insert()
i.execute(name='Mary', age=30, password='secret')
i.execute({'name': 'John', 'age': 42},
          {'name': 'Susan', 'age': 57},
          {'name': 'Carl', 'age': 33})

s = users.select()
rs = s.execute()

row = rs.fetchone()
print ('Id:', row[0])
print ('Name:', row['name'])
print ('Age:', row.age)
print ('Password:', row[users.c.password])

for row in rs:
    print (row.name, 'is', row.age, 'years old')
