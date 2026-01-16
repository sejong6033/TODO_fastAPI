from logging import INFO

from fastapi import FastAPI, Request, HTTPException
import pymysql
import os
import logging
from logging.handlers import RotatingFileHandler

# ---------------------------
# [TASK 1] 로그 저장 폴더 생성
# ---------------------------
# TODO: "logs"라는 이름의 폴더를 생성해주세요!
# Hint: os.makedirs()를 활용하면 됩니다. 이미 폴더가 있어도 에러가 나지 않도록 exist_ok=True 옵션 사용
os.makedirs("logs", exist_ok=True)

# ---------------------------
# [TASK 2] 로그 포맷 및 핸들러 설정
# ---------------------------
LOG_FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"

# TODO: LOG_FORMAT을 사용하여 formatter를 생성하세요
# Hint: logging.Formatter()를 사용하여 LOG_FORMAT을 전달
formatter = logging.Formatter(LOG_FORMAT)  # 이 부분을 채워주세요!

file_handler = RotatingFileHandler(
    # TODO: 로그 파일 경로를 지정하세요 (logs 폴더 안에 app.log 파일)
    # Hint: "logs/파일명.확장자" 형식으로 작성
    filename="logs/TODO.log",  # 이 부분을 채워주세요!

    # TODO: 로그 파일의 최대 크기를 바이트 단위로 지정하세요
    # Hint: 1MB = 1024 * 1024 바이트
    maxBytes=1024 * 1024,   # 이 부분을 채워주세요!

    # TODO: 보관할 백업 파일 개수를 지정하세요
    # Hint: 5개의 백업 파일을 유지하려면?
    backupCount=5,  # 이 부분을 채워주세요!

    encoding="utf-8"
)
file_handler.setFormatter(formatter)

console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)

# ---------------------------
# [TASK 3] 루트 로거 통합 설정
# ---------------------------
root_logger = logging.getLogger()

# TODO: 로그 레벨을 INFO로 설정하세요
# Hint: logging 모듈의 INFO 상수를 사용하세요
root_logger.setLevel(INFO)  # 이 부분을 채워주세요!

# TODO: 파일 핸들러를 루트 로거에 추가하세요
# Hint: addHandler() 메서드를 사용하여 file_handler를 추가
root_logger.addHandler(file_handler)
# TODO: 콘솔 핸들러를 루트 로거에 추가하세요
# Hint: addHandler() 메서드를 사용하여 console_handler를 추가
root_logger.addHandler(console_handler)

logging.getLogger("uvicorn").handlers = root_logger.handlers
logging.getLogger("uvicorn.access").handlers = root_logger.handlers

app = FastAPI()


# 데이터베이스 연결 설정 (본인 환경에 맞게 수정)
def get_db():
    return pymysql.connect(
        host="localhost",
        port=3306,
        user="tester",
        password="tester",
        database="llmagent"
    )



@app.post("/todos")
async def create_todo(request: Request):
    body = await request.json()
    content = body.get("content")

    if not content:
        # TODO: ERROR 레벨로 로그를 기록하세요
        # Hint: logging.error()를 사용하여 "제목이 없는 할 일 생성 시도: content missing" 메시지 기록
        logging.error("제목이 없는 할 일 생성 시도: content missing")
        raise HTTPException(status_code=400, detail="content is required")

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO todo (content) VALUES (%s)", (content,))
    conn.commit()

    todo_id = cursor.lastrowid

    # TODO: INFO 레벨로 로그를 기록하세요
    # Hint: logging.info()를 사용하여 "새로운 할 일 생성 완료: ID {todo_id}" 메시지 기록 (f-string 사용)
    logging.info(f"새로운 할 일 생성 완료: ID {todo_id}")

    cursor.execute("SELECT id, content, created_at FROM todo WHERE id = %s", (todo_id,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()

    return {"id": row[0], "content": row[1], "created_at": str(row[2])}


# ---------------------------
# READ (전체 조회)
# ---------------------------
@app.get("/todos")
def get_todos():
    """전체 todo 목록을 최신순으로 조회"""
    conn = get_db()
    cursor = conn.cursor()

    # SELECT: 전체 todo를 id 내림차순으로 조회
    cursor.execute(
        "SELECT id, content, created_at FROM todo ORDER BY id DESC"
    )
    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    # 여러 개의 row를 JSON 리스트로 변환하여 반환
    return [
        {
            "id": r[0],
            "content": r[1],
            "created_at": str(r[2])
        }
        for r in rows
    ]


# ---------------------------
# DELETE (삭제)
# ---------------------------
@app.delete("/todos/{todo_id}")
def delete_todo(todo_id: int):
    """특정 todo를 삭제"""
    conn = get_db()
    cursor = conn.cursor()

    # DELETE: id가 일치하는 todo 삭제
    cursor.execute(
        "DELETE FROM todo WHERE id = %s",
        (todo_id,)
    )
    conn.commit()

    # 실제로 삭제된 행의 개수
    affected = cursor.rowcount

    cursor.close()
    conn.close()

    # 삭제 대상이 없었을 경우 404 반환
    if affected == 0:
        raise HTTPException(status_code=404, detail="Todo not found")

    return {"message": "Todo deleted"}
