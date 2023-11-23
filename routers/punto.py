from fastapi import APIRouter, status, HTTPException, Depends
from typing import List, Annotated
from sqlalchemy.orm import Session
from sqlalchemy import select
from database.database import Base, engine
import schemas.punto
import models.models as models
import auth.auth as auth

# Create the database
Base.metadata.create_all(engine)

router = APIRouter()


@router.post("/punto", response_model=schemas.punto.Punto, status_code=status.HTTP_201_CREATED, tags=["punto"])
async def create_punto(punto: schemas.punto.PuntoCreate, token: Annotated[str, Depends(auth.oauth2_scheme)], current_user: Annotated[models.User, Depends(auth.get_current_user)]):

    # create a new database session
    session = Session(bind=engine, expire_on_commit=False)

    # create an instance of the Negocio database model
    puntodb = models.Punto(
        nombre=punto.nombre, direccion=punto.direccion, negocio_id=punto.negocio_id)

    # add it to the session and commit it
    session.add(puntodb)
    session.commit()
    session.refresh(puntodb)

    # close the session
    session.close()

    # return the punto object
    return puntodb


@router.get("/punto/{id}", response_model=schemas.punto.Punto, tags=["punto"])
async def read_punto(id: int, token: Annotated[str, Depends(auth.oauth2_scheme)]):

    # create a new database session
    session = Session(bind=engine, expire_on_commit=False)

    # get the kiosko item with the given id
    puntodb = session.query(models.Punto).get(id)

    # close the session
    session.close()

    if not puntodb:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Punto con id {id} no encontrado")

    return puntodb


@router.put("/punto/{id}", tags=["punto"])
async def update_punto(id: int, punto: schemas.punto.PuntoCreate, token: Annotated[str, Depends(auth.oauth2_scheme)], current_user: Annotated[models.User, Depends(auth.get_current_user)]):

    # create a new database session
    session = Session(bind=engine, expire_on_commit=False)

    # get the provincia item with the given id
    puntodb: schemas.punto.Punto = session.query(models.Punto).get(id)

    # update todo item with the given task (if an item with the given id was found)
    if puntodb:
       puntodb.nombre = punto.nombre
       puntodb.direccion = punto.direccion
       puntodb.negocio_id = punto.negocio_id

       session.commit()

    # close the session
    session.close()


@router.delete("/punto/{id}", status_code=status.HTTP_204_NO_CONTENT, tags=["punto"])
async def delete_punto(id: int, token: Annotated[str, Depends(auth.oauth2_scheme)], current_user: Annotated[models.User, Depends(auth.get_current_user)]):

   
    # create a new database session
    session = Session(bind=engine, expire_on_commit=False)

    # get the todo item with the given id
    puntodb = session.query(models.Punto).get(id)

    # if todo item with given id exists, delete it from the database. Otherwise raise 404 error
    if puntodb:
        session.delete(puntodb)
        session.commit()
        session.close()
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Punto con id {id} no encontrado")

    return None


@router.get("/puntos/{usuario}",response_model=List[schemas.punto.Punto], tags=["puntos"])
async def read_puntos_propietario(usuario: str, token: Annotated[str, Depends(auth.oauth2_scheme)], current_user: Annotated[models.User, Depends(auth.get_current_user)]):

    # create a new database session
    session = Session(bind=engine, expire_on_commit=False)

    # get the negocio item with the given id
    puntosdb = session.query(models.Punto.id,models.Punto.nombre, models.Punto.direccion, models.Negocio.nombre)\
        .join(models.Negocio)\
        .join(models.User)\
        .where(models.User.usuario == usuario)\
        .order_by(models.Punto.nombre)\
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

