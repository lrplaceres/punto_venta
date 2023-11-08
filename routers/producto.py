from fastapi import APIRouter, status, HTTPException
from typing import List
from sqlalchemy.orm import Session
from database.database import Base, engine
import schemas.producto
import models.models

# Create the database
Base.metadata.create_all(engine)

router = APIRouter()

@router.post("/producto", response_model=schemas.producto.Producto, status_code=status.HTTP_201_CREATED, tags=["producto"])
async def create_producto(producto: schemas.producto.ProductoCreate):

    # create a new database session
    session = Session(bind=engine, expire_on_commit=False)

    #buscar si existe producto
    existe_producto = session.query(models.models.Producto).where(models.models.Producto.nombre == producto.nombre, models.models.Producto.kiosko_id == producto.kiosko_id).count()
    existe_kiosko = session.query(models.models.Kiosko).get(producto.kiosko_id)
    if existe_producto:
        raise HTTPException(status_code=412, detail=f"producto nombre {producto.nombre} exist")
    
    if not existe_kiosko:
        raise HTTPException(status_code=412, detail=f"kiosko {producto.kiosko_id} not exist")


    # create an instance of the ToDo database model
    productodb = models.models.Producto(nombre = producto.nombre, kiosko_id = producto.kiosko_id)

    # add it to the session and commit it
    session.add(productodb)
    session.commit()
    session.refresh(productodb)

    # close the session
    session.close()

    # return the todo object
    return productodb

@router.get("/producto/{id}", tags=["producto"])
async def read_producto(id: int):
    
    # create a new database session
    session = Session(bind=engine, expire_on_commit=False)

    # get the kiosko item with the given id
    productodb = session.query(models.models.Producto).get(id)

    # close the session
    session.close()

    if not productodb:
        raise HTTPException(status_code=404, detail=f"producto item with id {id} not found")

    return productodb

@router.put("/producto/{id}", tags=["producto"])
async def update_producto(id: int, nombre: str, kiosko_id: int):

    # create a new database session
    session = Session(bind=engine, expire_on_commit=False)

    # get the producto item with the given id
    productodb: schemas.producto.Producto = session.query(models.models.Producto).get(id)
    
    if productodb.kiosko_id != kiosko_id:
         raise HTTPException(status_code=403, detail=f"producto not authorized")
    
    # update todo item with the given task (if an item with the given id was found)
    if productodb:
        productodb.nombre = nombre
        session.commit()

    # close the session
    session.close()

@router.delete("/producto/{id}", status_code=status.HTTP_204_NO_CONTENT, tags=["producto"])
async def delete_producto(id: int):
        
    # create a new database session
    session = Session(bind=engine, expire_on_commit=False)

    # get the todo item with the given id
    productodb = session.query(models.models.Producto).get(id)

    # if todo item with given id exists, delete it from the database. Otherwise raise 404 error
    if productodb:
        session.delete(productodb)
        session.commit()
        session.close()
    else:
        raise HTTPException(status_code=404, detail=f"producto item with id {id} not found")

    return None