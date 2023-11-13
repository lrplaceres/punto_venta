from fastapi import APIRouter, status, HTTPException, Depends
from typing import List, Annotated
from sqlalchemy.orm import Session
from database.database import Base, engine
import schemas.kiosko
import models.models as models
import bcrypt
import auth.auth as auth

# Create the database
Base.metadata.create_all(engine)

router = APIRouter()

@router.post("/kiosko", response_model=schemas.kiosko.Kiosko, status_code=status.HTTP_201_CREATED, tags=["kiosko"])
async def create_kiosko(kiosko: schemas.kiosko.KioskoCreate, token: Annotated[str, Depends(auth.oauth2_scheme)], current_user: Annotated[models.User, Depends(auth.get_current_user)]):

    if current_user.rol != "superadmin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"No está autorizado a realizar esta acción")

    # create a new database session
    session = Session(bind=engine, expire_on_commit=False)

    # create an instance of the ToDo database model
    kioskodb = models.Kiosko(nombre = kiosko.nombre, representante = kiosko.representante, activo = kiosko.activo, admin_id = kiosko.admin_id)

    # add it to the session and commit it
    session.add(kioskodb)
    session.commit()
    session.refresh(kioskodb)

    # close the session
    session.close()

    # return the todo object
    return kioskodb


@router.get("/kiosko/{id}", tags=["kiosko"])
async def read_kiosko(id: int, token: Annotated[str, Depends(auth.oauth2_scheme)]):
    
    # create a new database session
    session = Session(bind=engine, expire_on_commit=False)

    # get the kiosko item with the given id
    kioskodb = session.query(models.Kiosko).get(id)

    # close the session
    session.close()

    if not kioskodb:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Kiosko con id {id} no encontrado")

    return {
        "id": kioskodb.id,
        "nombre": kioskodb.nombre,
        "activo": kioskodb.activo,
        "representante": kioskodb.representante,
        "admin_id": kioskodb.admin_id
        }


@router.put("/kiosko/{id}", tags=["kiosko"])
async def update_kiosko(id: int, nombre: str, representante: str, activo: bool, token: Annotated[str, Depends(auth.oauth2_scheme)], current_user: Annotated[models.User, Depends(auth.get_current_user)]):

    if current_user.rol != "superadmin" and current_user.rol != "propietario":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"No está autorizado a realizar esta acción")

    # create a new database session
    session = Session(bind=engine, expire_on_commit=False)

    # get the provincia item with the given id
    kioskodb: schemas.kiosko.Kiosko = session.query(models.Kiosko).get(id)

    # update todo item with the given task (if an item with the given id was found)
    if kioskodb:
        kioskodb.nombre = nombre
        kioskodb.representante = representante
        kioskodb.activo = activo
        session.commit()

    # close the session
    session.close()


@router.delete("/kiosko/{id}", status_code=status.HTTP_204_NO_CONTENT, tags=["kiosko"])
async def delete_kiosko(id: int, token: Annotated[str, Depends(auth.oauth2_scheme)], current_user: Annotated[models.User, Depends(auth.get_current_user)]):

    if current_user.rol != "superadmin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"No está autorizado a realizar esta acción")
   
    # create a new database session
    session = Session(bind=engine, expire_on_commit=False)

    # get the todo item with the given id
    kioskodb = session.query(models.Kiosko).get(id)

    # if todo item with given id exists, delete it from the database. Otherwise raise 404 error
    if kioskodb:
        session.delete(kioskodb)
        session.commit()
        session.close()
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Kiosko con id {id} no encontrado")

    return None