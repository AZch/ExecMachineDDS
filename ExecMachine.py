import subprocess

from peewee import *
import pymysql
import json
from DataDB.GRUB import *
from threading import Thread
import time

databaseMain = None
isExec = False

class jsonDataDB():
    configName = 'openCfgExMach.json'
    db = 'db'
    dbName = 'name'
    dbHost = 'host'
    dbPosrt = 'port'
    dbUser = 'user'
    dbPsw = 'password'

    testFile = 'testFile'
    execFile = 'execFile'
    resFile = 'resFile'

def makeWork(execFile):
    procProg = subprocess.Popen(  # запускаем переданный файл
        execFile,
        cwd=execFile.split(
            "/" + execFile.split('/')[len(execFile.split('/')) - 1]
        )[0],
        creationflags=subprocess.CREATE_NEW_CONSOLE)
    procProg.wait()  # ждем пока программа отработает и выдаст результат
    isExec = False

class Work():
    def __init__(self):
        self.DB = ""
        self.USER = ""
        self.PASSWORD = ""
        self.HOST = ""
        self.PORT = 0


    def parseCfg(self):
        file = open(jsonDataDB.configName, 'r')
        with file:
            data = file.read()
            jsonData = json.loads(data)
            self.DB = jsonData[jsonDataDB.db][jsonDataDB.dbName]
            self.USER = jsonData[jsonDataDB.db][jsonDataDB.dbUser]
            self.PASSWORD = jsonData[jsonDataDB.db][jsonDataDB.dbPsw]
            self.HOST = jsonData[jsonDataDB.db][jsonDataDB.dbHost]
            self.PORT = jsonData[jsonDataDB.db][jsonDataDB.dbPosrt]

            self.execFile = jsonData[jsonDataDB.execFile]
            self.resFile = jsonData[jsonDataDB.resFile]
            self.testFile = jsonData[jsonDataDB.testFile]
			
    def checkDBData(self):
        if self.execFile == "":
            print("Execute file way:")
            self.execFile = input()
        if self.resFile == "":
            print("Result file way:")
            self.resFile = input()
        if self.testFile == 0:
            print("Test file way:")
            self.testFile = input()

    def saveToFile(self, fileWay, data):
        file = open(fileWay, 'w')
        if file == '':
            print(fileWay + " not open")
            return fileWay + " not open"

        file.write(data)
        file.close()

    def getDataFromFile(self, fileWay, code='cp866'):
        try:
            file = open(fileWay, 'r', encoding=code)
            if file == '':
                return fileWay + " not open"
            with file:
                data = file.read()
                return data
        except:
            return fileWay + " not open"

    def execProc(self):
        while True:
            proc = Select.selectProcByFlag(-1)
            if len(proc) > 0:
                Update.updProc(proc[0].idProc, flagExec=0, inputTest=proc[0].inputTest,
                               resFile=proc[0].resFile, userNameProc="ira", 
                               pos=proc[0].pos, bytes=proc[0].bytes)
                self.saveToFile(self.testFile, proc[0].inputTest)
                timeWait = proc[0].timewait
                ThreadWork = Thread(target=makeWork, args=[self.execFile])
                ThreadWork.start()
                timeStart = time.time()
                isExec = True
                isBreakTimeWait = False
                while isExec:
                    if time.time() - timeStart < timeWait:
                        isBreakTimeWait = True
                        break
                if not isBreakTimeWait:
                    Update.updProc(proc[0].idProc, flagExec=1, inputTest=proc[0].inputTest,
                               resFile=self.getDataFromFile(fileWay=self.resFile, code='cp866'), 
                               pos=proc[0].pos, bytes=proc[0].bytes)
                else:
                    Update.updProc(proc[0].idProc, flagExec=1, inputTest=proc[0].inputTest,
                               resFile="nope",
                               pos=proc[0].pos, bytes=proc[0].bytes)

    def main(self):
        self.parseCfg()
        self.checkDBData()
        self.execProc()
        taskss = Select.selectProcByFlag(-1)
        print([str(u.bytes) + str(u.pos) for u in taskss])
        #while True:

        pass

if __name__ == '__main__':
    DB = ""
    USER = ""
    PASSWORD = ""
    HOST = ""
    PORT = 0

    database = None
    work = Work()
    work.main()
