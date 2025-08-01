from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from backend.core.backend import create_user, authenticate_user

router = APIRouter(prefix="/auth")

class AuthRequest(BaseModel):
    username: str
    password: str

@router.post("/signup")
def signup(req: AuthRequest):
    ok = create_user(req.username, req.password)
    if not ok:
        raise HTTPException(status_code=400, detail="Username already exists")
    return {"message": "Signup successful"}

@router.post("/login")
def login(req: AuthRequest):
    if not authenticate_user(req.username, req.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    # TODO: return real JWT
    return {"token": "dummy-jwt-token"}