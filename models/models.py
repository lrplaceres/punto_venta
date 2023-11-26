from sqlalchemy import Column, Integer, String, ForeignKey, Float, Boolean, Date, UniqueConstraint
from database.database import Base
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Mapped
from datetime import date, datetime

class Negocio(Base):
    __tablename__ = 'negocio'
    id: Mapped[int] = Column(Integer, primary_key=True)
    nombre: Mapped[str] = Column(String(256))
    direccion: Mapped[str] = Column(String(256))
    informacion: Mapped[str] = Column(String(256))
    fecha_licencia: Mapped[datetime] = Column(Date)
    activo: Mapped[bool] = Column(Boolean, default=True)
    propietario_id: Mapped[int]= Column(Integer, ForeignKey("user.id"))

    propietarios: Mapped[int] = relationship("User", back_populates = "negocios")
    puntos: Mapped[int] = relationship("Punto", back_populates = "negocios", cascade="all, delete-orphan")
    productos: Mapped[int] = relationship("Producto", back_populates="negocios", cascade="all, delete-orphan")
    inventarios: Mapped[int] = relationship("Inventario", back_populates = "negocios", cascade="all, delete-orphan")

class Punto(Base):
    __tablename__ = 'punto'
    id: Mapped[int] = Column(Integer, primary_key=True)
    nombre: Mapped[str] = Column(String(256))
    direccion: Mapped[str] = Column(String(256))
    negocio_id:Mapped[int] = Column(Integer, ForeignKey("negocio.id"))

    negocios: Mapped[int] = relationship("Negocio", back_populates = "puntos")
    distribuciones: Mapped[int] = relationship("Distribucion", back_populates = "puntos", cascade="all, delete-orphan")


class Producto(Base):
    __tablename__ = 'producto'
    id: Mapped[int] = Column(Integer, primary_key=True)
    nombre: Mapped[str] = Column(String(256))
    negocio_id: Mapped[int] = Column(Integer, ForeignKey("negocio.id"))

    negocios: Mapped[int] = relationship("Negocio", back_populates = "productos")
    inventarios: Mapped[int] = relationship("Inventario", back_populates = "productos", cascade="all, delete-orphan")


class Inventario(Base):
    __tablename__ = 'inventario'
    id: Mapped[int] = Column(Integer, primary_key=True)
    producto_id: Mapped[str] = Column(Integer, ForeignKey("producto.id"))
    cantidad: Mapped[float] = Column(Float(2))
    um: Mapped[str] = Column(String(256))
    costo: Mapped[float] = Column(Float(2))
    precio_venta: Mapped[float] = Column(Float(2))
    fecha: Mapped[datetime] = Column(Date)
    negocio_id: Mapped[int] = Column(Integer, ForeignKey("negocio.id"))

    productos: Mapped[int] = relationship("Producto", back_populates = "inventarios")
    negocios: Mapped[int] = relationship("Negocio", back_populates = "inventarios")
    distribuciones: Mapped[int] = relationship("Distribucion", back_populates = "inventarios", cascade="all, delete-orphan")


class Distribucion(Base):
    __tablename__ = 'distribucion'
    id: Mapped[int] = Column(Integer, primary_key=True)
    inventario_id: Mapped[str] = Column(Integer, ForeignKey("inventario.id"))
    cantidad: Mapped[float] = Column(Float(2))
    fecha: Mapped[datetime] = Column(Date)
    punto_id: Mapped[str] = Column(Integer, ForeignKey("punto.id"))

    inventarios: Mapped[int] = relationship("Inventario", back_populates = "distribuciones")
    puntos: Mapped[int] = relationship("Punto", back_populates = "distribuciones")


class User(Base):
    __tablename__ = 'user'
    id: Mapped[int] = Column(Integer, primary_key=True)
    usuario: Mapped[str] = Column(String(256), unique=True)
    nombre: Mapped[str] = Column(String(256))
    email: Mapped[str] = Column(String(256))
    rol: Mapped[str] = Column(String(256))
    activo: Mapped[bool] = Column(Boolean)
    password: Mapped[str] = Column(String(256))

    negocios: Mapped[int|None] = relationship("Negocio", back_populates = "propietarios")