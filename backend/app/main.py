from fastapi import FastAPI
from routes.authorize_routes import router as authorize_router
from routes.callback_routes import router as callback_router

app = FastAPI(title="Sber OAuth Only Authorize")

app.include_router(authorize_router)
app.include_router(callback_router)
