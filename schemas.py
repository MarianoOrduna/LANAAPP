from pydantic import BaseModel
from typing import Optional
from datetime import date


# ---------- AUTENTICACIÓN ----------

class UserCreate(BaseModel):
    nombre: str
    correo: str
    password: str

class UserLogin(BaseModel):
    correo: str
    password: str

class UserOut(BaseModel):
    id_usuario: int
    nombre: str
    correo: str

    class Config:
        from_attributes = True


# ---------- TRANSACCIONES ----------

class TransactionCreate(BaseModel):
    tipo: str
    descripcion: str
    monto: float
    fecha: date
    id_categoria: int

class TransactionOut(TransactionCreate):
    id_transaccion: int

    class Config:
        from_attributes = True


# ---------- PRESUPUESTOS ----------

class BudgetCreate(BaseModel):
    monto: float
    fecha_crea: date
    fecha_venc: date
    id_categoria: int

class BudgetOut(BudgetCreate):
    id_presupuesto: int
    id_usuario: int  

    class Config:
        from_attributes = True


# ---------- PAGOS FIJOS ----------

class FixedPaymentCreate(BaseModel):
    descripcion: str
    monto: float
    fecha_inicio: date
    activo: bool
    categoria_id_categoria: int  

class FixedPaymentOut(BaseModel):
    id_pago_fijo: int
    descripcion: str
    monto: float
    fecha_inicio: date
    activo: bool
    categoria_id: int  

    class Config:
        from_attributes = True


# ---------- PAGOS ----------

class PagoCreate(BaseModel):
    descripcion: str
    monto: float
    fecha_pago: date
    metodo_pago: Optional[str] = None
    categoria_id_categoria: Optional[int] = None

class PagoOut(PagoCreate):
    id_pago: int
    id_usuario: int

    class Config:
        from_attributes = True
