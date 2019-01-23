from peewee import *
from ExecMachine import jsonDataDB
import json

file = open(jsonDataDB.configName, 'r')
with file:
    data = file.read()
    jsonData = json.loads(data)
    DB = jsonData[jsonDataDB.db][jsonDataDB.dbName]
    USER = jsonData[jsonDataDB.db][jsonDataDB.dbUser]
    PASSWORD = jsonData[jsonDataDB.db][jsonDataDB.dbPsw]
    HOST = jsonData[jsonDataDB.db][jsonDataDB.dbHost]
    PORT = jsonData[jsonDataDB.db][jsonDataDB.dbPosrt]

if DB == "":
    print("Database name:")
    DB = input()
if USER == "":
    print("Database user name:")
    USER = input()
if PASSWORD == "":
    print("Database password:")
    PASSWORD = input()
if HOST == "":
    print("Database host name:")
    HOST = input()
if PORT == 0:
    print("Database port:")
    PORT = int(input())

databaseMain = MySQLDatabase(DB, user=USER, password=PASSWORD, host=HOST, port=PORT)
databaseMain.connect()

class BaseModelDDS(Model):
    class Meta:
        database = databaseMain

class Tasks(BaseModelDDS):
    idTasks = PrimaryKeyField(null=False)
    method = CharField(max_length=1000)
    userName = CharField(max_length=100)

    class Meta:
        dbTable = 'tasks'
        orderBy = ('method',)

class Proc(BaseModelDDS):
    idProc = PrimaryKeyField(null=False)
    flagExec = IntegerField(default=None)
    inputTest = CharField(max_length=30000)
    resFile = TextField()
    pos = CharField(max_length=200)
    bytes = CharField(max_length=200)
    userNameProc = CharField(max_length=100)
    timewait = CharField(max_length=300)
    tasks = ForeignKeyField(Tasks, db_column='idTaskProc', related_name="proc")

    class Meta:
        dbTable = 'proc'
        orderBy = ('flagExec',)