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

    if current_user.rol == "superadmin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"No está autorizado a realizar esta acción")

    # create a new database session
    session = Session(bind=engine, expire_on_commit=False)

    existe_kiosko = session.query(models.Kiosko).get(venta.kiosko_id)
    existe_mercancia = session.query(models.Mercancia).get(venta.mercancia_id)
    if not existe_kiosko or not existe_mercancia:
        raise HTTPException(status_code=status.HTTP_412_PRECONDITION_FAILED, detail=f"Inventario no autorizado")
    
    # create an instance of the ToDo database model
    ventadb = models.Venta(mercancia_id = venta.mercancia_id, cantidad = venta.cantidad, precio = venta.precio, fecha = venta.fecha, kiosko_id = venta.kiosko_id)

    # add it to the session and commit it
    session.add(ventadb)
    session.commit()
    session.refresh(ventadb)

    # close the session
    session.close()

    # return the todo object
    return ventadb


@router.get("/venta/{id}", tags=["venta"])
async def read_venta(id: int, token: Annotated[str, Depends(auth.oauth2_scheme)], current_user: Annotated[models.User, Depends(auth.get_current_user)]):
    
    if current_user.rol == "superadmin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"No está autorizado a realizar esta acción")

    # create a new database session
    session = Session(bind=engine, expire_on_commit=False)

    # get the kiosko item with the given id
    ventadb = session.query(models.Venta).get(id)

    # close the session
    session.close()

    if not ventadb:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Venta con id {id} no encontrada")

    return ventadb


@router.put("/venta/{id}", tags=["venta"])
async def update_venta(id: int, mercancia_id: int, cantidad: float, precio: float, fecha: date, token: Annotated[str, Depends(auth.oauth2_scheme)], current_user: Annotated[models.User, Depends(auth.get_current_user)]):

    if current_user.rol == "superadmin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"No está autorizado a realizar esta acción")

    # create a new database session
    session = Session(bind=engine, expire_on_commit=False)

    existe_mercancia = session.query(models.Mercancia).get(mercancia_id)
    if not existe_mercancia:
        raise HTTPException(status_code=status.HTTP_412_PRECONDITION_FAILED, detail=f"Inventario no autorizado")

    # get the producto item with the given id
    ventadb: schemas.venta.Venta = session.query(models.Venta).get(id)    
    
    # update todo item with the given task (if an item with the given id was found)
    if ventadb:
        ventadb.mercancia_id = mercancia_id
        ventadb.cantidad = cantidad
        ventadb.precio = precio        
        ventadb.fecha = fecha        
        session.commit()

    # close the session
    session.close()


@router.delete("/venta/{id}", status_code=status.HTTP_204_NO_CONTENT, tags=["venta"])
async def delete_venta(id: int, token: Annotated[str, Depends(auth.oauth2_scheme)], current_user: Annotated[models.User, Depends(auth.get_current_user)]):

    if current_user.rol == "superadmin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"No está autorizado a realizar esta acción")
    
    # create a new database session
    session = Session(bind=engine, expire_on_commit=False)

    # get the todo item with the given id
    ventadb = session.query(models.Venta).get(id)

    # if todo item with given id exists, delete it from the database. Otherwise raise 404 error
    if ventadb:
        session.delete(ventadb)
        session.commit()
        session.close()
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Venta con id {id} no encontrado")

    return None