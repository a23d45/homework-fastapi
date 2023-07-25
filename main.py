from fastapi import FastAPI

from menu_app.router import router as menu_router

app = FastAPI()

app.include_router(
    router=menu_router,
    prefix='/api/v1',
)   

