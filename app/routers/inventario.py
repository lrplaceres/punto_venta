from uuid import uuid3, uuid4
from fastapi import APIRouter, status, HTTPException, Depends
from typing import List, Annotated
from sqlalchemy.orm import Session
import sqlalchemy as db
from ..database.database import Base, engine
from ..schemas import inventario
from ..models import models
from datetime import date
from ..auth import auth
from ..log import log

# Create the database
Base.metadata.create_all(engine)

router = APIRouter()


@router.post("/inventario", response_model=inventario.Inventario, status_code=status.HTTP_201_CREATED, tags=["inventario"])
async def create_inventario(inventario: inventario.InventarioCreate, token: Annotated[str, Depends(auth.oauth2_scheme)], current_user: Annotated[models.User, Depends(auth.get_current_user)]):

    # validando rol de usuario autenticado
    if current_user.rol != "propietario":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"No está autorizado a realizar esta acción")

    # create a new database session
    session = Session(bind=engine, expire_on_commit=False)

    # verificar si usuario autenticado es propietario del negocio
    prop_negocio = session.query(models.Negocio)\
        .where(models.Negocio.id == inventario.negocio_id,
               models.Negocio.propietario_id == current_user.id, models.Negocio.fecha_licencia >= date.today())\
        .count()

    # verificar si usuario autenticado es propietario del producto
    prop_producto = session.query(models.Producto)\
        .join(models.Negocio)\
        .where(models.Negocio.id == inventario.negocio_id,
               models.Producto.id == inventario.producto_id,  models.Negocio.fecha_licencia >= date.today())\
        .count()

    if not prop_producto or not prop_negocio:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"No está autorizado a realizar esta acción")

    # create an instance of the Inventario database model
    inventariodb = models.Inventario(producto_id=inventario.producto_id, cantidad=inventario.cantidad,
                                     um=inventario.um, costo=inventario.costo, precio_venta=inventario.precio_venta,
                                     fecha=inventario.fecha, negocio_id=inventario.negocio_id, monto = inventario.costo * inventario.cantidad)

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


@router.get("/inventario/{id}", response_model=inventario.Inventario, tags=["inventario"])
async def read_inventario(id: int, token: Annotated[str, Depends(auth.oauth2_scheme)], current_user: Annotated[models.User, Depends(auth.get_current_user)]):

    # validando rol de usuario autenticado
    if current_user.rol != "propietario":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"No está autorizado a realizar esta acción")

    # create a new database session
    session = Session(bind=engine, expire_on_commit=False)

    # get the inventario item with the given id
    inventariodb: inventario.Inventario = session.query(
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
async def update_inventario(id: int, inventario: inventario.Inventario, token: Annotated[str, Depends(auth.oauth2_scheme)], current_user: Annotated[models.User, Depends(auth.get_current_user)]):

    # validando rol de usuario autenticado
    if current_user.rol != "propietario":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"No está autorizado a realizar esta acción")

    # create a new database session
    session = Session(bind=engine, expire_on_commit=False)

    # get the producto item with the given id
    inventariodb: inventario.Inventario = session.query(
        models.Inventario).get(id)

    # verificar si usuario autenticado es propietario del negocio
    if inventariodb:
        prop_negocio = session.query(models.Negocio)\
            .where(models.Negocio.id == inventario.negocio_id,
                   models.Negocio.propietario_id == current_user.id, models.Negocio.fecha_licencia >= date.today())\
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
        inventariodb.monto = inventario.costo * inventario.cantidad
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
    inventariodb: inventario.Inventario = session.query(
        models.Inventario).get(id)

    # verificar si usuario autenticado es propietario del negocio
    if inventariodb:
        prop_negocio = session.query(models.Negocio)\
            .where(models.Negocio.id == inventariodb.negocio_id, models.Negocio.propietario_id == current_user.id, models.Negocio.fecha_licencia >= date.today())\
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


@router.get("/inventarios/", tags=["inventarios"], description="Productos en inventario por propietario")
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
        .where(models.User.usuario.like(current_user.usuario))\
        .order_by(models.Inventario.fecha.desc(), models.Producto.nombre)\
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


@router.get("/inventarios-a-distribuir/", tags=["inventarios"], description="Productos en Inventario no distribuidos")
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
                                  models.Inventario.cantidad,
                                  models.Inventario.fecha,
                                  models.Inventario.costo,
                                  db.func.sum(db.func.coalesce((models.Distribucion.cantidad), 0)),
                                  models.Inventario.negocio_id, models.Negocio.nombre)\
        .select_from(models.Inventario)\
        .join(models.Producto, models.Producto.id == models.Inventario.producto_id)\
        .join(models.Negocio, models.Negocio.id == models.Inventario.negocio_id)\
        .join(models.User, models.User.id == models.Negocio.propietario_id)\
        .outerjoin(models.Distribucion, models.Distribucion.inventario_id == models.Inventario.id)\
        .where(models.User.usuario.like(current_user.usuario))\
        .group_by(models.Inventario.producto_id, models.Inventario.costo, models.Inventario.id, models.Producto.nombre, models.Negocio.nombre)\
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
                "existencia": row[2] - row[5],
                "nombre_negocio": row[7],
            })

    session.close()

    if not inventariosdb:
        raise HTTPException(
            status_code=404, detail=f"Inventarios no encontrados")

    return resultdb


@router.get("/inventarios-almacen/", tags=["inventarios"], description="Productos en Inventario no distribuidos")
async def cantidad_distribuida_inventario(token: Annotated[str, Depends(auth.oauth2_scheme)], current_user: Annotated[models.User, Depends(auth.get_current_user)]):

    # validando rol de usuario autenticado
    if current_user.rol != "propietario":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"No está autorizado a realizar esta acción")

    # create a new database session
    session = Session(bind=engine, expire_on_commit=False)

    # get the inventario item with the given id
    inventariosdb = session.query(models.Producto.nombre,
                                  db.func.sum(db.func.coalesce((models.Inventario.cantidad), 0)),
                                  models.Inventario.costo,
                                  db.func.sum(db.func.coalesce((models.Distribucion.cantidad), 0)),
                                  models.Inventario.negocio_id,
                                  models.Negocio.nombre)\
        .select_from(models.Inventario)\
        .join(models.Producto, models.Producto.id == models.Inventario.producto_id)\
        .join(models.Negocio, models.Negocio.id == models.Inventario.negocio_id)\
        .outerjoin(models.Distribucion, models.Distribucion.inventario_id == models.Inventario.id)\
        .where(models.Negocio.propietario_id == current_user.id)\
        .group_by(models.Inventario.producto_id, models.Inventario.costo, models.Producto.nombre,
                  models.Negocio.nombre, models.Inventario.negocio_id)\
        .order_by(models.Producto.nombre)\
        .all()

    resultdb = []
    for row in inventariosdb:
        if row[1] - row[3]:
            resultdb.append({
                "id": uuid4(),
                "nombre": row[0],
                "cantidad": row[1],
                "costo": row[2],
                "distribuido": row[3],
                "negocio_id": row[4],
                "existencia": row[1] - row[3],
                "nombre_negocio": row[5],
            })

    session.close()

    if not inventariosdb:
        raise HTTPException(
            status_code=404, detail=f"Inventarios no encontrados")

    return resultdb


@router.get("/inventarios-costos-brutos/{fecha_inicio}/{fecha_fin}/{negocio}", tags=["inventarios"], description="Monto propietario")
async def read_inventarios_propietario(fecha_inicio: date, fecha_fin: date, negocio: int, token: Annotated[str, Depends(auth.oauth2_scheme)], current_user: Annotated[models.User, Depends(auth.get_current_user)]):

    # validando rol de usuario autenticado
    if current_user.rol != "propietario":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"No está autorizado a realizar esta acción")
                            
    # validando rango de fecha
    if fecha_inicio > fecha_fin:
        raise HTTPException(status_code=status.HTTP_412_PRECONDITION_FAILED,
                            detail=f"La fecha fin debe ser mayor que la fecha inicio")

    # create a new database session
    session = Session(bind=engine, expire_on_commit=False)

    # get the negocio item with the given id
    puntosdb = session.query(db.func.sum(models.Inventario.monto),
                            db.extract("year", models.Inventario.fecha), db.extract("month", models.Inventario.fecha),
                            db.extract("day", models.Inventario.fecha))\
        .join(models.Negocio)\
        .join(models.User)\
        .join(models.Producto, models.Inventario.producto_id == models.Producto.id)\
        .where(models.User.usuario.like(current_user.usuario),
                db.func.date(models.Inventario.fecha) >= fecha_inicio, db.func.date(models.Inventario.fecha) <= fecha_fin,
                models.Negocio.id == negocio)\
        .group_by(db.extract("year", models.Inventario.fecha), db.extract("month", models.Inventario.fecha), db.extract("day", models.Inventario.fecha))\
        .order_by(db.extract("year", models.Inventario.fecha), db.extract("month", models.Inventario.fecha), db.extract("day", models.Inventario.fecha).desc())\
        .all()

    resultdb = []
    for row in puntosdb:
        resultdb.append({
            "monto": row[0],
            "fecha": f"{row[1]}-{row[2]}-{row[3]}",
            "id": f"id{row[1]}-{row[2]}-{row[3]}",
        })

    session.close()
    return resultdb


@router.get("/inventarios-contador/{fecha_inicio}/{fecha_fin}", tags=["admin"], description="Contador de inventarios")
async def read_count_inventarios(fecha_inicio: date, fecha_fin: date, token: Annotated[str, Depends(auth.oauth2_scheme)], current_user: Annotated[models.User, Depends(auth.get_current_user)]):

    #validando rol de usuario autenticado
    if current_user.rol != "superadmin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"No está autorizado a realizar esta acción")

    # create a new database session
    session = Session(bind=engine, expire_on_commit=False)

    # get the inventarios item with the given id
    contadorInventarios = session.query(models.Inventario).count()

    contadorInventariosFecha = session.query(models.Inventario)\
                                .where(models.Inventario.fecha_creado >= fecha_inicio, models.Inventario.fecha_creado <= fecha_fin)\
                                .count()

    # close the session
    session.close()
    
    return {"cantidad_inventarios": contadorInventarios, "nuevos_inventarios":contadorInventariosFecha }


@router.get("/inventarios-tarjeta/{fecha_inicio}/{fecha_fin}/{id}", tags=["inventarios"], description="Productos en inventario por propietario")
async def read_inventarios_propietario(fecha_inicio: date, fecha_fin: date, id: int, token: Annotated[str, Depends(auth.oauth2_scheme)], current_user: Annotated[models.User, Depends(auth.get_current_user)]):

    # validando rol de usuario autenticado
    if current_user.rol != "propietario":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"No está autorizado a realizar esta acción")

    # create a new database session
    session = Session(bind=engine, expire_on_commit=False)

    # get the negocio item with the given id
    inventariodb = session.query(models.Inventario.id, models.Producto.nombre,
                             models.Inventario.cantidad, models.Negocio.nombre,
                             models.Inventario.costo, models.Inventario.fecha, 
                             models.Inventario.precio_venta)\
        .select_from(models.Inventario)\
        .join(models.Negocio)\
        .join(models.Producto, models.Inventario.producto_id == models.Producto.id)\
        .where(models.Negocio.propietario_id == current_user.id, models.Inventario.fecha >= fecha_inicio,
                models.Inventario.fecha <= fecha_fin, models.Producto.id == id)\
        .order_by(models.Inventario.fecha.desc(), models.Producto.nombre)\
        .all()

    resultdb = []
    for row in inventariodb:
        resultdb.append({
            "id": row[0],
            "nombre": row[1],
            "cantidad": row[2],
            "negocio_id": row[3],
            "costo": row[4],
            "fecha": row[5],
            "precio_venta": row[6],
            "accion": "Entrada",
        })

    distribucionesdb = session.query(models.Inventario.id, models.Producto.nombre,
                             models.Distribucion.cantidad, models.Negocio.nombre,
                             models.Inventario.costo, models.Inventario.fecha, 
                             models.Inventario.precio_venta)\
        .select_from(models.Distribucion)\
        .join(models.Punto, models.Punto.id == models.Distribucion.punto_id)\
        .join(models.Negocio, models.Negocio.id == models.Punto.negocio_id)\
        .join(models.Inventario, models.Inventario.id == models.Distribucion.inventario_id)\
        .join(models.Producto, models.Producto.id == models.Inventario.producto_id)\
        .where(models.Negocio.propietario_id == current_user.id, models.Distribucion.fecha >= fecha_inicio,
                models.Distribucion.fecha <= fecha_fin, models.Producto.id == id)\
        .order_by(models.Distribucion.fecha.desc(), models.Producto.nombre)\
        .all()
    
    for row in distribucionesdb:
        resultdb.append({
            "id": uuid4(),
            "nombre": row[1],
            "cantidad": row[2],
            "negocio_id": row[3],
            "costo": row[4],
            "fecha": row[5],
            "precio_venta": row[6],
            "accion": "Salida",
        })

    resultdb.sort(key=lambda result : result['fecha'], reverse=True)

    session.close()
    return resultdb