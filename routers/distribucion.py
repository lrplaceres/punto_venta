from fastapi import APIRouter, status, HTTPException, Depends
from typing import List, Annotated
from sqlalchemy.orm import Session
import sqlalchemy as db
from database.database import Base, engine
import schemas.distribucion
import models.models as models
import auth.auth as auth

# Create the database
Base.metadata.create_all(engine)

router = APIRouter()


@router.post("/distribucion", response_model=schemas.distribucion.Distribucion, status_code=status.HTTP_201_CREATED, tags=["distribucion"])
async def create_distribucion(distribucion: schemas.distribucion.DistribucionCreate, token: Annotated[str, Depends(auth.oauth2_scheme)], current_user: Annotated[models.User, Depends(auth.get_current_user)]):

    # validando rol de usuario autenticado
    if current_user.rol != "propietario":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"No está autorizado a realizar esta acción")

    # create a new database session
    session = Session(bind=engine, expire_on_commit=False)

    # verificar si usuario autenticado es propietario del negocio buscando por punto
    prop_negocio = session.query(models.Punto)\
        .join(models.Negocio)\
        .where(models.Punto.id == distribucion.punto_id,
               models.Negocio.propietario_id == current_user.id)\
        .count()

    print(prop_negocio)
    # verificar si usuario autenticado es propietario del inventario
    prop_inventario = session.query(models.Inventario)\
        .join(models.Negocio)\
        .where(models.Inventario.id == distribucion.inventario_id,
               models.Negocio.propietario_id == current_user.id)\
        .count()

    if not prop_negocio or not prop_inventario:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"No está autorizado a realizar esta acción")

    # create an instance of the distribucion database model
    distribuciondb = models.Distribucion(inventario_id=distribucion.inventario_id,
                                         cantidad=distribucion.cantidad, fecha=distribucion.fecha,
                                         punto_id=distribucion.punto_id)

    # add it to the session and commit it
    session.add(distribuciondb)
    session.commit()
    session.refresh(distribuciondb)

    # close the session
    session.close()

    # return the distribucion object
    return distribuciondb


@router.get("/distribucion/{id}", tags=["distribucion"])
async def read_distribucion(id: int, token: Annotated[str, Depends(auth.oauth2_scheme)], current_user: Annotated[models.User, Depends(auth.get_current_user)]):

    # validando rol de usuario autenticado
    if current_user.rol != "propietario":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"No está autorizado a realizar esta acción")

    # create a new database session
    session = Session(bind=engine, expire_on_commit=False)

    # get the kiosko item with the given id
    distribuciondb: schemas.distribucion.Distribucion = session.query(
        models.Distribucion.id, models.Distribucion.cantidad, models.Distribucion.fecha,
        models.Distribucion.inventario_id, models.Distribucion.punto_id,
        models.Inventario.negocio_id, models.Inventario.cantidad)\
        .join(models.Inventario)\
        .where(models.Distribucion.id == id)\
        .first()

    cantidad_distribuida = session.query(db.func.sum(models.Distribucion.cantidad).label("cantidad_distribuida"))\
        .where(models.Distribucion.inventario_id == distribuciondb[3])\
        .group_by(models.Distribucion.inventario_id)\
        .first()
 
    resultdb: dict = {
        "id": distribuciondb[0],
        "cantidad": distribuciondb[1],
        "fecha": distribuciondb[2],
        "inventario_id": distribuciondb[3],
        "punto_id": distribuciondb[4],
        "negocio_id": distribuciondb[5],
        "cantidad_inventario": distribuciondb[6],
        "cantidad_distribuida": cantidad_distribuida.cantidad_distribuida,
    }

    # verificar si usuario autenticado es propietario del negocio
    if distribuciondb:
        # verificar si usuario autenticado es propietario del negocio buscando por punto
        prop_negocio = session.query(models.Punto)\
            .join(models.Negocio)\
            .where(models.Punto.id == resultdb.get("punto_id"),
                   models.Negocio.propietario_id == current_user.id)\
            .count()

        # verificar si usuario autenticado es propietario del inventario
        prop_inventario = session.query(models.Inventario)\
            .join(models.Negocio)\
            .where(models.Inventario.id == resultdb.get("inventario_id"),
                   models.Negocio.propietario_id == current_user.id)\
            .count()

        if not prop_negocio or not prop_inventario:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail=f"No está autorizado a realizar esta acción")

    # close the session
    session.close()

    if not distribuciondb:
        raise HTTPException(
            status_code=404, detail=f"Distribución con id {id} no encontrada")

    return resultdb


@router.put("/distribucion/{id}", tags=["distribucion"])
async def update_distribucion(id: int, distribucion: schemas.distribucion.DistribucionCreate, token: Annotated[str, Depends(auth.oauth2_scheme)], current_user: Annotated[models.User, Depends(auth.get_current_user)]):

    # validando rol de usuario autenticado
    if current_user.rol != "propietario":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"No está autorizado a realizar esta acción")

    # create a new database session
    session = Session(bind=engine, expire_on_commit=False)

    # get the producto item with the given id
    distribuciondb: schemas.distribucion.Distribucion = session.query(
        models.Distribucion).get(id)

    # verificar si usuario autenticado es propietario del negocio
    if distribuciondb:
        # verificar si usuario autenticado es propietario del negocio buscando por punto
        prop_negocio = session.query(models.Punto)\
            .join(models.Negocio)\
            .where(models.Punto.id == distribucion.punto_id,
                   models.Negocio.propietario_id == current_user.id)\
            .count()

        # verificar si usuario autenticado es propietario del inventario
        prop_inventario = session.query(models.Inventario)\
            .join(models.Negocio)\
            .where(models.Inventario.id == distribucion.inventario_id,
                   models.Negocio.propietario_id == current_user.id)\
            .count()

        if not prop_negocio or not prop_inventario:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail=f"No está autorizado a realizar esta acción")

    # update distribucion item with the given task (if an item with the given id was found)
    if distribuciondb:
        distribuciondb.inventario_id = distribucion.inventario_id
        distribuciondb.cantidad = distribucion.cantidad
        distribuciondb.fecha = distribucion.fecha
        distribuciondb.punto_id = distribucion.punto_id
        session.commit()

    # close the session
    session.close()


@router.delete("/distribucion/{id}", status_code=status.HTTP_204_NO_CONTENT, tags=["distribucion"])
async def delete_distribucion(id: int, token: Annotated[str, Depends(auth.oauth2_scheme)], current_user: Annotated[models.User, Depends(auth.get_current_user)]):

    # validando rol de usuario autenticado
    if current_user.rol != "propietario":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"No está autorizado a realizar esta acción")

    # create a new database session
    session = Session(bind=engine, expire_on_commit=False)

    # get the distribucion item with the given id
    distribuciondb: schemas.inventario.Inventario = session.query(
        models.Distribucion).get(id)

    # verificar si usuario autenticado es propietario del negocio
    if distribuciondb:
        # verificar si usuario autenticado es propietario del negocio buscando por punto
        prop_negocio = session.query(models.Punto)\
            .join(models.Negocio)\
            .where(models.Punto.id == distribuciondb.punto_id,
                   models.Negocio.propietario_id == current_user.id)\
            .count()

        # verificar si usuario autenticado es propietario del inventario
        prop_inventario = session.query(models.Inventario)\
            .join(models.Negocio)\
            .where(models.Inventario.id == distribuciondb.inventario_id,
                   models.Negocio.propietario_id == current_user.id)\
            .count()

        if not prop_negocio or not prop_inventario:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail=f"No está autorizado a realizar esta acción")

    # if distribucion item with given id exists, delete it from the database. Otherwise raise 404 error
    if distribuciondb:
        session.delete(distribuciondb)
        session.commit()
        session.close()
    else:
        raise HTTPException(
            status_code=404, detail=f"Distribución con id {id} no encontrado")

    return None


@router.get("/distribuciones/", tags=["distribuciones"])
async def read_distribuciones_propietario(token: Annotated[str, Depends(auth.oauth2_scheme)], current_user: Annotated[models.User, Depends(auth.get_current_user)]):

    # validando rol de usuario autenticado
    if current_user.rol != "propietario":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"No está autorizado a realizar esta acción")

    # create a new database session
    session = Session(bind=engine, expire_on_commit=False)

    # get the distribuciones item with the given id
    distribucionesdb = session.query(models.Distribucion.id, models.Distribucion.cantidad,
                                     models.Distribucion.fecha, models.Punto.nombre,
                                     models.Negocio.nombre, models.Producto.nombre,
                                     models.Inventario.costo)\
        .select_from(models.Distribucion)\
        .join(models.Punto, models.Punto.id == models.Distribucion.punto_id)\
        .join(models.Negocio, models.Negocio.id == models.Punto.negocio_id)\
        .join(models.User, models.User.id == models.Negocio.propietario_id)\
        .join(models.Inventario, models.Inventario.id == models.Distribucion.inventario_id)\
        .join(models.Producto, models.Producto.id == models.Inventario.producto_id)\
        .where(models.User.usuario == current_user.usuario)\
        .all()

    resultdb = []
    for row in distribucionesdb:
        resultdb.append({
            "id": row[0],
            "cantidad": row[1],
            "fecha": row[2],
            "punto_id": row[3],
            "negocio_id": row[4],
            "producto_id": row[5],
            "costo": row[6],
        })

    session.close()
    return resultdb
