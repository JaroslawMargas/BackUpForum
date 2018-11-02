#!/usr/bin/python
# -*- coding: utf-8 -*-
import logging
import mechanize
from bs4 import BeautifulSoup as BS
import fileStream
import numberConverter
import sys
import SQLConnector

str_nextLink = "Następny"
str_advertisement = "Reklama"
str_logOut = "Wyloguj"

moduleLogger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

class SideParser():

    def __init__ (self,logger=None):
        self.logger = logger or logging.getLogger(__name__)
        self.br = mechanize.Browser()
        self.fileCount  = 0  #counter for files.
        self.id = 0 #counter for id in file
        self.nextLink =""  #link for new page 
        self.logOutUser = ""

        self.sql = SQLConnector.MySql(host='localhost',user='root',password='rootpassword',dbName = 'fora')
        self.sql.openSqlConnection()
        self.sql.deleteDatabase()
        self.sql.createDB()
        self.sql.setCursorExecutor()
        self.sql.createTable()
        self.sql.closeConnection()
    
    #need to ignore the robots.txt
    def ignoreRobots(self):
        self.br.set_handle_robots(False)
        
    def openBrowser(self,browseAdres):    
        self.br.open(browseAdres)
        #print all forms
        for f in self.br.forms():
                self.logger.info(format(f))
        return True
    
    # example form
    # <form action="login.php" method="post" target="_top">
    # <input class="post" name="username" size="25" maxlength="40" value="" type="text">

    #find and select atr:action="login.php"
    def selectForm(self,attribute,atrValue):
        if(self.br.select_form(predicate=lambda frm: attribute in frm.attrs and frm.attrs[attribute] == atrValue)):
            self.logger.debug("Error Form Selection")
            return True
        else:
            self.logger.info("Form Selected")
 
    #if form is selected, then enter user and  password
    def logUser(self):
        userInput = str(raw_input("Please enter user to continue: "))
        self.br.form['username'] = userInput #userInput
        self.logOutUser = userInput
        password = str(raw_input("Please enter password to continue: "))
        self.br.form['password'] = password #password
        self.br.submit()
       
    # Create TXT file with fileName (increase name ++) 
    # Open browser and read all links with attribute and value
    # Append each link to file
    def readLinks_SaveToFile(self,fileName,linkAtrName,linkAtrValue,SQLtableName):
        streamFile = fileStream.FileStream()
        fileNameExt = streamFile.createTxtFile("Link_"+fileName)
        
#        self.fileCount = 1
        numberLeadZero = numberConverter.NumberConverter()


        try:
            self.sql.openSqlConnection()
            self.sql.setCursorExecutor()
        except:
            self.logger.debug("SQL Connection error.")

        
        for link in self.br.links():     
            for name,value in link.attrs:
                if name == linkAtrName and value == linkAtrValue:
                    idLeading = numberLeadZero.toLeadingZero(self.id)
                    self.logger.info("ReadLinks: {}".format(link.url))
                    streamFile.appendString(fileNameExt,idLeading+"|"+link.url)


                    self.sql.insertLink(SQLtableName,[fileName,link.url])
                    self.id += 1
        del streamFile,numberLeadZero
        try:
            self.sql.closeConnection()
        except:
            self.logger.debug("SQL Close connection error.")

        
        
   
    def getFileCounter(self):
        return self.fileCount
    
    def printCurrentHtml(self):
        g_response= self.br.response()
        soup = BS(g_response)  #BeautifulSoup
        self.logger.info(format(soup))
        
    def printCurrentResponse(self):
        g_response= self.br.response()
        self.logger.info("RESPONSE: {}".format(g_response))

           
    def logOut(self):
        target_text=str_logOut+' [ '+self.logOutUser+' ][IMG]'+str_logOut+' [ '+self.logOutUser+' ]'
        for link in self.br.links():
            if link.text == target_text:
#                 self.logger.info("The user is log out")        
                break
            
        if(self.br.follow_link(link)):
            self.logger.info("User log out")
        else:
            self.logger.debug("User log out error")
            
                
        self.logger.info("URL: {}".format(self.br.geturl()))
    
    # Create TXT file with name INDEX and read main links. Save it in file.
    # Open INDEX file and read line by line links.
    # Open each link and read POSTED links. Save it in ID++ file.
    # Link maps is created.
    def createLinkMap(self):
        
        self.fileCount = 0
        self.id = 1
        numberLeadZero = numberConverter.NumberConverter()
        idLeading = numberLeadZero.toLeadingZero(self.fileCount)
        self.readLinks_SaveToFile(idLeading,'class','forumlink','main')
        
        self.id = 1
        with open("Link_"+idLeading+".txt", "r") as f:
            for line in f:
                str_line = str(line)
                #print str_line
                idLink,link = str_line.split("|")
                #print idLink
                #print link
                self.br.open(link)
                self.readLinks_SaveToFile(idLink,'class','topictitle','link')     
        f.close()
                  
    # Check if Post has next page.
    def checkNextPage(self,link):
        self.br.open(link)   #open idLink.txt
        g_response= self.br.response()  #set current response from side.
        soup = BS(g_response,"html5lib")  #set instance BeautifulSoup
        checker = None
        for post in soup.findAll("span", {"class": "nav"}):
            for a in post.findAll('a'):
                if(a.get_text().encode('utf-8') == str_nextLink):
                    self.nextLink = a.get('href')
                    checker = True
        if (checker == None):
            return True
        else:
            return False    
        
    # Save all users 
    # Save all Posts
    # If next page exist repeat it
    def readPost_CreateFile(self,idLinkName):
        
        self.sql.openSqlConnection()
        self.sql.setCursorExecutor()
        with open("Link_"+idLinkName+".txt", "r") as fl:
                    streamFile = fileStream.FileStream()
                    for line in fl:
                        str_line = str(line)
                        #print str_line
                        idLink,link = str_line.split("|")
                        self.logger.info("Id Link: {}".format(idLink)) 
                        self.logger.info("Link: {}".format(link))     
                        self.nextLink = link 
                        fileName = streamFile.createTxtFile("Post_"+idLink)
                        while True:
                            self.br.open(self.nextLink)
                            #open link and read POST
                            g_response= self.br.response()  #set current response from side.


                            soup = BS(g_response,"html5lib")  #set instance BeautifulSoup

                             
                            for user in soup.findAll("span", {"class": "name"}):
                                if(user.b):
                                    if(user.get_text().encode('utf-8') != str_advertisement):

                                        streamFile.appendString(fileName,"Users: "+user.get_text().encode('utf-8'))          

                  
                                        
                                        self.sql.insertUser("users",[user.get_text().encode('utf-8')])
                                                  

                            for post in soup.findAll("span", {"class": "postbody"}):
                                #if the post is a script, ignore it
                                if(post.script):
                                        continue
                                else:
                                    streamFile.appendString(fileName,"Posts: "+post.get_text().encode('utf-8'))
                                    
                            if(self.checkNextPage(self.nextLink)):
                                break
        fl.close()
        self.sql.closeConnection()
          
    # create a posts map.
    def createPostsMap(self):
        self.fileCount = 0
        numberLeadZero = numberConverter.NumberConverter()
        fileNameLeading = numberLeadZero.toLeadingZero(self.fileCount)
        with open("Link_"+fileNameLeading+".txt", "r") as fl:   #open Link_000.txt
            for line in fl:
                str_line = str(line)
                #print str_line
                idLink,link = str_line.split("|")
                self.logger.info("Id Link: {}".format(idLink)) #001
                self.logger.info("Link: {}".format(link))  #link
                self.readPost_CreateFile(idLink)
                
        fl.close()