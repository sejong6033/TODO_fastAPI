import os

import pymysql
from dotenv import load_dotenv

load_dotenv()


db_user = os.getenv("db_user")
db_password = os.getenv("db_password")
db_database = os.getenv("db_database")

# 데이터베이스 연결 설정
def get_db():
    return pymysql.connect(
        host="localhost",
        port=3306,
        user=db_user,
        password=db_password,
        database=db_database,
    )