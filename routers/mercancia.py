from fastapi import APIRouter, status, HTTPException
from typing import List
from sqlalchemy.orm import Session
from database.database import Base, engine
import schemas.mercancia
import models.models
from datetime import date

# Create the database
Base.metadata.create_all(engine)

router = APIRouter()

@router.post("/mercancia", response_model=schemas.mercancia.Mercancia, status_code=status.HTTP_201_CREATED, tags=["mercancia"])
async def create_mercancia(mercancia: schemas.mercancia.MercanciaCreate):

    # create a new database session
    session = Session(bind=engine, expire_on_commit=False)

    existe_kiosko = session.query(models.models.Kiosko).get(mercancia.kiosko_id)
    existe_producto = session.query(models.models.Producto).get(mercancia.producto_id)
    if not existe_kiosko:
        raise HTTPException(status_code=412, detail=f"mercancia not authorized")
    if not existe_producto:
        raise HTTPException(status_code=412, detail=f"mercancia not authorized")

    # create an instance of the ToDo database model
    mercanciadb = models.models.Mercancia(producto_id = mercancia.producto_id, cantidad = mercancia.cantidad, um = mercancia.um, costo = mercancia.costo, fecha = mercancia.fecha, kiosko_id = mercancia.kiosko_id)

    # add it to the session and commit it
    session.add(mercanciadb)
    session.commit()
    session.refresh(mercanciadb)

    # close the session
    session.close()

    # return the todo object
    return mercanciadb

@router.get("/mercancia/{id}", tags=["mercancia"])
async def read_mercancia(id: int):
    
    # create a new database session
    session = Session(bind=engine, expire_on_commit=False)

    # get the kiosko item with the given id
    mercanciadb = session.query(models.models.Mercancia).get(id)

    # close the session
    session.close()

    if not mercanciadb:
        raise HTTPException(status_code=404, detail=f"mercancia item with id {id} not found")

    return mercanciadb

@router.put("/mercancia/{id}", tags=["mercancia"])
async def update_mercancia(id: int, producto_id: int, cantidad: float, um: str, costo: float, fecha: date):

    # create a new database session
    session = Session(bind=engine, expire_on_commit=False)

    existe_producto = session.query(models.models.Producto).get(producto_id)
    if not existe_producto:
        raise HTTPException(status_code=412, detail=f"mercancia not authorized")

    # get the producto item with the given id
    mercanciadb: schemas.mercancia.Mercancia = session.query(models.models.Mercancia).get(id)    
    
    # update todo item with the given task (if an item with the given id was found)
    if mercanciadb:
        mercanciadb.producto_id = producto_id
        mercanciadb.cantidad = cantidad
        mercanciadb.um = um        
        mercanciadb.costo = costo     
        mercanciadb.fecha = fecha    
        session.commit()

    # close the session
    session.close()

@router.delete("/mercancia/{id}", status_code=status.HTTP_204_NO_CONTENT, tags=["mercancia"])
async def delete_mercancia(id: int):
        
    # create a new database session
    session = Session(bind=engine, expire_on_commit=False)

    # get the todo item with the given id
    mercanciadb = session.query(models.models.Mercancia).get(id)

    # if todo item with given id exists, delete it from the database. Otherwise raise 404 error
    if mercanciadb:
        session.delete(mercanciadb)
        session.commit()
        session.close()
    else:
        raise HTTPException(status_code=404, detail=f"mercancia item with id {id} not found")

    return None