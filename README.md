# 🥥 Proyecto ERP Comida - Juguería Coconut

Sistema ERP Móvil (Mobile-First) completo para la gestión de pedidos, caja, control de insumos Poka-Yoke y pantalla de cocina (KDS) diseñado para juguerías, cafeterías y restobares.

---

## 📱 Módulos del Sistema

### 1. 🍹 Carta Digital de Clientes (`index.html`)
- **Interfaz Móvil Nativa**: Optimizada para celulares sin necesidad de pellizcar o hacer zoom.
- **Categorías Deslizables**: Filtros táctiles rápidos (`Elixires`, `Smoothies`, `Bowls`, `Panqueques`).
- **Personalización Poka-Yoke**: Modal dinámico que limita automáticamente la cantidad de frutas, endulzantes y toppings según el tipo de producto.
- **Zona del Pulgar (Thumb Zone)**: Carrito flotante en la parte inferior con Bottom Sheet interactivo.
- **Confirmación WhatsApp & QR Yape**: Envío de comandas detalladas por WhatsApp con número Yape y opción de pago en efectivo o posconsumo.

### 2. 💳 Panel de Caja & Administración (`cajero.html`)
- **Control Tabulado Segmentado**: Cambio rápido entre **`💰 Cobros Pendientes`** y **`🎛️ Stock Insumos`**.
- **Métricas KPI en Vivo**: Mini tarjetas de resumen con Saldo de Caja, Ingresos y Egresos.
- **Control de Disponibilidad**: Desactivación instantánea de insumos agotados, actualizando en tiempo real la disponibilidad de la carta.

### 3. 👨‍🍳 Pantalla de Cocina KDS (`kds.html`)
- **Producción en Lote (Batching)**: Resumen acumulado de productos requeridos para acelerar la preparación.
- **Comandas de Ensamble**: Visualización clara de insumos elegidos por el cliente y botón de 1 toque `✓ Marcar Listo`.

---

## 🛠️ Tecnologías Utilizadas

- **Backend**: Python 3, FastAPI, SQLAlchemy, SQLite, Uvicorn.
- **Frontend**: Vanilla JavaScript (ES6+), HTML5, TailwindCSS, Vanilla CSS (Glassmorphism).

---

## 🚀 Instalación y Ejecución Local

1. **Clonar el repositorio**:
   ```bash
   git clone https://github.com/jharod99/proyecto-erp-comida.git
   cd proyecto-erp-comida
   ```

2. **Instalar dependencias**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Poblar la base de datos de prueba**:
   ```bash
   python poblar_bd.py
   ```

4. **Iniciar el servidor local**:
   ```bash
   python -m uvicorn main:app --host 0.0.0.0 --port 8000
   ```

5. **Acceder desde tu navegador o celular**:
   - 🍹 **Carta para Clientes**: `http://localhost:8000/frontend/index.html`
   - 💳 **Panel de Caja**: `http://localhost:8000/frontend/cajero.html`
   - 👨‍🍳 **Cocina KDS**: `http://localhost:8000/frontend/kds.html`

---

## ☁️ Despliegue en la Nube (Render.com)

- **Entorno**: Python 3
- **Comando de Inicio**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
