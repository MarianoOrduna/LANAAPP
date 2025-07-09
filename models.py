from sqlalchemy import Column, Integer, String, Date, DECIMAL, ForeignKey, Enum, Boolean, DateTime
from sqlalchemy.orm import relationship
from database import Base
import enum


class TipoNotificacion(str, enum.Enum):
    email = "email"
    sms = "sms"


class TipoTransaccion(str, enum.Enum):
    ingreso = "ingreso"
    gasto = "gasto"

class Usuario(Base):
    __tablename__ = "usuario"

    id_usuario = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nombre = Column(String(100))
    correo = Column(String(100), unique=True, index=True)
    contrasena = Column(String(255))
    fecha_registro = Column(Date)

    transacciones = relationship("Transaccion", back_populates="usuario")
    presupuestos = relationship("Presupuesto", back_populates="usuario")
    pagos = relationship("Pago", back_populates="usuario")
    pagos_fijos = relationship("PagoFijo", back_populates="usuario")
    notificaciones = relationship("Notificacion", back_populates="usuario")

class Categoria(Base):
    __tablename__ = "categoria"

    id_categoria = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nombre = Column(String(100))

    transacciones = relationship("Transaccion", back_populates="categoria")
    pagos = relationship("Pago", back_populates="categoria")
    pagos_fijos = relationship("PagoFijo", back_populates="categoria")
    gastos = relationship("Gasto", back_populates="categoria")

class Transaccion(Base):
    __tablename__ = "transacciones"

    id_transaccion = Column(Integer, primary_key=True, index=True, autoincrement=True)
    id_usuario = Column(Integer, ForeignKey("usuario.id_usuario"))
    tipo = Column(Enum(TipoTransaccion))
    descripcion = Column(String(255))
    monto = Column(DECIMAL(10, 2))
    fecha = Column(Date)
    id_categoria = Column(Integer, ForeignKey("categoria.id_categoria"))

    usuario = relationship("Usuario", back_populates="transacciones")
    categoria = relationship("Categoria", back_populates="transacciones")
    ingresos = relationship("Ingreso", back_populates="transaccion")
    gastos = relationship("Gasto", back_populates="transaccion")

class Ingreso(Base):
    __tablename__ = "ingresos"

    id_ingreso = Column(Integer, primary_key=True, index=True, autoincrement=True)
    id_transaccion = Column(Integer, ForeignKey("transacciones.id_transaccion"))
    concepto = Column(String(255))
    comprobante = Column(String(50))
    fecha = Column(Date)

    transaccion = relationship("Transaccion", back_populates="ingresos")

class Gasto(Base):
    __tablename__ = "gastos"

    id_gasto = Column(Integer, primary_key=True, index=True, autoincrement=True)
    id_transaccion = Column(Integer, ForeignKey("transacciones.id_transaccion"))
    concepto = Column(String(255))
    comprobante = Column(String(50))
    estado = Column(String(50))
    metodo_pago = Column(String(100))
    id_categoria = Column(Integer, ForeignKey("categoria.id_categoria"))

    transaccion = relationship("Transaccion", back_populates="gastos")
    categoria = relationship("Categoria", back_populates="gastos")

class Presupuesto(Base):
    __tablename__ = "presupuesto"

    id_presupuesto = Column(Integer, primary_key=True, index=True, autoincrement=True)
    id_usuario = Column(Integer, ForeignKey("usuario.id_usuario"))
    id_categoria = Column(Integer, ForeignKey("categoria.id_categoria"))
    monto = Column(DECIMAL(10, 2))
    fecha_crea = Column(Date)
    fecha_venc = Column(Date)

    usuario = relationship("Usuario", back_populates="presupuestos")
    categoria = relationship("Categoria")  


class Pago(Base):
    __tablename__ = "pagos"

    id_pago = Column(Integer, primary_key=True, index=True, autoincrement=True)
    id_usuario = Column(Integer, ForeignKey("usuario.id_usuario"))
    descripcion = Column(String(255))
    monto = Column(DECIMAL(10, 2))
    fecha_pago = Column(Date)
    metodo_pago = Column(String(100))
    categoria_id_categoria = Column(Integer, ForeignKey("categoria.id_categoria"))

    usuario = relationship("Usuario", back_populates="pagos")
    categoria = relationship("Categoria", back_populates="pagos")


class PagoFijo(Base):
    __tablename__ = "pagos_fijos"

    id_pago_fijo = Column(Integer, primary_key=True, index=True, autoincrement=True)
    id_usuario = Column(Integer, ForeignKey("usuario.id_usuario"))
    descripcion = Column(String(255))
    monto = Column(DECIMAL(10, 2))
    fecha_inicio = Column(Date)
    activo = Column(Boolean)
    categoria_id = Column("categoria_id_categoria", Integer, ForeignKey("categoria.id_categoria"))

    usuario = relationship("Usuario", back_populates="pagos_fijos")
    categoria = relationship("Categoria", back_populates="pagos_fijos")



class Notificacion(Base):
    __tablename__ = "notificaciones"

    id_notificacion = Column(Integer, primary_key=True, index=True, autoincrement=True)
    id_usuario = Column(Integer, ForeignKey("usuario.id_usuario"))
    tipo = Column(Enum(TipoNotificacion))
    mensaje = Column(String(500))
    fecha_envio = Column(DateTime)
    excede_presupuesto = Column(Boolean, default=False)

    usuario = relationship("Usuario", back_populates="notificaciones")
