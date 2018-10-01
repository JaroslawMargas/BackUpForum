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

            
    def ConnectToServer(self):
        self.logger.info('Connection initialization')
        
        #hostInput = str(raw_input("Please enter host to continue: "))
        #userInput = str(raw_input("Please enter user to continue: "))
       # passwdInput = str(raw_input("Please enter password to continue: "))
        
        hostInput = "localhost"
        userInput = "root"
        passwdInput = "rootpassword"
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
   
    def SetCursorExecutor(self,mydb):
        mycursor = mydb.cursor()
        mycursor.execute("USE {}".format(DB_NAME))
        return mycursor

    def CreateDB(self,mycursor):
        try:
            mycursor.execute(
            "CREATE DATABASE {} DEFAULT CHARACTER SET 'utf8'".format(DB_NAME))
            self.logger.info('Database created')
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_DB_CREATE_EXISTS:
                self.logger.debug("Failed create database: {}".format(err))
                
        
    def DeleteDatabase(self,mycursor):
        try:
            mycursor.execute("DROP DATABASE name")
            self.logger.info('Database dropped/deleted')
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_DB_DROP_EXISTS:
                self.logger.debug("Failed drop database: {}".format(err))
            elif err.errno == errorcode.ER_DB_DROP_RMDIR:
                self.logger.debugg()
                
    def ConnectToDB(self,mydb):
        try:
            mydb.connect(database=DB_NAME)
            self.logger.info("Connected to: "+DB_NAME)
        except mysql.connector.Error as err:
            self.logger.debug(err)
            
            
    def CloseDB(self,mydb):
        mydb.close()
    
    def CreateTable(self,mycursor):
        for tableName in TABLES:
            tableDescription = TABLES[tableName]
            try:
                mycursor.execute(tableDescription)
            except mysql.connector.Error as err:
                if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
                    self.logger.debug("Table exist")
                else:
                    self.logger.debug(format(err))


# test 
sql = MySql()
mydb = sql.ConnectToServer() 
cursor = sql.SetCursorExecutor(mydb)
#sql.DeleteDatabase(cursor)
sql.CreateDB(cursor)
sql.CreateTable(cursor)
#sql.ConnectToDB(mydb)
#sql.CloseDB(mydb)

