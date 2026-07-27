import json
from decimal import Decimal
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from database import get_db
from models import Pedido, Cliente, ProductoBase, Insumo, RecetaInsumo
from schemas import (
    PedidoCreate,
    PedidoResponse,
    DetalleItem,
)

router = APIRouter(prefix="/api/pedidos", tags=["Gestión de Pedidos"])


def helper_parse_pedido(pedido: Pedido) -> PedidoResponse:
    """Helper para deserializar el detalle_json en la respuesta del pedido."""
    try:
        raw_items = json.loads(pedido.detalle_json)
        parsed_items = [DetalleItem(**item) for item in raw_items]
    except Exception:
        parsed_items = []

    return PedidoResponse(
        id=pedido.id,
        telefono_cliente=pedido.telefono_cliente,
        detalle_json=pedido.detalle_json,
        detalle_items=parsed_items,
        total=pedido.total,
        metodo_pago=pedido.metodo_pago or "yape",
        momento_pago=pedido.momento_pago or "inmediato",
        estado=pedido.estado,
        fecha_hora=pedido.fecha_hora
    )


@router.post("", response_model=PedidoResponse, status_code=status.HTTP_201_CREATED, summary="Crear un nuevo pedido (Soporta Yape/Efectivo e Inmediato/Al Consumir)")
def crear_pedido(pedido_in: PedidoCreate, db: Session = Depends(get_db)):
    """
    CREACIÓN DE PEDIDO DINÁMICO:
    1. Si momento_pago == 'despues_consumo', el pedido pasa DIRECTAMENTE a 'en_cocina' para prepararse al instante.
    2. Si momento_pago == 'inmediato', el pedido queda en 'esperando_pago' hasta verificar voucher.
    """
    if not pedido_in.items:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El pedido debe contener al menos un producto."
        )

    # 1. CRM: Verificar o crear Cliente
    cliente = db.query(Cliente).filter(Cliente.telefono == pedido_in.telefono_cliente).first()
    if not cliente:
        nombre_cliente = pedido_in.nombre_cliente.strip() if pedido_in.nombre_cliente else "Cliente General"
        cliente = Cliente(
            telefono=pedido_in.telefono_cliente,
            nombre=nombre_cliente,
            total_gastado=Decimal("0.00")
        )
        db.add(cliente)
        db.flush()

    total_calculado = Decimal("0.00")
    items_congelados: List[dict] = []

    # 2. Verificación Estricta de Insumos y Receta
    for item in pedido_in.items:
        producto_db = db.query(ProductoBase).filter(ProductoBase.id == item.producto_base_id).first()
        if not producto_db:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"El producto base ID {item.producto_base_id} no existe en el catálogo."
            )

        if not producto_db.disponible:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"El producto '{producto_db.nombre}' ya no se encuentra disponible (Agotado)."
            )

        # Verificación de Receta
        recetas_obligatorias = (
            db.query(RecetaInsumo)
            .filter(RecetaInsumo.producto_id == producto_db.id, RecetaInsumo.es_obligatorio == True)
            .all()
        )
        for rec in recetas_obligatorias:
            ins_req = db.query(Insumo).filter(Insumo.id == rec.insumo_id).first()
            if not ins_req or not ins_req.disponible:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"El producto '{producto_db.nombre}' no se puede preparar porque su insumo base '{ins_req.nombre if ins_req else 'requerido'}' está agotado."
                )

        # Verificación de Insumos Seleccionados
        insumos_validados: List[str] = []
        for nombre_insumo in item.insumos_seleccionados:
            insumo_db = db.query(Insumo).filter(Insumo.nombre == nombre_insumo).first()
            if not insumo_db or not insumo_db.disponible:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"El insumo opcional '{nombre_insumo}' se agotó hace un momento. Por favor actualiza tu carrito."
                )
            insumos_validados.append(insumo_db.nombre)

        precio_unitario = Decimal(str(producto_db.precio))
        cantidad = item.cantidad
        subtotal_item = precio_unitario * cantidad
        total_calculado += subtotal_item

        items_congelados.append({
            "producto_base_id": producto_db.id,
            "nombre_producto": producto_db.nombre,
            "cantidad": cantidad,
            "precio_unitario": str(precio_unitario),
            "insumos_seleccionados": insumos_validados,
            "subtotal": str(subtotal_item)
        })

    # DETERMINAR ESTADO INICIAL SEGÚN MOMENTO DE PAGO
    metodo = pedido_in.metodo_pago or "yape"
    momento = pedido_in.momento_pago or "inmediato"

    # Si se paga al consumir o en efectivo en caja, se envía directo a cocina
    estado_inicial = "en_cocina" if momento == "despues_consumo" else "esperando_pago"

    nuevo_pedido = Pedido(
        telefono_cliente=cliente.telefono,
        detalle_json=json.dumps(items_congelados, ensure_ascii=False),
        total=total_calculado,
        metodo_pago=metodo,
        momento_pago=momento,
        estado=estado_inicial
    )

    db.add(nuevo_pedido)
    db.commit()
    db.refresh(nuevo_pedido)

    return helper_parse_pedido(nuevo_pedido)


@router.get("", response_model=List[PedidoResponse], summary="Listar pedidos (Filtro por estado opcional)")
def listar_pedidos(estado: Optional[str] = Query(None, description="Filtra por estado: esperando_pago, en_cocina, completado, rechazado"), db: Session = Depends(get_db)):
    query = db.query(Pedido)
    if estado:
        query = query.filter(Pedido.estado == estado)
    
    pedidos = query.order_by(Pedido.fecha_hora.desc()).all()
    return [helper_parse_pedido(p) for p in pedidos]


@router.get("/{pedido_id}", response_model=PedidoResponse, summary="Obtener detalle de un pedido por ID")
def obtener_pedido(pedido_id: int, db: Session = Depends(get_db)):
    pedido = db.query(Pedido).filter(Pedido.id == pedido_id).first()
    if not pedido:
        raise HTTPException(status_code=404, detail=f"Pedido #{pedido_id} no encontrado")
    return helper_parse_pedido(pedido)


@router.get("/cliente/{telefono}", response_model=List[PedidoResponse], summary="Historial de pedidos por cliente")
def obtener_pedidos_cliente(telefono: str, db: Session = Depends(get_db)):
    pedidos = (
        db.query(Pedido)
        .filter(Pedido.telefono_cliente == telefono)
        .order_by(Pedido.fecha_hora.desc())
        .all()
    )
    return [helper_parse_pedido(p) for p in pedidos]
