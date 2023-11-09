from fastapi import APIRouter, status, HTTPException
from typing import List
from sqlalchemy.orm import Session
from database.database import Base, engine
import schemas.user
import models.models
from datetime import date

# Create the database
Base.metadata.create_all(engine)

router = APIRouter()

@router.post("/user", response_model=schemas.user.UserInDB, status_code=status.HTTP_201_CREATED, tags=["user"])
async def create_user(user: schemas.user.UserInDB):

    # create a new database session
    session = Session(bind=engine, expire_on_commit=False)
    
    # create an instance of the ToDo database model
    userdb = models.models.User(usuario = user.usuario, nombre = user.nombre, email = user.email, rol = user.rol, activo =  user.activo, password = user.password)

    # add it to the session and commit it
    session.add(userdb)
    session.commit()
    session.refresh(userdb)

    # close the session
    session.close()

    # return the todo object
    return userdb

@router.get("/user/{id}", tags=["user"])
async def read_user(id: int):
    
    # create a new database session
    session = Session(bind=engine, expire_on_commit=False)

    # get the kiosko item with the given id
    userdb = session.query(models.models.User).get(id)

    # close the session
    session.close()

    if not userdb:
        raise HTTPException(status_code=404, detail=f"user item with id {id} not found")

    return userdb

@router.put("/user/{id}", tags=["user"])
async def update_user(id: int, usuario:str, nombre:str, email:str, rol:str, activo:bool, password:str):

    # create a new database session
    session = Session(bind=engine, expire_on_commit=False)

    # get the producto item with the given id
    userdb: schemas.user.UserInDB = session.query(models.models.User).get(id)    
    
    # update todo item with the given task (if an item with the given id was found)
    if userdb:
        userdb.usuario = usuario 
        userdb.nombre = nombre 
        userdb.email = email 
        userdb.rol = rol 
        userdb.activo = activo
        userdb.password = password
        session.commit()

    # close the session
    session.close()

@router.delete("/user/{id}", status_code=status.HTTP_204_NO_CONTENT, tags=["user"])
async def delete_user(id: int):
        
    # create a new database session
    session = Session(bind=engine, expire_on_commit=False)

    # get the todo item with the given id
    userdb = session.query(models.models.User).get(id)

    # if todo item with given id exists, delete it from the database. Otherwise raise 404 error
    if userdb:
        session.delete(userdb)
        session.commit()
        session.close()
    else:
        raise HTTPException(status_code=404, detail=f"inventario item with id {id} not found")

    return None