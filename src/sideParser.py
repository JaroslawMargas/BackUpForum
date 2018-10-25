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
        self.m_count  = 0  #counter for files.
        self.m_nextLink =""  #link for new page 
        self.m_logOutUser = ""
        
        self.sql = SQLConnector.MySql(host='localhost',user='root',password='rootpassword',dbName = 'name')
         
    #need to ignore the robots.txt
    def ignore_robots(self):
        self.br.set_handle_robots(False)
        
    def open_browser(self,browseAdres):    
        self.br.open(browseAdres)
        #print all forms
        for f in self.br.forms():
                self.logger.info(format(f))
    
    # example form
    # <form action="login.php" method="post" target="_top">
    # <input class="post" name="username" size="25" maxlength="40" value="" type="text">

    #find and select atr:action="login.php"
    def selectForm(self,attribute,atrValue):
        try:
            self.br.select_form(predicate=lambda frm: attribute in frm.attrs and frm.attrs[attribute] == atrValue)
        except:
            sys.exit("Selecting problem.")
 
    #if form is selected, then enter user and  password
    def log_user(self):
        userInput = str(raw_input("Please enter user to continue: "))
        self.br.form['username'] = userInput #userInput
        self.m_logOutUser = userInput
        password = str(raw_input("Please enter password to continue: "))
        self.br.form['password'] = password #password
        self.br.submit()
       
    # Create TXT file with fileName (increase name ++) 
    # Open browser and read all links with attribute and value
    # Append each link to file
    def readLinks_SaveToFile(self,fileName,linkAtrName,linkAtrValue,SQLtableName):
        streamFile = fileStream.FileStream()
        fileNameExt = streamFile.createTxtFile(fileName)
        
        self.m_count = 1
        numberLeadZero = numberConverter.NumberConverter()
    
        self.sql.OpenSqlConnection()
        
        for link in self.br.links():     
            for name,value in link.attrs:
                if name == linkAtrName and value == linkAtrValue:
                    idLeading = numberLeadZero.toLeadingZero(self.m_count)
                    self.logger.info("ReadLinks: {}".format(link.url))
                    streamFile.appendString(fileNameExt,idLeading+"|"+link.url)
                    self.sql.InsertLink(SQLtableName,(fileName,link.url)) 
                    self.m_count += 1
        del streamFile,numberLeadZero
        self.sql.CloseConnection()
        
        
   
    def getCounter(self):
        return self.m_count
    
    def printCurrentHtml(self):
        g_response= self.br.response()
        soup = BS(g_response)  #BeautifulSoup
        self.logger.info(format(soup))
        
    def printCurrentResponse(self):
        g_response= self.br.response()
        self.logger.info("RESPONSE: {}".format(g_response))

           
    def logOut(self):
        target_text=str_logOut+' [ '+self.m_logOutUser+' ][IMG]'+str_logOut+' [ '+self.m_logOutUser+' ]'
        for link in self.br.links():
            if link.text == target_text:
                self.logger.info("The user is log out")        
                break
        self.br.follow_link(link)
        self.logger.info("URL: {}".format(self.br.geturl()))
    
    # Create TXT file with name INDEX and read main links. Save it in file.
    # Open INDEX file and read line by line links.
    # Open each link and read POSTED links. Save it in ID++ file.
    # Link maps is created.
    def createLinkMap(self,artibuteName,artibuteValue):
        
        numberLeadZero = numberConverter.NumberConverter()
        idLeading = numberLeadZero.toLeadingZero(self.m_count)
        self.readLinks_SaveToFile(idLeading,'class','forumlink','main')
        
        with open(idLeading+".txt", "r") as f:
            for line in f:
                str_line = str(line)
                #print str_line
                idLink,link = str_line.split("|")
                #print idLink
                #print link
                self.br.open(link)
                self.readLinks_SaveToFile(idLink,artibuteName,artibuteValue,'link')     
        f.close()
                  
    # Check if Post has next page.
    def checkNextPage(self,link):
        self.br.open(link)   #open idLink.txt
        g_response= self.br.response()  #set current response from side.
        soup = BS(g_response)  #set instance BeautifulSoup
        checker = None
        for post in soup.findAll("span", {"class": "nav"}):
            for a in post.findAll('a'):
                if(a.get_text().encode('utf-8') == str_nextLink):
                    self.m_nextLink = a.get('href')
                    checker = True
        if (checker == None):
            return True
        else:
            return False    
        
    # Save all users 
    # Save all Posts
    # If next page exist repeat it
    def readPost_CreateFile(self,idLink):
            with open(idLink+".txt", "r") as fl:
                        streamFile = fileStream.FileStream()
                        for line in fl:
                            str_line = str(line)
                            #print str_line
                            idLink,link = str_line.split("|")
                            self.logger.info("Id Link: {}".format(idLink)) 
                            self.logger.info("Link: {}".format(link))     
                            self.m_nextLink = link 
                            fileName = streamFile.createTxtFile(idLink)
                            while True:
                                self.br.open(self.m_nextLink)
                                #open link and read POST
                                g_response= self.br.response()  #set current response from side.
                                soup = BS(g_response)  #set instance BeautifulSoup
                                 
                                for user in soup.findAll("span", {"class": "name"}):
                                    if(user.b):
                                        if(user.get_text().encode('utf-8') != str_advertisement):
                                            
                                            streamFile.appendString(fileName,"Users: "+user.get_text().encode('utf-8'))
                                for post in soup.findAll("span", {"class": "postbody"}):
                                    #if the post is a script, ignore it
                                    if(post.script):
                                            continue
                                    else:
                                        streamFile.appendString(fileName,"Posts: "+post.get_text().encode('utf-8'))
                                        
                                if(self.checkNextPage(self.m_nextLink)):
                                    break
            fl.close()
          
    # create a posts map.
    def createPostsMap(self,filename):
        with open(filename, "r") as f:
            for line in f:
                str_line = str(line)
                #print str_line
                idLink,link = str_line.split("|")
                self.logger.info("Id Link: {}".format(idLink)) 
                self.logger.info("Link: {}".format(link))
                self.readPost_CreateFile(idLink)
                
        f.close()