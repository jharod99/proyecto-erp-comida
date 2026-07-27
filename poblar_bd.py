import json
from decimal import Decimal
from database import engine, Base, SessionLocal
from models import ProductoBase, Insumo, RecetaInsumo, Cliente, Pedido, Caja


def poblar_base_de_datos():
    print("Reconstruyendo las tablas de la base de datos (SQLite)...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    try:
        print("Inyectando Productos Base con Imágenes de Alta Calidad...")
        productos = [
            ProductoBase(
                nombre="Jugo Inmunidad",
                categoria="Elixir Funcional",
                precio=Decimal("12.00"),
                disponible=True,
                imagen_url="https://images.unsplash.com/photo-1613478223719-2ab802602423?auto=format&fit=crop&w=600&q=80"
            ),
            ProductoBase(
                nombre="Jugo Detox Profundo",
                categoria="Elixir Funcional",
                precio=Decimal("14.00"),
                disponible=True,
                imagen_url="https://images.unsplash.com/photo-1540420773420-3366772f4999?auto=format&fit=crop&w=600&q=80"
            ),
            ProductoBase(
                nombre="Jugo Energía Pura",
                categoria="Elixir Funcional",
                precio=Decimal("13.00"),
                disponible=True,
                imagen_url="https://images.unsplash.com/photo-1534353473418-4cfa6c56fd38?auto=format&fit=crop&w=600&q=80"
            ),
            ProductoBase(
                nombre="Smoothie Proteico",
                categoria="Smoothie",
                precio=Decimal("16.00"),
                disponible=True,
                imagen_url="https://images.unsplash.com/photo-1553530666-ba11a7da3888?auto=format&fit=crop&w=600&q=80"
            ),
            ProductoBase(
                nombre="Smoothie Vitalidad",
                categoria="Smoothie",
                precio=Decimal("15.00"),
                disponible=True,
                imagen_url="https://images.unsplash.com/photo-1502741224143-90386d7f8c82?auto=format&fit=crop&w=600&q=80"
            ),
            ProductoBase(
                nombre="Bowl Açai Tropical",
                categoria="Bowl",
                precio=Decimal("20.00"),
                disponible=True,
                imagen_url="https://images.unsplash.com/photo-1590301157890-4810ed352733?auto=format&fit=crop&w=600&q=80"
            ),
            ProductoBase(
                nombre="Bowl Mango Sunset",
                categoria="Bowl",
                precio=Decimal("18.00"),
                disponible=True,
                imagen_url="https://images.unsplash.com/photo-1546069901-ba9599a7e63c?auto=format&fit=crop&w=600&q=80"
            ),
            ProductoBase(
                nombre="Base de Panqueque Fit",
                categoria="Postre Fit",
                precio=Decimal("18.00"),
                disponible=True,
                imagen_url="https://images.unsplash.com/photo-1567620905732-2d1ec7ab7445?auto=format&fit=crop&w=600&q=80"
            ),
            ProductoBase(
                nombre="Jugo Edición Limitada",
                categoria="Edición Especial",
                precio=Decimal("22.00"),
                disponible=False,
                imagen_url="https://images.unsplash.com/photo-1553530666-ba11a7da3888?auto=format&fit=crop&w=600&q=80"
            ),
        ]
        db.add_all(productos)
        db.flush()

        print("Inyectando Insumos Personalizables y Recetas...")
        insumos = [
            # Frutas
            Insumo(nombre="Fresas", tipo="Fruta", disponible=True),
            Insumo(nombre="Arándanos", tipo="Fruta", disponible=True),
            Insumo(nombre="Mango", tipo="Fruta", disponible=True),
            Insumo(nombre="Plátano", tipo="Fruta", disponible=True),
            Insumo(nombre="Frambuesas", tipo="Fruta", disponible=True),
            Insumo(nombre="Pitahaya", tipo="Fruta", disponible=True),
            Insumo(nombre="Pulpa de Açai", tipo="Fruta", disponible=True),

            # Endulzantes
            Insumo(nombre="Fruto del Monje", tipo="Endulzante", disponible=True),
            Insumo(nombre="Stevia", tipo="Endulzante", disponible=True),
            Insumo(nombre="Panela Orgánica", tipo="Endulzante", disponible=True),
            Insumo(nombre="Miel de Agave", tipo="Endulzante", disponible=True),

            # Toppings
            Insumo(nombre="Nibs de Cacao", tipo="Topping", disponible=True),
            Insumo(nombre="Semillas de Chía", tipo="Topping", disponible=True),
            Insumo(nombre="Almendras Laminadas", tipo="Topping", disponible=True),
            Insumo(nombre="Coco Tostado", tipo="Topping", disponible=True),
        ]
        db.add_all(insumos)
        db.flush()

        # Dependencias de Recetas
        recetas = [
            RecetaInsumo(producto_id=productos[5].id, insumo_id=insumos[6].id, es_obligatorio=True), # Bowl Açai -> Pulpa de Açai
            RecetaInsumo(producto_id=productos[6].id, insumo_id=insumos[2].id, es_obligatorio=True), # Bowl Mango -> Mango
            RecetaInsumo(producto_id=productos[7].id, insumo_id=insumos[3].id, es_obligatorio=True), # Panqueque -> Plátano
        ]
        db.add_all(recetas)

        print("Inyectando Cliente de prueba...")
        cliente_demo = Cliente(
            telefono="987654321",
            nombre="María García",
            total_gastado=Decimal("0.00")
        )
        db.add(cliente_demo)

        print("Inyectando Pedido de prueba...")
        detalle_pedido_demo = [
            {
                "producto_base_id": productos[7].id,
                "nombre_producto": "Base de Panqueque Fit",
                "cantidad": 2,
                "precio_unitario": "18.00",
                "insumos_seleccionados": ["Fresas", "Fruto del Monje", "Almendras Laminadas"],
                "subtotal": "36.00"
            },
            {
                "producto_base_id": productos[0].id,
                "nombre_producto": "Jugo Inmunidad",
                "cantidad": 1,
                "precio_unitario": "12.00",
                "insumos_seleccionados": ["Stevia"],
                "subtotal": "12.00"
            }
        ]

        pedido_demo = Pedido(
            telefono_cliente="987654321",
            detalle_json=json.dumps(detalle_pedido_demo, ensure_ascii=False),
            total=Decimal("48.00"),
            estado="esperando_pago"
        )
        db.add(pedido_demo)

        print("Inyectando apertura de Caja...")
        caja_apertura = Caja(
            tipo="ingreso",
            monto=Decimal("100.00"),
            concepto="Apertura de Caja Inicial"
        )
        db.add(caja_apertura)

        db.commit()
        print("¡Base de datos del Proyecto Coconut poblada con éxito!")

    except Exception as e:
        db.rollback()
        print(f"Error poblando la base de datos: {e}")
        raise e
    finally:
        db.close()


if __name__ == "__main__":
    poblar_base_de_datos()