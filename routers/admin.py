from decimal import Decimal
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from models import Pedido, Caja, Cliente
from schemas import (
    PedidoResponse,
    CajaCreate,
    CajaResponse,
    PedidoAprobarRequest,
)
from routers.orders import helper_parse_pedido

router = APIRouter(prefix="/api/admin", tags=["Módulo Administrador y Caja"])


# ==========================================
# FLUJO DE VALIDACIÓN MANUAL DE PAGO / COBRO EN CAJA
# ==========================================
@router.post("/pedidos/{pedido_id}/aprobar", response_model=PedidoResponse, summary="Aprobar / Cobrar pedido (Efectivo o Yape -> Caja)")
def aprobar_pago_pedido(
    pedido_id: int,
    request: Optional[PedidoAprobarRequest] = None,
    db: Session = Depends(get_db)
):
    """
    FLUJO POKA-YOKE DE COBRO Y APROBACIÓN:
    1. Verifica que el pedido esté en 'esperando_pago' o 'en_cocina'.
    2. Cambia el estado a 'completado'.
    3. Registra automáticamente el ingreso financiero en la tabla Caja.
    """
    pedido = db.query(Pedido).filter(Pedido.id == pedido_id).first()
    if not pedido:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pedido #{pedido_id} no encontrado."
        )

    if pedido.estado not in ["esperando_pago", "en_cocina"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El pedido #{pedido_id} no se encuentra pendiente de cobro (Estado actual: '{pedido.estado}')."
        )

    # 1. Cambiar estado a 'completado'
    pedido.estado = "completado"

    # 2. Registrar movimiento en Caja
    metodo_txt = "Efectivo" if pedido.metodo_pago == "efectivo" else "Yape/Plin"
    concepto_default = f"Cobro Venta #{pedido.id} ({metodo_txt})"
    concepto = request.concepto_pago if (request and request.concepto_pago) else concepto_default

    nuevo_movimiento_caja = Caja(
        tipo="ingreso",
        monto=pedido.total,
        concepto=concepto
    )
    db.add(nuevo_movimiento_caja)

    # 3. Actualizar cliente si existe
    cliente = db.query(Cliente).filter(Cliente.telefono == pedido.telefono_cliente).first()
    if cliente:
        cliente.total_gastado = Decimal(str(cliente.total_gastado)) + Decimal(str(pedido.total))

    db.commit()
    db.refresh(pedido)

    return helper_parse_pedido(pedido)


@router.post("/pedidos/{pedido_id}/rechazar", response_model=PedidoResponse, summary="Rechazar o anular pedido")
def rechazar_pago_pedido(pedido_id: int, db: Session = Depends(get_db)):
    """
    Anula o rechaza el pedido.
    No inyecta ingresos a la Caja.
    """
    pedido = db.query(Pedido).filter(Pedido.id == pedido_id).first()
    if not pedido:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pedido #{pedido_id} no encontrado."
        )

    if pedido.estado not in ["esperando_pago", "en_cocina"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El pedido #{pedido_id} ya se encuentra procesado (Estado actual: '{pedido.estado}')."
        )

    pedido.estado = "rechazado"
    db.commit()
    db.refresh(pedido)

    return helper_parse_pedido(pedido)


# ==========================================
# MÓDULO DE CAJA (INGRESOS Y EGRESOS)
# ==========================================
@router.get("/caja", summary="Obtener movimientos y resumen de Caja")
def obtener_resumen_caja(db: Session = Depends(get_db)):
    """
    Devuelve la lista completa de movimientos de caja junto con el saldo total de la jornada.
    """
    movimientos = db.query(Caja).order_by(Caja.fecha_hora.desc()).all()

    total_ingresos = Decimal("0.00")
    total_egresos = Decimal("0.00")

    for mov in movimientos:
        monto_dec = Decimal(str(mov.monto))
        if mov.tipo.lower() == "ingreso":
            total_ingresos += monto_dec
        elif mov.tipo.lower() == "egreso":
            total_egresos += monto_dec

    saldo_actual = total_ingresos - total_egresos

    movimientos_response = [
        CajaResponse.model_validate(mov) for mov in movimientos
    ]

    return {
        "status": "success",
        "total_ingresos": total_ingresos,
        "total_egresos": total_egresos,
        "saldo_actual": saldo_actual,
        "movimientos": movimientos_response
    }


@router.post("/caja", response_model=CajaResponse, status_code=status.HTTP_201_CREATED, summary="Registrar movimiento manual en Caja")
def registrar_movimiento_caja(movimiento: CajaCreate, db: Session = Depends(get_db)):
    """Permite registrar un egreso (compra insumos) u otro ingreso manual en la Caja."""
    if movimiento.tipo.lower() not in ["ingreso", "egreso"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El tipo de movimiento debe ser 'ingreso' o 'egreso'."
        )

    nuevo_mov = Caja(**movimiento.model_dump())
    db.add(nuevo_mov)
    db.commit()
    db.refresh(nuevo_mov)

    return nuevo_mov
