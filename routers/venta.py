from fastapi import APIRouter, status, HTTPException
from typing import List
from sqlalchemy.orm import Session
from database.database import Base, engine
import schemas.venta
import models.models
from datetime import date

# Create the database
Base.metadata.create_all(engine)

router = APIRouter()

@router.post("/venta", response_model=schemas.venta.Venta, status_code=status.HTTP_201_CREATED, tags=["venta"])
async def create_venta(venta: schemas.venta.VentaCreate):

    # create a new database session
    session = Session(bind=engine, expire_on_commit=False)

    existe_kiosko = session.query(models.models.Kiosko).get(venta.kiosko_id)
    existe_mercancia = session.query(models.models.Mercancia).get(venta.mercancia_id)
    if not existe_kiosko:
        raise HTTPException(status_code=412, detail=f"mercancia not authorized")
    if not existe_mercancia:
        raise HTTPException(status_code=412, detail=f"mercancia not authorized")

    # create an instance of the ToDo database model
    ventadb = models.models.Venta(mercancia_id = venta.mercancia_id, cantidad = venta.cantidad, precio = venta.precio, fecha = venta.fecha, kiosko_id = venta.kiosko_id)

    # add it to the session and commit it
    session.add(ventadb)
    session.commit()
    session.refresh(ventadb)

    # close the session
    session.close()

    # return the todo object
    return ventadb

@router.get("/venta/{id}", tags=["venta"])
async def read_venta(id: int):
    
    # create a new database session
    session = Session(bind=engine, expire_on_commit=False)

    # get the kiosko item with the given id
    ventadb = session.query(models.models.Venta).get(id)

    # close the session
    session.close()

    if not ventadb:
        raise HTTPException(status_code=404, detail=f"venta item with id {id} not found")

    return ventadb

@router.put("/venta/{id}", tags=["venta"])
async def update_venta(id: int, mercancia_id: int, cantidad: float, precio: float, fecha: date):

    # create a new database session
    session = Session(bind=engine, expire_on_commit=False)

    existe_mercancia = session.query(models.models.Mercancia).get(mercancia_id)
    if not existe_mercancia:
        raise HTTPException(status_code=412, detail=f"mercancia not authorized")

    # get the producto item with the given id
    ventadb: schemas.venta.Venta = session.query(models.models.Venta).get(id)    
    
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
async def delete_producto(id: int):
        
    # create a new database session
    session = Session(bind=engine, expire_on_commit=False)

    # get the todo item with the given id
    ventadb = session.query(models.models.Venta).get(id)

    # if todo item with given id exists, delete it from the database. Otherwise raise 404 error
    if ventadb:
        session.delete(ventadb)
        session.commit()
        session.close()
    else:
        raise HTTPException(status_code=404, detail=f"venta item with id {id} not found")

    return None