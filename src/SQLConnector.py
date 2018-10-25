import logging
import mysql.connector
import sys
from mysql.connector import errorcode

moduleLogger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

#DB_NAME = 'name' 

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

    def __init__(self, logger=None, host=None, user=None, password=None, dbName = ''):
        self.logger = logger or logging.getLogger(__name__)
        self.host = host
        self.user = user
        self.password = password
        self.dbName = dbName
        
        self.mydB = None
        self.cursor = None
            
    def OpenSqlConnection(self):
        self.logger.info('Connection initialization')
    
        try:
            mydB = mysql.connector.connect(
                host=self.host,
                user=self.user,
                passwd=self.password
                )
            self.mydB = mydB
            self.CreateCursorExecutor()
            self.SetCursorExecutor()
            
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                self.logger.debug("Something is wrong with your user name or password: {}".format(err))
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                self.logger.debug("Database does not exist: {}".format(err))
            else:
                self.logger.debug(err)
            sys.exit("Closed connection")
    
    def CloseConnection(self):
        self.mydB.close()
        self.cursor.close()
        
    def CreateCursorExecutor(self):
        self.cursor = self.mydB.cursor()
    
    def SetCursorExecutor(self):
        self.cursor.execute("USE {}".format(self.dbName))

    def CreateDB(self):
        try:
            self.cursor.execute(
            "CREATE DATABASE {} DEFAULT CHARACTER SET 'utf8'".format(self.dbName))
            self.logger.info('Database created')
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_DB_CREATE_EXISTS:
                self.logger.debug("Failed create database: {}".format(err))
                
        
    def DeleteDatabase(self):
        try:
            self.cursor.execute("DROP DATABASE "+self.dbName)
            self.logger.info('Database dropped/deleted')
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_DB_DROP_EXISTS:
                self.logger.debug("Failed drop database: {}".format(err))
            elif err.errno == errorcode.ER_DB_DROP_RMDIR:
                self.logger.debugg()

    def CreateTable(self):
        for tableName in TABLES:
            tableDescription = TABLES[tableName]
            try:
                self.cursor.execute(tableDescription)
                self.logger.info("Create table: "+tableName)
            except mysql.connector.Error as err:
                if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
                    self.logger.debug("Table exist")
                else:
                    self.logger.debug(format(err))

    def showTables(self):
        self.cursor.execute("SHOW TABLES")
        tablesList = [self.cursor.fetchall()] 
        return tablesList
    
    def getColumnsNotIncrement(self, dBTable):
        self.cursor.execute("SHOW COLUMNS FROM "+self.dbName+"."+dBTable+" WHERE EXTRA NOT LIKE '%auto_increment%'")
        columnLst = [column[0] for column in self.cursor.fetchall()]
        return columnLst
    
    def InsertLink(self, tableName, valList):
        columnInTableList = self.getColumnsNotIncrement(tableName)
        colNames = ''
        for x in range(columnInTableList.__len__()): #
            colNames +=columnInTableList[x]+","
        try:
            sql = "INSERT INTO "+tableName+" ("+colNames[0:-1]+") VALUES (%s, %s)" #remove last ","
            self.cursor.execute(sql, valList)
            self.mydB.commit()
            self.logger.info('Data are inserted and committed')
        except mysql.connector.Error as err:
            self.logger.debug(err)
        

# sql = MySql(host='localhost',user='root',password='rootpassword',dbName = 'name')
# sql.OpenSqlConnection()
# sql.CreateTable()
# #sql.DeleteDatabase()
# tableList = sql.showTables()
# 
# for itm in tableList:
#     print itm
# columnList = sql.getColumnsNotIncrement('link')
# for itm in columnList:
#      print itm
#      
# #sql.InsertLink('main',("344","dsgdfgds"))
# sql.CloseConnection()
