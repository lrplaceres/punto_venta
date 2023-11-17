from fastapi import APIRouter, status, HTTPException, Depends
from typing import List, Annotated
from sqlalchemy.orm import Session
from database.database import Base, engine
import schemas.user
import models.models as models
from datetime import date
import auth.auth as auth

# Create the database
Base.metadata.create_all(engine)

router = APIRouter()

@router.post("/user", response_model=schemas.user.User, status_code=status.HTTP_201_CREATED, tags=["user"])
#async def create_user(user: schemas.user.UserInDB, token: Annotated[str, Depends(auth.oauth2_scheme)], current_user: Annotated[models.User, Depends(auth.get_current_user)]):
async def create_user(user: schemas.user.UserInDB):

    # create a new database session
    session = Session(bind=engine, expire_on_commit=False)

    #comprobar si existe usuario
    usuario_buscado = session.query(models.User).where(models.User.usuario == user.usuario).count()

    if usuario_buscado:
        raise HTTPException(status_code=status.HTTP_412_PRECONDITION_FAILED, detail=f"Usuario no disponible")
    
    # create an instance of the ToDo database model
    userdb = models.User(usuario = user.usuario, nombre = user.nombre, email = user.email, rol = user.rol, activo =  user.activo, password = auth.pwd_context.hash(user.password))

    # add it to the session and commit it
    session.add(userdb)
    session.commit()
    session.refresh(userdb)

    # close the session
    session.close()

    # return the todo object
    return userdb


@router.get("/user", response_model=List[schemas.user.UserList], tags=["user"])
#async def read_user(token: Annotated[str, Depends(auth.oauth2_scheme)], current_user: Annotated[models.User, Depends(auth.get_current_user)]):
async def read_users_list():
    
    # create a new database session
    session = Session(bind=engine, expire_on_commit=False)

    # get the kiosko item with the given id
    usersdb = session.query(models.User).all()

    # close the session
    session.close()

    return usersdb


@router.get("/user/{id}", response_model=schemas.user.User, tags=["user"])
#async def read_user(id: int, token: Annotated[str, Depends(auth.oauth2_scheme)], current_user: Annotated[models.User, Depends(auth.get_current_user)]):
async def read_user(id: int):
    
    # create a new database session
    session = Session(bind=engine, expire_on_commit=False)

    # get the kiosko item with the given id
    userdb = session.query(models.User).get(id)

    # close the session
    session.close()

    if not userdb:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"user item with id {id} not found")

    return userdb


@router.put("/user/{id}", tags=["user"])
async def update_user(id: int, usuario:str, nombre:str, email:str, rol:str, activo:bool, password:str, token: Annotated[str, Depends(auth.oauth2_scheme)], current_user: Annotated[models.User, Depends(auth.get_current_user)]):

    # create a new database session
    session = Session(bind=engine, expire_on_commit=False)

    #comprobar si existe usuario
    usuario_buscado = session.query(models.User).where(models.User.usuario == user.usuario).count()

    if usuario_buscado:
        raise HTTPException(status_code=status.HTTP_412_PRECONDITION_FAILED, detail=f"Usuario no disponible")

    # get the producto item with the given id
    userdb: schemas.user.UserInDB = session.query(models.User).get(id)    
    
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
async def delete_user(id: int, token: Annotated[str, Depends(auth.oauth2_scheme)], current_user: Annotated[models.User, Depends(auth.get_current_user)]):
        
    # create a new database session
    session = Session(bind=engine, expire_on_commit=False)

    # get the todo item with the given id
    userdb = session.query(models.User).get(id)

    # if todo item with given id exists, delete it from the database. Otherwise raise 404 error
    if userdb:
        session.delete(userdb)
        session.commit()
        session.close()
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"inventario item with id {id} not found")

    return None