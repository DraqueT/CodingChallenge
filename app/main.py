from fastapi import FastAPI

from app.api.routes import router
from app.api.validation import add_exception_handlers


def create_app() -> FastAPI:
    warehouse_app = FastAPI(title="Order Routing Service")
    add_exception_handlers(warehouse_app)
    warehouse_app.include_router(router)
    return warehouse_app


app = create_app()
