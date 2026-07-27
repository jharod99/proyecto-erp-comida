from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Boolean, Numeric, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from database import Base


def default_utcnow():
    return datetime.now(timezone.utc)


class ProductoBase(Base):
    """
    Catálogo principal de productos (Jugos, Smoothies, Bowls, Bases de Panqueques).
    El campo `disponible` actúa como interruptor binario.
    """
    __tablename__ = "productos_base"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False, index=True)
    categoria = Column(String(50), nullable=False, index=True)  # Ej: "Elixires", "Smoothies", "Bowls", "Postres Fit"
    precio = Column(Numeric(10, 2), nullable=False)
    disponible = Column(Boolean, default=True, nullable=False)
    imagen_url = Column(String(500), nullable=True)

    recetas = relationship("RecetaInsumo", back_populates="producto", cascade="all, delete-orphan")


class Insumo(Base):
    """
    Insumos personalizables u obligatorios (Frutas, Endulzantes, Toppings).
    Si un insumo obligatorio se agota (`disponible == False`), los productos finales que dependen de él se ocultan automáticamente.
    """
    __tablename__ = "insumos_personalizables"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    tipo = Column(String(50), nullable=False)  # "Fruta", "Endulzante", "Topping", "Base"
    disponible = Column(Boolean, default=True, nullable=False)

    recetas = relationship("RecetaInsumo", back_populates="insumo", cascade="all, delete-orphan")


class RecetaInsumo(Base):
    """
    Tabla de Dependencias / Receta (BOM).
    Relaciona qué insumos requiere obligatoriamente un producto final.
    """
    __tablename__ = "receta_insumos"

    id = Column(Integer, primary_key=True, index=True)
    producto_id = Column(Integer, ForeignKey("productos_base.id"), nullable=False, index=True)
    insumo_id = Column(Integer, ForeignKey("insumos_personalizables.id"), nullable=False, index=True)
    es_obligatorio = Column(Boolean, default=True, nullable=False)

    producto = relationship("ProductoBase", back_populates="recetas")
    insumo = relationship("Insumo", back_populates="recetas")


class Cliente(Base):
    """
    Módulo de Clientes.
    """
    __tablename__ = "clientes"

    telefono = Column(String(20), primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    total_gastado = Column(Numeric(10, 2), default=0.00, nullable=False)
    fecha_registro = Column(DateTime, default=default_utcnow, nullable=False)

    pedidos = relationship("Pedido", back_populates="cliente")


class Pedido(Base):
    """
    Registro de Pedidos.
    Estados: 'esperando_pago', 'en_cocina', 'completado', 'rechazado'
    Métodos de Pago: 'yape', 'efectivo'
    Momentos de Pago: 'inmediato', 'despues_consumo'
    """
    __tablename__ = "pedidos"

    id = Column(Integer, primary_key=True, index=True)
    telefono_cliente = Column(String(20), ForeignKey("clientes.telefono"), nullable=False, index=True)
    detalle_json = Column(Text, nullable=False)
    total = Column(Numeric(10, 2), nullable=False)
    metodo_pago = Column(String(20), default="yape", nullable=False)  # "yape", "efectivo"
    momento_pago = Column(String(30), default="inmediato", nullable=False)  # "inmediato", "despues_consumo"
    estado = Column(String(30), default="esperando_pago", nullable=False, index=True)
    fecha_hora = Column(DateTime, default=default_utcnow, nullable=False)

    cliente = relationship("Cliente", back_populates="pedidos")


class Caja(Base):
    """
    Módulo de Control de Caja (Ingresos y Egresos).
    """
    __tablename__ = "caja"

    id = Column(Integer, primary_key=True, index=True)
    tipo = Column(String(10), nullable=False)  # "ingreso" o "egreso"
    monto = Column(Numeric(10, 2), nullable=False)
    concepto = Column(String(255), nullable=False)
    fecha_hora = Column(DateTime, default=default_utcnow, nullable=False)
