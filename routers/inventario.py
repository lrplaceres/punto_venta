from fastapi import APIRouter, status, HTTPException, Depends
from typing import List, Annotated
from sqlalchemy.orm import Session
import sqlalchemy as db
from database.database import Base, engine
import schemas.inventario
import models.models as models
from datetime import date
import auth.auth as auth
import log.log as log

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
        .where(models.Negocio.id == inventario.negocio_id,
               models.Negocio.propietario_id == current_user.id)\
        .count()

    # verificar si usuario autenticado es propietario del producto
    prop_producto = session.query(models.Producto)\
        .join(models.Negocio)\
        .where(models.Negocio.id == inventario.negocio_id,
               models.Producto.id == inventario.producto_id)\
        .count()

    if not prop_producto or not prop_negocio:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"No está autorizado a realizar esta acción")

    # create an instance of the Inventario database model
    inventariodb = models.Inventario(producto_id=inventario.producto_id, cantidad=inventario.cantidad,
                                     um=inventario.um, costo=inventario.costo, precio_venta=inventario.precio_venta,
                                     fecha=inventario.fecha, negocio_id=inventario.negocio_id)

    # add it to the session and commit it
    session.add(inventariodb)
    session.commit()
    session.refresh(inventariodb)

    log.create_log({
        "usuario": current_user.usuario,
        "accion": "CREATE",
        "tabla": "Inventario",
        "descripcion": f"Ha creado el id {inventariodb.id}"
    })

    # close the session
    session.close()

    # return the inventario object
    return inventariodb


@router.get("/inventario/{id}", response_model=schemas.inventario.Inventario, tags=["inventario"])
async def read_inventario(id: int, token: Annotated[str, Depends(auth.oauth2_scheme)], current_user: Annotated[models.User, Depends(auth.get_current_user)]):

    # validando rol de usuario autenticado
    if current_user.rol != "propietario":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"No está autorizado a realizar esta acción")

    # create a new database session
    session = Session(bind=engine, expire_on_commit=False)

    # get the inventario item with the given id
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
            .where(models.Negocio.id == inventario.negocio_id,
                   models.Negocio.propietario_id == current_user.id)\
            .count()

        if not prop_negocio:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail=f"No está autorizado a realizar esta acción")

    # update inventario item with the given task (if an item with the given id was found)
    if inventariodb:
        inventariodb.producto_id = inventario.producto_id
        inventariodb.cantidad = inventario.cantidad
        inventariodb.um = inventario.um
        inventariodb.costo = inventario.costo
        inventariodb.precio_venta = inventario.precio_venta
        inventariodb.fecha = inventario.fecha
        inventariodb.negocio_id = inventario.negocio_id
        session.commit()

        log.create_log({
            "usuario": current_user.usuario,
            "accion": "UPDATE",
            "tabla": "Inventario",
            "descripcion": f"Ha editado el id {inventariodb.id}"
        })

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

    # get the inventario item with the given id
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

    # if inventario item with given id exists, delete it from the database. Otherwise raise 404 error
    if inventariodb:
        session.delete(inventariodb)
        session.commit()
        session.close()

        log.create_log({
            "usuario": current_user.usuario,
            "accion": "DELETE",
            "tabla": "Inventario",
            "descripcion": f"Ha eliminado el id {inventariodb.id}"
        })
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
    puntosdb = session.query(models.Inventario.id, models.Producto.nombre, models.Inventario.cantidad, models.Negocio.nombre, models.Inventario.costo, models.Inventario.fecha, models.Inventario.precio_venta)\
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
            "costo": row[4],
            "fecha": row[5],
            "precio_venta": row[6],
        })

    session.close()
    return resultdb


# inventarios que es posible distribuir
@router.get("/inventarios-a-distribuir/", tags=["inventarios"])
async def cantidad_distribuida_inventario(token: Annotated[str, Depends(auth.oauth2_scheme)], current_user: Annotated[models.User, Depends(auth.get_current_user)]):

    # validando rol de usuario autenticado
    if current_user.rol != "propietario":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"No está autorizado a realizar esta acción")

    # create a new database session
    session = Session(bind=engine, expire_on_commit=False)

    # get the inventario item with the given id
    inventariosdb = session.query(models.Inventario.id,
                                  models.Producto.nombre,
                                  db.func.sum(db.func.coalesce(
                                      (models.Inventario.cantidad), 0)),
                                  models.Inventario.fecha,
                                  models.Inventario.costo,
                                  db.func.sum(db.func.coalesce(
                                      (models.Distribucion.cantidad), 0)),
                                  models.Inventario.negocio_id,
                                  )\
        .select_from(models.Inventario)\
        .join(models.Producto, models.Producto.id == models.Inventario.producto_id)\
        .join(models.Negocio, models.Negocio.id == models.Inventario.negocio_id)\
        .join(models.User, models.User.id == models.Negocio.propietario_id)\
        .outerjoin(models.Distribucion, models.Distribucion.inventario_id == models.Inventario.id)\
        .where(models.User.usuario == current_user.usuario)\
        .group_by(models.Inventario.producto_id, models.Inventario.costo)\
        .order_by(models.Producto.nombre)\
        .all()

    resultdb = []
    for row in inventariosdb:
        if row[2] - row[5]:
            resultdb.append({
                "id": row[0],
                "nombre": row[1],
                "cantidad": row[2],
                "fecha": row[3],
                "costo": row[4],
                "distribuido": row[5],
                "negocio_id": row[6],
            })

    session.close()

    if not inventariosdb:
        raise HTTPException(
            status_code=404, detail=f"Inventarios no encontrados")

    return resultdb
