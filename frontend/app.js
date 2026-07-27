/* ==========================================
   PROYECTO COCONUT - FRONTEND LOGIC (VANILLA JS + TAILWINDCSS MOBILE)
   ========================================== */

const API_BASE = '/api';
const WHATSAPP_NUMERO = '51987654321'; // Número de WhatsApp de la Juguería

// ESTADO GLOBAL
let menuData = { productos_base: [], insumos: [] };
let inventarioDataAdmin = { productos_base: [], insumos: [], recetas_dependencias: [] };
let categoriaSeleccionada = 'Todos';
let carrito = [];
let productoSeleccionadoParaCustom = null;
let limitesActualesModal = { Fruta: 1, Endulzante: 1, Topping: 1 };

// TOGGLE MODAL STAFF / NAVEGACIÓN
function toggleStaffMenu() {
    const modal = document.getElementById('staff-access-modal');
    if (modal) {
        modal.classList.add('active');
    }
}

function cerrarStaffMenu() {
    const modal = document.getElementById('staff-access-modal');
    if (modal) {
        modal.classList.remove('active');
    }
}

function toggleMenuMobile() {
    toggleStaffMenu();
}

// ==========================================
// MÓDULO 1: MENÚ DE CLIENTES (MOBILE-FIRST)
// ==========================================
async function cargarMenu() {
    try {
        const response = await fetch(`${API_BASE}/menu`);
        if (!response.ok) throw new Error("Error cargando el menú");
        
        menuData = await response.json();
        renderizarCatalogo(filtrarProductosPorCategoria(menuData.productos_base));
    } catch (error) {
        console.error("Error al obtener menú:", error);
        const container = document.getElementById('catalog-container');
        if (container) {
            container.innerHTML = `<p class="text-rose-400 text-xs col-span-full text-center py-6">Error al conectar con la carta de jugos.</p>`;
        }
    }
}

function filtrarCategoria(cat) {
    categoriaSeleccionada = cat;
    
    const btns = document.querySelectorAll('#category-filters button');
    btns.forEach(btn => {
        if (btn.innerText.includes(cat) || (cat === 'Todos' && btn.innerText.includes('Todos'))) {
            btn.classList.add('active');
        } else {
            btn.classList.remove('active');
        }
    });

    renderizarCatalogo(filtrarProductosPorCategoria(menuData.productos_base));
}

function filtrarProductosPorCategoria(productos) {
    if (!productos) return [];
    if (categoriaSeleccionada === 'Todos') return productos;
    return productos.filter(p => p.categoria.toLowerCase().includes(categoriaSeleccionada.toLowerCase()));
}

function renderizarCatalogo(productos) {
    const container = document.getElementById('catalog-container');
    if (!container) return;

    if (!productos || productos.length === 0) {
        container.innerHTML = `<p class="text-slate-400 text-xs col-span-full text-center py-8">No hay opciones disponibles en esta sección.</p>`;
        return;
    }

    container.innerHTML = productos.map(prod => {
        const estaDisponible = prod.disponible;
        const opacityClass = estaDisponible ? '' : 'opacity-40 grayscale pointer-events-none relative';

        return `
            <div class="bg-slate-900/90 border border-slate-800 rounded-2xl overflow-hidden flex flex-col justify-between shadow-lg ${opacityClass}">
                <div class="relative w-full h-36 bg-slate-950">
                    <img src="${prod.imagen_url || 'https://images.unsplash.com/photo-1613478223719-2ab802602423?auto=format&fit=crop&w=600&q=80'}" alt="${escapeHtml(prod.nombre)}" class="w-full h-full object-cover">
                    <span class="absolute top-2 left-2 bg-slate-950/80 backdrop-blur-md text-emerald-400 text-[10px] font-extrabold px-2.5 py-0.5 rounded-full border border-slate-800 uppercase tracking-wider">${escapeHtml(prod.categoria)}</span>
                    ${!estaDisponible ? `<span class="absolute top-2 right-2 bg-rose-600 text-white font-extrabold text-[10px] px-2 py-0.5 rounded-full shadow-lg">Agotado</span>` : ''}
                </div>
                <div class="p-3 flex flex-col justify-between flex-1">
                    <div>
                        <h3 class="font-extrabold text-sm text-white ${!estaDisponible ? 'line-through text-slate-500' : ''}">${escapeHtml(prod.nombre)}</h3>
                    </div>
                    <div class="mt-2.5 flex items-center justify-between gap-2">
                        <span class="text-emerald-400 font-black text-base">S/ ${parseFloat(prod.precio).toFixed(2)}</span>
                        ${estaDisponible ? `
                            <button onclick="abrirModalCustomizar(${prod.id})" class="bg-emerald-500 hover:bg-emerald-400 active:scale-95 text-white font-extrabold text-xs py-1.5 px-3 rounded-xl shadow-md shadow-emerald-500/20 transition">
                                + Elegir
                            </button>
                        ` : `
                            <span class="text-[11px] text-rose-400 font-bold">No disponible</span>
                        `}
                    </div>
                </div>
            </div>
        `;
    }).join('');
}

// CÁLCULO DE LÍMITES POKA-YOKE
function obtenerLimitesInsumosPorProducto(producto) {
    const esPanquequeOBowl = producto.categoria.includes("Postre") || 
                             producto.categoria.includes("Bowl") || 
                             producto.nombre.toLowerCase().includes("panqueque") || 
                             producto.nombre.toLowerCase().includes("bowl");
    
    return {
        "Fruta": esPanquequeOBowl ? 3 : 1,
        "Endulzante": 1,
        "Topping": esPanquequeOBowl ? 2 : 1
    };
}

function abrirModalCustomizar(productoId) {
    const prod = menuData.productos_base.find(p => p.id === productoId);
    if (!prod || !prod.disponible) return;

    productoSeleccionadoParaCustom = prod;
    limitesActualesModal = obtenerLimitesInsumosPorProducto(prod);

    document.getElementById('modal-product-title').innerText = prod.nombre;
    document.getElementById('modal-product-desc').innerText = `${prod.categoria} • S/ ${parseFloat(prod.precio).toFixed(2)}`;

    const insumosContainer = document.getElementById('insumos-container');
    const tipos = ["Fruta", "Endulzante", "Topping"];

    insumosContainer.innerHTML = tipos.map(tipo => {
        const insumosDelTipo = menuData.insumos.filter(i => i.tipo === tipo);
        if (insumosDelTipo.length === 0) return '';

        const maximoPermitido = limitesActualesModal[tipo] || 1;

        return `
            <div class="mb-3 bg-slate-900/60 p-2.5 rounded-2xl border border-slate-800/80">
                <div class="flex justify-between items-center mb-1.5">
                    <h4 class="text-[11px] font-black text-emerald-400 uppercase tracking-wider flex items-center gap-1">
                        <span>${tipo === 'Fruta' ? '🍎' : (tipo === 'Endulzante' ? '🍯' : '🌰')}</span>
                        <span>Elegir ${tipo}(s)</span>
                    </h4>
                    <span id="counter-badge-${tipo}" class="text-[10px] font-extrabold bg-emerald-500/20 text-emerald-300 px-2 py-0.5 rounded-full border border-emerald-500/30">
                        0 / ${maximoPermitido}
                    </span>
                </div>

                <div class="chip-group">
                    ${insumosDelTipo.map(ins => {
                        const insDisponible = ins.disponible;
                        return `
                            <div class="${!insDisponible ? 'opacity-40 pointer-events-none' : ''}">
                                <input type="checkbox" id="insumo-${ins.id}" value="${escapeHtml(ins.nombre)}" 
                                       data-tipo="${tipo}" 
                                       data-disponible="${insDisponible}" 
                                       ${!insDisponible ? 'disabled' : ''} 
                                       onchange="actualizarContadorToppingsModal()" 
                                       style="display:none;">
                                <label for="insumo-${ins.id}" id="label-insumo-${ins.id}" class="${!insDisponible ? 'line-through' : ''}">
                                    ${escapeHtml(ins.nombre)} ${!insDisponible ? '(Agotado)' : ''}
                                </label>
                            </div>
                        `;
                    }).join('')}
                </div>
            </div>
        `;
    }).join('');

    actualizarContadorToppingsModal();
    document.getElementById('custom-modal').classList.add('active');
}

function actualizarContadorToppingsModal() {
    const tipos = ["Fruta", "Endulzante", "Topping"];

    tipos.forEach(tipo => {
        const maxTipo = limitesActualesModal[tipo] || 1;
        const checkboxesDisponiblesTipo = document.querySelectorAll(`#insumos-container input[type="checkbox"][data-tipo="${tipo}"][data-disponible="true"]`);
        const marcadosTipo = document.querySelectorAll(`#insumos-container input[type="checkbox"][data-tipo="${tipo}"][data-disponible="true"]:checked`);
        const badge = document.getElementById(`counter-badge-${tipo}`);

        const count = marcadosTipo.length;
        if (badge) {
            badge.innerText = `${count} / ${maxTipo}`;
            if (count >= maxTipo) {
                badge.className = "text-[10px] font-extrabold bg-amber-500/20 text-amber-300 px-2 py-0.5 rounded-full border border-amber-500/30";
            } else {
                badge.className = "text-[10px] font-extrabold bg-emerald-500/20 text-emerald-300 px-2 py-0.5 rounded-full border border-emerald-500/30";
            }
        }

        checkboxesDisponiblesTipo.forEach(cb => {
            const label = document.getElementById(`label-insumo-${cb.id.replace('insumo-', '')}`);
            if (!cb.checked) {
                if (count >= maxTipo) {
                    cb.disabled = true;
                    if (label) label.classList.add('opacity-30', 'cursor-not-allowed', 'pointer-events-none');
                } else {
                    cb.disabled = false;
                    if (label) label.classList.remove('opacity-30', 'cursor-not-allowed', 'pointer-events-none');
                }
            } else {
                cb.disabled = false;
                if (label) label.classList.remove('opacity-30', 'cursor-not-allowed', 'pointer-events-none');
            }
        });
    });
}

function cerrarModal() {
    document.getElementById('custom-modal').classList.remove('active');
    productoSeleccionadoParaCustom = null;
}

function agregarAlCarritoDesdeModal() {
    if (!productoSeleccionadoParaCustom) return;

    const checkboxes = document.querySelectorAll('#insumos-container input[type="checkbox"]:checked');
    const insumosElegidos = Array.from(checkboxes).map(cb => cb.value);

    carrito.push({
        producto_base_id: productoSeleccionadoParaCustom.id,
        nombre_producto: productoSeleccionadoParaCustom.nombre,
        cantidad: 1,
        precio_unitario: productoSeleccionadoParaCustom.precio,
        insumos_seleccionados: insumosElegidos,
        subtotal: productoSeleccionadoParaCustom.precio
    });

    cerrarModal();
    actualizarCarritoUI();
}

function actualizarCarritoUI() {
    const container = document.getElementById('cart-items-container');
    const totalSpan = document.getElementById('cart-total');
    const stickyTotalSpan = document.getElementById('sticky-cart-total');
    const stickyCountSpan = document.getElementById('sticky-cart-count');

    let totalDecimal = 0;
    let cantidadTotal = 0;

    carrito.forEach(item => {
        totalDecimal += parseFloat(item.subtotal);
        cantidadTotal += item.cantidad;
    });

    if (stickyTotalSpan) stickyTotalSpan.innerText = `S/ ${totalDecimal.toFixed(2)}`;
    if (stickyCountSpan) stickyCountSpan.innerText = cantidadTotal;
    if (totalSpan) totalSpan.innerText = `S/ ${totalDecimal.toFixed(2)}`;

    if (!container) return;

    if (carrito.length === 0) {
        container.innerHTML = `<p class="text-slate-400 text-xs text-center py-4">Tu carrito está vacío.</p>`;
        return;
    }

    container.innerHTML = carrito.map((item, index) => {
        const sub = parseFloat(item.subtotal);
        return `
            <div class="flex items-center justify-between p-2.5 bg-slate-900/80 border border-slate-800 rounded-xl">
                <div class="flex-1 pr-2">
                    <div class="font-extrabold text-xs text-white">${escapeHtml(item.nombre_producto)} (x${item.cantidad})</div>
                    <div class="text-[10px] text-slate-400 mt-0.5">
                        ${item.insumos_seleccionados.length > 0 ? item.insumos_seleccionados.join(', ') : 'Sin adicionales'}
                    </div>
                </div>
                <div class="flex items-center gap-2">
                    <span class="font-black text-xs text-emerald-400">S/ ${sub.toFixed(2)}</span>
                    <button onclick="eliminarDelCarrito(${index})" class="text-rose-400 hover:text-rose-300 font-bold text-base px-1">&times;</button>
                </div>
            </div>
        `;
    }).join('');

    actualizarInfoPagoUI();
}

function eliminarDelCarrito(index) {
    carrito.splice(index, 1);
    actualizarCarritoUI();
}

function abrirBottomSheetCarrito() {
    const sheet = document.getElementById('cart-bottom-sheet');
    if (sheet) {
        sheet.classList.add('active');
        actualizarInfoPagoUI();
    }
}

function cerrarBottomSheetCarrito() {
    const sheet = document.getElementById('cart-bottom-sheet');
    if (sheet) sheet.classList.remove('active');
}

function actualizarInfoPagoUI() {
    const infoBox = document.getElementById('info-pago-box');
    if (!infoBox) return;

    const radioMetodo = document.querySelector('input[name="radio-metodo-pago"]:checked');
    const radioMomento = document.querySelector('input[name="radio-momento-pago"]:checked');

    const metodo = radioMetodo ? radioMetodo.value : 'yape';
    const momento = radioMomento ? radioMomento.value : 'inmediato';

    if (metodo === 'yape' && momento === 'inmediato') {
        infoBox.innerHTML = `
            <div class="flex items-center justify-between text-left mb-1.5">
                <div>
                    <span class="text-[9px] font-bold text-slate-400 block uppercase tracking-wider">📱 Yapea o Plinea al:</span>
                    <span class="text-sm font-black text-emerald-400">987 654 321</span>
                </div>
                <button type="button" onclick="copiarNumeroYape()" class="text-[10px] bg-slate-800 text-emerald-300 font-bold px-2 py-0.5 rounded-lg border border-slate-700">
                    📋 Copiar
                </button>
            </div>
            <div class="bg-white p-1.5 rounded-lg inline-block shadow-md">
                <img src="https://api.qrserver.com/v1/create-qr-code/?size=110x110&data=YAPE-PROYECTO-COCONUT" alt="QR Yape" class="w-20 h-20 mx-auto">
            </div>
            <p class="text-[10px] text-slate-300 mt-1">
                👉 Envías el comprobante por WhatsApp al confirmar.
            </p>
        `;
    } else if (metodo === 'yape' && momento === 'despues_consumo') {
        infoBox.innerHTML = `
            <div class="text-left space-y-0.5">
                <span class="text-xs font-black text-emerald-400">📱 Yape al consumir</span>
                <p class="text-[10px] text-slate-300">
                    Pedido directo a cocina. Yapearás al <strong>987 654 321</strong> en caja al finalizar.
                </p>
            </div>
        `;
    } else if (metodo === 'efectivo' && momento === 'despues_consumo') {
        infoBox.innerHTML = `
            <div class="text-left space-y-0.5">
                <span class="text-xs font-black text-amber-400">💵 Efectivo al Consumir</span>
                <p class="text-[10px] text-slate-300">
                    Preparación inmediata. Pagarás en caja al finalizar tu consumo.
                </p>
            </div>
        `;
    } else {
        infoBox.innerHTML = `
            <div class="text-left space-y-0.5">
                <span class="text-xs font-black text-emerald-400">💵 Efectivo en Caja</span>
                <p class="text-[10px] text-slate-300">
                    Por favor acércate a la caja a cancelar tu pedido en efectivo.
                </p>
            </div>
        `;
    }
}

function copiarNumeroYape() {
    navigator.clipboard.writeText('987654321');
    alert('📋 ¡Número Yape (987654321) copiado!');
}

async function enviarPedido() {
    const telefono = document.getElementById('cliente-telefono').value.trim();
    const nombre = document.getElementById('cliente-nombre').value.trim();

    if (!telefono) {
        alert("Por favor ingresa tu número de teléfono.");
        return;
    }

    if (carrito.length === 0) {
        alert("Tu carrito está vacío.");
        return;
    }

    const radioMetodo = document.querySelector('input[name="radio-metodo-pago"]:checked');
    const radioMomento = document.querySelector('input[name="radio-momento-pago"]:checked');

    const metodo = radioMetodo ? radioMetodo.value : 'yape';
    const momento = radioMomento ? radioMomento.value : 'inmediato';

    const payload = {
        telefono_cliente: telefono,
        nombre_cliente: nombre || "Cliente General",
        metodo_pago: metodo,
        momento_pago: momento,
        items: carrito.map(item => ({
            producto_base_id: item.producto_base_id,
            nombre_producto: item.nombre_producto,
            cantidad: item.cantidad,
            precio_unitario: item.precio_unitario.toString(),
            insumos_seleccionados: item.insumos_seleccionados,
            subtotal: item.subtotal.toString()
        }))
    };

    try {
        const response = await fetch(`${API_BASE}/pedidos`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        const data = await response.json();

        if (!response.ok) {
            alert(`⚠️ Aviso: ${data.detail || 'Uno de los insumos ya no está disponible.'}`);
            cargarMenu();
            cerrarBottomSheetCarrito();
            return;
        }

        document.getElementById('created-order-id').innerText = data.id;
        document.getElementById('created-order-total').innerText = `S/ ${parseFloat(data.total).toFixed(2)}`;
        document.getElementById('created-order-metodo').innerText = `${metodo === 'efectivo' ? '💵 Efectivo' : '📱 Yape'} (${momento === 'despues_consumo' ? 'Al Consumir' : 'Ahora'})`;

        const waLink = generarEnlaceWhatsApp(data, nombre, telefono, metodo, momento);
        const waBtn = document.getElementById('whatsapp-order-btn');
        if (waBtn) waBtn.href = waLink;

        cerrarBottomSheetCarrito();
        document.getElementById('payment-modal').classList.add('active');

        window.open(waLink, '_blank');

        carrito = [];
        actualizarCarritoUI();

    } catch (error) {
        console.error("Error al enviar pedido:", error);
        alert("Error de conexión al procesar el pedido.");
    }
}

function generarEnlaceWhatsApp(pedidoData, nombreCliente, telefonoCliente, metodo, momento) {
    let itemsTexto = "";
    if (pedidoData.detalle_items && pedidoData.detalle_items.length > 0) {
        itemsTexto = pedidoData.detalle_items.map(it => 
            `• *${it.cantidad}x ${it.nombre_producto}* (S/ ${parseFloat(it.subtotal).toFixed(2)})\n  └ Insumos: ${it.insumos_seleccionados.length > 0 ? it.insumos_seleccionados.join(', ') : 'Sin adicionales'}`
        ).join('\n');
    }

    const metodoTexto = metodo === 'efectivo' ? '💵 Efectivo' : '📱 Yape / Plin';
    const momentoTexto = momento === 'despues_consumo' ? '🍽️ Pagar al Consumir' : '⚡ Pagar Ahora';

    const mensaje = 
`🥥 *NUEVO PEDIDO - JUGUERÍA COCONUT* 🥥

📋 *Pedido N°:* #${pedidoData.id}
👤 *Cliente:* ${nombreCliente || 'Cliente'} (${telefonoCliente})
💰 *Monto Total:* S/ ${parseFloat(pedidoData.total).toFixed(2)}
💳 *Forma de Pago:* ${metodoTexto} (${momentoTexto})

🛒 *Detalle de tu Pedido:*
${itemsTexto}

${momento === 'despues_consumo' 
    ? '👨‍🍳 *¡Pedido en cocina!* Pagarás S/ ' + parseFloat(pedidoData.total).toFixed(2) + ' al finalizar tu consumo.'
    : '📱 Adjunto aquí mi comprobante por *S/ ' + parseFloat(pedidoData.total).toFixed(2) + '* para prepararlo! 🍹'}`;

    return `https://wa.me/${WHATSAPP_NUMERO}?text=${encodeURIComponent(mensaje)}`;
}

function finalizarModalPago() {
    document.getElementById('payment-modal').classList.remove('active');
}

// ==========================================
// MÓDULO 2: PANEL DEL CAJERO & CAJA
// ==========================================
function switchTabCajero(tab) {
    const secCaja = document.getElementById('section-caja');
    const secInv = document.getElementById('section-inventario');
    const btnCaja = document.getElementById('tab-btn-caja');
    const btnInv = document.getElementById('tab-btn-inventario');

    if (tab === 'caja') {
        secCaja.style.display = 'block';
        secInv.style.display = 'none';
        btnCaja.classList.add('active');
        btnInv.classList.remove('active');
    } else {
        secCaja.style.display = 'none';
        secInv.style.display = 'block';
        btnCaja.classList.remove('active');
        btnInv.classList.add('active');
        cargarControlInventario();
    }
}

async function cargarDatosCajero() {
    await Promise.all([cargarResumenCaja(), cargarPedidosPendientes()]);
}

async function cargarResumenCaja() {
    try {
        const res = await fetch(`${API_BASE}/admin/caja`);
        if (!res.ok) return;

        const data = await res.json();
        document.getElementById('caja-saldo-actual').innerText = `S/ ${parseFloat(data.saldo_actual).toFixed(2)}`;
        document.getElementById('caja-total-ingresos').innerText = `S/ ${parseFloat(data.total_ingresos).toFixed(2)}`;
        document.getElementById('caja-total-egresos').innerText = `S/ ${parseFloat(data.total_egresos).toFixed(2)}`;

        const listContainer = document.getElementById('caja-movimientos-list');
        if (listContainer && data.movimientos) {
            listContainer.innerHTML = data.movimientos.map(mov => `
                <div style="display: flex; justify-content: space-between; align-items: center; padding: 8px 0; border-bottom: 1px solid var(--border-color); font-size: 0.82rem;">
                    <div>
                        <strong style="color: #fff;">${escapeHtml(mov.concepto)}</strong>
                        <div style="font-size: 0.72rem; color: var(--text-muted);">${new Date(mov.fecha_hora).toLocaleTimeString()}</div>
                    </div>
                    <span style="font-weight: 800; color: ${mov.tipo === 'ingreso' ? 'var(--primary)' : 'var(--danger)'};">
                        ${mov.tipo === 'ingreso' ? '+' : '-'} S/ ${parseFloat(mov.monto).toFixed(2)}
                    </span>
                </div>
            `).join('');
        }
    } catch (err) {
        console.error("Error al cargar resumen de caja:", err);
    }
}

async function cargarPedidosPendientes() {
    try {
        const res = await fetch(`${API_BASE}/pedidos`);
        if (!res.ok) return;

        const todosPedidos = await res.json();
        const pendientes = todosPedidos.filter(p => p.estado === 'esperando_pago' || p.estado === 'en_cocina');

        const badgeElem = document.getElementById('badge-pendientes-count');
        if (badgeElem) badgeElem.innerText = pendientes.length;

        const container = document.getElementById('pedidos-pendientes-list');
        if (!container) return;

        if (pendientes.length === 0) {
            container.innerHTML = `<p style="color: var(--text-muted); font-size: 0.85rem;">No hay pedidos pendientes de cobro.</p>`;
            return;
        }

        container.innerHTML = pendientes.map(ped => {
            const items = ped.detalle_items || [];
            const esEfectivo = ped.metodo_pago === 'efectivo';
            const esPostConsumo = ped.momento_pago === 'despues_consumo';

            return `
                <div class="card-mobile" style="border-left: 4px solid ${esEfectivo ? 'var(--info)' : 'var(--accent)'}; padding: 1rem;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
                        <span class="card-title" style="font-size: 1rem;">Pedido #${ped.id}</span>
                        <span class="badge ${esEfectivo ? 'badge-info' : 'badge-warning'}">
                            ${esEfectivo ? '💵 Efectivo' : '📱 Yape'} ${esPostConsumo ? '(Al Consumir)' : ''}
                        </span>
                    </div>
                    <p style="font-size: 0.78rem; color: var(--text-muted); margin-bottom: 8px;">
                        Cliente: <strong>${escapeHtml(ped.telefono_cliente)}</strong> | ${new Date(ped.fecha_hora).toLocaleTimeString()}
                    </p>
                    
                    <div style="margin: 6px 0 10px 0; font-size: 0.82rem; background: #060d19; padding: 8px 10px; border-radius: 10px; border: 1px solid var(--border-color);">
                        ${items.map(it => `
                            <div>• ${it.cantidad}x <strong>${escapeHtml(it.nombre_producto)}</strong> (${it.insumos_seleccionados.join(', ')})</div>
                        `).join('')}
                    </div>

                    <div style="display: flex; flex-direction: column; gap: 8px;">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <span style="font-size: 0.78rem; color: var(--text-muted);">Monto Total</span>
                            <span class="price-tag" style="font-size: 1.25rem;">S/ ${parseFloat(ped.total).toFixed(2)}</span>
                        </div>
                        <div style="display: flex; gap: 6px;">
                            <button onclick="aprobarPago(${ped.id})" class="btn" style="padding: 10px; font-size: 0.85rem; flex: 2;">
                                ✓ Cobrar S/ ${parseFloat(ped.total).toFixed(2)}
                            </button>
                            <button onclick="rechazarPago(${ped.id})" class="btn btn-danger" style="padding: 10px; font-size: 0.85rem; flex: 1;">
                                ✕ Anular
                            </button>
                        </div>
                    </div>
                </div>
            `;
        }).join('');
    } catch (err) {
        console.error("Error al cargar pedidos pendientes:", err);
    }
}

async function aprobarPago(pedidoId) {
    try {
        const res = await fetch(`${API_BASE}/admin/pedidos/${pedidoId}/aprobar`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ concepto_pago: `Cobro Venta Pedido #${pedidoId}` })
        });

        if (res.ok) {
            cargarDatosCajero();
            mostrarToast(`Cobro registrado para Pedido #${pedidoId}`);
        } else {
            const err = await res.json();
            alert(`Error en cobro: ${err.detail}`);
        }
    } catch (err) {
        console.error("Error en aprobarPago:", err);
    }
}

async function rechazarPago(pedidoId) {
    if (!confirm(`¿Anular el pedido #${pedidoId}?`)) return;
    try {
        const res = await fetch(`${API_BASE}/admin/pedidos/${pedidoId}/rechazar`, { method: 'POST' });
        if (res.ok) {
            cargarDatosCajero();
        }
    } catch (err) {
        console.error("Error en rechazarPago:", err);
    }
}

// CONTROL DE INVENTARIO
async function cargarControlInventario() {
    try {
        const res = await fetch(`${API_BASE}/menu/admin/inventario_completo`);
        if (!res.ok) return;

        inventarioDataAdmin = await res.json();
        filtrarSeleccionInsumos();
        filtrarSeleccionProductos();
        renderizarControlRecetas(inventarioDataAdmin.recetas_dependencias);

    } catch (err) {
        console.error("Error al cargar inventario:", err);
    }
}

function filtrarSeleccionInsumos() {
    const sel = document.getElementById('filter-insumos-select');
    if (!sel) return;
    const valor = sel.value;

    if (valor === 'Todos') {
        renderizarControlInsumos(inventarioDataAdmin.insumos);
    } else {
        const filtrados = inventarioDataAdmin.insumos.filter(ins => ins.tipo.toLowerCase().includes(valor.toLowerCase()));
        renderizarControlInsumos(filtrados);
    }
}

function filtrarSeleccionProductos() {
    const sel = document.getElementById('filter-productos-select');
    if (!sel) return;
    const valor = sel.value;

    if (valor === 'Todos') {
        renderizarControlProductos(inventarioDataAdmin.productos_base);
    } else {
        const filtrados = inventarioDataAdmin.productos_base.filter(p => p.categoria.toLowerCase().includes(valor.toLowerCase()));
        renderizarControlProductos(filtrados);
    }
}

function renderizarControlInsumos(lista) {
    const container = document.getElementById('inventory-insumos-list');
    if (!container) return;

    if (!lista || lista.length === 0) {
        container.innerHTML = `<p style="color: var(--text-muted); font-size: 0.85rem;">No hay insumos en esta categoría.</p>`;
        return;
    }

    container.innerHTML = lista.map(ins => `
        <div style="display: flex; justify-content: space-between; align-items: center; background: #060d19; padding: 8px 12px; border-radius: 10px; border: 1px solid var(--border-color);">
            <div>
                <strong style="color: #fff; font-size: 0.85rem;">${escapeHtml(ins.nombre)}</strong>
                <span style="font-size: 0.72rem; color: var(--primary); margin-left: 4px; font-weight: 700;">(${escapeHtml(ins.tipo)})</span>
            </div>
            <button onclick="toggleDisponibilidadInsumo(${ins.id}, ${!ins.disponible})" 
                    class="btn ${ins.disponible ? '' : 'btn-danger'}" 
                    style="width: auto; padding: 6px 12px; font-size: 0.78rem;">
                ${ins.disponible ? '✓ Disponible' : '✕ Agotado'}
            </button>
        </div>
    `).join('');
}

function renderizarControlProductos(lista) {
    const container = document.getElementById('inventory-productos-list');
    if (!container) return;

    if (!lista || lista.length === 0) {
        container.innerHTML = `<p style="color: var(--text-muted); font-size: 0.85rem;">No hay productos en esta categoría.</p>`;
        return;
    }

    container.innerHTML = lista.map(prod => `
        <div style="display: flex; justify-content: space-between; align-items: center; background: #060d19; padding: 8px 12px; border-radius: 10px; border: 1px solid var(--border-color);">
            <div>
                <strong style="color: #fff; font-size: 0.85rem;">${escapeHtml(prod.nombre)}</strong>
                <span style="font-size: 0.72rem; color: var(--text-muted); margin-left: 4px;">S/ ${parseFloat(prod.precio).toFixed(2)}</span>
            </div>
            <button onclick="toggleDisponibilidadProducto(${prod.id}, ${!prod.disponible})" 
                    class="btn ${prod.disponible ? '' : 'btn-danger'}" 
                    style="width: auto; padding: 6px 12px; font-size: 0.78rem;">
                ${prod.disponible ? '✓ Disponible' : '✕ Agotado'}
            </button>
        </div>
    `).join('');
}

function renderizarControlRecetas(lista) {
    const container = document.getElementById('inventory-recetas-list');
    if (!container) return;

    if (!lista || lista.length === 0) {
        container.innerHTML = `<p style="color: var(--text-muted); font-size: 0.85rem;">No hay reglas de recetas.</p>`;
        return;
    }

    container.innerHTML = lista.map(rec => `
        <div style="display: flex; justify-content: space-between; align-items: center; background: #060d19; padding: 8px 10px; border-radius: 8px; border: 1px solid var(--border-color); font-size: 0.8rem;">
            <div>
                <strong style="color: #fff;">${escapeHtml(rec.nombre_producto)}</strong> requiere <strong style="color: var(--primary);">${escapeHtml(rec.nombre_insumo)}</strong>
            </div>
            <span class="badge badge-warning" style="font-size: 0.7rem;">Obligatorio</span>
        </div>
    `).join('');
}

async function toggleDisponibilidadInsumo(insumoId, nuevoEstado) {
    try {
        const res = await fetch(`${API_BASE}/menu/insumos/${insumoId}/disponibilidad?disponible=${nuevoEstado}`, { method: 'PATCH' });
        if (res.ok) {
            await cargarControlInventario();
            cargarMenu();
            mostrarToast("Inventario actualizado.");
        }
    } catch (err) {
        console.error("Error al conmutar insumo:", err);
    }
}

async function toggleDisponibilidadProducto(productoId, nuevoEstado) {
    try {
        const res = await fetch(`${API_BASE}/menu/productos/${productoId}/disponibilidad?disponible=${nuevoEstado}`, { method: 'PATCH' });
        if (res.ok) {
            await cargarControlInventario();
            cargarMenu();
            mostrarToast("Estado de producto actualizado.");
        }
    } catch (err) {
        console.error("Error al conmutar producto:", err);
    }
}

function guardarCambiosStockManual() {
    mostrarToast("✅ Cambios de disponibilidad guardados.");
}

function mostrarToast(mensaje) {
    const toast = document.getElementById('toast-notification');
    if (!toast) return;
    toast.innerText = mensaje;
    toast.classList.add('show');
    setTimeout(() => toast.classList.remove('show'), 3000);
}

// ==========================================
// MÓDULO 3: KDS PANTALLA DE COCINA
// ==========================================
async function cargarKDS() {
    try {
        const res = await fetch(`${API_BASE}/kds/activos`);
        if (!res.ok) return;

        const data = await res.json();

        const totalBadge = document.getElementById('kds-total-pedidos-badge');
        if (totalBadge) totalBadge.innerText = `${data.total_pedidos_en_cocina} Pedido(s)`;

        const batchContainer = document.getElementById('kds-batch-container');
        if (batchContainer) {
            if (!data.resumen_produccion_lotes || data.resumen_produccion_lotes.length === 0) {
                batchContainer.innerHTML = `<p style="color: #a7f3d0; font-size: 0.8rem;">Sin lotes requeridos en este momento.</p>`;
            } else {
                batchContainer.innerHTML = data.resumen_produccion_lotes.map(batch => `
                    <div style="background: #060d19; border: 1px solid var(--primary); padding: 6px 12px; border-radius: 12px; display: flex; align-items: center; gap: 8px; font-size: 0.82rem; font-weight: 800; color: #fff;">
                        <span style="background: var(--primary-gradient); color: #fff; width: 24px; height: 24px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 0.85rem;">${batch.cantidad_total}</span>
                        <span>${escapeHtml(batch.nombre_producto)}</span>
                    </div>
                `).join('');
            }
        }

        const ordersContainer = document.getElementById('kds-orders-container');
        if (ordersContainer) {
            if (!data.pedidos_para_ensamble || data.pedidos_para_ensamble.length === 0) {
                ordersContainer.innerHTML = `<p style="color: var(--text-muted); font-size: 0.85rem;">No hay comandas activas pendientes.</p>`;
                return;
            }

            ordersContainer.innerHTML = data.pedidos_para_ensamble.map(ped => `
                <div class="card-mobile" style="border-top: 4px solid var(--primary); padding: 1rem;">
                    <div>
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
                            <span class="card-title" style="font-size: 1rem;">Comanda #${ped.pedido_id}</span>
                            <span class="badge badge-info" style="font-size: 0.72rem;">${new Date(ped.fecha_hora).toLocaleTimeString()}</span>
                        </div>
                        <p style="font-size: 0.78rem; color: var(--text-muted); margin-bottom: 8px;">
                            Cliente: <strong>${escapeHtml(ped.telefono_cliente)}</strong>
                        </p>

                        <div style="display: flex; flex-direction: column; gap: 6px; margin-bottom: 0.85rem;">
                            ${ped.items.map(it => `
                                <div style="background: #060d19; padding: 8px 10px; border-radius: 8px; border: 1px solid var(--border-color);">
                                    <div style="font-weight: 800; color: #fff; font-size: 0.85rem;">• ${it.cantidad}x ${escapeHtml(it.nombre_producto)}</div>
                                    <div style="font-size: 0.78rem; color: var(--primary); margin-top: 2px;">
                                        👉 ${it.insumos_seleccionados.length > 0 ? it.insumos_seleccionados.join(' + ') : 'Sin adicionales'}
                                    </div>
                                </div>
                            `).join('')}
                        </div>
                    </div>

                    <button onclick="completarPedidoKDS(${ped.pedido_id})" class="btn" style="padding: 10px; font-size: 0.85rem;">
                        ✓ Marcar Listo
                    </button>
                </div>
            `).join('');
        }

    } catch (err) {
        console.error("Error cargando KDS:", err);
    }
}

async function completarPedidoKDS(pedidoId) {
    try {
        const res = await fetch(`${API_BASE}/kds/pedidos/${pedidoId}/completar`, { method: 'POST' });
        if (res.ok) {
            cargarKDS();
        } else {
            const err = await res.json();
            alert(`Error completando comanda: ${err.detail}`);
        }
    } catch (err) {
        console.error("Error en completarPedidoKDS:", err);
    }
}

// UTILS
function escapeHtml(str) {
    if (!str) return '';
    return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;');
}

// LISTENERS INICIALES
document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('catalog-container')) {
        cargarMenu();
    }
    const btnCrear = document.getElementById('btn-crear-pedido');
    if (btnCrear) {
        btnCrear.addEventListener('click', enviarPedido);
    }
});
