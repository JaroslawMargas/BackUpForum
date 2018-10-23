import logging
import mysql.connector
import time
import sys
from mysql.connector import errorcode

moduleLogger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

DB_NAME = 'name' 

TABLES = {}
TABLES['main'] = (
    "CREATE TABLE `main` ("
    "  `id` int(11) NOT NULL AUTO_INCREMENT,"   #PK
    "  `number` varchar(10) not NULL,"               #UNIQUE
    "  `link` varchar(255) NOT NULL,"
    "  PRIMARY KEY (`id`)"
#    "  PRIMARY KEY (`id`),UNIQUE KEY(`number`)"
    ") ENGINE=InnoDB")

TABLES['link'] = (
    "CREATE TABLE `link` ("
    "  `id` int(11) NOT NULL AUTO_INCREMENT,"   #PK
    "  `main_id` varchar(10) not NULL,"               #UNIQUE
    "  `link` varchar(255) NOT NULL,"
    "  PRIMARY KEY (`id`)"
#    "  PRIMARY KEY (`id`),UNIQUE KEY(`number`)"
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

    def showTables(self,mycursor,dBName):
        cursor = self.SetCursorExecutor(mycursor, dBName)
        cursor.execute("SHOW TABLES")
        tablesList = [cursor.fetchall()] 
        return tablesList
    
    def getColumnsNotIncrement(self,mycursor,dBName,tableName):
        cursor = self.SetCursorExecutor(mycursor, dBName)
        cursor.execute("SHOW COLUMNS FROM "+dBName+"."+tableName+" WHERE EXTRA NOT LIKE '%auto_increment%'")
        columnLst = [column[0] for column in cursor.fetchall()]
        return columnLst
    
    def InsertLink(self,mycursor,dBName,tableName,mydb,valList):
        cursor = self.SetCursorExecutor(mycursor, dBName)
        columnInTableList = self.getColumnsNotIncrement(cursor,dBName,tableName)
        colNames = ''
        for x in range(columnInTableList.__len__()): #
            colNames +=columnInTableList[x]+","
        try:
            sql = "INSERT INTO "+tableName+" ("+colNames[0:-1]+") VALUES (%s, %s)" #remove last ","
            cursor.execute(sql, valList)
            mydb.commit()
            self.logger.info('Data are inserted and committed')
        except mysql.connector.Error as err:
            self.logger.debug(err)
        

sql = MySql()
mydb = sql.ConnectToServer('localhost','root','rootpassword') 
cursor = sql.CreateCursorExecutor(mydb)
sql.CreateDB(cursor,DB_NAME)
cursor = sql.SetCursorExecutor(cursor,DB_NAME)
#sql.DeleteDatabase(cursor,DB_NAME)
sql.CreateTable(cursor)
#tableList = sql.showTables(cursor,DB_NAME)
#for itm in tableList:
#    print itm
# columnList = sql.getColumnsNotIncrement(cursor, DB_NAME, 'main')
# for itm in columnList:
#     print itm
     
#sql.InsertLink(cursor,DB_NAME,'main',mydb,("344","dsgdfgds"))
#sql.ConnectToDB(mydb,DB_NAME)
sql.CloseDB(mydb)
