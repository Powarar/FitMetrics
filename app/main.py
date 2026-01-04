from fastapi import FastAPI
from app.core.middleware import logging_middleware

app = FastAPI()

app.middleware("http")(logging_middleware)

@app.get('/health')
def get_health():
    return {"status" : "ok"}