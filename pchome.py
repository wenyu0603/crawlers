import requests
import pprint
import re

import mysql.connector
from mysql.connector import errorcode

DB_NAME = 'pchome'

try:
  cnx = mysql.connector.connect(user='root',password = 'emily880603', host = '127.0.0.1')
except mysql.connector.Error as err:
  if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
    print("Something is wrong with your user name or password")
  elif err.errno == errorcode.ER_BAD_DB_ERROR:
    print("Database does not exist")
  else:
    print(err)
else:
  print('successfully connected to MySQL server')

cursor = cnx.cursor()


#Create database if not exist
def create_database(cursor):
    try:
        cursor.execute(
            "CREATE DATABASE {} DEFAULT CHARACTER SET 'utf8'".format(DB_NAME))
    except mysql.connector.Error as err:
        print("Failed creating database: {}".format(err))
        exit(1)

try:
    cursor.execute("USE {}".format(DB_NAME))
except mysql.connector.Error as err:
    print("Database {} does not exists.".format(DB_NAME))
    if err.errno == errorcode.ER_BAD_DB_ERROR:
        create_database(cursor)
        print("Database {} created successfully.".format(DB_NAME))
        cnx.database = DB_NAME
    else:
        print(err)
        exit(1)

#Creating database

TABLES = {}
TABLES['products'] = (
    "CREATE TABLE `products` ("
    "  `id` int NOT NULL AUTO_INCREMENT,"
    "  `name` varchar(50) NOT NULL,"
    "  `price` int NOT NULL,"
    "  PRIMARY KEY (`id`)"
    ") ENGINE=InnoDB")

for table_name in TABLES:
    table_description = TABLES[table_name]
    try:
        print("Creating table {}: ".format(table_name), end='')
        cursor.execute(table_description)
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
            print("already exists.")
        else:
            print(err.msg)
    else:
        print("OK")


add_product = ("INSERT INTO products "
               "(name, price) "
               "VALUES (%s, %s)")

r = requests.get('https://ecshweb.pchome.com.tw/search/v3.4/all/results?q=%E6%9B%B2%E9%9D%A2%E8%9E%A2%E5%B9%95&page=1&sort=sale/dc')
if r.status_code == requests.codes.ok:
    data = r.json()
    # pprint.pprint(data)
    for product in data['prods']:
        name = product['name']
        price = product['price']
        if len(name) > 50:
            name = name[:50]
        print(name)
        print(price)
        data_product = (name, price)
        # Insert new product
        cursor.execute(add_product, data_product)

# Make sure data is committed to the database
cnx.commit()

print('closing')

cursor.close()
cnx.close()


	