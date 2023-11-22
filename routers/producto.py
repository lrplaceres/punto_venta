from fastapi import APIRouter, status, HTTPException, Depends
from typing import List, Annotated
from sqlalchemy.orm import Session
from database.database import Base, engine
import schemas.producto
import models.models as models
import auth.auth as auth

# Create the database
Base.metadata.create_all(engine)

router = APIRouter()

@router.post("/producto", response_model=schemas.producto.Producto, status_code=status.HTTP_201_CREATED, tags=["producto"])
async def create_producto(producto: schemas.producto.ProductoCreate, token: Annotated[str, Depends(auth.oauth2_scheme)], current_user: Annotated[models.User, Depends(auth.get_current_user)]):

    if current_user.rol != "propietario":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"No está autorizado a realizar esta acción")

    # create a new database session
    session = Session(bind=engine, expire_on_commit=False)

    #buscar si existe producto
    existe_producto = session.query(models.Producto).where(models.Producto.nombre == producto.nombre, models.Producto.kiosko_id == producto.kiosko_id).count()
    existe_kiosko = session.query(models.Kiosko).get(producto.kiosko_id)
    if existe_producto:
        raise HTTPException(status_code=status.HTTP_412_PRECONDITION_FAILED, detail=f"El producto {producto.nombre} ya existe")
    
    if not existe_kiosko:
        raise HTTPException(status_code=status.HTTP_412_PRECONDITION_FAILED, detail=f"El kiosko {producto.kiosko_id} no existe")


    # create an instance of the ToDo database model
    productodb = models.Producto(nombre = producto.nombre, kiosko_id = producto.kiosko_id)

    # add it to the session and commit it
    session.add(productodb)
    session.commit()
    session.refresh(productodb)

    # close the session
    session.close()

    # return the todo object
    return productodb


@router.get("/producto/{id}", tags=["producto"])
async def read_producto(id: int, token: Annotated[str, Depends(auth.oauth2_scheme)], current_user: Annotated[models.User, Depends(auth.get_current_user)]):
    
    if current_user.rol != "propietario":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"No está autorizado a realizar esta acción")

    # create a new database session
    session = Session(bind=engine, expire_on_commit=False)

    # get the kiosko item with the given id
    productodb = session.query(models.Producto).get(id)

    # close the session
    session.close()

    if not productodb:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"El producto con id {id} no encontrado")

    return productodb


@router.put("/producto/{id}", tags=["producto"])
async def update_producto(id: int, nombre: str, kiosko_id: int, token: Annotated[str, Depends(auth.oauth2_scheme)], current_user: Annotated[models.User, Depends(auth.get_current_user)]):
    
    if current_user.rol != "propietario":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"No está autorizado a realizar esta acción")

    # create a new database session
    session = Session(bind=engine, expire_on_commit=False)

    # get the producto item with the given id
    productodb: schemas.producto.Producto = session.query(models.Producto).get(id)
    
    if productodb.kiosko_id != kiosko_id:
         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Producto no autorizado")
    
    # update todo item with the given task (if an item with the given id was found)
    if productodb:
        productodb.nombre = nombre
        session.commit()

    # close the session
    session.close()


@router.delete("/producto/{id}", status_code=status.HTTP_204_NO_CONTENT, tags=["producto"])
async def delete_producto(id: int, token: Annotated[str, Depends(auth.oauth2_scheme)], current_user: Annotated[models.User, Depends(auth.get_current_user)]):

    if current_user.rol != "propietario":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"No está autorizado a realizar esta acción")
    
    # create a new database session
    session = Session(bind=engine, expire_on_commit=False)

    # get the todo item with the given id
    productodb = session.query(models.Producto).get(id)

    # if todo item with given id exists, delete it from the database. Otherwise raise 404 error
    if productodb:
        session.delete(productodb)
        session.commit()
        session.close()
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"El producto con id {id} no encontrado")

    return None