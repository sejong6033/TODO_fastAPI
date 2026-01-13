# test_db.py
import pymysql

try:
    print("1. 연결 시도 중...")
    conn = pymysql.connect(
        host="127.0.0.1",
        port=3306,
        user="tester",
        password="tester",  # docker-compose 비번과 일치해야 함
        database="llmagent"
    )
    print("2. 연결 성공! 🎉")
    conn.close()
except Exception as e:
    print(f"3. 에러 발생: {e}")