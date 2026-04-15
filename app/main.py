from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Annotated

from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

app = FastAPI(title="Sample FastAPI (secure training)")


# In-memory users/items for demo purposes only (no DB, no external calls)
@dataclass(frozen=True)
class User:
    id: int
    username: str


_USERS = {
    1: User(id=1, username="alice"),
    2: User(id=2, username="bob"),
}


class LoginRequest(BaseModel):
    user_id: int = Field(..., ge=1)


class LoginResponse(BaseModel):
    token: str


def _token_for_user(user_id: int) -> str:
    # Demo-only token format; not meant for production auth.
    # The goal here is to show *authorization checks* in handlers.
    return f"demo-user:{user_id}"


def current_user_id_dep(
    x_demo_token: str | None = Header(default=None, alias="X-Demo-Token"),
) -> int:
    if not x_demo_token:
        raise HTTPException(status_code=401, detail="Missing X-Demo-Token")
    if not x_demo_token.startswith("demo-user:"):
        raise HTTPException(status_code=401, detail="Invalid X-Demo-Token")
    try:
        return int(x_demo_token.split(":", 1)[1])
    except ValueError as exc:
        raise HTTPException(status_code=401, detail="Invalid X-Demo-Token") from exc


CurrentUserId = Annotated[int, Depends(current_user_id_dep)]


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/login", response_model=LoginResponse)
def login(body: LoginRequest) -> LoginResponse:
    if body.user_id not in _USERS:
        raise HTTPException(status_code=404, detail="Unknown user")
    return LoginResponse(token=_token_for_user(body.user_id))


@app.get("/users/{user_id}/profile")
def get_profile(user_id: int, current_user_id: CurrentUserId) -> dict[str, str | int]:
    # IDOR prevention: enforce that the caller can only see their own profile.
    if user_id != current_user_id:
        raise HTTPException(status_code=403, detail="Forbidden")

    user = _USERS.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Not found")

    return {"id": user.id, "username": user.username}


_BASE_DIR = (Path(__file__).parent / "data").resolve()


@app.get("/download/{name}")
def download_file(name: str) -> FileResponse:
    # Path traversal prevention: only allow files within app/data
    candidate = (_BASE_DIR / name).resolve()

    try:
        candidate.relative_to(_BASE_DIR)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Invalid path") from exc

    if not candidate.is_file():
        raise HTTPException(status_code=404, detail="Not found")

    return FileResponse(path=str(candidate), filename=candidate.name)
