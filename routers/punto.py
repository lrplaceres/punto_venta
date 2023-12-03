from fastapi import APIRouter, status, HTTPException, Depends
from typing import List, Annotated
from sqlalchemy.orm import Session
from sqlalchemy import select
from database.database import Base, engine
import schemas.punto
import models.models as models
import auth.auth as auth
import log.log as log

# Create the database
Base.metadata.create_all(engine)

router = APIRouter()


@router.post("/punto", response_model=schemas.punto.Punto, status_code=status.HTTP_201_CREATED, tags=["punto"])
async def create_punto(punto: schemas.punto.PuntoCreate, token: Annotated[str, Depends(auth.oauth2_scheme)], current_user: Annotated[models.User, Depends(auth.get_current_user)]):

    # validando rol de usuario autenticado
    if current_user.rol != "propietario":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"No está autorizado a realizar esta acción")

    # create a new database session
    session = Session(bind=engine, expire_on_commit=False)

    # verificar si usuario autenticado es propietario del negocio
    prop_negocio = session.query(models.Negocio)\
        .where(models.Negocio.id == punto.negocio_id, models.Negocio.propietario_id == current_user.id)\
        .count()

    if not prop_negocio:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"No está autorizado a realizar esta acción")

    # create an instance of the Punto database model
    puntodb = models.Punto(
        nombre=punto.nombre, direccion=punto.direccion, negocio_id=punto.negocio_id)

    # add it to the session and commit it
    session.add(puntodb)
    session.commit()
    session.refresh(puntodb)

    log.create_log({
        "usuario": current_user.usuario,
        "accion": "CREATE",
        "tabla": "Punto",
        "descripcion": f"Ha creado el id {puntodb.id}"
    })

    # close the session
    session.close()

    # return the punto object
    return puntodb


@router.get("/punto/{id}", response_model=schemas.punto.Punto, tags=["punto"])
async def read_punto(id: int, token: Annotated[str, Depends(auth.oauth2_scheme)], current_user: Annotated[models.User, Depends(auth.get_current_user)]):

    # validando rol de usuario autenticado
    if current_user.rol != "propietario":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"No está autorizado a realizar esta acción")

    # create a new database session
    session = Session(bind=engine, expire_on_commit=False)

    # get the punto item with the given id
    puntodb: schemas.punto.Punto = session.query(models.Punto).get(id)

    # verificar si usuario autenticado es propietario del negocio
    if puntodb:
        prop_negocio = session.query(models.Negocio)\
            .where(models.Negocio.id == puntodb.negocio_id,
                   models.Negocio.propietario_id == current_user.id)\
            .count()

        if not prop_negocio:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail=f"No está autorizado a realizar esta acción")

    # close the session
    session.close()

    if not puntodb:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Punto con id {id} no encontrado")

    return puntodb


@router.put("/punto/{id}", tags=["punto"])
async def update_punto(id: int, punto: schemas.punto.PuntoCreate, token: Annotated[str, Depends(auth.oauth2_scheme)], current_user: Annotated[models.User, Depends(auth.get_current_user)]):

    # validando rol de usuario autenticado
    if current_user.rol != "propietario":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"No está autorizado a realizar esta acción")

    # create a new database session
    session = Session(bind=engine, expire_on_commit=False)

    # get the provincia item with the given id
    puntodb: schemas.punto.Punto = session.query(models.Punto).get(id)

    # verificar si usuario autenticado es propietario del negocio
    if puntodb:
        prop_negocio = session.query(models.Negocio)\
            .where(models.Negocio.id == puntodb.negocio_id,
                   models.Negocio.propietario_id == current_user.id)\
            .count()

        if not prop_negocio:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail=f"No está autorizado a realizar esta acción")

    # update punto item with the given task (if an item with the given id was found)
    if puntodb:
        puntodb.nombre = punto.nombre
        puntodb.direccion = punto.direccion
        puntodb.negocio_id = punto.negocio_id

        session.commit()

        log.create_log({
            "usuario": current_user.usuario,
            "accion": "UPDATE",
            "tabla": "Punto",
            "descripcion": f"Ha editado el id {puntodb.id}"
        })

    # close the session
    session.close()


@router.delete("/punto/{id}", status_code=status.HTTP_204_NO_CONTENT, tags=["punto"])
async def delete_punto(id: int, token: Annotated[str, Depends(auth.oauth2_scheme)], current_user: Annotated[models.User, Depends(auth.get_current_user)]):

    # validando rol de usuario autenticado
    if current_user.rol != "propietario":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"No está autorizado a realizar esta acción")

    # create a new database session
    session = Session(bind=engine, expire_on_commit=False)

    # get the punto item with the given id
    puntodb: schemas.punto.Punto = session.query(models.Punto).get(id)

    # verificar si usuario autenticado es propietario del negocio
    if puntodb:
        prop_negocio = session.query(models.Negocio)\
            .where(models.Negocio.id == puntodb.negocio_id,
                   models.Negocio.propietario_id == current_user.id)\
            .count()

        if not prop_negocio:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail=f"No está autorizado a realizar esta acción")

    # if punto item with given id exists, delete it from the database. Otherwise raise 404 error
    if puntodb:
        session.delete(puntodb)
        session.commit()
        session.close()

        log.create_log({
            "usuario": current_user.usuario,
            "accion": "DELETE",
            "tabla": "Punto",
            "descripcion": f"Ha eliminado el id {puntodb.id}"
        })
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Punto con id {id} no encontrado")

    return None


@router.get("/puntos/", response_model=List[schemas.punto.Punto], tags=["puntos"])
async def read_puntos_propietario(token: Annotated[str, Depends(auth.oauth2_scheme)], current_user: Annotated[models.User, Depends(auth.get_current_user)]):

    # validando rol de usuario autenticado
    if current_user.rol != "propietario":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"No está autorizado a realizar esta acción")

    # create a new database session
    session = Session(bind=engine, expire_on_commit=False)

    # get the negocio item with the given id
    puntosdb = session.query(models.Punto.id, models.Punto.nombre, models.Punto.direccion, models.Negocio.nombre)\
        .join(models.Negocio)\
        .join(models.User)\
        .where(models.User.usuario == current_user.usuario)\
        .order_by(models.Punto.id)\
        .all()

    resultdb = []
    for row in puntosdb:
        resultdb.append({
            "id": row[0],
            "nombre": row[1],
            "direccion": row[2],
            "negocio_id": row[3]
        })

    session.close()
    return resultdb


@router.get("/puntos-negocio/{id}", response_model=List[schemas.punto.Punto], tags=["puntos"])
async def read_punto(id: int, token: Annotated[str, Depends(auth.oauth2_scheme)], current_user: Annotated[models.User, Depends(auth.get_current_user)]):

    # validando rol de usuario autenticado
    if current_user.rol != "propietario":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"No está autorizado a realizar esta acción")

    # create a new database session
    session = Session(bind=engine, expire_on_commit=False)

    # get the punto item with the given id
    puntosdb = session.query(models.Punto).where(
        models.Punto.negocio_id == id).all()

    # verificar si usuario autenticado es propietario del negocio
    if puntosdb:
        prop_negocio = session.query(models.Negocio)\
            .where(models.Negocio.id == id,
                   models.Negocio.propietario_id == current_user.id)\
            .count()

        if not prop_negocio:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail=f"No está autorizado a realizar esta acción")

    # close the session
    session.close()

    if not puntosdb:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"No se han encontrado Puntos del negocio {id}")

    return puntosdb
