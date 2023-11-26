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

    #validando rol de usuario autenticado
    if current_user.rol != "propietario":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"No está autorizado a realizar esta acción")

    # create a new database session
    session = Session(bind=engine, expire_on_commit=False)

    # verificar si usuario autenticado es propietario del negocio
    prop_negocio = session.query(models.Negocio)\
        .where(models.Negocio.id == producto.negocio_id, models.Negocio.propietario_id == current_user.id)\
        .count()

    if not prop_negocio:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"No está autorizado a realizar esta acción")

    existe_producto = session.query(models.Producto).where(
        models.Producto.nombre == producto.nombre, models.Producto.negocio_id == producto.negocio_id).count()

    if existe_producto:
        raise HTTPException(status_code=status.HTTP_412_PRECONDITION_FAILED,
                            detail=f"El producto {producto.nombre} ya existe")

    # create an instance of the ToDo database model
    productodb = models.Producto(
        nombre=producto.nombre, negocio_id=producto.negocio_id)

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

    #validando rol de usuario autenticado
    if current_user.rol != "propietario":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"No está autorizado a realizar esta acción")

    # create a new database session
    session = Session(bind=engine, expire_on_commit=False)

    # get the kiosko item with the given id
    productodb = session.query(models.Producto).get(id)

    # verificar si usuario autenticado es propietario del negocio
    if productodb:
        prop_negocio = session.query(models.Negocio)\
            .where(models.Negocio.id == productodb.negocio_id, models.Negocio.propietario_id == current_user.id)\
            .count()

        if not prop_negocio:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail=f"No está autorizado a realizar esta acción")

    # close the session
    session.close()

    if not productodb:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"El producto con id {id} no encontrado")

    return productodb


@router.put("/producto/{id}", tags=["producto"])
async def update_producto(id: int, producto: schemas.producto.Producto, token: Annotated[str, Depends(auth.oauth2_scheme)], current_user: Annotated[models.User, Depends(auth.get_current_user)]):

    #validando rol de usuario autenticado
    if current_user.rol != "propietario":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"No está autorizado a realizar esta acción")

    # create a new database session
    session = Session(bind=engine, expire_on_commit=False)

    # get the producto item with the given id
    productodb: schemas.producto.Producto = session.query(
        models.Producto).get(id)

    # verificar si usuario autenticado es propietario del negocio
    if productodb:
        prop_negocio = session.query(models.Negocio)\
            .where(models.Negocio.id == productodb.negocio_id, models.Negocio.propietario_id == current_user.id)\
            .count()

        if not prop_negocio:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail=f"No está autorizado a realizar esta acción")

    # update todo item with the given task (if an item with the given id was found)
    if productodb:
        productodb.nombre = producto.nombre
        productodb.negocio_id = producto.negocio_id
        session.commit()

    # close the session
    session.close()


@router.delete("/producto/{id}", status_code=status.HTTP_204_NO_CONTENT, tags=["producto"])
async def delete_producto(id: int, token: Annotated[str, Depends(auth.oauth2_scheme)], current_user: Annotated[models.User, Depends(auth.get_current_user)]):

    #validando rol de usuario autenticado
    if current_user.rol != "propietario":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"No está autorizado a realizar esta acción")

    # create a new database session
    session = Session(bind=engine, expire_on_commit=False)

    # get the todo item with the given id
    productodb = session.query(models.Producto).get(id)

    # verificar si usuario autenticado es propietario del negocio
    if productodb:
        prop_negocio = session.query(models.Negocio)\
            .where(models.Negocio.id == productodb.negocio_id, models.Negocio.propietario_id == current_user.id)\
            .count()

        if not prop_negocio:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail=f"No está autorizado a realizar esta acción")

    # if todo item with given id exists, delete it from the database. Otherwise raise 404 error
    if productodb:
        session.delete(productodb)
        session.commit()
        session.close()
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"El producto con id {id} no encontrado")

    return None


@router.get("/productos/", response_model=List[schemas.producto.Producto], tags=["productos"])
async def read_productos_propietario(token: Annotated[str, Depends(auth.oauth2_scheme)], current_user: Annotated[models.User, Depends(auth.get_current_user)]):

    #validando rol de usuario autenticado
    if current_user.rol != "propietario":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"No está autorizado a realizar esta acción")
                            
    # create a new database session
    session = Session(bind=engine, expire_on_commit=False)

    negociosdb = session.query(models.Producto.id, models.Producto.nombre, models.Negocio.nombre)\
        .join(models.Negocio)\
        .join(models.User)\
        .where(models.User.usuario == current_user.usuario)\
        .all()

    resultdb = []

    for row in negociosdb:
        resultdb.append({
            "id": row[0],
            "nombre": row[1],
            "negocio_id": row[2]
        })

    # close the session
    session.close()

    return resultdb
