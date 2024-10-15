
import datetime
import os
def writeLog(logTxt):
    currDatetime = datetime.datetime.now()
    logDate = currDatetime.strftime("%m")+"-"+ currDatetime.strftime("%d")+"-"+ currDatetime.strftime("%Y")
    if not os.path.exists('./log'):
        os.makedirs('./log')
    fileName = "./log/WebScaperLog_"+str(logDate)+".txt"
    f = open(fileName, "a")
    appendTxt = str(currDatetime) +": "+logTxt+' \n'
    f.write(appendTxt)
    f.close()

#log("Test")