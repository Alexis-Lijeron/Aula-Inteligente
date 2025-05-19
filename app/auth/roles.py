from fastapi import Depends, HTTPException
from app.auth.auth_bearer import JWTBearer


def admin_required(payload: dict = Depends(JWTBearer())):
    if payload.get("is_doc") != False:
        raise HTTPException(status_code=403, detail="Solo administradores")
    return payload


def docente_required(payload: dict = Depends(JWTBearer())):
    if payload.get("is_doc") != True:
        raise HTTPException(status_code=403, detail="Solo docentes")
    return payload
