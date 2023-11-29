from fastapi import APIRouter, status, HTTPException, Depends
from typing import List, Annotated
from sqlalchemy.orm import Session
from database.database import Base, engine
import schemas.venta
import models.models as models
from datetime import date
import auth.auth as auth

# Create the database
Base.metadata.create_all(engine)

router = APIRouter()


@router.post("/venta", response_model=schemas.venta.Venta, status_code=status.HTTP_201_CREATED, tags=["venta"])
async def create_venta(venta: schemas.venta.VentaCreate, token: Annotated[str, Depends(auth.oauth2_scheme)], current_user: Annotated[models.User, Depends(auth.get_current_user)]):

    # validando rol de usuario autenticado
    if current_user.rol != "propietario" and current_user.rol != "dependiente":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"No está autorizado a realizar esta acción")

    # create a new database session
    session = Session(bind=engine, expire_on_commit=False)

    # create an instance of the venta database model
    ventadb = models.Venta(distribucion_id=venta.distribucion_id, cantidad=venta.cantidad,
                           precio=venta.precio, fecha=venta.fecha, punto_id=venta.punto_id, usuario_id=current_user.id)

    # add it to the session and commit it
    session.add(ventadb)
    session.commit() 
    session.refresh(ventadb)

    # close the session
    session.close()

    # return the venta object
    return ventadb


@router.get("/venta/{id}", tags=["venta"])
async def read_venta(id: int, token: Annotated[str, Depends(auth.oauth2_scheme)], current_user: Annotated[models.User, Depends(auth.get_current_user)]):

    # validando rol de usuario autenticado
    if current_user.rol == "propietario" or current_user.rol == "dependiente":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"No está autorizado a realizar esta acción")

    # create a new database session
    session = Session(bind=engine, expire_on_commit=False)

    # get the venta item with the given id
    ventadb = session.query(models.Venta).get(id)

    # close the session
    session.close()

    if not ventadb:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Venta con id {id} no encontrada")

    return ventadb


@router.put("/venta/{id}", tags=["venta"])
async def update_venta(id: int, venta:schemas.venta.VentaCreate, token: Annotated[str, Depends(auth.oauth2_scheme)], current_user: Annotated[models.User, Depends(auth.get_current_user)]):

    # validando rol de usuario autenticado
    if current_user.rol == "propietario" or current_user.rol == "dependiente":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"No está autorizado a realizar esta acción")

    # create a new database session
    session = Session(bind=engine, expire_on_commit=False)

    # get the venta item with the given id
    ventadb: schemas.venta.Venta = session.query(models.Venta).get(id)

    # update todo item with the given task (if an item with the given id was found)
    if ventadb:
        ventadb.distribucion_id = venta.distribucion_id
        ventadb.cantidad = venta.cantidad
        ventadb.precio = venta.precio
        ventadb.fecha = venta.fecha
        ventadb.punto_id = venta.punto_id
        ventadb.usuario_id = venta.usuario_id
        session.commit()

    # close the session
    session.close()


@router.delete("/venta/{id}", status_code=status.HTTP_204_NO_CONTENT, tags=["venta"])
async def delete_venta(id: int, token: Annotated[str, Depends(auth.oauth2_scheme)], current_user: Annotated[models.User, Depends(auth.get_current_user)]):

    # validando rol de usuario autenticado
    if current_user.rol == "propietario" or current_user.rol == "dependiente":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"No está autorizado a realizar esta acción")

    # create a new database session
    session = Session(bind=engine, expire_on_commit=False)

    # get the venta item with the given id
    ventadb = session.query(models.Venta).get(id)

    # if todo item with given id exists, delete it from the database. Otherwise raise 404 error
    if ventadb:
        session.delete(ventadb)
        session.commit()
        session.close()
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Venta con id {id} no encontrado")

    return None
