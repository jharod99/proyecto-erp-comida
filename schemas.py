from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict


# ==========================================
# SCHEMAS: PRODUCTO BASE
# ==========================================
class ProductoBaseBase(BaseModel):
    nombre: str = Field(..., example="Jugo Inmunidad")
    categoria: str = Field(..., example="Elixir Funcional")
    precio: Decimal = Field(..., decimal_places=2, ge=0, example=Decimal("12.00"))
    disponible: bool = True
    imagen_url: Optional[str] = Field(None, example="https://images.unsplash.com/photo-1613478223719-2ab802602423?auto=format&fit=crop&w=500&q=80")


class ProductoBaseCreate(ProductoBaseBase):
    pass


class ProductoBaseUpdate(BaseModel):
    nombre: Optional[str] = None
    categoria: Optional[str] = None
    precio: Optional[Decimal] = None
    disponible: Optional[bool] = None
    imagen_url: Optional[str] = None


class ProductoBaseResponse(ProductoBaseBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


# ==========================================
# SCHEMAS: INSUMO PERSONALIZABLE
# ==========================================
class InsumoBase(BaseModel):
    nombre: str = Field(..., example="Fresas")
    tipo: str = Field(..., example="Fruta")  # "Fruta", "Endulzante", "Topping"
    disponible: bool = True


class InsumoCreate(InsumoBase):
    pass


class InsumoUpdate(BaseModel):
    nombre: Optional[str] = None
    tipo: Optional[str] = None
    disponible: Optional[bool] = None


class InsumoResponse(InsumoBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


# ==========================================
# SCHEMAS: CLIENTE (CRM)
# ==========================================
class ClienteBase(BaseModel):
    telefono: str = Field(..., example="987654321")
    nombre: str = Field(..., example="Juan Pérez")


class ClienteCreate(ClienteBase):
    pass


class ClienteResponse(ClienteBase):
    total_gastado: Decimal = Decimal("0.00")
    fecha_registro: datetime
    model_config = ConfigDict(from_attributes=True)


# ==========================================
# SCHEMAS: DETALLE DE ITEM & PEDIDO
# ==========================================
class DetalleItem(BaseModel):
    producto_base_id: int
    nombre_producto: str
    cantidad: int = Field(default=1, ge=1)
    precio_unitario: Decimal = Field(..., decimal_places=2)
    insumos_seleccionados: List[str] = Field(default_factory=list, example=["Fresas", "Fruto del Monje", "Nibs de Cacao"])
    subtotal: Decimal = Field(..., decimal_places=2)


class PedidoCreate(BaseModel):
    telefono_cliente: str = Field(..., example="987654321")
    nombre_cliente: Optional[str] = Field(None, example="Juan Pérez")
    metodo_pago: Optional[str] = Field("yape", example="yape")  # "yape", "efectivo"
    momento_pago: Optional[str] = Field("inmediato", example="inmediato")  # "inmediato", "despues_consumo"
    items: List[DetalleItem]


class PedidoResponse(BaseModel):
    id: int
    telefono_cliente: str
    detalle_json: str
    detalle_items: Optional[List[DetalleItem]] = None
    total: Decimal
    metodo_pago: str = "yape"
    momento_pago: str = "inmediato"
    estado: str  # "esperando_pago", "en_cocina", "completado", "rechazado"
    fecha_hora: datetime
    model_config = ConfigDict(from_attributes=True)


class PedidoAprobarRequest(BaseModel):
    concepto_pago: Optional[str] = Field("Pago Aprobado", example="Pago Aprobado - Pedido #1")


# ==========================================
# SCHEMAS: CAJA
# ==========================================
class CajaCreate(BaseModel):
    tipo: str = Field(..., example="ingreso")  # "ingreso" o "egreso"
    monto: Decimal = Field(..., decimal_places=2, gt=0)
    concepto: str = Field(..., example="Venta Pedido #1")


class CajaResponse(CajaCreate):
    id: int
    fecha_hora: datetime
    model_config = ConfigDict(from_attributes=True)


# ==========================================
# SCHEMAS: MENÚ ACTIVO (INVENTARIO BINARIO)
# ==========================================
class MenuActivoResponse(BaseModel):
    status: str = "success"
    productos_base: List[ProductoBaseResponse]
    insumos: List[InsumoResponse]
