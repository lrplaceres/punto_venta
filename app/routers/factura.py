import json
from fastapi import APIRouter, status, HTTPException, Depends
from typing import List, Annotated
from sqlalchemy.orm import Session
from app.schemas.detallesPago import detallesPago
from app.schemas.pedido import Pedido
from ..database.database import Base, engine
from ..models import models
from ..auth import auth
from ..log import log
from datetime import date


# Create the database
Base.metadata.create_all(engine)

router = APIRouter()

@router.post("/factura", status_code=status.HTTP_201_CREATED, tags=["factura"])
async def create_factura(carrito: List[Pedido], detallesPago:detallesPago, totalPedido:float, token: Annotated[str, Depends(auth.oauth2_scheme)], current_user: Annotated[models.User, Depends(auth.get_current_user)]):
    
    # validando rol de usuario autenticado
    if current_user.rol != "propietario" and current_user.rol != "dependiente":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"No está autorizado a realizar esta acción")
    
    session = Session(bind=engine, expire_on_commit=False)
    ventas = []
     
    for row in carrito:
        # create an instance of the venta database model
        ventadb = models.Venta(distribucion_id=row.distribucion_id, cantidad=row.cantidad,
                            precio=row.precio, fecha=detallesPago.fecha, punto_id=row.punto_id,
                            usuario_id=current_user.id, monto=row.cantidad * row.precio,
                            pago_diferido = False, descripcion = None,
                            pago_electronico = detallesPago.pago_electronico, no_operacion = detallesPago.no_operacion)
        
        # add it to the session and commit it
        session.add(ventadb)
        session.commit()
        session.refresh(ventadb)

        ventas.append({
            "producto": row.nombre_producto,
            "cantidad": row.cantidad,
            "precio": row.precio,
            "monto": row.precio * row.cantidad,
            "punto": row.nombre_punto,
            'id': ventadb.id
        })

        log.create_log({
            "usuario": current_user.usuario,
            "accion": "CREATE",
            "tabla": "Venta",
            "descripcion": f"Ha creado el id {ventadb.id}"
        })

   
    facturadb = models.Factura(monto = totalPedido, ventas = json.dumps(ventas), fecha = detallesPago.fecha,
                               pago_electronico = detallesPago.pago_electronico, no_operacion = detallesPago.no_operacion,
                               punto_id= detallesPago.punto_id)
    
    session.add(facturadb)
    session.commit()
    session.refresh(facturadb)

    
    # close the session
    session.close()

    # return the venta object
    return facturadb


@router.get("/factura/{id}", tags=["factura"], description="Obtener factura")
async def read_venta(id: int, token: Annotated[str, Depends(auth.oauth2_scheme)], current_user: Annotated[models.User, Depends(auth.get_current_user)]):

    # validando rol de usuario autenticado
    if current_user.rol != "propietario" and current_user.rol != "dependiente":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"No está autorizado a realizar esta acción")

    # create a new database session
    session = Session(bind=engine, expire_on_commit=False)
    
    # get the venta item with the given id
     # get the negocio item with the given id
    facturadb = session.query(models.Factura.id, models.Factura.monto, models.Factura.pago_electronico,
                            models.Factura.no_operacion, models.Punto.nombre, models.Factura.ventas, models.Factura.fecha)\
        .join(models.Punto, models.Punto.id == models.Factura.punto_id)\
        .join(models.Negocio, models.Negocio.id == models.Punto.negocio_id)\
        .where(models.Negocio.propietario_id == current_user.id, models.Factura.id == id)\
        .first()

    session.close()

    # close the session
    session.close()

    if not facturadb:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Factura con id {id} no encontrada")
         
    resultdb: dict = {
        "id": facturadb[0],
        "monto": facturadb[1],
        "pago_electronico": facturadb[2],
        "no_operacion": facturadb[3],
        "nombre_punto": facturadb[4],
        "ventas": facturadb[5],
        "fecha": facturadb[6],
    }
    return resultdb


@router.get("/facturas", tags=["facturas"], description="Listado de facturas de un propietario")
async def read_facturas_propietario(token: Annotated[str, Depends(auth.oauth2_scheme)], current_user: Annotated[models.User, Depends(auth.get_current_user)]):

    # validando rol de usuario autenticado
    if current_user.rol != "propietario":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"No está autorizado a realizar esta acción")

    # create a new database session
    session = Session(bind=engine, expire_on_commit=False)

    # get the negocio item with the given id
    facturasdb = session.query(models.Factura.id, models.Factura.monto, models.Factura.pago_electronico,
                            models.Factura.no_operacion, models.Punto.nombre, models.Factura.fecha)\
        .join(models.Punto, models.Punto.id == models.Factura.punto_id)\
        .join(models.Negocio, models.Negocio.id == models.Punto.negocio_id)\
        .where(models.Negocio.propietario_id == current_user.id)\
        .order_by(models.Factura.fecha.desc())\
        .all()

    session.close()

    resultdb = []

    for row in facturasdb:
        resultdb.append({
            "id": row[0],
            "monto": row[1],
            "pago_electronico": row[2],
            "no_operacion": row[3],
            "nombre_punto": row[4],
            "fecha": row[5],
        })
     
    return resultdb


@router.delete("/factura/{id}", status_code=status.HTTP_204_NO_CONTENT, tags=["factura"], description="Eliminar factura")
async def delete_venta(id: int, token: Annotated[str, Depends(auth.oauth2_scheme)], current_user: Annotated[models.User, Depends(auth.get_current_user)]):

    # validando rol de usuario autenticado
    if current_user.rol != "propietario" and current_user.rol != "dependiente":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"No está autorizado a realizar esta acción")

    # create a new database session
    session = Session(bind=engine, expire_on_commit=False)

    # get the factura item with the given id
    #ventadb = session.query(models.Venta).get(id)

    if current_user.rol == "propietario":
        # get the venta item with the given id
        facturadb = session.query(models.Factura)\
            .join(models.Punto, models.Punto.id == models.Factura.punto_id)\
            .join(models.Negocio, models.Negocio.id == models.Punto.negocio_id)\
            .where(models.Factura.id == id, models.Negocio.propietario_id == current_user.id, models.Negocio.fecha_licencia >= date.today())\
            .first()

    if current_user.rol == "dependiente":
        facturadb = session.query(models.Factura)\
            .join(models.Negocio, models.Negocio.id == models.Punto.negocio_id)\
            .where(models.Factura.id == id, models.Punto.id == current_user.punto_id, models.Venta.usuario_id == current_user.id,
                    models.Negocio.fecha_licencia >= date.today())\
            .first()

    # if todo item with given id exists, delete it from the database. Otherwise raise 404 error
    if facturadb:

        res = json.loads(facturadb.ventas)
        
        for row in res:
            ventadb =  session.query(models.Venta).get(row.get("id"))
            session.delete(ventadb)
            session.commit()


        session.delete(facturadb)
        session.commit()
        session.close()

        log.create_log({
            "usuario": current_user.usuario,
            "accion": "DELETE",
            "tabla": "Factura",
            "descripcion": f"Ha eliminado el id {facturadb.id}"
        })
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Venta con id {id} no encontrado")

    return None