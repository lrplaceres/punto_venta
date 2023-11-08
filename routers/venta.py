from fastapi import APIRouter, status, HTTPException
from typing import List
from sqlalchemy.orm import Session
from database.database import Base, engine
import schemas.venta
import models.models

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
    ventadb = models.models.Mercancia(mercancia_id = venta.mercancia_id, cantidad = venta.cantidad, costo = venta.costo, fecha = venta.fecha, kiosko_id = venta.kiosko_id)

    # add it to the session and commit it
    session.add(ventadb)
    session.commit()
    session.refresh(ventadb)

    # close the session
    session.close()

    # return the todo object
    return mercanciadb

@router.get("/venta/{id}", tags=["venta"])
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

@router.put("/venta/{id}", tags=["venta"])
async def update_producto(id: int, producto_id: int, cantidad: float, um: str, costo: float):

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
    if mercanciadb:
        session.delete(ventadb)
        session.commit()
        session.close()
    else:
        raise HTTPException(status_code=404, detail=f"venta item with id {id} not found")

    return None