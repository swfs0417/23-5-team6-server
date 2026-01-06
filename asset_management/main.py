from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from asset_management.app.user.routes import router as user_router

app = FastAPI(title="Asset Management API")

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://d1vqqxs5v1ouxk.cloudfront.net",
                   "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check():
    return {"status": "ok"}


app.include_router(user_router, prefix="/api")
