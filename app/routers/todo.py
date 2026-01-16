from fastapi import APIRouter, Request, HTTPException
from app.db import get_db
from app.core.logger import setup_logger


router = APIRouter()

logger = setup_logger()

# ---------------------------
# CREATE (생성)
# ---------------------------
@router.post("/todos")
async def create_todo(request: Request):
    body = await request.json()
    content = body.get("content")

    if not content:
        logger.error("제목이 없는 할 일 생성 시도: content missing")
        raise HTTPException(status_code=400, detail="content is required")

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO todo (content) VALUES (%s)", (content,))
    conn.commit()

    todo_id = cursor.lastrowid

    logger.info(f"새로운 할 일 생성 완료: ID {todo_id}")

    cursor.execute("SELECT id, content, created_at FROM todo WHERE id = %s", (todo_id,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()

    return {"id": row[0], "content": row[1], "created_at": str(row[2])}

# ---------------------------
# READ (전체 조회)
# ---------------------------
@router.get("/todos")
def get_todos():
    """전체 todo 목록을 최신순으로 조회"""
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT id, content, created_at FROM todo ORDER BY id DESC")
    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    return [
        {"id": r[0], "content": r[1], "created_at": str(r[2])}
        for r in rows
    ]

# ---------------------------
# DELETE (삭제)
# ---------------------------
@router.delete("/todos/{todo_id}")
def delete_todo(todo_id: int):
    """특정 todo를 삭제"""
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM todo WHERE id = %s", (todo_id,))
    conn.commit()

    affected = cursor.rowcount

    cursor.close()
    conn.close()

    if affected == 0:
        logger.error(f"없는 목록({todo_id})을 지우려함..")
        raise HTTPException(status_code=404, detail="Todo not found")

    return {"message": "Todo deleted"}