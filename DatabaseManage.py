import mysql.connector

class DatabaseMannage: 
    mydb: mysql.connector.connect = None
    def __init__(self, db_host: str, db_user: str, db_password: str,  db_port = 3306):
        self.mydb = mysql.connector.connect(
            host=db_host,
            user=db_user,
            password=db_password,
            port=db_port
        )
    
    def create_database(self, db_name):
        mycursor = self.mydb.cursor()
        mycursor.execute("CREATE DATABASE " + db_name)

    def databases(self):
        mycursor = self.mydb.cursor()
        mycursor.execute("SHOW DATABASES")
        return [database[0] for database in mycursor.fetchall()]