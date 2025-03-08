import uuid
from uuid import UUID
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import create_engine, Column, String, DateTime
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from pydantic import BaseModel, EmailStr, Field
from jose import JWTError, jwt
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@db/users")
SECRET_KEY = os.getenv("SECRET_KEY", "super_secret_key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@asynccontextmanager
async def lifespan(_: FastAPI):
    print("Initializing database...")
    Base.metadata.create_all(bind=engine)
    yield
    print("Shutting down...")

app = FastAPI(lifespan=lifespan)

class User(Base):
    __tablename__ = "users"
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    birth_date = Column(String, nullable=True)
    email = Column(String, unique=True, index=True, nullable=False)
    phone = Column(String, nullable=True)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))

class UserInfo(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    birth_date: str | None = None
    phone: str | None = None

class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)
    user_info: UserInfo | None = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_jwt_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return UUID(payload["user_id"])
    except (JWTError, ValueError):
        raise HTTPException(status_code=401, detail="Invalid or expired token")

@app.post("/register")
def register_user(user_register: UserRegister, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == user_register.email).first():
        raise HTTPException(status_code=400, detail="User with this email already exists")

    hashed_password = pwd_context.hash(user_register.password)
    user = User(id=uuid.uuid4(), email=user_register.email, hashed_password=hashed_password)
    for field, value in user_register.user_info.model_dump(exclude_unset=True).items():
        setattr(user, field, value)

    db.add(user)
    db.commit()
    db.refresh(user)

    return {"message": "User registered successfully"}

@app.post("/login")
def login(user_data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == user_data.email).first()
    if not user or not pwd_context.verify(user_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    token = create_access_token({"user_id": str(user.id)})
    return {"message": "Login successful", "access_token": token, "token_type": "bearer"}

@app.put("/update-profile")
def update_profile(user_info: UserInfo, user_id: UUID = Depends(verify_jwt_token), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    for field, value in user_info.model_dump(exclude_unset=True).items():
        setattr(user, field, value)
    
    user.updated_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(user)

    return {"message": "Profile updated successfully"}

@app.get("/profile")
def get_profile(user_id: UUID = Depends(verify_jwt_token), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "birth_date": user.birth_date,
        "phone": user.phone,
        "created_at": user.created_at,
        "updated_at": user.updated_at,
    }
