from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
import models
from schemas import (
    UserCreate, UserLogin, UserOut,
    TransactionCreate, TransactionOut,
    BudgetCreate, BudgetOut,
    FixedPaymentCreate, FixedPaymentOut
)
from auth import hash_password, verify_password, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES, SECRET_KEY, ALGORITHM
from datetime import timedelta
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from typing import List

app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


from fastapi.openapi.utils import get_openapi

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="API de Finanzas Personales",
        version="1.0.0",
        description="Documentación de API con JWT",
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT"
        }
    }
    for path in openapi_schema["paths"].values():
        for operation in path.values():
            operation["security"] = [{"BearerAuth": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi



def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Token inválido")
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido")
    
    user = db.query(models.Usuario).filter(models.Usuario.id_usuario == int(user_id)).first()
    if user is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return user



@app.post("/register", response_model=UserOut)
def register(user: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(models.Usuario).filter(models.Usuario.correo == user.correo).first()
    if existing:
        raise HTTPException(status_code=400, detail="Correo ya registrado")
    hashed = hash_password(user.password)
    nuevo_usuario = models.Usuario(nombre=user.nombre, correo=user.correo, contrasena=hashed)
    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)
    return nuevo_usuario



@app.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(models.Usuario).filter(models.Usuario.correo == user.correo).first()
    if not db_user or not verify_password(user.password, db_user.contrasena):
        raise HTTPException(status_code=400, detail="Credenciales inválidas")
    token = create_access_token(
        data={"sub": str(db_user.id_usuario)},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {"access_token": token, "token_type": "bearer"}



@app.post("/transacciones", response_model=TransactionOut)
def crear_transaccion(t: TransactionCreate, db: Session = Depends(get_db), current_user: models.Usuario = Depends(get_current_user)):
    transaccion = models.Transaccion(
        tipo=t.tipo,
        descripcion=t.descripcion,
        monto=t.monto,
        fecha=t.fecha,
        id_categoria=t.id_categoria,
        id_usuario=current_user.id_usuario
    )
    db.add(transaccion)
    db.commit()
    db.refresh(transaccion)
    return transaccion

@app.get("/transacciones", response_model=List[TransactionOut])
def obtener_transacciones(db: Session = Depends(get_db), current_user: models.Usuario = Depends(get_current_user)):
    return db.query(models.Transaccion).filter(models.Transaccion.id_usuario == current_user.id_usuario).all()

@app.get("/transacciones/{id}", response_model=TransactionOut)
def obtener_transaccion(id: int, db: Session = Depends(get_db), current_user: models.Usuario = Depends(get_current_user)):
    t = db.query(models.Transaccion).filter(models.Transaccion.id_transaccion == id, models.Transaccion.id_usuario == current_user.id_usuario).first()
    if not t:
        raise HTTPException(status_code=404, detail="No encontrada")
    return t

@app.put("/transacciones/{id}", response_model=TransactionOut)
def actualizar_transaccion(id: int, trans: TransactionCreate, db: Session = Depends(get_db), current_user: models.Usuario = Depends(get_current_user)):
    t = db.query(models.Transaccion).filter(models.Transaccion.id_transaccion == id, models.Transaccion.id_usuario == current_user.id_usuario).first()
    if not t:
        raise HTTPException(status_code=404, detail="No encontrada")
    for attr, value in trans.dict().items():
        setattr(t, attr, value)
    db.commit()
    db.refresh(t)
    return t

@app.delete("/transacciones/{id}")
def eliminar_transaccion(id: int, db: Session = Depends(get_db), current_user: models.Usuario = Depends(get_current_user)):
    t = db.query(models.Transaccion).filter(models.Transaccion.id_transaccion == id, models.Transaccion.id_usuario == current_user.id_usuario).first()
    if not t:
        raise HTTPException(status_code=404, detail="No encontrada")
    db.delete(t)
    db.commit()
    return {"detail": "Eliminada"}



@app.get("/resumen/categorias")
def resumen_por_categoria(db: Session = Depends(get_db), current_user: models.Usuario = Depends(get_current_user)):
    from sqlalchemy import func
    resumen = db.query(models.Categoria.nombre, func.sum(models.Transaccion.monto))\
        .join(models.Transaccion, models.Categoria.id_categoria == models.Transaccion.id_categoria)\
        .filter(models.Transaccion.id_usuario == current_user.id_usuario)\
        .group_by(models.Categoria.nombre).all()
    return [{"categoria": r[0], "total": float(r[1])} for r in resumen]



@app.post("/presupuestos", response_model=BudgetOut)
def crear_presupuesto(p: BudgetCreate, db: Session = Depends(get_db), current_user: models.Usuario = Depends(get_current_user)):
    nuevo = models.Presupuesto(
        monto=p.monto,
        fecha_crea=p.fecha_crea,
        fecha_venc=p.fecha_venc,
        id_usuario=current_user.id_usuario  
    )
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo



@app.get("/presupuestos", response_model=List[BudgetOut])
def obtener_presupuestos(db: Session = Depends(get_db)):
    return db.query(models.Presupuesto).all()

@app.put("/presupuestos/{id}", response_model=BudgetOut)
def actualizar_presupuesto(id: int, p: BudgetCreate, db: Session = Depends(get_db)):
    b = db.query(models.Presupuesto).filter(models.Presupuesto.id_presupuesto == id).first()
    if not b:
        raise HTTPException(status_code=404, detail="No encontrado")
    for attr, value in p.dict().items():
        setattr(b, attr, value)
    db.commit()
    db.refresh(b)
    return b

@app.delete("/presupuestos/{id}")
def eliminar_presupuesto(id: int, db: Session = Depends(get_db)):
    b = db.query(models.Presupuesto).filter(models.Presupuesto.id_presupuesto == id).first()
    if not b:
        raise HTTPException(status_code=404, detail="No encontrado")
    db.delete(b)
    db.commit()
    return {"detail": "Eliminado"}

@app.post("/pagos-fijos", response_model=FixedPaymentOut)
def crear_pago(
    p: FixedPaymentCreate,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    nuevo = models.PagoFijo(
        descripcion=p.descripcion,
        monto=p.monto,
        fecha_inicio=p.fecha_inicio,
        activo=p.activo,
        categoria_id=p.categoria_id_categoria,  
        id_usuario=current_user.id_usuario
    )
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo


@app.get("/pagos-fijos", response_model=List[FixedPaymentOut])
def obtener_pagos(db: Session = Depends(get_db), current_user: models.Usuario = Depends(get_current_user)):
    return db.query(models.PagoFijo).filter(models.PagoFijo.id_usuario == current_user.id_usuario).all()


@app.put("/pagos-fijos/{id}", response_model=FixedPaymentOut)
def actualizar_pago(
    id: int,
    p: FixedPaymentCreate,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    pago = db.query(models.PagoFijo).filter(
        models.PagoFijo.id_pago_fijo == id,
        models.PagoFijo.id_usuario == current_user.id_usuario
    ).first()
    if not pago:
        raise HTTPException(status_code=404, detail="No encontrado")
    for attr, value in p.dict().items():
        if attr == "categoria_id_categoria":
            setattr(pago, "categoria_id", value)
        else:
            setattr(pago, attr, value)
    db.commit()
    db.refresh(pago)
    return pago


@app.delete("/pagos-fijos/{id}")
def eliminar_pago(
    id: int,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    pago = db.query(models.PagoFijo).filter(
        models.PagoFijo.id_pago_fijo == id,
        models.PagoFijo.id_usuario == current_user.id_usuario
    ).first()
    if not pago:
        raise HTTPException(status_code=404, detail="No encontrado")
    db.delete(pago)
    db.commit()
    return {"detail": "Eliminado"}
