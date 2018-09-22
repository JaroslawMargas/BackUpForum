class FileStream:
    
    def createTxtFile(self,name):
        try:
            fileCreated = open(name+'.txt',"w")
        except IOError:
            print "Could not create File."
        with fileCreated:
            fileCreated.close()
        return fileCreated.name
    

    def writeString(self,fileName,strToWrite):
        with open(fileName, 'w') as f:
            f.write(strToWrite+'\n')
            f.close()
    
    def appendString(self,fileName,strToAppend):
        with open(fileName, 'a+') as f:
            f.write(strToAppend+'\n')
            f.close()
        
    
    def readFile(self,fileName):
        with open(fileName, 'r') as f:
            for line in f:
                print line,
            #f.readlines() as 
            #f.readline(x)
            # it reads a 3th line only
        
    def returnLinesNumberInFile(self,filename):
        lines = 0
        for line in open(filename):
            lines += 1
        return lines

    def readLineInFile(self,fileName,numLine):
        with open(fileName, "r") as f:
            #print f.readline(numLine)
            #return f.readline()
            for i, line in enumerate(f):
                if i == numLine:
                    return line
                    break
                    
