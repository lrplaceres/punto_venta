from fastapi import APIRouter, status, HTTPException
from typing import List
from sqlalchemy.orm import Session
from database.database import Base, engine
import schemas.inventario
import models.models
from datetime import date

# Create the database
Base.metadata.create_all(engine)

router = APIRouter()

@router.post("/inventario", response_model=schemas.inventario.Inventario, status_code=status.HTTP_201_CREATED, tags=["inventario"])
async def create_inventario(inventario: schemas.inventario.InventarioCreate):

    # create a new database session
    session = Session(bind=engine, expire_on_commit=False)

    existe_kiosko = session.query(models.models.Kiosko).get(inventario.kiosko_id)
    existe_producto = session.query(models.models.Producto).get(inventario.producto_id)
    if not existe_kiosko:
        raise HTTPException(status_code=412, detail=f"inventario not authorized")
    if not existe_producto:
        raise HTTPException(status_code=412, detail=f"inventario not authorized")

    # create an instance of the ToDo database model
    inventariodb = models.models.Integer(producto_id = inventario.producto_id, cantidad = inventario.cantidad, um = inventario.um, costo = inventario.costo, fecha = inventario.fecha, kiosko_id = inventario.kiosko_id)

    # add it to the session and commit it
    session.add(inventariodb)
    session.commit()
    session.refresh(inventariodb)

    # close the session
    session.close()

    # return the todo object
    return inventariodb

@router.get("/inventario/{id}", tags=["inventario"])
async def readinventario(id: int):
    
    # create a new database session
    session = Session(bind=engine, expire_on_commit=False)

    # get the kiosko item with the given id
    inventariodb = session.query(models.models.Inventario).get(id)

    # close the session
    session.close()

    if not inventariodb:
        raise HTTPException(status_code=404, detail=f"inventario item with id {id} not found")

    return inventariodb

@router.put("/inventario/{id}", tags=["inventario"])
async def update_inventario(id: int, producto_id: int, cantidad: float, um: str, costo: float, fecha: date):

    # create a new database session
    session = Session(bind=engine, expire_on_commit=False)

    existe_producto = session.query(models.models.Producto).get(producto_id)
    if not existe_producto:
        raise HTTPException(status_code=412, detail=f"inventario not authorized")

    # get the producto item with the given id
    inventariodb: schemas.inventario.Inventario = session.query(models.models.Inventario).get(id)    
    
    # update todo item with the given task (if an item with the given id was found)
    if inventariodb:
        inventariodb.producto_id = producto_id
        inventariodb.cantidad = cantidad
        inventariodb.um = um        
        inventariodb.costo = costo     
        inventariodb.fecha = fecha    
        session.commit()

    # close the session
    session.close()

@router.delete("/inventario/{id}", status_code=status.HTTP_204_NO_CONTENT, tags=["inventario"])
async def delete_inventario(id: int):
        
    # create a new database session
    session = Session(bind=engine, expire_on_commit=False)

    # get the todo item with the given id
    inventariodb = session.query(models.models.Inventario).get(id)

    # if todo item with given id exists, delete it from the database. Otherwise raise 404 error
    if inventariodb:
        session.delete(inventariodb)
        session.commit()
        session.close()
    else:
        raise HTTPException(status_code=404, detail=f"inventario item with id {id} not found")

    return None