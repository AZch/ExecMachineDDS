import os
import signal
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

    taskkill = 'taskkill'



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
            self.procKill = jsonData[jsonDataDB.taskkill]
			
            '''
            fileCfg = open(jsonDataDB.configName, 'w')

            dataToCfg = {}
            dataToCfg[jsonDataDB.db] = {}
            dataToCfg[jsonDataDB.db][jsonDataDB.dbName] = DB
            dataToCfg[jsonDataDB.db][jsonDataDB.dbHost] = HOST
            dataToCfg[jsonDataDB.db][jsonDataDB.dbPosrt] = PORT
            dataToCfg[jsonDataDB.db][jsonDataDB.dbUser] = USER
            dataToCfg[jsonDataDB.db][jsonDataDB.dbPsw] = PASSWORD

            fileCfg.write(json.dumps(dataToCfg, indent=4, ensure_ascii=False))
            fileCfg.close()'''
			
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
			
    def makeWork(self, execFile):
        self.procProg = subprocess.Popen(  # запускаем переданный файл
            execFile,
            cwd=execFile.split(
                "/" + execFile.split('/')[len(execFile.split('/')) - 1]
            )[0],
            creationflags=subprocess.CREATE_NEW_CONSOLE)
        self.procProg.wait()  # ждем пока программа отработает и выдаст результат
        self.isExec = False

    def execProc(self):
        while True:
            proc = Select.selectProcByFlag(-1)
            if len(proc) > 0:
                Update.updProc(proc[0].idProc, flagExec=0, inputTest=proc[0].inputTest,
                               resFile=proc[0].resFile, userNameProc="", 
                               pos=proc[0].pos, bytes=proc[0].bytes, timewait=proc[0].timewait)
                self.saveToFile(self.testFile, proc[0].inputTest)
                timeWait = float(proc[0].timewait)
                ThreadWork = Thread(target=self.makeWork, args=[self.execFile])
                ThreadWork.start()
                timeStart = time.time()
                self.isExec = True
                isBreakTimeWait = False
                while self.isExec:
                    if time.time() - timeStart > timeWait:
                        isBreakTimeWait = True
                        break
                if not isBreakTimeWait:
                    Update.updProc(proc[0].idProc, flagExec=1, inputTest=proc[0].inputTest,
                               resFile=self.getDataFromFile(fileWay=self.resFile, code='cp866'), 
                               pos=proc[0].pos, bytes=proc[0].bytes, timewait=proc[0].timewait)
                else:
                    try:
                        os.killpg(os.getpgid(self.procProg.pid), signal.SIGTERM)
                    except:
                        print("no del cmd")
                    try:
                        os.system("TASKKILL /IM " + self.procKill)
                    except:
                        print('no exec taskkill')
                    Update.updProc(proc[0].idProc, flagExec=1, inputTest=proc[0].inputTest,
                               resFile="nope",
                               pos=proc[0].pos, bytes=proc[0].bytes, timewait=proc[0].timewait)
                time.sleep(3)

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
