from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import models, database
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI()

# Подключение к БД
models.Base.metadata.create_all(bind=database.engine)


# 📌 Pydantic-схема для пользователя
class UserCreate(BaseModel):
    name: str
    email: str
    age: Optional[int] = None


class UserResponse(UserCreate):
    id: int

    class Config:
        orm_mode = True


# 📌 Получить всех пользователей
@app.get("/users/", response_model=List[UserResponse])
def get_users(db: Session = Depends(database.get_db)):
    return db.query(models.User).all()


# 📌 Получить пользователя по ID
@app.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


# 📌 Создать нового пользователя
@app.post("/users/", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(database.get_db)):
    new_user = models.User(**user.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


# 📌 Обновить данные пользователя (PUT)
@app.put("/users/{user_id}", response_model=UserResponse)
def update_user(user_id: int, updated_user: UserCreate, db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.name = updated_user.name
    user.email = updated_user.email
    user.age = updated_user.age
    db.commit()
    db.refresh(user)
    return user


# 📌 Частично обновить данные (PATCH)
@app.patch("/users/{user_id}", response_model=UserResponse)
def patch_user(user_id: int, user_data: dict, db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    for key, value in user_data.items():
        setattr(user, key, value)

    db.commit()
    db.refresh(user)
    return user


# 📌 Удалить пользователя
@app.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(user)
    db.commit()
    return {"message": "User deleted successfully"}

