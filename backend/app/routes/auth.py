from datetime import datetime
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.user import User
from app.core.auth import (
    get_current_user, create_access_token,
    verify_password, get_password_hash
)
from app.schemas.models import UserCreate, UserLogin, Token, User as UserSchema

router = APIRouter(
    prefix="/api/auth",
    tags=["auth"],
    responses={401: {"description": "Non autorisé"}},
)

@router.post("/register", response_model=Token)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    """Enregistrement d'un nouvel utilisateur"""
    # Vérifier si l'utilisateur existe
    if db.query(User).filter(User.username == user.username).first():
        raise HTTPException(status_code=400, detail="Nom d'utilisateur déjà pris")
        
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email déjà utilisé")
    
    # Créer nouvel utilisateur
    db_user = User(
        username=user.username,
        email=user.email,
        password_hash=get_password_hash(user.password)
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Créer token
    access_token = create_access_token(data={"sub": str(db_user.id)})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": db_user.id
    }

@router.post("/login", response_model=Token)
async def login(user: UserLogin, db: Session = Depends(get_db)):
    """Connexion d'un utilisateur"""
    # Vérifier l'utilisateur
    db_user = db.query(User).filter(User.username == user.username).first()
    if not db_user or not verify_password(user.password, db_user.password_hash):
        raise HTTPException(
            status_code=401,
            detail="Nom d'utilisateur ou mot de passe incorrect"
        )
    
    # Mettre à jour dernière connexion
    db_user.last_login = datetime.utcnow()
    db.commit()
    
    # Créer token
    access_token = create_access_token(data={"sub": str(db_user.id)})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": db_user.id
    }

@router.get("/me", response_model=UserSchema)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Obtenir les informations de l'utilisateur connecté"""
    return current_user
