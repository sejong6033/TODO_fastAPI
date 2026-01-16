from fastapi import FastAPI
from app.core.logger import setup_logger
from app.routers.todo import router as todo_router # 👈 우리가 만든 라우터 가져오기


logger = setup_logger()
app = FastAPI()
app.include_router(todo_router)

@app.get("/")
def read_root():
    return {"message": "Welcome to sejong API"}