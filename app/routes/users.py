import logging
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from BookStore.app.models.model import User as UserModel
from BookStore.app.dependencies.db_dependencies import get_db
from BookStore.app.schemas.user import User
from BookStore.app.schemas.create_user import CreateUser
from BookStore.app.dependencies.usr_dependencies import get_current_user_oauth2
from BookStore.app.auth.auth import get_password_hash
from BookStore.app.schemas.patch_user import UpdateIsActiveUser, UpdatePass

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/", response_model=User)
def create_user(user: CreateUser,
                db: Session = Depends(get_db),
                admin_user: User = Depends(get_current_user_oauth2)):
    logger.info(f"Adding new user...")
    check_user = db.query(UserModel).filter(UserModel.username == user.username).first()
    if check_user:
        raise HTTPException(status_code=409, detail="User already exists")

    hash_pwd = get_password_hash(user.hashed_password)

    db_user = UserModel(
        role=user.role,
        username=user.username,
        hashed_password=hash_pwd,
        is_active=user.is_active,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@router.get("/", response_model=list[User])
def get_users(db: Session = Depends(get_db),
              limit: int = Query(10, ge=1, le=100),
              offset: int = Query(0, ge=0),
              admin_user: User = Depends(get_current_user_oauth2)):
    logger.info("Get users...")

    users = db.query(UserModel).order_by(UserModel.id.desc())

    return users.offset(offset).limit(limit).all()


@router.get("/user_id/{user_id}", response_model=User)
def get_user_by_id(user_id: int,
                   db: Session = Depends(get_db),
                   admin_user: User = Depends(get_current_user_oauth2)):
    logger.info("Get user by id")
    user = db.query(UserModel).filter(UserModel.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user


@router.get("/username/{username}", response_model=User)
def get_user_by_username(username: str,
                         db: Session = Depends(get_db),
                         admin_user: User = Depends(get_current_user_oauth2)):
    logger.info("Get user by username")
    logger.info(username)
    user = db.query(UserModel).filter(UserModel.username == username).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user


@router.patch("/is_active/{user_id}", response_model=User)
def update_is_active_user(user_id: int,
                          data: UpdateIsActiveUser,
                          db: Session = Depends(get_db),
                          admin_user: User = Depends(get_current_user_oauth2)):
    logger.info("Update is active for user")

    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if admin_user.role != "Administrator" or user.username == "admin":
        raise HTTPException(status_code=405, detail="Not allowed")

    updates = data.dict(exclude_unset=True)
    for field, value in updates.items():
        setattr(user, field, value)

    db.commit()
    db.refresh(user)
    return user


@router.patch("/credentials/{user_id}", response_model=User)
def update_passwd(user_id: int,
                  data: UpdatePass,
                  db: Session = Depends(get_db),
                  admin_user: User = Depends(get_current_user_oauth2)):
    logger.info("Update credentials for user")

    user = db.query(UserModel).filter(UserModel.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if admin_user.username != user.username:
        raise HTTPException(status_code=405, detail="Not allowed")

    updates = data.dict(exclude_unset=True)

    for field, value in updates.items():
        if field == "hashed_password":
            value = get_password_hash(value)
        setattr(user, field, value)

    db.commit()
    db.refresh(user)
    return user


@router.delete("/{user_id}", status_code=204)
def delete_user(user_id: int,
                db: Session = Depends(get_db),
                admin_user: User = Depends(get_current_user_oauth2)):
    logger.info("Delete user")

    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    is_not_active_user = db.query(UserModel).filter(UserModel.id == user_id,
                                                    UserModel.is_active.is_(False)).first()

    if not is_not_active_user:
        raise HTTPException(status_code=405, detail="Not allowed")

    if admin_user.username != "admin":
        raise HTTPException(status_code=405, detail="Not allowed")

    db.delete(is_not_active_user)
    db.commit()
