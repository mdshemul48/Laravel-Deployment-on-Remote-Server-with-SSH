import os
from peewee import *


host:str = os.getenv("DB_HOST")
port:int = os.getenv("DB_PORT")
user:str = os.getenv("DB_USER")
password:str = os.getenv("DB_PASSWORD")
database:str = os.getenv("DB_DATABASE")

db = MySQLDatabase(database, user=user, password=password, host=host, port=port)

class BaseModel(Model):
    class Meta:
        database = db

class RemoteServerCredentials(BaseModel):
    id = PrimaryKeyField()
    name = CharField()
    host = CharField()
    port = IntegerField()
    username = CharField()
    password = CharField()
    

db.connect()
db.create_tables([RemoteServerCredentials])