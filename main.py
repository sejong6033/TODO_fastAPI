import time
from fastapi import FastAPI, Request, HTTPException , status
from fastapi.responses import JSONResponse
import pymysql
from loguru import logger  # loguru 사용

app = FastAPI()

def get_db():
    return pymysql.connect(
        host="localhost",
        port=3306,
        user="tester",
        password="tester",
        database="llmagent",
    )


# ---------------------------
# CREATE
# ---------------------------
@app.post("/todos")
async def create_todo(request: Request):
    # [Log Point 1] Request 진입: 어떤 클라이언트가 어떤 데이터를 보내려 하는지 기록
    client_ip = request.client.host if request.client else "unknown"
    logger.info(f"[{client_ip}] POST /todos 요청 진입")

    header = request.headers
    logger.info(header)
    logger.info(f"Method : {request.method}")
    logger.info(f"URL : {request.url}")
    logger.info(f"Query_Params : {request.query_params}")

    body = await request.json()
    content = body.get("content")

    # [Log Point 2] 데이터 유효성 검사 직전/직후: 데이터가 뭘로 들어왔는지(Debug 레벨 추천)
    logger.debug(f"요청 Body 데이터: {body}")

    if not content:
        # [Log Point 3] 예외 발생 시: 에러가 나서 튕겨내기 직전에 기록 (Error 또는 Warning)
        logger.warning("Content 누락으로 인한 400 에러 반환")
        raise HTTPException(status_code=400, detail="content is required")

    conn = get_db()
    cursor = conn.cursor()

    try:
        # INSERT 실행
        cursor.execute(
            'INSERT INTO todo (content) VALUES (%s)',
            (content,)
        )
        conn.commit()

        todo_id = cursor.lastrowid
        # [Log Point 4] 중요 로직 처리 후: DB에 실제 반영된 ID 확인
        logger.info(f"DB Insert 성공 - 생성된 ID: {todo_id}")

        # SELECT 실행
        cursor.execute(
            'SELECT id, content, created_at FROM todo WHERE id = %s',
            (todo_id,)
        )
        row = cursor.fetchone()

    except Exception as e:
        # [Log Point 5] DB 에러 등 예상치 못한 에러 잡기
        logger.error(f"DB 처리 중 에러 발생: {e}")
        raise e  # 로그만 찍고 에러는 다시 던져서 FastAPI가 처리하게 함

    finally:
        # 리소스 정리
        cursor.close()
        conn.close()

    response_data = {
        "id": row[0],
        "content": row[1],
        "created_at": str(row[2])
    }

    response = JSONResponse(content=response_data)
    response.status_code = status.HTTP_201_CREATED

    logger.info(f"응답 헤더 확인: {response.status_code} : {dict(response.headers)}")

    return response_data


# ---------------------------
# READ
# ---------------------------
@app.get("/todos")
def get_todos():
    # [Log Point 1] Request 진입
    logger.info("GET /todos 요청 진입")

    conn = get_db()
    cursor = conn.cursor()

    try:
        cursor.execute('SELECT * FROM todo')
        rows = cursor.fetchall()

        # [Log Point 2] 조회 결과 요약: 전체 데이터를 다 찍으면 로그가 너무 길어지므로 갯수 정도만 찍음
        logger.info(f"전체 조회 성공: 총 {len(rows)}건")

    finally:
        cursor.close()
        conn.close()

    return [
        {
            "id": r[0],
            "content": r[1],
            "created_at": str(r[2])
        }
        for r in rows
    ]


# ---------------------------
# DELETE
# ---------------------------
@app.delete("/todos/{todo_id}")
def delete_todo(todo_id: int):
    # [Log Point 1] Request 진입: 삭제하려는 대상 ID 기록
    logger.info(f"DELETE /todos/{todo_id} 요청 진입")

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        'DELETE FROM todo WHERE id = %s',
        (todo_id,)
    )
    conn.commit()
    affected = cursor.rowcount

    cursor.close()
    conn.close()

    if affected == 0:
        # [Log Point 2] 예외 상황: 없는 데이터를 지우려 했을 때
        logger.warning(f"삭제 실패 - 존재하지 않는 ID: {todo_id}")
        raise HTTPException(status_code=404, detail="Todo not found")

    # [Log Point 3] 정상 처리 완료
    logger.info(f"삭제 완료 - ID: {todo_id}")

    return {"message": "Todo deleted"}