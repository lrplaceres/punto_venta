from fastapi import APIRouter, status, HTTPException, Depends
from typing import List, Annotated
from sqlalchemy.orm import Session
from database.database import Base, engine
import schemas.kiosko
import models.models as models
import auth.auth as auth

# Create the database
Base.metadata.create_all(engine)

router = APIRouter()

@router.get("/kioskos/{usuario}", response_model_by_alias=List[models.Kiosko], tags=["kioskos"])
async def read_kioskos_propietarios(usuario: str,token: Annotated[str, Depends(auth.oauth2_scheme)], current_user: Annotated[models.User, Depends(auth.get_current_user)]):
    
    # create a new database session
    session = Session(bind=engine, expire_on_commit=False)

    # get the admin item with the given usuario
    admin = session.query(models.User).where(models.User.usuario == usuario).first()
    
    kioskosdb = session.query(models.Kiosko).where(models.Kiosko.admin_id == admin.id).all()

    # close the session
    session.close()

    return kioskosdb