import json
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from models import Pedido
from schemas import PedidoResponse, DetalleItem
from routers.orders import helper_parse_pedido

router = APIRouter(prefix="/api/kds", tags=["KDS - Pantalla de Cocina"])


@router.get("/activos", summary="Obtener pantalla KDS con Agrupamiento por Lotes y Ensamble")
def obtener_kds_activos(db: Session = Depends(get_db)):
    """
    EXCELENCIA OPERACIONAL EN COCINA:
    1. Filtra únicamente los pedidos aprobados en estado 'en_cocina'.
    2. RESUMEN PRODUCCIÓN POR LOTES: Agrupa y suma la preparación base (ej. 'Preparar 3 Bases de Panqueque Fit').
    3. ENSAMBLE INDIVIDUAL: Muestra el detalle exacto por comanda (frutas, endulzantes y toppings).
    """
    pedidos_en_cocina = (
        db.query(Pedido)
        .filter(Pedido.estado == "en_cocina")
        .order_by(Pedido.fecha_hora.asc())
        .all()
    )

    conteo_lotes: Dict[str, int] = {}
    pedidos_ensamble: List[Dict[str, Any]] = []

    for pedido in pedidos_en_cocina:
        parsed_items: List[Dict[str, Any]] = []
        try:
            items_raw = json.loads(pedido.detalle_json)
            for item in items_raw:
                nombre_prod = item.get("nombre_producto", "Producto")
                cantidad = int(item.get("cantidad", 1))

                # Agrupamiento para Producción por Lotes
                conteo_lotes[nombre_prod] = conteo_lotes.get(nombre_prod, 0) + cantidad

                parsed_items.append({
                    "producto_base_id": item.get("producto_base_id"),
                    "nombre_producto": nombre_prod,
                    "cantidad": cantidad,
                    "insumos_seleccionados": item.get("insumos_seleccionados", [])
                })
        except Exception:
            pass

        pedidos_ensamble.append({
            "pedido_id": pedido.id,
            "telefono_cliente": pedido.telefono_cliente,
            "fecha_hora": pedido.fecha_hora,
            "items": parsed_items
        })

    # Formatear el resumen de lotes como lista
    resumen_produccion_lotes = [
        {"nombre_producto": prod, "cantidad_total": cant}
        for prod, cant in conteo_lotes.items()
    ]

    return {
        "status": "success",
        "total_pedidos_en_cocina": len(pedidos_en_cocina),
        "resumen_produccion_lotes": resumen_produccion_lotes,
        "pedidos_para_ensamble": pedidos_ensamble
    }


@router.post("/pedidos/{pedido_id}/completar", response_model=PedidoResponse, summary="Marcar pedido como completado en KDS")
def completar_pedido_kds(pedido_id: int, db: Session = Depends(get_db)):
    """
    Marcar un pedido como completado en cocina. Pasa el estado de 'en_cocina' a 'completado'.
    """
    pedido = db.query(Pedido).filter(Pedido.id == pedido_id).first()
    if not pedido:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pedido #{pedido_id} no encontrado."
        )

    if pedido.estado != "en_cocina":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El pedido #{pedido_id} no se encuentra en estado 'en_cocina' (Estado actual: '{pedido.estado}')."
        )

    pedido.estado = "completado"
    db.commit()
    db.refresh(pedido)

    return helper_parse_pedido(pedido)


@router.get("/completados", response_model=List[PedidoResponse], summary="Obtener historial de pedidos completados en cocina")
def obtener_kds_completados(db: Session = Depends(get_db)):
    """Muestra los últimos pedidos completados en cocina."""
    pedidos = (
        db.query(Pedido)
        .filter(Pedido.estado == "completado")
        .order_by(Pedido.fecha_hora.desc())
        .limit(20)
        .all()
    )
    return [helper_parse_pedido(p) for p in pedidos]
