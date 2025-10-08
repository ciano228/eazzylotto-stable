from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.core.config import settings
from app.models.user import User
from app.database.connection import get_db

# Configuration du cryptage des mots de passe
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Configuration OAuth2 pour FastAPI
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Vérifier un mot de passe en clair avec sa version hachée"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Générer le hash d'un mot de passe"""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Créer un token JWT avec des claims standards"""
    if not data or "sub" not in data:
        raise ValueError("Les données du token doivent contenir un 'sub' (subject)")
        
    to_encode = data.copy()
    
    # Ajout du temps d'expiration
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # Ajout des claims standards JWT
    to_encode.update({
        "exp": expire,  # Expiration
        "iat": datetime.utcnow(),  # Issued At
        "iss": "eazzylotto",  # Issuer
        "type": "access"  # Type de token
    })
    
    try:
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt
    except Exception as e:
        raise ValueError(f"Erreur lors de la création du token: {str(e)}")

def verify_token(token: str) -> Optional[str]:
    """Vérifier un token JWT et retourner l'ID utilisateur"""
    try:
        # Vérifier le format du token
        if not token or not isinstance(token, str):
            return None
            
        # Décoder et vérifier le token
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        
        # Vérifier les champs requis
        user_id: str = payload.get("sub")
        exp = payload.get("exp")
        
        if not user_id or not exp:
            return None
            
        # Vérifier si le token n'est pas expiré
        if datetime.utcnow() > datetime.fromtimestamp(exp):
            return None
            
        return user_id
        
    except JWTError:
        return None
    except Exception:
        return None

async def get_current_user(token: str = Depends(oauth2_scheme), db = Depends(get_db)) -> User:
    """Récupérer l'utilisateur actuel à partir du token JWT"""
    token_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token invalide ou expiré",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    user_exception = HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Utilisateur non trouvé",
    )
    
    try:
        user_id = verify_token(token)
        if user_id is None:
            raise token_exception
            
        user = db.query(User).filter(User.id == int(user_id)).first()
        if user is None:
            raise user_exception
            
        return user
        
    except JWTError:
        raise token_exception
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Format d'ID utilisateur invalide"
        )
