from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from models import ProductoBase, Insumo, RecetaInsumo
from schemas import (
    MenuActivoResponse,
    ProductoBaseResponse,
    ProductoBaseCreate,
    InsumoResponse,
    InsumoCreate,
)

router = APIRouter(prefix="/api/menu", tags=["Menú y Catálogo"])


# ==========================================
# ENDPOINT PÚBLICO: MENÚ CON EVALUACIÓN DE DISPONIBILIDAD Y RECETAS
# ==========================================
@router.get("", response_model=MenuActivoResponse, summary="Obtener el menú público con estado de disponibilidad Poka-Yoke")
def obtener_menu_activo(db: Session = Depends(get_db)):
    """
    DEVUELVE EL CATÁLOGO COMPLETO EVALUADO:
    1. Evalúa la disponibilidad individual del producto e insumos.
    2. POKA-YOKE DE RECETA: Si un producto requiere un insumo obligatorio que está agotado, marca disponible = False para la UI.
    """
    todos_insumos = db.query(Insumo).all()
    insumos_activos_ids = {i.id for i in todos_insumos if i.disponible}

    todos_productos = db.query(ProductoBase).all()
    productos_evaluados = []

    for prod in todos_productos:
        # Copiamos la instancia o datos para evaluar disponibilidad efectiva
        disponible_efectivo = prod.disponible

        if disponible_efectivo:
            # Verificar si algún insumo obligatorio está agotado
            recetas_obligatorias = (
                db.query(RecetaInsumo)
                .filter(RecetaInsumo.producto_id == prod.id, RecetaInsumo.es_obligatorio == True)
                .all()
            )
            for rec in recetas_obligatorias:
                if rec.insumo_id not in insumos_activos_ids:
                    disponible_efectivo = False
                    break

        prod_resp = ProductoBaseResponse(
            id=prod.id,
            nombre=prod.nombre,
            categoria=prod.categoria,
            precio=prod.precio,
            disponible=disponible_efectivo,
            imagen_url=prod.imagen_url
        )
        productos_evaluados.append(prod_resp)

    insumos_resp = [InsumoResponse.model_validate(i) for i in todos_insumos]

    return MenuActivoResponse(
        status="success",
        productos_base=productos_evaluados,
        insumos=insumos_resp
    )


# ==========================================
# ENDPOINTS ADMINISTRATIVOS: GESTIÓN DE CATÁLOGO, RECETAS E INVENTARIO
# ==========================================
@router.get("/admin/inventario_completo", summary="Obtener todo el inventario de productos, insumos y recetas para el Panel Poka-Yoke")
def obtener_inventario_completo(db: Session = Depends(get_db)):
    """Devuelve la lista completa de productos, insumos y sus recetas de dependencia para la gestión de stock."""
    productos = db.query(ProductoBase).all()
    insumos = db.query(Insumo).all()
    recetas = db.query(RecetaInsumo).all()

    recetas_list = []
    for r in recetas:
        prod = db.query(ProductoBase).filter(ProductoBase.id == r.producto_id).first()
        ins = db.query(Insumo).filter(Insumo.id == r.insumo_id).first()
        if prod and ins:
            recetas_list.append({
                "id": r.id,
                "producto_id": prod.id,
                "nombre_producto": prod.nombre,
                "insumo_id": ins.id,
                "nombre_insumo": ins.nombre,
                "es_obligatorio": r.es_obligatorio
            })

    return {
        "status": "success",
        "productos_base": [ProductoBaseResponse.model_validate(p) for p in productos],
        "insumos": [InsumoResponse.model_validate(i) for i in insumos],
        "recetas_dependencias": recetas_list
    }


@router.post("/recetas", summary="Asociar dependencia de insumo a un producto base")
def asociar_receta(producto_id: int, insumo_id: int, es_obligatorio: bool = True, db: Session = Depends(get_db)):
    prod = db.query(ProductoBase).filter(ProductoBase.id == producto_id).first()
    ins = db.query(Insumo).filter(Insumo.id == insumo_id).first()

    if not prod or not ins:
        raise HTTPException(status_code=404, detail="Producto o insumo no encontrado")

    nueva_receta = RecetaInsumo(producto_id=producto_id, insumo_id=insumo_id, es_obligatorio=es_obligatorio)
    db.add(nueva_receta)
    db.commit()
    db.refresh(nueva_receta)

    return {"status": "success", "mensaje": f"Insumo '{ins.nombre}' vinculado a '{prod.nombre}' (Obligatorio: {es_obligatorio})"}


@router.get("/admin/productos", response_model=List[ProductoBaseResponse], summary="Obtener todos los productos (Admin)")
def obtener_todos_productos(db: Session = Depends(get_db)):
    return db.query(ProductoBase).all()


@router.post("/productos", response_model=ProductoBaseResponse, status_code=status.HTTP_201_CREATED, summary="Crear nuevo producto base")
def crear_producto(producto: ProductoBaseCreate, db: Session = Depends(get_db)):
    db_producto = ProductoBase(**producto.model_dump())
    db.add(db_producto)
    db.commit()
    db.refresh(db_producto)
    return db_producto


@router.patch("/productos/{producto_id}/disponibilidad", response_model=ProductoBaseResponse, summary="Cambiar disponibilidad de un producto (Poka-Yoke)")
def cambiar_disponibilidad_producto(producto_id: int, disponible: bool, db: Session = Depends(get_db)):
    db_producto = db.query(ProductoBase).filter(ProductoBase.id == producto_id).first()
    if not db_producto:
        raise HTTPException(status_code=404, detail=f"Producto con ID {producto_id} no encontrado")

    db_producto.disponible = disponible
    db.commit()
    db.refresh(db_producto)
    return db_producto


@router.get("/admin/insumos", response_model=List[InsumoResponse], summary="Obtener todos los insumos (Admin)")
def obtener_todos_insumos(db: Session = Depends(get_db)):
    return db.query(Insumo).all()


@router.post("/insumos", response_model=InsumoResponse, status_code=status.HTTP_201_CREATED, summary="Crear nuevo insumo")
def crear_insumo(insumo: InsumoCreate, db: Session = Depends(get_db)):
    db_insumo = Insumo(**insumo.model_dump())
    db.add(db_insumo)
    db.commit()
    db.refresh(db_insumo)
    return db_insumo


@router.patch("/insumos/{insumo_id}/disponibilidad", response_model=InsumoResponse, summary="Cambiar disponibilidad de un insumo (Poka-Yoke)")
def cambiar_disponibilidad_insumo(insumo_id: int, disponible: bool, db: Session = Depends(get_db)):
    db_insumo = db.query(Insumo).filter(Insumo.id == insumo_id).first()
    if not db_insumo:
        raise HTTPException(status_code=404, detail=f"Insumo con ID {insumo_id} no encontrado")

    db_insumo.disponible = disponible
    db.commit()
    db.refresh(db_insumo)
    return db_insumo
