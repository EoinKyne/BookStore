from fastapi import APIRouter, Depends, HTTPException, status
from BookStore.app.auth.auth import create_access_token
from fastapi.security import OAuth2PasswordRequestForm
from BookStore.app.schemas.auth import TokenResponse, LoginRequest
from BookStore.app.auth.auth import verify_password
from BookStore.app.database.user_db import USERS_DB


router = APIRouter(prefix="/auth", tags=["Auth"])


#@router.post("/login", response_model=TokenResponse)
#async def login(credentials: LoginRequest):
#    user = USERS_DB.get(credentials.username)
#    if not user or not verify_password(credentials.password, user.hashed_password):
#        raise HTTPException(
#            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized"
#        )
#    token = create_access_token({"sub": user.username})
#    return {"access_token": token, "token_type": "bearer"}


@router.post("/login/form", response_model=TokenResponse)
async def login_form(form_data: OAuth2PasswordRequestForm = Depends()):
    user = USERS_DB.get(form_data.username)

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid User")
    token = create_access_token({"sub": user.username})
    return {"access_token": token, "token_type": "bearer"}


