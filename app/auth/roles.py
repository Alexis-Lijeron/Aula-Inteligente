from fastapi import Depends, HTTPException
from app.auth.auth_bearer import JWTBearer
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError  # type: ignore
from app.config import settings


def admin_required(payload: dict = Depends(JWTBearer())):
    if payload.get("is_doc") != False:
        raise HTTPException(status_code=403, detail="Solo administradores")
    return payload


def docente_required(payload: dict = Depends(JWTBearer())):
    if payload.get("is_doc") != True:
        raise HTTPException(status_code=403, detail="Solo docentes")
    return payload


# NUEVO: permite docentes y admin
def docente_o_admin_required(payload: dict = Depends(JWTBearer())):
    if payload.get("is_doc") not in [True, False]:
        raise HTTPException(status_code=403, detail="Acceso no autorizado")
    return payload
