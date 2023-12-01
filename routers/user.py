from fastapi import APIRouter, status, HTTPException, Depends
from typing import List, Annotated
from sqlalchemy.orm import Session
from database.database import Base, engine
import schemas.user
import models.models as models
from datetime import date
import auth.auth as auth
import log.log as log

# Create the database
Base.metadata.create_all(engine)

router = APIRouter()


@router.post("/user", response_model=schemas.user.User, status_code=status.HTTP_201_CREATED, tags=["user"])
async def create_user(user: schemas.user.UserInDB, token: Annotated[str, Depends(auth.oauth2_scheme)], current_user: Annotated[models.User, Depends(auth.get_current_user)]):

    # validando rol de usuario autenticado
    if current_user.rol != "superadmin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"No está autorizado a realizar esta acción")

    # create a new database session
    session = Session(bind=engine, expire_on_commit=False)

    # comprobar si existe usuario
    usuario_buscado = session.query(models.User).where(
        models.User.usuario == user.usuario).count()

    if usuario_buscado:
        raise HTTPException(
            status_code=status.HTTP_412_PRECONDITION_FAILED, detail=f"Usuario no disponible. Intente con otro.")

    # create an instance of the user database model
    userdb = models.User(usuario=user.usuario, nombre=user.nombre, email=user.email,
                         rol=user.rol, activo=user.activo, password=auth.pwd_context.hash(user.password))

    # add it to the session and commit it
    session.add(userdb)
    session.commit()
    session.refresh(userdb)

    log.create_log({
        "usuario": current_user.usuario,
        "accion": "CREATE",
        "tabla": "User",
        "descripcion": f"Ha creado el id {userdb.id}"
    })

    # close the session
    session.close()

    # return the user object
    return userdb


@router.get("/user", response_model=List[schemas.user.UserList], tags=["user"])
async def read_users_list(token: Annotated[str, Depends(auth.oauth2_scheme)], current_user: Annotated[models.User, Depends(auth.get_current_user)]):

    #validando rol de usuario autenticado
    if current_user.rol != "superadmin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"No está autorizado a realizar esta acción")

    # create a new database session
    session = Session(bind=engine, expire_on_commit=False)

    # get the kiosko item with the given id
    usersdb = session.query(models.User).all()

    # close the session
    session.close()

    return usersdb


@router.get("/user/propietarios", response_model=List[schemas.user.UserList], tags=["user"])
async def read_users_listpropietarios(token: Annotated[str, Depends(auth.oauth2_scheme)], current_user: Annotated[models.User, Depends(auth.get_current_user)]):

    #validando rol de usuario autenticado
    if current_user.rol != "superadmin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"No está autorizado a realizar esta acción")

    # create a new database session
    session = Session(bind=engine, expire_on_commit=False)

    # listado de propietarios
    usersdb = session.query(models.User).where(
        models.User.rol == "propietario", models.User.activo == "1")

    # close the session
    session.close()

    return usersdb


@router.get("/user/{id}", response_model=schemas.user.User, tags=["user"])
async def read_user(id: int, token: Annotated[str, Depends(auth.oauth2_scheme)], current_user: Annotated[models.User, Depends(auth.get_current_user)]):

    # validando rol de usuario autenticado
    if current_user.rol != "superadmin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"No está autorizado a realizar esta acción")

    # create a new database session
    session = Session(bind=engine, expire_on_commit=False)

    # get the kiosko item with the given id
    userdb = session.query(models.User).get(id)

    # close the session
    session.close()

    if not userdb:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"El usuario {id} no ha sido encontrado")

    return userdb


@router.put("/user/{id}", tags=["user"])
async def update_user(id: int, user: schemas.user.UserEdit, token: Annotated[str, Depends(auth.oauth2_scheme)], current_user: Annotated[models.User, Depends(auth.get_current_user)]):

    # validando rol de usuario autenticado
    if current_user.rol != "superadmin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"No está autorizado a realizar esta acción")

    # create a new database session
    session = Session(bind=engine, expire_on_commit=False)

    # get the producto item with the given id
    userdb: schemas.user.UserInDB = session.query(models.User).get(id)

    # update user item with the given task (if an item with the given id was found)
    if userdb:
        userdb.nombre = user.nombre
        userdb.email = user.email
        userdb.rol = user.rol
        userdb.activo = user.activo
        session.commit()

        log.create_log({
        "usuario": current_user.usuario,
        "accion": "UPDATE",
        "tabla": "User",
        "descripcion": f"Ha editado el id {userdb.id}"
    })

    # close the session
    session.close()


@router.delete("/user/{id}", status_code=status.HTTP_204_NO_CONTENT, tags=["user"])
async def delete_user(id: int, token: Annotated[str, Depends(auth.oauth2_scheme)], current_user: Annotated[models.User, Depends(auth.get_current_user)]):

    # validando rol de usuario autenticado
    if current_user.rol != "superadmin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"No está autorizado a realizar esta acción")

    # create a new database session
    session = Session(bind=engine, expire_on_commit=False)

    # get the user item with the given id
    userdb = session.query(models.User).get(id)

    # if user item with given id exists, delete it from the database. Otherwise raise 404 error
    if userdb:
        session.delete(userdb)
        session.commit()
        session.close()

        log.create_log({
        "usuario": current_user.usuario,
        "accion": "DELETE",
        "tabla": "User",
        "descripcion": f"Ha eliminado el id {userdb.id}"
    })
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"El usuario {id} no ha sido encontrado")

    return None
