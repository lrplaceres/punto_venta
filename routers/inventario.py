from fastapi import APIRouter, status, HTTPException, Depends
from typing import List, Annotated
from sqlalchemy.orm import Session
from database.database import Base, engine
import schemas.inventario
import models.models as models
from datetime import date
import auth.auth as auth

# Create the database
Base.metadata.create_all(engine)

router = APIRouter()


@router.post("/inventario", response_model=schemas.inventario.Inventario, status_code=status.HTTP_201_CREATED, tags=["inventario"])
async def create_inventario(inventario: schemas.inventario.InventarioCreate, token: Annotated[str, Depends(auth.oauth2_scheme)], current_user: Annotated[models.User, Depends(auth.get_current_user)]):

    # validando rol de usuario autenticado
    if current_user.rol != "propietario":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"No está autorizado a realizar esta acción")

    # create a new database session
    session = Session(bind=engine, expire_on_commit=False)

    # verificar si usuario autenticado es propietario del negocio
    prop_negocio = session.query(models.Negocio)\
        .where(models.Negocio.id == inventario.negocio_id,\
            models.Negocio.propietario_id == current_user.id)\
        .count()

    if not prop_negocio:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"No está autorizado a realizar esta acción")

    prop_producto = session.query(models.Producto)\
        .join(models.Negocio)\
        .where(models.Negocio.id == inventario.negocio_id,\
            models.Producto.id == inventario.producto_id)\
        .count()

    if not prop_producto:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"No está autorizado a realizar esta acción")

    # create an instance of the ToDo database model
    inventariodb = models.Inventario(producto_id=inventario.producto_id, cantidad=inventario.cantidad,
                                     um=inventario.um, costo=inventario.costo, fecha=inventario.fecha, negocio_id=inventario.negocio_id)

    # add it to the session and commit it
    session.add(inventariodb)
    session.commit()
    session.refresh(inventariodb)

    # close the session
    session.close()

    # return the todo object
    return inventariodb


@router.get("/inventario/{id}", tags=["inventario"])
async def read_inventario(id: int, token: Annotated[str, Depends(auth.oauth2_scheme)], current_user: Annotated[models.User, Depends(auth.get_current_user)]):

    # validando rol de usuario autenticado
    if current_user.rol != "propietario":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"No está autorizado a realizar esta acción")

    # create a new database session
    session = Session(bind=engine, expire_on_commit=False)

    # get the kiosko item with the given id
    inventariodb = session.query(models.Inventario).get(id)

    # verificar si usuario autenticado es propietario del negocio
    if inventariodb:
        prop_negocio = session.query(models.Negocio)\
            .where(models.Negocio.id == inventariodb.negocio_id, models.Negocio.propietario_id == current_user.id)\
            .count()

        if not prop_negocio:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail=f"No está autorizado a realizar esta acción")

    # close the session
    session.close()

    if not inventariodb:
        raise HTTPException(
            status_code=404, detail=f"Inventario con id {id} no encontrado")

    return inventariodb


@router.put("/inventario/{id}", tags=["inventario"])
async def update_inventario(id: int, inventario: schemas.inventario.Inventario, token: Annotated[str, Depends(auth.oauth2_scheme)], current_user: Annotated[models.User, Depends(auth.get_current_user)]):

    # validando rol de usuario autenticado
    if current_user.rol != "propietario":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"No está autorizado a realizar esta acción")

    # create a new database session
    session = Session(bind=engine, expire_on_commit=False)

    # get the producto item with the given id
    inventariodb: schemas.inventario.Inventario = session.query(
        models.Inventario).get(id)

    # verificar si usuario autenticado es propietario del negocio
    if inventariodb:
        prop_negocio = session.query(models.Negocio)\
            .where(models.Negocio.id == inventariodb.negocio_id, models.Negocio.propietario_id == current_user.id)\
            .count()

        if not prop_negocio:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail=f"No está autorizado a realizar esta acción")

    # update todo item with the given task (if an item with the given id was found)
    if inventariodb:
        inventariodb.producto_id = inventario.producto_id
        inventariodb.cantidad = inventario.cantidad
        inventariodb.um = inventario.um
        inventariodb.costo = inventario.costo
        inventariodb.fecha = inventario.fecha
        inventariodb.negocio_id = inventario.negocio_id
        session.commit()

    # close the session
    session.close()


@router.delete("/inventario/{id}", status_code=status.HTTP_204_NO_CONTENT, tags=["inventario"])
async def delete_inventario(id: int, token: Annotated[str, Depends(auth.oauth2_scheme)], current_user: Annotated[models.User, Depends(auth.get_current_user)]):

    # validando rol de usuario autenticado
    if current_user.rol != "propietario":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"No está autorizado a realizar esta acción")

    # create a new database session
    session = Session(bind=engine, expire_on_commit=False)

    # get the todo item with the given id
    inventariodb = session.query(models.Inventario).get(id)

    # verificar si usuario autenticado es propietario del negocio
    if inventariodb:
        prop_negocio = session.query(models.Negocio)\
            .where(models.Negocio.id == inventariodb.negocio_id, models.Negocio.propietario_id == current_user.id)\
            .count()

        if not prop_negocio:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail=f"No está autorizado a realizar esta acción")

    # if todo item with given id exists, delete it from the database. Otherwise raise 404 error
    if inventariodb:
        session.delete(inventariodb)
        session.commit()
        session.close()
    else:
        raise HTTPException(
            status_code=404, detail=f"Inventario con id {id} no encontrado")

    return None


@router.get("/inventarios/", tags=["inventarios"])
async def read_inventarios_propietario(token: Annotated[str, Depends(auth.oauth2_scheme)], current_user: Annotated[models.User, Depends(auth.get_current_user)]):

    # validando rol de usuario autenticado
    if current_user.rol != "propietario":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"No está autorizado a realizar esta acción")

    # create a new database session
    session = Session(bind=engine, expire_on_commit=False)

    # get the negocio item with the given id
    puntosdb = session.query(models.Inventario.id, models.Producto.nombre, models.Inventario.cantidad, models.Negocio.nombre)\
        .select_from(models.Inventario)\
        .join(models.Negocio)\
        .join(models.User)\
        .join(models.Producto, models.Inventario.producto_id == models.Producto.id)\
        .where(models.User.usuario == current_user.usuario)\
        .all()

    resultdb = []
    for row in puntosdb:
        resultdb.append({
            "id": row[0],
            "nombre": row[1],
            "cantidad": row[2],
            "negocio_id": row[3],
        })

    session.close()
    return resultdb
