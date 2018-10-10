import logging
import mysql.connector
import time
import sys
from mysql.connector import errorcode

moduleLogger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

DB_NAME = 'name' 

TABLES = {}
TABLES['index'] = (
    "CREATE TABLE `index` ("
    "  `id` int(11) NOT NULL AUTO_INCREMENT,"   #PK
    "  `index` int(11) not NULL,"               #UNIQUE
    "  `link` varchar(14) NOT NULL,"
    "  PRIMARY KEY (`id`),UNIQUE KEY(`index`)"
    ") ENGINE=InnoDB")

class MySql(object):

    def __init__(self,logger=None):
        self.logger = logger or logging.getLogger(__name__)

            
    def ConnectToServer(self,hostInput,userInput,passwdInput):
        self.logger.info('Connection initialization')
    
        try:
            mydb = mysql.connector.connect(
                host=hostInput,
                user=userInput,
                passwd=passwdInput
                )
            return mydb
            
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                self.logger.debug("Something is wrong with your user name or password: {}".format(err))
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                self.logger.debug("Database does not exist: {}".format(err))
            else:
                self.logger.debug(err)
            sys.exit("Closed connection")
   
    def CreateCursorExecutor(self,mydb):
        mycursor = mydb.cursor()
        return mycursor
    
    def SetCursorExecutor(self,mycursor,dBName):
        mycursor.execute("USE {}".format(dBName))
        return mycursor

    def CreateDB(self,mycursor,dBName):
        try:
            mycursor.execute(
            "CREATE DATABASE {} DEFAULT CHARACTER SET 'utf8'".format(dBName))
            self.logger.info('Database created')
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_DB_CREATE_EXISTS:
                self.logger.debug("Failed create database: {}".format(err))
                
        
    def DeleteDatabase(self,mycursor,dBName):
        try:
            mycursor.execute("DROP DATABASE "+dBName)
            self.logger.info('Database dropped/deleted')
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_DB_DROP_EXISTS:
                self.logger.debug("Failed drop database: {}".format(err))
            elif err.errno == errorcode.ER_DB_DROP_RMDIR:
                self.logger.debugg()
                
    def ConnectToDB(self,mydb,dBName):
        try:
            mydb.connect(database=dBName)
            self.logger.info("Connected to: "+dBName)
        except mysql.connector.Error as err:
            self.logger.debug(err)
            
            
    def CloseDB(self,mydb):
        mydb.close()
    
    def CreateTable(self,mycursor):
        for tableName in TABLES:
            tableDescription = TABLES[tableName]
            try:
                mycursor.execute(tableDescription)
                self.logger.info("Create table: "+tableName)
            except mysql.connector.Error as err:
                if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
                    self.logger.debug("Table exist")
                else:
                    self.logger.debug(format(err))


# test 
sql = MySql()
mydb = sql.ConnectToServer('localhost','root','rootpassword') 
cursor = sql.CreateCursorExecutor(mydb)
sql.CreateDB(cursor,DB_NAME)
cursor = sql.SetCursorExecutor(cursor,DB_NAME)
#sql.DeleteDatabase(cursor,DB_NAME)
sql.CreateTable(cursor)
#sql.ConnectToDB(mydb,DB_NAME)
#sql.CloseDB(mydb)

