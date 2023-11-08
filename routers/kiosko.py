from fastapi import APIRouter, status, HTTPException
from typing import List
from sqlalchemy.orm import Session
from database.database import Base, engine
import schemas.kiosko
import models.models
import bcrypt

# Create the database
Base.metadata.create_all(engine)

router = APIRouter()

@router.post("/kiosko", response_model=schemas.kiosko.Kiosko, status_code=status.HTTP_201_CREATED, tags=["kiosko"])
async def create_kiosko(kiosko: schemas.kiosko.KioskoCreate):

    # create a new database session
    session = Session(bind=engine, expire_on_commit=False)

    #buscar si existe admin
    admin = session.query(models.models.Kiosko).where(models.models.Kiosko.useradmin == kiosko.useradmin).count()
    if admin:
        raise HTTPException(status_code=412, detail=f"kiosko admin {kiosko.useradmin} exist")

    #hash password
    kiosko.passwadmin = kiosko.passwadmin.encode()
    sal = bcrypt.gensalt()
    pass_admin_hasheada = bcrypt.hashpw(kiosko.passwadmin, sal)

    # create an instance of the ToDo database model
    kioskodb = models.models.Kiosko(nombre = kiosko.nombre, representante = kiosko.representante, activo = kiosko.activo, useradmin = kiosko.useradmin, passwadmin = pass_admin_hasheada)

    # add it to the session and commit it
    session.add(kioskodb)
    session.commit()
    session.refresh(kioskodb)

    # close the session
    session.close()

    # return the todo object
    return kioskodb

@router.get("/kiosko/{id}", tags=["kiosko"])
async def read_kiosko(id: int):
    
    # create a new database session
    session = Session(bind=engine, expire_on_commit=False)

    # get the kiosko item with the given id
    kioskodb = session.query(models.models.Kiosko).get(id)

    # close the session
    session.close()

    if not kioskodb:
        raise HTTPException(status_code=404, detail=f"kiosko item with id {id} not found")

    return {
        "id": kioskodb.id,
        "nombre": kioskodb.nombre,
        "activo": kioskodb.activo,
        "representante": kioskodb.representante,
        "useradmin": kioskodb.useradmin
        }

@router.put("/kiosko/{id}", tags=["kiosko"])
async def update_kiosko(id: int, nombre: str, representante: str, activo: bool, passwadmin: str):

    # create a new database session
    session = Session(bind=engine, expire_on_commit=False)

    # get the provincia item with the given id
    kioskodb: schemas.kiosko.Kiosko = session.query(models.models.Kiosko).get(id)

    #hash password
    passwadmin = passwadmin.encode()
    sal = bcrypt.gensalt()
    pass_admin_hasheada = bcrypt.hashpw(passwadmin, sal)

    # update todo item with the given task (if an item with the given id was found)
    if kioskodb:
        kioskodb.nombre = nombre
        kioskodb.representante = representante
        kioskodb.activo = activo
        kioskodb.passwadmin = pass_admin_hasheada
        session.commit()

    # close the session
    session.close()

@router.delete("/kiosko/{id}", status_code=status.HTTP_204_NO_CONTENT, tags=["kiosko"])
async def delete_kiosko(id: int):
        
    # create a new database session
    session = Session(bind=engine, expire_on_commit=False)

    # get the todo item with the given id
    kioskodb = session.query(models.models.Kiosko).get(id)

    # if todo item with given id exists, delete it from the database. Otherwise raise 404 error
    if kioskodb:
        session.delete(kioskodb)
        session.commit()
        session.close()
    else:
        raise HTTPException(status_code=404, detail=f"kiosko item with id {id} not found")

    return None