from fastapi import APIRouter, status, HTTPException, Depends
from typing import List, Annotated
from sqlalchemy.orm import Session
import sqlalchemy as db
from database.database import Base, engine
import schemas.venta
import models.models as models
from datetime import date, datetime
import auth.auth as auth
import log.log as log

# Create the database
Base.metadata.create_all(engine)

router = APIRouter()


@router.post("/venta", response_model=schemas.venta.Venta, status_code=status.HTTP_201_CREATED, tags=["venta"])
async def create_venta(venta: schemas.venta.VentaCreate, token: Annotated[str, Depends(auth.oauth2_scheme)], current_user: Annotated[models.User, Depends(auth.get_current_user)]):

    # validando rol de usuario autenticado
    if current_user.rol != "propietario" and current_user.rol != "dependiente":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"No está autorizado a realizar esta acción")

    # create a new database session
    session = Session(bind=engine, expire_on_commit=False)

    # create an instance of the venta database model
    ventadb = models.Venta(distribucion_id=venta.distribucion_id, cantidad=venta.cantidad,
                           precio=venta.precio, fecha=venta.fecha, punto_id=venta.punto_id,
                            usuario_id=current_user.id, monto=venta.cantidad * venta.precio)

    # add it to the session and commit it
    session.add(ventadb)
    session.commit()
    session.refresh(ventadb)

    log.create_log({
        "usuario": current_user.usuario,
        "accion": "CREATE",
        "tabla": "Venta",
        "descripcion": f"Ha creado el id {ventadb.id}"
    })

    # close the session
    session.close()

    # return the venta object
    return ventadb


@router.get("/venta/{id}", response_model=schemas.venta.VentaCreate, tags=["venta"])
async def read_venta(id: int, token: Annotated[str, Depends(auth.oauth2_scheme)], current_user: Annotated[models.User, Depends(auth.get_current_user)]):

    # validando rol de usuario autenticado
    if current_user.rol != "propietario" and current_user.rol != "dependiente":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"No está autorizado a realizar esta acción")

    # create a new database session
    session = Session(bind=engine, expire_on_commit=False)

    # get the venta item with the given id
    ventadb = session.query(models.Venta).get(id)

    # close the session
    session.close()

    if not ventadb:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Venta con id {id} no encontrada")

    return ventadb


@router.put("/venta/{id}", tags=["venta"])
async def update_venta(id: int, venta: schemas.venta.VentaCreate, token: Annotated[str, Depends(auth.oauth2_scheme)], current_user: Annotated[models.User, Depends(auth.get_current_user)]):

    # validando rol de usuario autenticado
    if current_user.rol != "propietario" and current_user.rol != "dependiente":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"No está autorizado a realizar esta acción")

    # create a new database session
    session = Session(bind=engine, expire_on_commit=False)

    # get the venta item with the given id
    ventadb: schemas.venta.Venta = session.query(models.Venta).get(id)

    # update todo item with the given task (if an item with the given id was found)
    if ventadb:
        ventadb.cantidad = venta.cantidad
        ventadb.precio = venta.precio
        ventadb.fecha = venta.fecha
        ventadb.monto = venta.cantidad * venta.precio
        session.commit()

        log.create_log({
            "usuario": current_user.usuario,
            "accion": "UPDATE",
            "tabla": "Venta",
            "descripcion": f"Ha editado el id {ventadb.id}"
        })

    # close the session
    session.close()


@router.delete("/venta/{id}", status_code=status.HTTP_204_NO_CONTENT, tags=["venta"])
async def delete_venta(id: int, token: Annotated[str, Depends(auth.oauth2_scheme)], current_user: Annotated[models.User, Depends(auth.get_current_user)]):

    # validando rol de usuario autenticado
    if current_user.rol != "propietario" and current_user.rol != "dependiente":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"No está autorizado a realizar esta acción")

    # create a new database session
    session = Session(bind=engine, expire_on_commit=False)

    # get the venta item with the given id
    ventadb = session.query(models.Venta).get(id)

    # if todo item with given id exists, delete it from the database. Otherwise raise 404 error
    if ventadb:
        session.delete(ventadb)
        session.commit()
        session.close()

        log.create_log({
            "usuario": current_user.usuario,
            "accion": "DELETE",
            "tabla": "Venta",
            "descripcion": f"Ha eliminado el id {ventadb.id}"
        })
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Venta con id {id} no encontrado")

    return None


@router.get("/ventas", tags=["ventas"])
async def read_ventas_propietario(token: Annotated[str, Depends(auth.oauth2_scheme)], current_user: Annotated[models.User, Depends(auth.get_current_user)]):

    # validando rol de usuario autenticado
    if current_user.rol != "propietario":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"No está autorizado a realizar esta acción")

    # create a new database session
    session = Session(bind=engine, expire_on_commit=False)

    # get the negocio item with the given id
    ventasdb = session.query(models.Venta.id, models.Producto.nombre,
                             models.Punto.nombre, models.Venta.cantidad,
                             models.Venta.precio, models.Venta.fecha,
                             models.User.nombre
                             )\
        .join(models.Distribucion, models.Distribucion.id == models.Venta.distribucion_id)\
        .join(models.Inventario, models.Inventario.id == models.Distribucion.inventario_id)\
        .join(models.Producto, models.Producto.id == models.Inventario.producto_id)\
        .join(models.Punto, models.Punto.id == models.Venta.punto_id)\
        .join(models.Negocio, models.Negocio.id == models.Punto.negocio_id)\
        .join(models.User, models.User.id == models.Venta.usuario_id)\
        .where(models.Negocio.propietario_id == current_user.id)\
        .order_by(models.Venta.fecha.desc())\
        .all()

    resultdb = []
    for row in ventasdb:
        resultdb.append({
            "id": row[0],
            "nombre_producto": row[1],
            "nombre_punto": row[2],
            "cantidad": row[3],
            "precio": row[4],
            "monto": row[3] * row[4],
            "fecha": row[5],
            "dependiente": row[6],
        })

    session.close()
    return resultdb


@router.get("/ventas-dia/{fecha}", tags=["ventas"])
async def read_ventas_propietario(fecha: date, token: Annotated[str, Depends(auth.oauth2_scheme)], current_user: Annotated[models.User, Depends(auth.get_current_user)]):

    # validando rol de usuario autenticado
    if current_user.rol != "propietario":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"No está autorizado a realizar esta acción")

    # create a new database session
    session = Session(bind=engine, expire_on_commit=False)

    # get the negocio item with the given id
    ventasdb = session.query(models.Producto.nombre,
                             models.Punto.nombre, db.func.sum(
                                 models.Venta.cantidad),
                             models.Venta.id)\
        .join(models.Distribucion, models.Distribucion.id == models.Venta.distribucion_id)\
        .join(models.Inventario, models.Inventario.id == models.Distribucion.inventario_id)\
        .join(models.Producto, models.Producto.id == models.Inventario.producto_id)\
        .join(models.Punto, models.Punto.id == models.Venta.punto_id)\
        .join(models.Negocio, models.Negocio.id == models.Punto.negocio_id)\
        .join(models.User, models.User.id == models.Venta.usuario_id)\
        .where(models.Negocio.propietario_id == current_user.id,
               db.func.extract("year", models.Venta.fecha) == fecha.year,
               db.func.extract("month", models.Venta.fecha) == fecha.month,
               db.func.extract("day", models.Venta.fecha) == fecha.day)\
        .group_by(models.Venta.distribucion_id)\
        .order_by(db.func.sum(models.Venta.cantidad).desc())\
        .all()

    resultdb = []
    for row in ventasdb:
        resultdb.append({
            "nombre_producto": row[0],
            "nombre_punto": row[1],
            "cantidad": row[2],
            "id": row[3]
        })

    session.close()
    return resultdb


@router.get("/ventas-periodo/{fecha_inicio}/{fecha_fin}", tags=["ventas"])
async def read_ventas_periodo(fecha_inicio: date, fecha_fin: date, token: Annotated[str, Depends(auth.oauth2_scheme)], current_user: Annotated[models.User, Depends(auth.get_current_user)]):

    # validando rol de usuario autenticado
    if current_user.rol != "propietario":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"No está autorizado a realizar esta acción")

     # validando rol de usuario autenticado
    if fecha_inicio > fecha_fin:
        raise HTTPException(status_code=status.HTTP_412_PRECONDITION_FAILED,
                            detail=f"La fecha fin debe ser mayor que la fecha inicio")

    # create a new database session
    session = Session(bind=engine, expire_on_commit=False)

    # get the negocio item with the given id
    ventasdb = session.query(models.Producto.nombre,
                             models.Punto.nombre, db.func.sum(
                                 models.Venta.cantidad),
                             models.Venta.id)\
        .join(models.Distribucion, models.Distribucion.id == models.Venta.distribucion_id)\
        .join(models.Inventario, models.Inventario.id == models.Distribucion.inventario_id)\
        .join(models.Producto, models.Producto.id == models.Inventario.producto_id)\
        .join(models.Punto, models.Punto.id == models.Venta.punto_id)\
        .join(models.Negocio, models.Negocio.id == models.Punto.negocio_id)\
        .join(models.User, models.User.id == models.Venta.usuario_id)\
        .where(models.Negocio.propietario_id == current_user.id,
               db.func.date(models.Venta.fecha) >= fecha_inicio, db.func.date(models.Venta.fecha) <= fecha_fin)\
        .group_by(models.Venta.distribucion_id)\
        .order_by(db.func.sum(models.Venta.cantidad).desc())\
        .all()

    resultdb = []
    for row in ventasdb:
        resultdb.append({
            "nombre_producto": row[0],
            "nombre_punto": row[1],
            "cantidad": row[2],
            "id": row[3]
        })

    session.close()
    return resultdb


@router.get("/ventas-utilidades-periodo/{fecha_inicio}/{fecha_fin}", tags=["ventas"])
async def read_utilidades_periodo(fecha_inicio: date, fecha_fin: date, token: Annotated[str, Depends(auth.oauth2_scheme)], current_user: Annotated[models.User, Depends(auth.get_current_user)]):

    # validando rol de usuario autenticado
    if current_user.rol != "propietario":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"No está autorizado a realizar esta acción")

     # validando rol de usuario autenticado
    if fecha_inicio > fecha_fin:
        raise HTTPException(status_code=status.HTTP_412_PRECONDITION_FAILED,
                            detail=f"La fecha fin debe ser mayor que la fecha inicio")

    # create a new database session
    session = Session(bind=engine, expire_on_commit=False)

    # get the negocio item with the given id
    ventasdb = session.query(models.Producto.nombre,
                             models.Punto.nombre, db.func.sum(models.Venta.cantidad),
                             models.Venta.id, models.Inventario.costo, 
                             db.func.sum(models.Venta.monto), models.Inventario.precio_venta)\
        .join(models.Distribucion, models.Distribucion.id == models.Venta.distribucion_id)\
        .join(models.Inventario, models.Inventario.id == models.Distribucion.inventario_id)\
        .join(models.Producto, models.Producto.id == models.Inventario.producto_id)\
        .join(models.Punto, models.Punto.id == models.Venta.punto_id)\
        .join(models.Negocio, models.Negocio.id == models.Punto.negocio_id)\
        .join(models.User, models.User.id == models.Venta.usuario_id)\
        .where(models.Negocio.propietario_id == current_user.id,
               db.func.date(models.Venta.fecha) >= fecha_inicio, db.func.date(models.Venta.fecha) <= fecha_fin)\
        .group_by(models.Venta.distribucion_id)\
        .order_by(db.func.sum(models.Venta.cantidad).desc())\
        .all()

    resultdb = []
    for row in ventasdb:
        resultdb.append({
            "id": row[3],
            "nombre_producto": row[0],
            "utilidad": row[5] - (row[4] * row[2]),
            "nombre_punto": row[1],
            "diferencia_utilidad": (row[5] - (row[4] * row[2])) - ((row[6] * row[2]) - (row[4] * row[2])),
            "cantidad": row[2],
            "precio_costo": row[4] * row[2],
            "monto": row[5],
            "precio_inventario": row[6],
            "utilidad_esperada": (row[6] * row[2]) - (row[4] * row[2]),
        })

    session.close()
    return resultdb