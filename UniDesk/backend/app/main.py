from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import auth, comments, tickets, users

app = FastAPI(title="UniDesk API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(tickets.router)
app.include_router(comments.router)
app.include_router(users.router)


@app.get("/health")
def health_check() -> dict:
    return {"status": "ok"}
